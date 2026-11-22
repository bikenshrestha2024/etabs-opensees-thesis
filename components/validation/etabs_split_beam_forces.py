"""Consolidate ETABS Element Forces - Beams from multiple XLSX files/sheets.

[REF docs/source/components/validation/etabs_split_beam_forces.py.md]
Excel's 1,048,576-row sheet limit is NOT the limit for this importer.
Sources remain read-only, each matching worksheet is consumed, and output
CSV may contain more than one million data rows. SQLite provides a disk-backed
unique-key store instead of retaining all station rows in Python RAM.

Strict mode rejects different gravity cases and conflicting overlapping rows.
This is source ETABS data ONLY, not ETABS/OpenSees reaction equivalence.

Usage:
 python -m components.validation.etabs_split_beam_forces OUTPUT_DIR part1.xlsx part2.xlsx part3.xlsx
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sqlite3
import tempfile
from pathlib import Path

IDENTITY = ("Story", "Unique Name", "Output Case", "Station")
CASE_NAME = "1. DL + LL"
NEEDED = ("story", "unique name", "output case", "station")


def _normalized(value):
    return " ".join(str(value if value is not None else "").strip().lower().split())


def _digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fp:
        for block in iter(lambda: fp.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def _headers(path):
    """Find all beam-force tables in a workbook, without loading data rows."""
    from openpyxl import load_workbook
    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        candidates = []
        for sheet in wb:
            for ix, record in enumerate(sheet.iter_rows(values_only=True)):
                labels = {_normalized(v): n for n, v in enumerate(record)
                          if v is not None and str(v).strip()}
                if all(k in labels for k in NEEDED):
                    columns = [str(v).strip() if v is not None else ""
                               for v in record]
                    named = [v for v in columns if v]
                    if len(named) != len(set(named)):
                        raise ValueError(f"{path}: duplicate column names in {sheet.title}")
                    candidates.append((sheet.title, ix, columns))
                    break
                if ix >= 29:
                    break
        if not candidates:
            raise ValueError(
                f"{path}: no Element Forces - Beams table found. "
                "Choose Beam Forces Element 1/2/3 (or workbook with those sheets), "
                "not a different ETABS export.")
        return candidates
    finally:
        wb.close()


def _stream_tables(path):
    """Yield (sheet-name, row) from every matching Excel worksheet."""
    from openpyxl import load_workbook
    candidates = _headers(path)
    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        for sheet_name, heading, columns in candidates:
            for record in wb[sheet_name].iter_rows(
                    min_row=heading + 2, values_only=True):
                if not any(v is not None and str(v).strip() for v in record):
                    continue
                row = {column: record[i] if i < len(record) else None
                       for i, column in enumerate(columns) if column}
                if any(row.get(col) is None for col in IDENTITY):
                    raise ValueError(
                        f"{path} / {sheet_name}: incomplete beam-force identity")
                yield sheet_name, row
    finally:
        wb.close()


def _same_value(lhs, rhs, *, atol, rtol):
    if lhs is None and rhs is None:
        return True
    if isinstance(lhs, (int, float)) and isinstance(rhs, (int, float)):
        return (math.isfinite(float(lhs)) and math.isfinite(float(rhs))
                and math.isclose(float(lhs), float(rhs),
                                 abs_tol=atol, rel_tol=rtol))
    return _normalized(lhs) == _normalized(rhs)


def consolidate(inputs, output_dir, *, case=CASE_NAME, atol=1e-6, rtol=1e-9):
    """[REF docs/source/components/validation/etabs_split_beam_forces.py.md]
    Merge any positive number of workbooks and all their beam-force sheets.
    No partial CSV/manifest is published on input validation failure.
    """
    if not inputs:
        raise ValueError("At least one ETABS beam-force workbook required")
    paths = [Path(p).expanduser().resolve() for p in inputs]
    if len({str(p).casefold() for p in paths}) != len(paths):
        raise ValueError("Same input workbook supplied twice")
    target = Path(output_dir).expanduser().resolve()
    if target.exists() and any(target.iterdir()):
        raise FileExistsError("Output directory must be new or empty")
    for path in paths:
        if (not path.is_file() or path.is_symlink()
                or path.suffix.lower() not in (".xlsx", ".xlsm")):
            raise ValueError("Missing, linked or non-Excel input file: " + str(path))

    columns = None
    manifest = []
    source_rows = 0
    duplicate_count = 0
    with tempfile.TemporaryDirectory(prefix="etabs_beam_sqlite_") as scratch:
        database = Path(scratch) / "stations.sqlite"
        db = sqlite3.connect(str(database))
        try:
            db.execute("CREATE TABLE stations (k TEXT PRIMARY KEY, row_json TEXT NOT NULL)")
            for path in paths:
                counts = {}
                for sheet_name, row in _stream_tables(path):
                    if _normalized(row["Output Case"]) != _normalized(case):
                        raise ValueError(
                            f"{path} / {sheet_name}: unexpected Output Case "
                            f"{row['Output Case']!r} (expected {case!r})")
                    keys = list(row)
                    if columns is None:
                        columns = keys
                    elif set(keys) != set(columns):
                        raise ValueError(
                            f"{path} / {sheet_name}: beam-force column schema "
                            "differs between parts")
                    # Preserve local identity, load case, output station, and
                    # response step. Do not collapse unlike histories.
                    identity = [_normalized(row[n]) for n in IDENTITY]
                    identity += [_normalized(row.get(n)) for n in
                                 ("Step Type", "Step Number") if n in row]
                    key = json.dumps(identity, ensure_ascii=False,
                                     separators=(",", ":"))
                    prior = db.execute(
                        "SELECT row_json FROM stations WHERE k=?", (key,)).fetchone()
                    if prior:
                        previous = json.loads(prior[0])
                        for col in columns:
                            if not _same_value(previous[col], row[col],
                                               atol=atol, rtol=rtol):
                                raise ValueError(
                                    f"Conflicting duplicate at {identity}, "
                                    f"column {col}: {previous[col]} vs {row[col]}")
                        duplicate_count += 1
                    else:
                        db.execute(
                            "INSERT INTO stations (k,row_json) VALUES (?,?)",
                            (key, json.dumps(row, allow_nan=False,
                                             ensure_ascii=False, default=str)))
                    counts[sheet_name] = counts.get(sheet_name, 0) + 1
                    source_rows += 1
                manifest.append({
                    "filename": path.name, "source_sha256": _digest(path),
                    "rows_read": sum(counts.values()),
                    "sheets": [{"name": name, "rows_read": n}
                               for name, n in counts.items()],
                })
            if not source_rows:
                raise ValueError("No beam-force rows recovered from selected sources")
            db.commit()
            unique = db.execute("SELECT COUNT(*) FROM stations").fetchone()[0]
            # The CSV is emitted only after every source row is validated.
            target.mkdir(parents=True, exist_ok=True)
            output = target / "ETABS_Beam_Forces_Consolidated.csv"
            with output.open("w", newline="", encoding="utf-8-sig") as fp:
                writer = csv.DictWriter(fp, fieldnames=columns, extrasaction="raise")
                writer.writeheader()
                for (payload,) in db.execute(
                        "SELECT row_json FROM stations ORDER BY k"):
                    writer.writerow(json.loads(payload))
        finally:
            db.close()

    summary = {
        "status": "ETABS_BEAM_FORCE_SOURCE_ONLY_NOT_OPENSEES_EQUIVALENCE",
        "case": case,
        "input_files": manifest,
        "source_rows": source_rows,
        "exact_or_tolerance_matched_overlaps": duplicate_count,
        "unique_rows": unique,
        "output": str(output),
        "output_format": "CSV_UNLIMITED_EXCEL_WORKSHEET_ROWS",
        "scope": "ETABS beam stations only; not joint reactions or solver matching",
        "limitations": [
            "Unexported stations cannot be verified from selected files",
            "Map ETABS unique names, local axes, stations and offsets to model",
            "Source table aggregation does not prove ETABS/OpenSees equivalence",
        ],
    }
    (target / "ETABS_Beam_Forces_Manifest.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    return summary


def main(argv=None):
    """[REF docs/source/components/validation/etabs_split_beam_forces.py.md]"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir")
    parser.add_argument("inputs", nargs="+")
    args = parser.parse_args(argv)
    print(json.dumps(consolidate(args.inputs, args.output_dir), indent=2))


if __name__ == "__main__":
    main()

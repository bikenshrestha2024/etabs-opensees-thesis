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
            # The identity columns are also present in some non-beam ETABS
            # tables; require a beam-specific worksheet title, export name,
            # or ETABS caption to avoid quietly importing column forces.
            beam_identity = (
                ("beam" in sheet.title.casefold()
                 and "force" in sheet.title.casefold())
                or ("beam forces element" in Path(path).stem.casefold())
            )
            for ix, record in enumerate(sheet.iter_rows(values_only=True)):
                if any("element forces - beams" in _normalized(value)
                       for value in record if value is not None):
                    beam_identity = True
                labels = {_normalized(v): n for n, v in enumerate(record)
                          if v is not None and str(v).strip()}
                if all(k in labels for k in NEEDED):
                    if not beam_identity:
                        # Same column shape is not evidence of a beam table.
                        break
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


_NATIVE_UNITS = {'Station': 'm', 'Elem Station': 'm', 'P': 'kN', 'V2': 'kN', 'V3': 'kN', 'T': 'kN-m', 'M2': 'kN-m', 'M3': 'kN-m'}


def _native_units_row(row):
    return (set(_NATIVE_UNITS).issubset(row)
            and all(row.get(name) == value for name, value in _NATIVE_UNITS.items())
            and all(value in (None, '') for name, value in row.items() if name not in _NATIVE_UNITS))


def _stream_tables(path, *, require_native_units=False):
    """Yield (sheet-name, row) from every matching Excel worksheet."""
    from openpyxl import load_workbook
    candidates = _headers(path)
    wb = load_workbook(path, read_only=True, data_only=not require_native_units)
    try:
        for sheet_name, heading, columns in candidates:
            for source_row, record in enumerate(wb[sheet_name].iter_rows(
                    min_row=heading + 2, values_only=True), start=heading + 2):
                row = {column: record[i] if i < len(record) else None
                       for i, column in enumerate(columns) if column}
                if require_native_units and source_row == heading + 2 and not _native_units_row(row):
                    raise ValueError(f"{path} / {sheet_name}: expected native beam-force table units")
                if not any(v is not None and str(v).strip() for v in record):
                    continue
                # Native ETABS exports carry a unit row immediately after
                # the headers. Skip only the exact kN-m table unit signature.
                if source_row == heading + 2 and _native_units_row(row):
                    continue
                if any(row.get(col) in (None, "") for col in IDENTITY):
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


def _case_is_selected(row, case, *, select_exact_case=False):
    """Strict legacy mode or explicitly requested literal case projection."""
    if select_exact_case:
        return row["Output Case"] == case
    if _normalized(row["Output Case"]) != _normalized(case):
        raise ValueError(f"unexpected Output Case {row['Output Case']!r} (expected {case!r})")
    return True


_NATIVE_IDENTITY = ("Story", "Beam", "Unique Name", "Output Case", "Case Type",
                    "Step Type", "Step Number", "Station", "Element", "Elem Station", "Location")


def _native_exact_identity(row):
    """Preserve complete native identity; do not round or case-fold."""
    if not set(_NATIVE_IDENTITY).union(_NATIVE_UNITS).issubset(row):
        raise ValueError("Incomplete native beam result schema")
    for name in ("Story", "Beam", "Unique Name", "Output Case", "Case Type", "Element"):
        if row[name] is None or not str(row[name]).strip():
            raise ValueError(f"Missing native beam identity: {name}")
    for name in _NATIVE_UNITS:
        value = row[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"Invalid native numeric beam field: {name}")
    if row["Station"] < 0 or row["Elem Station"] < 0:
        raise ValueError("Negative native beam station")
    return [row[name] for name in _NATIVE_IDENTITY]


def consolidate(inputs, output_dir, *, case=CASE_NAME, atol=1e-6, rtol=1e-9,
                select_exact_case=False, all_cases=False):
    """[REF docs/source/components/validation/etabs_split_beam_forces.py.md]
    Merge any positive number of workbooks and all their beam-force sheets.
    No partial CSV/manifest is published on input validation failure.
    """
    if all_cases and select_exact_case:
        raise ValueError("All-case and exact-case selection are mutually exclusive")
    if not isinstance(case, str) or not case.strip():
        raise ValueError("Specify a nonblank ETABS output case")
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
    scanned_source_rows = 0
    duplicate_count = 0
    with tempfile.TemporaryDirectory(prefix="etabs_beam_sqlite_") as scratch:
        database = Path(scratch) / "stations.sqlite"
        db = sqlite3.connect(str(database))
        try:
            db.execute("CREATE TABLE stations (k TEXT PRIMARY KEY, row_json TEXT NOT NULL)")
            for path in paths:
                counts, scanned, excluded, selected_cases = {}, {}, {}, {}
                digest_before = _digest(path)
                for sheet_name, row in _stream_tables(path, require_native_units=all_cases):
                    scanned[sheet_name] = scanned.get(sheet_name, 0) + 1
                    scanned_source_rows += 1
                    keys = list(row)
                    if columns is None:
                        columns = keys
                    elif set(keys) != set(columns):
                        raise ValueError(
                            f"{path} / {sheet_name}: beam-force column schema "
                            "differs between parts")
                    try:
                        selected = all_cases or _case_is_selected(row, case, select_exact_case=select_exact_case)
                    except ValueError as exc:
                        raise ValueError(f"{path} / {sheet_name}: {exc}") from exc
                    if not selected:
                        name = str(row["Output Case"])
                        excluded[name] = excluded.get(name, 0) + 1
                        continue
                    # Preserve local identity, load case, output station, and
                    # response step. Do not collapse unlike histories.
                    if all_cases:
                        identity = _native_exact_identity(row)
                    else:
                        identity = [_normalized(row[n]) for n in IDENTITY]
                        identity += [_normalized(row.get(n)) for n in
                                     ("Step Type", "Step Number") if n in row]
                    serialized = json.dumps(row, allow_nan=False, ensure_ascii=False,
                                            sort_keys=True, default=str)
                    key = json.dumps(identity, ensure_ascii=False,
                                     separators=(",", ":"))
                    prior = db.execute(
                        "SELECT row_json FROM stations WHERE k=?", (key,)).fetchone()
                    if prior:
                        if all_cases and prior[0] != serialized:
                            raise ValueError(f"Conflicting duplicate at {identity}")
                        previous = json.loads(prior[0])
                        for col in (() if all_cases else columns):
                            if not _same_value(previous[col], row[col],
                                               atol=atol, rtol=rtol):
                                raise ValueError(
                                    f"Conflicting duplicate at {identity}, "
                                    f"column {col}: {previous[col]} vs {row[col]}")
                        duplicate_count += 1
                    else:
                        db.execute(
                            "INSERT INTO stations (k,row_json) VALUES (?,?)",
                            (key, serialized))
                    name = str(row["Output Case"])
                    selected_cases[name] = selected_cases.get(name, 0) + 1
                    counts[sheet_name] = counts.get(sheet_name, 0) + 1
                    source_rows += 1
                if _digest(path) != digest_before:
                    raise ValueError(f"{path}: source workbook changed during scan")
                manifest.append({
                    "filename": path.name, "source_sha256": digest_before,
                    "rows_read": sum(counts.values()),
                    "rows_scanned": sum(scanned.values()),
                    "excluded_case_row_counts": excluded,
                    "selected_case_row_counts": selected_cases,
                    "sheets": [{"name": name, "rows_read": counts.get(name, 0),
                                "rows_scanned": n, "reached_excel_data_row_limit": n >= 1048573}
                               for name, n in scanned.items()],
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
        "case": None if all_cases else case,
        "input_files": manifest,
        "source_rows": source_rows,
        "scanned_source_rows": scanned_source_rows,
        "case_selection_policy": ("ALL_NATIVE_CASES_EXACT" if all_cases else
                                  "EXACT_EXPLICIT_PROJECTION" if select_exact_case else
                                  "STRICT_SINGLE_CASE"),
        "overlap_policy": "EXACT_NATIVE_PAYLOAD" if all_cases else "LEGACY_TOLERANCE",
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
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--all-cases", action="store_true",
                           help="Consolidate every native case using exact result identity and payload")
    selection.add_argument("--select-exact-case", metavar="CASE",
                        help="Explicitly select one literal case from all-case exports; "
                             "report excluded rows without claiming complete coverage")
    args = parser.parse_args(argv)
    print(json.dumps(consolidate(args.inputs, args.output_dir,
                                case=CASE_NAME if args.select_exact_case is None else args.select_exact_case,
                                select_exact_case=args.select_exact_case is not None,
                                all_cases=args.all_cases), indent=2))


if __name__ == "__main__":
    main()

"""Consolidate split ETABS 'Element Forces - Beams' Excel tables without row loss.

All input XLSX files remain unmodified. Use streaming workbook readers and CSV
output: the original ETABS full-table sheet can hit Excel's 1,048,576-row limit.
Duplicate keys must agree numerically and textually or the audit fails closed.

Usage:
 python -m components.validation.etabs_split_beam_forces OUTPUT_DIR part1.xlsx part2.xlsx part3.xlsx
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

IDENTITY = ("Story", "Unique Name", "Output Case", "Station")
IGNORED_IDENTITY = {"Label", "Case Type", "Step Type", "Step Number"}
CASE_NAME = "1. DL + LL"


def _normalized(value):
    return " ".join(str(value if value is not None else "").strip().lower().split())


def _digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fp:
        for block in iter(lambda: fp.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def _stream_rows(path):
    from openpyxl import load_workbook
    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        candidates = []
        for sheet in wb:
            # Search first 30 rows; ETABS exports sometimes prefix a table
            # caption and units above the actual column names.
            iterator = sheet.iter_rows(values_only=True)
            for ix, record in enumerate(iterator):
                labels = {_normalized(v): n for n, v in enumerate(record)
                          if v is not None and str(v).strip()}
                needed = ("story", "unique name", "output case", "station")
                if all(k in labels for k in needed):
                    columns = [str(v).strip() if v is not None else ""
                               for v in record]
                    candidates.append((sheet.title, ix, columns))
                    break
                if ix >= 29:
                    break
        if len(candidates) != 1:
            raise ValueError(f"{path}: expected exactly one beam-force table, found {len(candidates)}")
        name, heading, columns = candidates[0]
        if len(set(c for c in columns if c)) != len([c for c in columns if c]):
            raise ValueError(f"{path}: duplicate column names in sheet {name}")
        for record in wb[name].iter_rows(min_row=heading + 2, values_only=True):
            if not any(v is not None and str(v).strip() for v in record):
                continue
            row = {column: record[i] if i < len(record) else None
                   for i, column in enumerate(columns) if column}
            if any(row.get(col) is None for col in IDENTITY):
                raise ValueError(f"{path}: incomplete beam-force identity in {name}")
            yield row
    finally:
        wb.close()


def consolidate(inputs, output_dir, *, case=CASE_NAME, atol=1e-6, rtol=1e-9):
    if not inputs or len(inputs) < 1:
        raise ValueError("At least one ETABS beam-force workbook required")
    paths = [Path(x).resolve() for x in inputs]
    if len(set(paths)) != len(paths):
        raise ValueError("Same input workbook supplied twice")
    target = Path(output_dir).resolve()
    if target.exists() and any(target.iterdir()):
        raise FileExistsError("Output directory must be new or empty")
    records = {}
    column_names = None
    manifest = []
    duplicate_count = 0
    for path in paths:
        if not path.is_file() or path.is_symlink():
            raise ValueError("Missing or linked input file: " + str(path))
        count = 0
        for row in _stream_rows(path):
            if _normalized(row["Output Case"]) != _normalized(case):
                raise ValueError(f"{path}: unexpected Output Case {row['Output Case']!r}")
            keys = list(row)
            if column_names is None:
                column_names = keys
            elif set(keys) != set(column_names):
                raise ValueError(f"{path}: beam-force column schema differs between exports")
            # A unique beam may have multiple stations, but a station must
            # never be conflated across distinct steps.
            key = tuple(_normalized(row[n]) for n in IDENTITY)
            extra_key = tuple(_normalized(row.get(k)) for k in
                              ("Step Type", "Step Number") if k in row)
            key += extra_key
            existing = records.get(key)
            if existing is not None:
                for col in column_names:
                    lhs, rhs = existing[col], row[col]
                    if lhs is None and rhs is None:
                        continue
                    if isinstance(lhs, (int, float)) and isinstance(rhs, (int, float)):
                        if not (math.isfinite(float(lhs)) and math.isfinite(float(rhs))
                                and math.isclose(float(lhs), float(rhs), abs_tol=atol, rel_tol=rtol)):
                            raise ValueError(f"Conflicting duplicate at {key}, column {col}: {lhs} vs {rhs}")
                    elif _normalized(lhs) != _normalized(rhs):
                        raise ValueError(f"Conflicting duplicate at {key}, column {col}: {lhs} vs {rhs}")
                duplicate_count += 1
            else:
                records[key] = row
            count += 1
        manifest.append(dict(filename=path.name, source_sha256=_digest(path),
                             rows_read=count))
    if not records:
        raise ValueError("No beam-force rows recovered from source exports")
    # Fail before publishing a partial success. CSV has no worksheet row cap.
    target.mkdir(parents=True, exist_ok=True)
    output = target / "ETABS_Beam_Forces_Consolidated.csv"
    with output.open("w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(fp, fieldnames=column_names, extrasaction="raise")
        writer.writeheader()
        for key in sorted(records):
            writer.writerow(records[key])
    summary = dict(status="ETABS_BEAM_FORCE_SOURCE_ONLY_NOT_OPENSEES_EQUIVALENCE",
                   case=case, input_files=manifest, source_rows=sum(x["rows_read"] for x in manifest),
                   exact_or_tolerance_matched_overlaps=duplicate_count,
                   unique_rows=len(records), output=str(output),
                   scope="ETABS beam stations only; no joint reactions, wall-shell resultants or solver matching",
                   limitations=["Split workbooks do not verify unexported beam stations",
                                "Map ETABS member unique names and end locations to assembled solver segments",
                                "Rigid offsets, force axes and output station convention require comparison"])
    (target / "ETABS_Beam_Forces_Manifest.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir")
    parser.add_argument("inputs", nargs="+")
    args = parser.parse_args(argv)
    print(json.dumps(consolidate(args.inputs, args.output_dir), indent=2))


if __name__ == "__main__":
    main()

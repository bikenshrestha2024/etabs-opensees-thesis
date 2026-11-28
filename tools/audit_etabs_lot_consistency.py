"""[REF docs/source/tools/audit_etabs_lot_consistency.py.md]
Read explicitly selected ETABS analysis lots and write one consistency report.

Reference evidence only: no source workbook is modified, moved or uploaded, no
absolute path is written, and the report is never engineering acceptance.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCHEMA = "ETABS_LOT_CONSISTENCY_AUDIT_V1"


def _public_files(entries):
    """Keep identity (basename, size, SHA-256, worksheet inventory); drop local paths."""
    keep = ("sha256", "size_bytes", "status", "worksheet_count")
    out = []
    for position, entry in enumerate(entries, 1):
        record = {"lot_position": position,
                  "file_name": Path(entry.get("source_path") or entry.get("path") or "").name}
        record.update({k: entry[k] for k in keep if k in entry})
        record["worksheets"] = [
            {k: s[k] for k in ("sheet", "status", "nonempty_rows", "populated_cells", "numeric_cells",
                               "formula_cells", "error_cells", "nonfinite_numeric_cells", "content_sha256")
             if k in s} for s in entry.get("worksheets", ())]
        out.append(record)
    return out


def build_audit_document(paths, *, row_database, audit=None, report=None, progress=None):
    """Run (or accept precomputed) workbook audit and reference ingest; return the document.

    ``paths`` are the distinct lots to ingest as ONE reference. Pass every file
    to ``audit`` only; ``read_analysis_reference`` rejects a table that two
    workbooks both carry, so split parts of a combined lot cannot be mixed in.
    """
    from components.gravity.etabs_reaction_support_filter import PROJECT_PRIMARY_32
    from components.inputs.etabs_table_bundle import read_analysis_reference
    from components.validation.etabs_lot_consistency import (
        AnalysisReferenceRows, base_reaction_equilibrium, lot_consistency_report,
        time_history_reference_envelopes)
    if report is None:
        report = read_analysis_reference([Path(p) for p in paths], progress=progress, row_database=row_database)
    source = AnalysisReferenceRows(report, row_database)
    consistency = lot_consistency_report(source, expected_support_tags=PROJECT_PRIMARY_32, audit=audit)
    equilibrium = base_reaction_equilibrium(
        source.rows("Base Reactions"), source.rows("Joint Reactions"),
        source.rows("Objects and Elements - Joints"))
    envelopes = time_history_reference_envelopes(source)
    checks = report["checks"]
    return {
        "schema": SCHEMA, "status": "REFERENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE",
        "engineering_acceptance": "NOT_VERIFIED", "source_model_identity": "UNVERIFIED",
        "ingested_files": _public_files(report["files"]),
        "all_sheet_audit_files": _public_files(audit["files"]) if audit else None,
        "all_sheet_audit_totals": ({k: audit[k] for k in (
            "worksheet_count", "fully_scanned_worksheets", "nonempty_rows", "populated_cells")} if audit else None),
        "reference_tables": {name: {"unique_rows": t["unique_row_count"], "cases": len(t["case_row_counts"])}
                             for name, t in sorted(report["tables"].items())},
        "missing_tables": report["missing_tables"],
        "reader_checks": checks,
        "consistency": consistency,
        "base_reaction_equilibrium": equilibrium,
        "time_history_reference_envelopes": envelopes,
        "limitations": [
            "Workbook evidence only; native ETABS/OpenSees equivalence is NOT_VERIFIED.",
            "Support tags follow an observed ordering rule; the OpenSees node map is not in the workbooks.",
            "Time-history tables are Max/Min envelopes; no step series exists to compare.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-files", type=Path, nargs="+", required=True,
                        help="Distinct analysis lots to ingest as one reference (never a combined lot plus its parts)")
    parser.add_argument("--duplicate-check-files", type=Path, nargs="*", default=(),
                        help="Extra workbooks (for example split parts) included only in the all-sheet overlap audit")
    parser.add_argument("--output", type=Path, required=True, help="New JSON report path")
    parser.add_argument("--row-database", type=Path,
                        help="Optional NEW SQLite path to keep; default is a temporary file")
    args = parser.parse_args(argv)
    output = args.output.expanduser().absolute()
    if output.exists():
        parser.error("Refusing to overwrite an existing report: " + str(output))
    from components.inputs.etabs_table_bundle import audit_analysis_workbooks
    ingest = [p.expanduser().absolute() for p in args.analysis_files]
    everything = ingest + [p.expanduser().absolute() for p in args.duplicate_check_files]
    progress = lambda message: print(message, flush=True)
    audit = audit_analysis_workbooks(everything, progress=progress)
    if audit["status"] != "ALL_WORKSHEETS_SCANNED_NOT_ENGINEERING_VALIDATION":
        parser.error("Not every worksheet was scanned; see audit errors: " + json.dumps(audit["errors"])[:400])
    with tempfile.TemporaryDirectory() as scratch:
        database = args.row_database.expanduser().absolute() if args.row_database else Path(scratch) / "rows.sqlite3"
        document = build_audit_document(ingest, row_database=database, audit=audit, progress=progress)
    output.write_text(json.dumps(document, indent=1, allow_nan=False, default=str), encoding="utf-8")
    findings = document["consistency"]["findings"]
    print(f"Wrote {output.name}: {len(findings)} findings")
    for item in findings:
        print(f"  {item['severity']:7} {item['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

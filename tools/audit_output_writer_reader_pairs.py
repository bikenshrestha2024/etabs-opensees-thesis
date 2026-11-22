"""Whole-active-tree producer/consumer matrix for coordinated output migration.

[REF docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md]
Static AST inventory with explicit stage owners and possible local import edges.
Do NOT call a potential write a runtime writer, or a local import a verified
file consumer. Never relocate historic data or publish private result content.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import sys
from collections import Counter
from pathlib import Path

_ROOT=Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0,str(_ROOT))

from tools.audit_live_output_writers import scan_source, source_files
from components.inputs.output_contract import atomic_json

MODULE_OWNERS={
    "components/inputs/":"PROJECT_IO",
    "components/model/":"MODEL",
    "components/gravity/":"GRAVITY",
    "components/equivalent_static/":"ESM",
    "components/modal/":"MODAL",
    "components/response_spectrum/":"MRSM",
    "components/linear_time_history/":"LTHA",
    "components/nonlinear_time_history/":"NLTHA",
    "components/nbc105/":"NBC105",
    "components/validation/":"COMPARISONS",
    "components/ui/":"UI",
    "components/shared/":"SHARED",
    "tools/":"TOOLS",
    "src/":"SRC",
}


def _owner(path):
    return next((v for k,v in MODULE_OWNERS.items()
                 if path.startswith(k)),"ENTRYPOINT_OR_OTHER")


def _imports(tree):
    result=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            for item in node.names:
                result.add(item.name)
        elif isinstance(node,ast.ImportFrom) and node.module:
            result.add(node.module)
    return sorted(result)


def build_matrix(repo):
    root=Path(repo).expanduser().resolve(strict=True)
    scan=scan_source(root)
    by_path={item["source"]:item for item in scan["reader_writer_files"]}
    rows=[]
    counts=Counter()
    # Carry original source lines through to a reproducible per-stage queue.
    # Aggregate totals alone cannot prove every legacy writer was migrated.
    reference_lines=[]
    io_call_lines=[]
    for source_record in scan["files"]:
        source=source_record["source"]
        for ref in source_record["occurrences"]:
            row={"source":source,"owner":_owner(source),
                 "line":ref["line"],"kind":ref["kind"],
                 "method":ref.get("method",""),
                 "markers":";".join(ref.get("markers",[])),
                 "literal_context":ref.get("literal_context",""),
                 "migration_status":"SOURCE_REVIEW_REQUIRED_NOT_NATIVE_VALIDATED"}
            if ref["kind"]=="LITERAL_PATH_MARKER" and ref.get("legacy"):
                reference_lines.append(row)
            elif ref["kind"] in ("POTENTIAL_READ_CALL","POTENTIAL_WRITE_CALL"):
                io_call_lines.append(row)
    for path in source_files(root):
        rel=path.relative_to(root).as_posix()
        owner=_owner(rel)
        item=by_path.get(rel,{})
        readings=item.get("read_calls",0)
        writings=item.get("write_calls",0)
        legacy=item.get("legacy_markers",0)
        try:
            tree=ast.parse(path.read_text(encoding="utf-8-sig"),filename=rel)
            deps=_imports(tree)
        except (SyntaxError,UnicodeError,OSError) as exc:
            # Never silently omit one active source.
            deps=[]
            scan["parse_errors"].append({"path":rel,"error":type(exc).__name__})
        local=[name for name in deps if name.startswith(
            ("components.","tools.","src.","OpenSees_"))]
        if legacy and (readings or writings):
            status="LEGACY_PATH_OWNER_AND_READER_PARITY_REVIEW"
        elif writings:
            status="WRITER_READER_OUTPUT_CONTRACT_REVIEW"
        elif readings:
            status="READER_SAVED_CASE_FALLBACK_REVIEW"
        else:
            status="NO_DIRECT_IO_CALL_FOUND_STATIC_ONLY"
        rows.append({
            "source":rel,"owner":owner,
            "possible_read_calls":readings,"possible_write_calls":writings,
            "legacy_marker_count":legacy,
            "local_imports":local,
            "review_status":status,
            "engineering_approval":"NOT_ASSESSED",
        })
        counts[owner]+=1
    return {
        "schema":"THESIS_ALL_ACTIVE_OUTPUT_PAIR_MATRIX_V1",
        "scope":"ALL_ACTIVE_PYTHON_STATIC_AST_ONLY_NO_NATIVE_SOLVER_OR_FILE_MIGRATION",
        "source_count":len(rows),
        "owner_counts":dict(sorted(counts.items())),
        "totals":scan["totals"],
        "legacy_reference_lines":reference_lines,
        "reader_writer_candidate_lines":io_call_lines,
        "parse_errors":scan["parse_errors"],
        "producer_consumer_review_required":sum(
            x["review_status"]!="NO_DIRECT_IO_CALL_FOUND_STATIC_ONLY"
            for x in rows),
        "historical_results_mutated":False,
        "acceptance":"OPEN_UNTIL_WRITER_READER_NATIVE_SAVED_CASE_PARITY",
        "sources":rows,
    }


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",type=Path,default=_ROOT)
    parser.add_argument("--report-dir",type=Path,
                        help="Local diagnostics folder; never writes to GitHub")
    parser.add_argument("--fail-on-parse",action="store_true")
    parser.add_argument("--fail-on-open",action="store_true",
                        help="Strict acceptance: returns 2 until every active pair is verified")
    args=parser.parse_args(argv)
    report=build_matrix(args.repo)
    if args.report_dir:
        out=args.report_dir.expanduser()
        out.mkdir(parents=True,exist_ok=True)
        atomic_json(out/"all_active_output_pairs.json",report)
        with (out/"all_active_output_pairs.csv").open(
            "w",newline="",encoding="utf-8-sig") as stream:
            columns=("source","owner","possible_read_calls",
                     "possible_write_calls","legacy_marker_count",
                     "review_status","engineering_approval")
            writer=csv.DictWriter(stream,fieldnames=columns)
            writer.writeheader()
            for item in report["sources"]:
                writer.writerow({k:item.get(k) for k in columns})
        columns=("source","owner","line","kind","method","markers",
                 "literal_context","migration_status")
        for name,rows in (
                ("legacy_reference_line_register.csv",report["legacy_reference_lines"]),
                ("reader_writer_line_register.csv",report["reader_writer_candidate_lines"])):
            with (out/name).open("w",newline="",encoding="utf-8-sig") as stream:
                writer=csv.DictWriter(stream,fieldnames=columns)
                writer.writeheader()
                writer.writerows(rows)
    summary={key:report[key] for key in
             ("scope","source_count","owner_counts","totals",
              "producer_consumer_review_required","parse_errors","acceptance")}
    print(json.dumps(summary,indent=2,allow_nan=False))
    return 2 if ((args.fail_on_parse and report["parse_errors"])
                 or (args.fail_on_open and
                     report["producer_consumer_review_required"])) else 0


if __name__=="__main__":
    raise SystemExit(main())

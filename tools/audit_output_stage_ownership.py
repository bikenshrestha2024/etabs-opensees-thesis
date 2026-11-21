"""Inventory EVERY active Python writer and flag cross-stage output risks.

Static only. The inventory is not a proof of file origin, numerical
compliance, or a Windows ETABS/OpenSees execution. Unknown writer paths are
returned in review_queue, not silently treated as compliant.

Usage:
 python tools/audit_output_stage_ownership.py
 python tools/audit_output_stage_ownership.py --report-dir <LOCAL_DIRECTORY>
 python tools/audit_output_stage_ownership.py --strict
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from tools.audit_live_output_writers import scan_source

SOURCE_OWNERS={
    "components/gravity/":"GRAVITY",
    "components/equivalent_static/":"ESM",
    "components/modal/":"MODAL",
    "components/response_spectrum/":"MRSM",
    "components/linear_time_history/":"LTHA",
    "components/nonlinear_time_history/":"NLTHA",
    "components/validation/":"COMPARISONS",
    "components/model/":"MODEL",
    "components/inputs/":"PROJECT_IO",
    "components/ui/":"UI",
    "tools/":"TOOLS",
}
# These three caller/writer pairs previously bypassed canonical stage routing.
# The branch must not regress after fixing them; full native tests are separate.
REQUIRED_GUARDS={
    "components/gravity/gui_and_reports.py":"GRAVITY",
    "components/linear_time_history/runner_and_gui.py":"LTHA",
    "components/nonlinear_time_history/runner_and_gui.py":"NLTHA",
    "components/model/readiness_dashboard_gui.py":"SOFTWARE_DIAGNOSTICS",
}
REQUIRED_ESM={
    "components/equivalent_static/calculation_and_gui.py",
    "components/modal/rayleigh.py",
    "components/inputs/opensees_nbc_sync.py",
}
LEGACY="opensees_analysis_results"


def _guarded_caller(path,repo):
    tree=ast.parse((repo/path).read_text(encoding="utf-8-sig"))
    uses=[]
    for n in ast.walk(tree):
        if not isinstance(n,ast.Call) or not isinstance(n.func,ast.Name):
            continue
        if n.func.id not in ("analysis_output_folder","owned_run_destination"):
            continue
        stages=[k.value.value for k in n.keywords
                if k.arg=="stage" and isinstance(k.value,ast.Constant)]
        explicit=[arg.value for arg in n.args if isinstance(arg,ast.Constant)]
        uses.append((n.lineno,n.func.id,stages,explicit))
    return uses


def audit(repo=ROOT):
    repo=Path(repo).resolve(strict=True)
    data=scan_source(repo)
    counts=Counter()
    review_queue=[]
    for item in data["files"]:
        path=item["source"]
        owner=next((stage for prefix,stage in SOURCE_OWNERS.items()
                    if path.startswith(prefix)),"ROOT_OR_OTHER")
        count=sum(x["kind"]=="POTENTIAL_WRITE_CALL" for x in item["occurrences"])
        legacy=[x["line"] for x in item["occurrences"]
                if x["kind"]=="LITERAL_PATH_MARKER" and x.get("legacy")]
        counts[owner]+=count
        if legacy and count:
            review_queue.append({
                "path":path,"owner":owner,"possible_write_calls":count,
                "legacy_references":len(legacy),
                "lines":legacy[:15],
                "status":"STATIC_REVIEW_WRITER_READER_AND_SOURCE_IDENTITY",
            })
    review_queue.sort(key=lambda x:(-x["legacy_references"],x["path"]))
    violations=[]
    for p,stage in REQUIRED_GUARDS.items():
        if not (repo/p).is_file():
            violations.append({"path":p,"reason":"REQUIRED_GUI_MISSING"})
            continue
        calls=_guarded_caller(p,repo)
        if not any(fn=="owned_run_destination" and stage in positional
                   for _,fn,_,positional in calls):
            violations.append({"path":p,"reason":"NO_CANONICAL_USER_OUTPUT_GUARD"})
    checks="components/validation/response_checks.py"
    if (repo/checks).is_file():
        tree=ast.parse((repo/checks).read_text(encoding="utf-8-sig"))
        if not any(isinstance(node,ast.Call)
                   and isinstance(node.func,ast.Name)
                   and node.func.id=="create_case_run"
                   and any(isinstance(arg,ast.Constant)
                           and arg.value=="SOFTWARE_DIAGNOSTICS"
                           for arg in node.args)
                   for node in ast.walk(tree)):
            violations.append({"path":checks,
                               "reason":"IRREGULARITY_REVIEW_NOT_STAGE_SCOPED"})
    else:
        violations.append({"path":checks,"reason":"IRREGULARITY_REVIEW_MISSING"})
    for p in REQUIRED_ESM:
        if not (repo/p).is_file():
            violations.append({"path":p,"reason":"REQUIRED_ESM_PRODUCER_MISSING"})
            continue
        calls=_guarded_caller(p,repo)
        for line,fn,stages,_ in calls:
            if fn=="analysis_output_folder" and stages!=["ESM"]:
                violations.append({"path":p,"line":line,
                    "reason":"ESM_WRITER_OR_CALLER_UNSCOPED_SHARED_LEGACY_DESTINATION"})
    return {
        "schema":"THESIS_ACTIVE_OUTPUT_OWNERSHIP_INVENTORY_V2",
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "assessment":"STATIC_INVENTORY_NOT_RUNTIME_OUTPUT_OR_ENGINEERING_VERIFICATION",
        "active_python_scanned":data["totals"]["files"],
        "possible_write_calls":data["totals"]["possible_write_calls"],
        "source_owner_write_counts":dict(sorted(counts.items())),
        "legacy_writer_reference_candidates":len(review_queue),
        "review_queue":review_queue,
        "parse_errors":data["parse_errors"],
        "contract_violations":violations,
        "production_change_policy":"No silent physical model changes; review "
            "all producer+reader pairs and saved run manifests before migration.",
    }


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",type=Path,default=ROOT)
    parser.add_argument("--report-dir",type=Path)
    parser.add_argument("--strict",action="store_true",
                        help="Reject missing stage guards or invalid Python")
    args=parser.parse_args(argv)
    report=audit(args.repo)
    if args.report_dir is not None:
        target=args.report_dir
        target.mkdir(parents=True,exist_ok=True)
        (target/"all_active_output_ownership.json").write_text(
            json.dumps(report,indent=2)+"\n",encoding="utf-8")
        with (target/"legacy_reference_review_queue.csv").open(
                "w",newline="",encoding="utf-8") as stream:
            writer=csv.DictWriter(stream,fieldnames=(
                "path","owner","possible_write_calls",
                "legacy_references","lines","status"))
            writer.writeheader()
            for item in report["review_queue"]:
                writer.writerow({**item,"lines":",".join(map(str,item["lines"]))})
    summary={key:report[key] for key in (
        "assessment","active_python_scanned","possible_write_calls",
        "source_owner_write_counts","legacy_writer_reference_candidates",
        "parse_errors","contract_violations")}
    summary["legacy_candidate_files"]=[
        {"path":x["path"],"owner":x["owner"],
         "legacy_references":x["legacy_references"],
         "possible_write_calls":x["possible_write_calls"]}
        for x in report["review_queue"]]
    print(json.dumps(summary,indent=2))
    if args.strict and (report["parse_errors"] or report["contract_violations"]):
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())

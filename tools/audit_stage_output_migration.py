"""Read-only native-case output migration audit; optional local JSON export.

Run from the updated checkout on Windows:
  python tools/audit_stage_output_migration.py "D:\\Thesis Opensees\\ETABS 11-14-2026\\3"
  python tools/audit_stage_output_migration.py "D:\\Thesis Opensees\\ETABS 11-14-2026\\3" --write

[REF docs/source/components/inputs/output_contract.py.md]
The file layout is NOT a code-compliance or ETABS-equivalence assessment.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

# A direct `python tools/...` invocation must find the source checkout.
_ROOT=Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0,str(_ROOT))

from components.inputs.output_contract import SCHEMA, atomic_json, inspect_case_manifest, style_workbook
from components.inputs.output_layout import STAGE_FOLDERS, AUXILIARY_FOLDERS, export_root_for


def audit_stage_migration(export_dir):
    """[REF docs/source/components/inputs/output_contract.py.md]
    Inspect existing canonical run manifests and legacy roots without changes.

    This reports what is present, not whether the stage's producer was
    migrated, solver converged or the model satisfies NBC 105:2025.
    """
    root=export_root_for(export_dir)
    if not root.is_dir():
        raise NotADirectoryError(root)
    stages=[]
    for key,dirname in STAGE_FOLDERS.items():
        stage=root/dirname
        runs=stage/"RUNS"
        manifests=[]
        statuses={}
        unmanifested=[]
        if stage.is_symlink():
            unmanifested.append({"manifest":stage.relative_to(root).as_posix(),
                                 "problem":"SYMLINKED_STAGE_ROOT_REFUSED"})
        elif runs.is_symlink():
            unmanifested.append({"manifest":runs.relative_to(root).as_posix(),
                                 "problem":"SYMLINKED_RUN_ROOT_REFUSED"})
        elif runs.is_dir():
            # Existing run folders with no CASE_MANIFEST were invisible in
            # the earlier rglob-only inventory. Inspect precisely the
            # canonical RUNS/<state>/<case>/<run-id> depth, without following
            # linked intermediate directories or claiming a solver ran.
            for state_dir in sorted(runs.iterdir()):
                if state_dir.is_symlink():
                    unmanifested.append({
                        "manifest":state_dir.relative_to(root).as_posix(),
                        "problem":"SYMLINKED_RUN_STATE_REFUSED"})
                    continue
                if not state_dir.is_dir():
                    continue
                for case_dir in sorted(state_dir.iterdir()):
                    if case_dir.is_symlink():
                        unmanifested.append({
                            "manifest":case_dir.relative_to(root).as_posix(),
                            "problem":"SYMLINKED_RUN_CASE_REFUSED"})
                        continue
                    if not case_dir.is_dir():
                        continue
                    for run_dir in sorted(case_dir.iterdir()):
                        if run_dir.is_symlink():
                            unmanifested.append({
                                "manifest":run_dir.relative_to(root).as_posix(),
                                "problem":"SYMLINKED_RUN_FOLDER_REFUSED"})
                        elif run_dir.is_dir() and not (
                                run_dir/"00_INPUT_SOURCE"/"CASE_MANIFEST.json").is_file():
                            unmanifested.append({
                                "manifest":(run_dir/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
                                           ).relative_to(root).as_posix(),
                                "problem":"MISSING_CASE_MANIFEST"})
            for p in sorted(runs.rglob("CASE_MANIFEST.json")):
                if p.is_symlink() or any(q.is_symlink() for q in p.parents if q!=root):
                    continue
                try:
                    item=json.loads(p.read_text(encoding="utf-8-sig"))
                except (ValueError,OSError):
                    unmanifested.append({"manifest":p.relative_to(root).as_posix(),
                                         "problem":"UNREADABLE_OR_INVALID_JSON"})
                    continue
                if not isinstance(item, dict):
                    unmanifested.append({"manifest":p.relative_to(root).as_posix(),
                                         "problem":"NONOBJECT_CASE_MANIFEST"})
                    continue
                if item.get("schema")!=SCHEMA:
                    unmanifested.append({"manifest":p.relative_to(root).as_posix(),
                                         "problem":"UNKNOWN_MANIFEST_SCHEMA"})
                    continue
                details=inspect_case_manifest(p.parent.parent,expected_stage=key)
                statuses[details["solver_status"]]=statuses.get(details["solver_status"],0)+1
                manifests.append(details)
                if not details["valid"]:
                    unmanifested.append({
                        "manifest":p.relative_to(root).as_posix(),
                        "problem":"INVALID_CASE_CONTRACT",
                        "issues":details["issues"],
                    })
        stages.append({
            "stage":key,"directory":dirname,
            "exists":stage.is_dir() and not stage.is_symlink(),
            "symlink_refused":stage.is_symlink() or runs.is_symlink(),
            "run_manifest_count":len(manifests),
            "missing_run_manifest_count":sum(
                x["problem"]=="MISSING_CASE_MANIFEST" for x in unmanifested),
            "linked_run_path_count":sum(
                x["problem"].startswith("SYMLINKED_") for x in unmanifested),
            "solver_status_counts":statuses,
            "unreadable_or_invalid_manifests":unmanifested,
            "cases":manifests,
            "assessment":"FILESYSTEM_INVENTORY_ONLY",
        })
    legacy=root/"OpenSees_Analysis_Results"
    return {
        "schema":"THESIS_LIVE_STAGE_OUTPUT_MIGRATION_AUDIT_V1",
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "export_root":str(root),
        "assessment":"FILESYSTEM_ONLY_NOT_SOLVER_OR_ETABS_EQUIVALENCE",
        "legacy_analysis_root_exists":legacy.is_dir(),
        "legacy_linear_th_root_exists":(root/"06_LINEAR_TH").is_dir(),
        "legacy_nonlinear_th_root_exists":(root/"07_NONLINEAR_TH").is_dir(),
        "stages":stages,
        "auxiliary_folders":[{
            "name":key,"directory":folder,
            "exists":(root/folder).is_dir() and not (root/folder).is_symlink(),
            "symlink_refused":(root/folder).is_symlink(),
            "assessment":"AUXILIARY_FOLDER_NOT_SOLVER_STATUS"
        } for key,folder in AUXILIARY_FOLDERS.items()],
        "summary":{
            "stage_count":len(stages),
            "present_stage_count":sum(x["exists"] for x in stages),
            "run_manifest_count":sum(x["run_manifest_count"] for x in stages),
            "missing_run_manifest_count":sum(x["missing_run_manifest_count"]
                                             for x in stages),
            "linked_run_path_count":sum(x["linked_run_path_count"]
                                       for x in stages),
            "invalid_case_contract_count":sum(
                len(x["unreadable_or_invalid_manifests"]) for x in stages),
            "engineering_acceptance":"NOT_ESTABLISHED_BY_FILESYSTEM_AUDIT",
        },
        "native_checks_required":[
            "Windows Tkinter GUI opening and close/stop for all stage modules",
            "ETABS source identity and original assignment/Excel SHA unchanged",
            "32/76/97 foundation-support comparison with six-component reactions",
            "MESH_04/08/16 independent gravity solves and recovered shell-frame forces",
            "ULS/SLS modal and MRSM/ESM cases, drift, mass and force scaling",
            "Nonlinear RC wall/brace/device calibration and NLTHA full readiness",
        ],
    }



def export_uniform_inventory_excel(report, target):
    """[REF docs/source/components/inputs/output_contract.py.md]
    Publish the SAME formatted navigation workbook for every stage.

    Never reproduces private EDB/Excel contents or promotes solver completion
    to ETABS engineering equivalence.
    """
    from openpyxl import Workbook
    book=Workbook()
    overview=book.active
    overview.title="Stage summary"
    overview.append(("Stage","Folder","Present","Case manifests",
                     "Missing manifests","Linked run paths",
                     "Invalid cases","File audit status"))
    for stage in report["stages"]:
        overview.append((stage["stage"],stage["directory"],stage["exists"],
                         stage["run_manifest_count"],
                         stage["missing_run_manifest_count"],
                         stage["linked_run_path_count"],
                         len(stage["unreadable_or_invalid_manifests"]),
                         stage["assessment"]))
    cases=book.create_sheet("Case registry")
    cases.append(("Stage","Limit state","Case ID","Run ID","Solver status",
                  "Model SHA recorded","EDB SHA recorded","Units",
                  "Manifest valid","Issues","Engineering acceptance"))
    for stage in report["stages"]:
        for case in stage["cases"]:
            cases.append((stage["stage"],case.get("state"),case.get("case_id"),
                          case.get("run_id"),case.get("solver_status"),
                          case.get("model_sha256_recorded"),
                          case.get("source_edb_sha256_recorded"),
                          case.get("units"),case.get("valid"),
                          "; ".join(case.get("issues",[])),
                          "NOT_CERTIFIED_BY_AUDIT"))
    issues=book.create_sheet("Missing or inconsistent")
    issues.append(("Stage","Manifest","Problem","Details"))
    for stage in report["stages"]:
        for item in stage["unreadable_or_invalid_manifests"]:
            issues.append((stage["stage"],item["manifest"],item["problem"],
                           "; ".join(item.get("issues",[]))))
    auxiliary=book.create_sheet("Auxiliary folders")
    auxiliary.append(("Name","Directory","Present","Meaning"))
    for item in report["auxiliary_folders"]:
        auxiliary.append((item["name"],item["directory"],item["exists"],
                          item["assessment"]))
    readme=book.create_sheet("Read first")
    readme.append(("Field","Meaning"))
    readme.append(("Scope","Filesystem output consistency; not a structural analysis"))
    readme.append(("Source","Selected ETABS export folder; absolute local paths omitted"))
    readme.append(("Engineering acceptance","NOT ESTABLISHED BY FILE AUDIT"))
    readme.append(("Missing results","Not zero response; a separate native run is needed"))
    readme.append(("Solver completion","Does not establish full record duration, force equilibrium or code compliance"))
    for name in report["native_checks_required"]:
        readme.append(("Required native check",name))
    style_workbook(book)
    dest=Path(target)
    dest.parent.mkdir(parents=True,exist_ok=True)
    # New timestamped diagnostic files only; never replace original workbook.
    if dest.exists():
        raise FileExistsError(str(dest))
    book.save(dest)
    return dest



def main(argv=None):
    """[REF docs/source/components/inputs/output_contract.py.md] Local CLI."""
    parser=argparse.ArgumentParser(description="Audit output folders; no native solver")
    parser.add_argument("export_root",help="Existing ETABS export case folder")
    parser.add_argument("--write",action="store_true",help="Save local diagnostics JSON")
    args=parser.parse_args(argv)
    report=audit_stage_migration(args.export_root)
    for entry in report["stages"]:
        print(f"{entry['directory']}: present={entry['exists']} "
              f"manifested_runs={entry['run_manifest_count']} "
              f"statuses={entry['solver_status_counts']}")
    print("Audit is FILESYSTEM ONLY; not ETABS/OpenSees or NBC acceptance.")
    if args.write:
        root=export_root_for(args.export_root)
        out=root/"09_SOFTWARE_DIAGNOSTICS"/"MIGRATION_AUDITS"
        # Match the writer-audit publisher: refuse linked destinations
        # rather than writing private project paths outside this export case.
        run_parent=out/"RUNS"
        for directory in (out.parent,out,run_parent):
            if directory.is_symlink():
                raise ValueError("Refusing linked migration-audit output directory: "+str(directory))
        stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        run=run_parent/stamp
        run.mkdir(parents=True,exist_ok=False)
        target=atomic_json(run/"JSON"/"Live_Stage_Output_Audit.json",report)
        workbook=export_uniform_inventory_excel(
            report,run/"EXCEL"/"Live_Stage_Output_Audit.xlsx")
        print("Local audit JSON:",target)
        print("Uniform stage and case Excel:",workbook)
    return report


if __name__=="__main__":
    main()

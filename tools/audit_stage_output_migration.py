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

from components.inputs.output_contract import SCHEMA, atomic_json
from components.inputs.output_layout import STAGE_FOLDERS, export_root_for


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
        if runs.is_dir():
            for p in sorted(runs.rglob("CASE_MANIFEST.json")):
                if p.is_symlink() or any(q.is_symlink() for q in p.parents if q!=root):
                    continue
                try:
                    item=json.loads(p.read_text(encoding="utf-8-sig"))
                except (ValueError,OSError):
                    unmanifested.append({"manifest":p.relative_to(root).as_posix(),
                                         "problem":"UNREADABLE_OR_INVALID_JSON"})
                    continue
                if item.get("schema")!=SCHEMA:
                    unmanifested.append({"manifest":p.relative_to(root).as_posix(),
                                         "problem":"UNKNOWN_MANIFEST_SCHEMA"})
                    continue
                statuses[item.get("solver_status","MISSING_STATUS")]=(
                    statuses.get(item.get("solver_status","MISSING_STATUS"),0)+1)
                manifests.append({
                    "run":p.parent.parent.relative_to(root).as_posix(),
                    "state":item.get("state"),
                    "case_id":item.get("case_id"),
                    "solver_status":item.get("solver_status"),
                    "engineering_acceptance":item.get("structural_acceptance"),
                    "model_sha256_recorded":bool(item.get("model_sha256")),
                    "source_edb_sha256_recorded":bool(item.get("source_edb_sha256")),
                })
        stages.append({
            "stage":key,"directory":dirname,"exists":stage.is_dir(),
            "run_manifest_count":len(manifests),
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
        "native_checks_required":[
            "Windows Tkinter GUI opening and close/stop for all stage modules",
            "ETABS source identity and original assignment/Excel SHA unchanged",
            "32/76/97 foundation-support comparison with six-component reactions",
            "MESH_04/08/16 independent gravity solves and recovered shell-frame forces",
            "ULS/SLS modal and MRSM/ESM cases, drift, mass and force scaling",
            "Nonlinear RC wall/brace/device calibration and NLTHA full readiness",
        ],
    }


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
        stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        target=atomic_json(out/("Live_Stage_Output_Audit_"+stamp+".json"),report)
        print("Local audit:",target)
    return report


if __name__=="__main__":
    main()

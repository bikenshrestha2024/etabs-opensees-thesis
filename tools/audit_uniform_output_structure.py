"""Read-only audit of canonical ETABS/OpenSees output structure.

Scans manifests, folder ownership, legacy paths and module visibility.
Does not move/delete any outputs, recurse into source spreadsheets, or claim
ETABS/OpenSees equivalence. Only metadata is published.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from components.inputs.output_layout import (
    ALL_STAGE_FOLDERS, STAGE_FOLDERS, export_root_for,
)
from components.inputs.output_contract import inspect_case_manifest, atomic_json


def audit_export_layout(export_dir):
    selected=Path(export_dir).expanduser()
    if any(p.is_symlink() for p in (selected,*selected.parents)):
        raise ValueError("Refusing linked export directory")
    root=selected.resolve(strict=True)
    if not root.is_dir() or export_root_for(root)!=root:
        raise ValueError("Select the original export root, not a nested module/run")
    sections=[]
    issues=[]
    for stage,folder in ALL_STAGE_FOLDERS.items():
        location=root/folder
        if location.is_symlink():
            issues.append({"stage":stage,"issue":"LINKED_STAGE_REFUSED"})
            sections.append({"stage":stage,"folder":folder,"status":"LINKED_REFUSED",
                             "cases":[]})
            continue
        runs=location/"RUNS"
        cases=[]
        if runs.is_symlink():
            issues.append({"stage":stage,"issue":"LINKED_RUNS_REFUSED"})
        elif runs.is_dir():
            # Modern contract: RUNS / state / case / run-id.
            for state in sorted(runs.iterdir()):
                if state.is_symlink():
                    issues.append({"stage":stage,"issue":"LINKED_STATE_REFUSED"})
                    continue
                if not state.is_dir():
                    continue
                for case in sorted(state.iterdir()):
                    if case.is_symlink():
                        issues.append({"stage":stage,"issue":"LINKED_CASE_REFUSED"})
                        continue
                    if not case.is_dir():
                        continue
                    for run in sorted(case.iterdir()):
                        if run.is_symlink():
                            issues.append({"stage":stage,"issue":"LINKED_RUN_REFUSED"})
                            continue
                        if not run.is_dir():
                            continue
                        result=inspect_case_manifest(run,expected_stage=stage)
                        cases.append({
                            "relative_run":run.relative_to(root).as_posix(),
                            "manifest_valid":result["valid"],
                            "issues":result["issues"],
                            "solver_status":result["solver_status"],
                            "engineering_acceptance":result["engineering_acceptance"],
                        })
                        if not result["valid"]:
                            issues.append({"stage":stage,"run":run.relative_to(root).as_posix(),
                                           "issue":"INVALID_CASE_MANIFEST",
                                           "details":result["issues"]})
        legacy=[]
        for relative in ("OpenSees_Analysis_Results",
                         "01_ETABS_EXPORT/03_BEAM_FORCES"):
            prior=root/relative
            if ((stage=="ETABS_EXPORT" and relative.endswith("03_BEAM_FORCES"))
                    or (stage=="GRAVITY" and relative=="OpenSees_Analysis_Results")):
                if prior.is_symlink():
                    issues.append({"stage":stage,"issue":"LINKED_LEGACY_REFUSED"})
                elif prior.is_dir():
                    legacy.append(relative)
        # A stage may still contain historical flat producer outputs. Surface
        # their ownership for review; do not silently relocate them.
        stage_flat=[]
        if location.is_dir():
            for child in sorted(location.iterdir()):
                if child.is_symlink():
                    issues.append({"stage":stage,"issue":"LINKED_STAGE_CHILD_REFUSED"})
                elif child.is_file() and child.suffix.lower() in (
                    ".json",".csv",".xlsx",".xlsm",".html",".pdf",".png",
                    ".jpg",".jpeg",".zip",".log"):
                    stage_flat.append({"filename":child.name,
                                       "size_bytes":child.stat().st_size})
        sections.append({"stage":stage,"folder":folder,
                         "status":"PRESENT" if location.is_dir() else "ABSENT",
                         "cases":cases,"historical_locations":legacy,
                         "loose_stage_artifacts":stage_flat})
    # Root-level derived artifacts are inventory-only warnings; they may be
    # intentionally preserved by older export/analysis consumers. Never move
    # or infer deletion safety from file names.
    derived={".json",".csv",".xlsx",".xlsm",".html",".pdf",".png",
             ".jpg",".jpeg",".zip",".log"}
    loose=[]
    for item in sorted(root.iterdir()):
        if item.is_symlink():
            issues.append({"stage":"PROJECT_ROOT","issue":"LINKED_ROOT_CHILD_REFUSED"})
        elif item.is_file() and item.suffix.lower() in derived:
            loose.append({"relative_path":item.name,"size_bytes":item.stat().st_size,
                          "status":"LEGACY_OR_UNCLASSIFIED_REVIEW_ONLY"})
    return {
        "schema":"THESIS_OUTPUT_STRUCTURE_AUDIT_V1",
        "scope":"METADATA_ONLY_READ_ONLY_NO_SOLVER_OR_ENGINEERING_ACCEPTANCE",
        "stages":sections,
        "loose_root_artifacts":loose,
        "review_flags":["ROOT_LEVEL_ARTIFACTS_NEED_OWNER_REVIEW"] if loose else [],
        "issues":issues,
        "case_counts":{row["stage"]:len(row["cases"]) for row in sections},
        "engineering_status":"NOT_ASSESSED",
    }


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-root",type=Path,required=True)
    parser.add_argument("--output",type=Path,
                        help="Optional JSON report path; defaults to stdout only")
    args=parser.parse_args(argv)
    report=audit_export_layout(args.export_root)
    if args.output:
        destination=args.output.expanduser()
        if destination.is_absolute():
            parent=args.export_root.expanduser().resolve(strict=True)
            if parent not in destination.resolve().parents:
                parser.error("Output JSON must remain inside the selected export")
        atomic_json(destination,report)
    print(json.dumps(report,indent=2,allow_nan=False))
    return 1 if report["issues"] else 0


if __name__=="__main__":
    raise SystemExit(main())

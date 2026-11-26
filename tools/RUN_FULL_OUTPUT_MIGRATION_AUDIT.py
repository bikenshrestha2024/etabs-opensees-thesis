"""Single local run for ALL active output owner/reader and disk audits.

[REF docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md]
No ETABS/OpenSees solver, file relocation, overwrite of historical evidence,
or online upload. Read-only evidence collection plus one new canonical audit run.
Run on Windows:
 python tools/RUN_FULL_OUTPUT_MIGRATION_AUDIT.py --export-root "D:\\Thesis Opensees\\ETABS 11-22-2026"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO=Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0,str(_REPO))

from components.inputs.output_contract import (
    create_case_run, atomic_json, record_case_status,
)
from tools.audit_output_writer_reader_pairs import build_matrix
from tools.audit_uniform_output_structure import audit_export_layout
from tools.audit_stage_output_migration import audit_stage_migration
from tools.audit_output_stage_ownership import audit as audit_active_owners
from tools.audit_output_storage import scan_output


def run_full_audit(export_root, *, repository=_REPO, hash_duplicates=False, validate_files=False):
    root=Path(export_root).expanduser()
    if any(x.is_symlink() for x in (root,*root.parents)):
        raise ValueError("Refusing linked project export")
    root=root.resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(root)
    repo=Path(repository).resolve(strict=True)
    # No outputs are created before all inventory scans complete.
    source=build_matrix(repo)
    layout=audit_export_layout(root)
    stage=audit_stage_migration(root)
    owners=audit_active_owners(repo)
    disk=scan_output(root,hash_duplicates=hash_duplicates,include_entries=True,
                     validate_files=validate_files)
    if source["parse_errors"] or owners["parse_errors"]:
        raise ValueError("Active source cannot be fully parsed; no audit published")
    run=create_case_run(root,"SOFTWARE_DIAGNOSTICS",
                        "ALL_MODULE_OUTPUT_MIGRATION_AUDIT",
                        state="SOURCE_ONLY",units="kN-m-s")
    try:
        output=run/"02_RESULTS"
        for filename,document in (
            ("01_ALL_ACTIVE_WRITERS_READERS.json",source),
            ("02_PROJECT_OUTPUT_LAYOUT.json",layout),
            ("03_STAGE_MIGRATION.json",stage),
            ("04_ACTIVE_OUTPUT_OWNERSHIP.json",owners),
            ("05_ALL_OUTPUT_FILE_INVENTORY.json",disk),
        ):
            atomic_json(output/filename,document)
        outcome={
            "schema":"THESIS_ALL_MODULE_OUTPUT_MIGRATION_STATUS_V1",
            "status":"INVENTORY_COMPLETED_ENGINEERING_AND_MIGRATION_OPEN",
            "sources_inspected":source["source_count"],
            "owners":source["owner_counts"],
            "project_output_files_inspected":disk["total_files"],
            "project_output_bytes_accounted":disk["total_bytes"],
            "duplicate_hash_check":"REQUESTED" if hash_duplicates else "NOT_REQUESTED",
            "exact_duplicate_groups":len(disk["exact_duplicate_groups"]),
            "format_checks_requested":validate_files,
            "format_check_counts":disk["format_check_counts"],
            "embedded_format_check_counts":disk["embedded_format_check_counts"],
            "excel_formula_cache_inventory":disk["excel_formula_cache_inventory"],
            "archive_manifest_inventory":disk["archive_manifest_inventory"],
            "file_evidence_review_required_count":disk["file_evidence_review_required_count"],
            "disk_scan_error_count":len(disk["scan_errors"]),
            "producer_consumer_review_required":
                source["producer_consumer_review_required"],
            "stage_case_count":layout["case_counts"],
            "layout_issue_count":len(layout["issues"]),
            "owner_guard_violation_count":len(owners["contract_violations"]),
            "legacy_root_artifact_count":len(layout["loose_root_artifacts"]),
            "source_archive_moved":False,
            "engineering_acceptance":"NOT_VERIFIED",
            "required_next_gates":[
                "ALL_ACTIVE_PRODUCER_AND_CONSUMER_PARITY",
                "ALL_SAVED_CASES_REOPENED",
                "EXACT_EDB_AND_MODEL_DIGEST_MATCH",
                "NATIVE_WINDOWS_ETABS_OPENSEES_EXECUTION",
                "SUPPORT_REACTIONS_32_76_97_ACCEPTANCE",
            ],
        }
        atomic_json(output/"00_SUMMARY.json",outcome)
        record_case_status(run,"INCOMPLETE",
            message="All-module metadata inventory only; no native model equivalence or completed migration")
        return run,outcome
    except Exception:
        record_case_status(run,"FAILED",
            message="All-module output migration metadata collection failed")
        raise


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-root",type=Path,required=True)
    parser.add_argument("--repo",type=Path,default=_REPO)
    parser.add_argument("--hash-duplicates",action="store_true",help="SHA-check same-size duplicate candidates; never delete")
    parser.add_argument("--validate-files",action="store_true",help="Read JSON/text, check archive members, Excel formula caches and PNG signatures; not numerical validation")
    args=parser.parse_args(argv)
    run,summary=run_full_audit(args.export_root,repository=args.repo,
                              hash_duplicates=args.hash_duplicates,validate_files=args.validate_files)
    print(json.dumps({"audit_run":str(run),**summary},indent=2))
    return 2 if summary["producer_consumer_review_required"] or (
        summary["layout_issue_count"] or summary["owner_guard_violation_count"] or
        summary["disk_scan_error_count"] or summary["file_evidence_review_required_count"]) else 0


if __name__=="__main__":
    raise SystemExit(main())

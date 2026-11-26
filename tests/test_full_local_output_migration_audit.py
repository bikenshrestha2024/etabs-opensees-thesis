"""All-module local output audit produces only a new diagnostics run.

[REF docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md]
No native ETABS/OpenSees operations and no movement of historical evidence.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.RUN_FULL_OUTPUT_MIGRATION_AUDIT import run_full_audit
from components.inputs.output_contract import inspect_case_manifest


class FullLocalOutputAuditTests(unittest.TestCase):
    def test_all_module_reports_in_one_source_only_run(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"OpenSees_Analysis_Results").mkdir()
            historical=root/"OpenSees_Analysis_Results"/"old.json"
            historical.write_text('{"source":"historic"}',encoding="utf-8")
            mock_source={
                "parse_errors":[],"source_count":1,
                "owner_counts":{"GRAVITY":1},
                "producer_consumer_review_required":1,
            }
            mock_owners={"parse_errors":[],"contract_violations":[]}
            mock_stage={"summary":{"stage_count":7}}
            with patch("tools.RUN_FULL_OUTPUT_MIGRATION_AUDIT.build_matrix",
                       return_value=mock_source),patch(
                       "tools.RUN_FULL_OUTPUT_MIGRATION_AUDIT.audit_active_owners",
                       return_value=mock_owners),patch(
                       "tools.RUN_FULL_OUTPUT_MIGRATION_AUDIT.audit_stage_migration",
                       return_value=mock_stage):
                run,status=run_full_audit(root,hash_duplicates=True,validate_files=True)
            self.assertTrue(run.is_dir())
            self.assertIn("09_SOFTWARE_DIAGNOSTICS",run.parts)
            self.assertEqual(status["sources_inspected"],1)
            self.assertEqual(status["project_output_files_inspected"],1)
            self.assertFalse(status["source_archive_moved"])
            self.assertEqual(status["duplicate_hash_check"],"REQUESTED")
            self.assertEqual(status["format_check_counts"],{"JSON_PARSED":1})
            self.assertEqual(status["disk_scan_error_count"],0)
            import json
            disk=json.loads((run/"02_RESULTS"/"05_ALL_OUTPUT_FILE_INVENTORY.json").read_text())
            self.assertEqual(len(disk["files"]),1)
            self.assertEqual(disk["files"][0]["relative_path"],"OpenSees_Analysis_Results/old.json")
            result=run/"02_RESULTS"
            for name in (
                "00_SUMMARY.json","01_ALL_ACTIVE_WRITERS_READERS.json",
                "02_PROJECT_OUTPUT_LAYOUT.json","03_STAGE_MIGRATION.json",
                "04_ACTIVE_OUTPUT_OWNERSHIP.json",
                "05_ALL_OUTPUT_FILE_INVENTORY.json"):
                self.assertTrue((result/name).is_file())
            self.assertEqual(inspect_case_manifest(run)["solver_status"],
                             "INCOMPLETE")
            self.assertEqual(historical.read_text(encoding="utf-8"),
                             '{"source":"historic"}')
            self.assertEqual(status["engineering_acceptance"],"NOT_VERIFIED")


if __name__=="__main__":
    unittest.main()

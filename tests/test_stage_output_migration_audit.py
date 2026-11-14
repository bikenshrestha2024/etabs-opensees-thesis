"""Audit-only stage verification is non-mutating unless --write is requested."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from components.inputs.output_contract import create_case_run, record_case_status
from tools.audit_stage_output_migration import audit_stage_migration


class NativeStageMigrationAuditTests(unittest.TestCase):
    def test_dry_run_and_explicit_write_are_separate(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"OpenSees_Analysis_Results"/"older").mkdir(parents=True)
            modal=create_case_run(root,"MODAL","X_MODE",state="ULS")
            record_case_status(modal,"COMPLETED_SOLVER_ONLY")
            first=audit_stage_migration(root)
            self.assertTrue(first["legacy_analysis_root_exists"])
            modal_entry=next(x for x in first["stages"] if x["stage"]=="MODAL")
            self.assertEqual(modal_entry["run_manifest_count"],1)
            self.assertEqual(modal_entry["solver_status_counts"]["COMPLETED_SOLVER_ONLY"],1)
            self.assertEqual(modal_entry["cases"][0]["engineering_acceptance"],"NOT_VERIFIED")
            self.assertFalse((root/"09_SOFTWARE_DIAGNOSTICS").exists())
            script=Path(__file__).resolve().parents[1]/"tools"/"audit_stage_output_migration.py"
            completed=subprocess.run([sys.executable,str(script),str(root)],
                                     capture_output=True,text=True,check=True)
            self.assertIn("FILESYSTEM ONLY",completed.stdout)
            self.assertFalse((root/"09_SOFTWARE_DIAGNOSTICS").exists())
            subprocess.run([sys.executable,str(script),str(root),"--write"],
                           capture_output=True,text=True,check=True)
            files=list((root/"09_SOFTWARE_DIAGNOSTICS"/"MIGRATION_AUDITS").glob("*.json"))
            self.assertEqual(len(files),1)
            data=json.loads(files[0].read_text())
            self.assertEqual(data["schema"],"THESIS_LIVE_STAGE_OUTPUT_MIGRATION_AUDIT_V1")
            self.assertEqual(data["assessment"],"FILESYSTEM_ONLY_NOT_SOLVER_OR_ETABS_EQUIVALENCE")


if __name__=="__main__":
    unittest.main()

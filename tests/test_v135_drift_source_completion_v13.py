"""Fail-closed V135 drift: source identity + completed solver run are required."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from components.validation.design_checks import (
    run,saved_drift_solver_status,
)


class V135DriftSourceAndCompletionTests(unittest.TestCase):
    def test_current_sha_with_no_run_status_is_not_a_drift_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            model=root/"OpenSees_Complete_Model_Data_V118.json"
            model.write_text('{"frames":[],"shells":[]}',encoding="utf-8")
            digest=hashlib.sha256(model.read_bytes()).hexdigest()
            results=root/"05_MRSM"/"RUNS"/"ULS"/"case"/"run1"/"02_RESULTS"
            results.mkdir(parents=True)
            response=results/"MRSM_Results_V132.json"
            def save_response(sha):
                response.write_text(json.dumps({"X_E0":{
                    "model_sha256":sha,"limit_state":"ULS","axis":"X",
                    "stories":[{"story_number":1,"design_drift_ratio":0.005}]
                }}))
            def assess():
                with patch("components.validation.settings_audit.audit",
                           return_value={"rows":[]}):
                    return run(root)[0]
            save_response(digest)
            report=assess()
            self.assertEqual(report["drift_source_mismatch_excluded_count"],0)
            self.assertEqual(report["drift_source_unverified_row_count"],0)
            self.assertEqual(report["drift_run_completion_unverified_row_count"],1)
            row=report["tables"]["Seismic drift"][0]
            self.assertEqual(row["raw_limit_status"],"PASS")
            self.assertEqual(row["status"],"NOT EVALUATED")
            self.assertEqual(row["run_completion_status"],"NO_RUN_COMPLETION_MANIFEST")
            manifest=results.parent/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
            manifest.parent.mkdir()
            manifest.write_text(json.dumps({
                "solver_status":"COMPLETED_SOLVER_ONLY",
                "model_sha256":digest
            }))
            report=assess()
            self.assertEqual(report["drift_run_completion_unverified_row_count"],0)
            self.assertEqual(report["tables"]["Seismic drift"][0]["status"],"PASS")
            manifest.write_text(json.dumps({
                "solver_status":"INCOMPLETE","model_sha256":digest
            }))
            report=assess()
            self.assertEqual(report["tables"]["Seismic drift"][0]["status"],
                             "NOT EVALUATED")
            save_response("b"*64)
            manifest.write_text(json.dumps({
                "solver_status":"COMPLETED_SOLVER_ONLY","model_sha256":digest
            }))
            report=assess()
            self.assertEqual(report["tables"]["Seismic drift"],[])
            self.assertGreater(report["drift_source_mismatch_excluded_count"],0)
            self.assertTrue(any(r.get("status") in (
                "SOURCE_MANIFEST_RESULT_SHA_CONFLICT_EXCLUDED",
                "SOURCE_MODEL_SHA_MISMATCH_EXCLUDED")
                for r in report["tables"]["Open items"]))

    def test_legacy_drift_csv_without_hash_cannot_be_marked_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"OpenSees_Complete_Model_Data_V118.json").write_text(
                '{"frames":[],"shells":[]}',encoding="utf-8")
            legacy=root/"OpenSees_Analysis_Results"
            legacy.mkdir()
            csvfile=legacy/"Drift_Check_ULS_X.csv"
            csvfile.write_text(
                "limit_state,design_drift_ratio,story_number,axis\n"
                "ULS,0.003,1,X\n",encoding="utf-8")
            self.assertEqual(saved_drift_solver_status(csvfile),
                             "NO_RUN_COMPLETION_MANIFEST")
            with patch("components.validation.settings_audit.audit",
                       return_value={"rows":[]}):
                report,_=run(root)
            row=report["tables"]["Seismic drift"][0]
            self.assertEqual(row["source_identity_status"],"NOT_VERIFIED")
            self.assertEqual(row["status"],"NOT EVALUATED")
            self.assertEqual(row["raw_limit_status"],"PASS")


if __name__=="__main__":
    unittest.main()

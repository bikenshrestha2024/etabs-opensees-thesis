"""Review-only serialized source SHA checks; no ETABS/OpenSees solver."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from components.validation.saved_case_identity import (
    current_export_model_sha,recorded_result_model_sha,identity_screen,
)
from components.validation.case_review import collect


class ReviewSourceIntegrityTests(unittest.TestCase):
    def test_current_export_rows_are_filtered_for_wrong_model(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            source=root/"OpenSees_Complete_Model_Data_V118.json"
            source.write_text('{"model":"accepted source"}',encoding="utf-8")
            digest=hashlib.sha256(source.read_bytes()).hexdigest()
            saved=root/"05_MRSM"/"RUNS"/"ULS"/"case"/"run"/"02_RESULTS"
            saved.mkdir(parents=True)
            file=saved/"MRSM_Results_V132.json"
            file.write_text(json.dumps({"X_E0":{"model_sha256":"b"*64,
                "limit_state":"ULS","axis":"X","stories":[{
                "story_number":1,"design_drift_ratio":0.01
            }]}}))
            # Current-source mismatch is never presented as a valid plotted
            # result, although full historical source evidence is retained.
            result=collect(root)
            self.assertEqual(result["drift"],[])
            self.assertGreater(result["source_mismatch_excluded_count"],0)
            self.assertEqual(result["selected_serialized_model_sha256"],digest)
            self.assertIn("SOURCE_MODEL_SHA_MISMATCH_EXCLUDED",
                          [x.get("status") for x in result["issues"]])
            file.write_text(json.dumps({"X_E0":{"model_sha256":digest,
                "limit_state":"ULS","axis":"X","stories":[{
                "story_number":1,"design_drift_ratio":0.01
            }]}}))
            result2=collect(root)
            self.assertEqual(len(result2["drift"]),1)
            self.assertEqual(result2["source_mismatch_excluded_count"],0)
            self.assertEqual(result2["drift"][0]["source_identity_status"],
                             "MATCHED_SERIALIZED_MODEL_SHA_NOT_ETABS_EQUIVALENCE")

    def test_manifest_payload_source_conflict_excluded_even_when_manifest_matches(self):
        from components.validation.saved_case_identity import (
            recorded_result_model_sha,source_model_hash_evidence,identity_screen)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            result=root/"05_MRSM"/"RUNS"/"ULS"/"case"/"r1"/"02_RESULTS"
            result.mkdir(parents=True)
            manifest=result.parent/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
            manifest.parent.mkdir()
            manifest.write_text(json.dumps({"model_sha256":"a"*64}))
            numeric=result/"MRSM_Results_V132.json"
            numeric.write_text(json.dumps({"X_E0":{
                "model_sha256":"b"*64,
                "stories":[{"story_number":1,"design_drift_ratio":0.01}]
            }}))
            evidence=source_model_hash_evidence(numeric,"X_E0")
            self.assertTrue(evidence["conflict"])
            self.assertIsNone(recorded_result_model_sha(numeric,"X_E0"))
            selected,issues=identity_screen(
                [{"file":str(numeric),"case":"X_E0"}],
                expected_model_sha="a"*64)
            self.assertEqual(selected,[])
            self.assertEqual(issues[0]["status"],
                             "SOURCE_MANIFEST_RESULT_SHA_CONFLICT_EXCLUDED")
            self.assertEqual(issues[0]["payload_model_sha256"],"b"*64)
            numeric.write_text(json.dumps({"X_E0":{
                "model_sha256":"a"*64,
                "stories":[{"story_number":1,"design_drift_ratio":0.01}]
            }}))
            selected,issues=identity_screen(
                [{"file":str(numeric),"case":"X_E0"}],
                expected_model_sha="a"*64)
            self.assertEqual(len(selected),1)
            self.assertEqual(issues,[])
            self.assertEqual(selected[0]["source_identity_status"],
                             "MATCHED_SERIALIZED_MODEL_SHA_NOT_ETABS_EQUIVALENCE")

    def test_manifest_sha_and_missing_legacy_identity(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            numeric=root/"05_MRSM"/"RUNS"/"ULS"/"source"/"run"/"02_RESULTS"
            numeric.mkdir(parents=True)
            manifest=numeric.parent/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({"model_sha256":"c"*64}))
            file=numeric/"Deformation_MRSM_ULS_X_E0_V132.json"
            file.write_text('{"nodes":{}}')
            self.assertEqual(recorded_result_model_sha(file),"c"*64)
            selected,warnings=identity_screen([{"file":str(file),"case":"X_E0"}],
                                              expected_model_sha="a"*64)
            self.assertEqual(selected,[])
            self.assertEqual(len(warnings),1)
            unknown=root/"OpenSees_Analysis_Results"/"Drift_Check_ULS_Y_E0.csv"
            unknown.parent.mkdir(parents=True)
            unknown.write_text("story_number,design_drift_ratio\n1,0.001\n")
            selected,warnings=identity_screen([{"file":str(unknown)}],
                                              expected_model_sha="a"*64)
            self.assertEqual(len(selected),1)
            self.assertEqual(selected[0]["source_identity_status"],"NOT_VERIFIED")


if __name__=="__main__":
    unittest.main()

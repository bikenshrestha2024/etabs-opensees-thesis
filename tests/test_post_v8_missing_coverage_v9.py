"""Fail-closed regression of missing irregularity/stiffness evidence and history."""
import json
import hashlib
import tempfile
import unittest
from pathlib import Path

from components.validation.saved_stiffness import merge_saved_stiffness
from components.shared.case_status import (
    CaseLedger,update_history_case,history_batch_exit_gate,
)


class MissingStiffnessCoverageTests(unittest.TestCase):
    def test_no_saved_stiffness_is_incomplete_and_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"OpenSees_Complete_Model_Data_V118.json").write_text("{}")
            result={"checks":[]}
            for _ in range(2):
                result=merge_saved_stiffness(root,result)
                self.assertEqual(result["overall"],"INCOMPLETE")
                self.assertEqual(result["stiffness_import_coverage"],[])
                missing=[r for r in result["checks"] if r.get("status")=="NOT EVALUATED"]
                self.assertEqual(len(missing),4)
                self.assertEqual(
                    {r["check"] for r in missing},
                    {f"{state} {axis} soft-storey coverage"
                     for state in ("ULS","SLS") for axis in ("X","Y")})

    def test_partial_model_matched_stiffness_is_still_incomplete(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            source=root/"OpenSees_Complete_Model_Data_V118.json"
            source.write_text("{}")
            digest=hashlib.sha256(source.read_bytes()).hexdigest()
            folder=root/"05_MRSM"/"RUNS"/"ULS"/"case"/"run"/"02_RESULTS"
            folder.mkdir(parents=True)
            (folder/"Irregularity_X_E0_V132.json").write_text(json.dumps({
                "model_sha256":digest,"limit_state":"ULS","response_case":"X_E0",
                "checks":[{"check":"Soft story above","value":0.7,
                           "storey":1,"status":"IRREGULAR"}]}))
            output=merge_saved_stiffness(root,{"checks":[]})
            self.assertEqual(output["overall"],"IRREGULAR")
            self.assertEqual(output["stiffness_import_coverage"],[["ULS","X"]])
            self.assertEqual(len([r for r in output["checks"] if
                                  r.get("status")=="NOT EVALUATED"]),3)

    def test_missing_source_and_corrupt_saved_result_do_not_crash_review(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            folder=root/"05_MRSM"/"RUNS"/"ULS"/"case"/"run"/"02_RESULTS"
            folder.mkdir(parents=True)
            (folder/"Irregularity_X_E0_V132.json").write_text("{not json")
            output=merge_saved_stiffness(root,{"checks":[]})
            self.assertEqual(output["overall"],"INCOMPLETE")
            self.assertEqual(len([r for r in output["checks"]
                                  if r.get("status")=="NOT EVALUATED"]),4)
            statuses={i["status"] for i in output["stiffness_evidence_issues"]}
            self.assertIn("MISSING_SOURCE_MODEL",statuses)
            self.assertIn("UNREADABLE_STIFFNESS_EVIDENCE",statuses)

    def test_invalid_sixtyfour_characters_not_accepted_as_sha256(self):
        from components.validation.saved_case_identity import (
            recorded_result_model_sha,identity_screen)
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            file=folder/"MRSM_Results_V132.json"
            file.write_text(json.dumps({
                "X_E0":{"model_sha256":"z"*64}
            }))
            self.assertIsNone(recorded_result_model_sha(file,"X_E0"))
            selected,issues=identity_screen(
                [{"file":str(file),"case":"X_E0"}],
                expected_model_sha="a"*64)
            # An explicitly present but malformed digest is stronger negative
            # evidence than an absent optional legacy digest: exclude it.
            self.assertEqual(selected,[])
            self.assertEqual(len(issues),1)
            self.assertEqual(issues[0]["status"],
                             "INVALID_RESULT_MODEL_SHA_EXCLUDED")
            file.write_text(json.dumps({"X_E0":{"stories":[]}}))
            selected,issues=identity_screen(
                [{"file":str(file),"case":"X_E0"}],
                expected_model_sha="a"*64)
            self.assertEqual(len(selected),1)
            self.assertEqual(selected[0]["source_identity_status"],"NOT_VERIFIED")
            self.assertEqual(issues,[])

    def test_truncated_history_cannot_become_completed_via_late_ok(self):
        with tempfile.TemporaryDirectory() as td:
            ledger=CaseLedger(Path(td)/"ledger.json",["Kobe_XY"])
            update_history_case(ledger,"[START] Kobe_XY:")
            update_history_case(ledger,"[TRUNCATED] Kobe_XY: analyzed 0.1s of 45.29s")
            update_history_case(ledger,"[OK] Kobe_XY: script termination")
            self.assertEqual(ledger.rows["Kobe_XY"]["status"],"TRUNCATED")
            self.assertEqual(history_batch_exit_gate(ledger,0)["status"],"INCOMPLETE")


if __name__=="__main__":
    unittest.main()

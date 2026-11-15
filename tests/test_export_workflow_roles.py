"""Solver-independent case discovery, reviewed brace identity and file layout."""
import json
import tempfile
import unittest
from pathlib import Path

from OpenSees_Workflow_V144 import workflow_status
from components.model.display_ids import member_identity, display_label


class OutputAndIdentityTests(unittest.TestCase):
    def test_brace_family_and_specialized_roles_are_separate(self):
        self.assertEqual(member_identity("BRACE"),
                         {"prefix":"BR","family":"BRACE","brace_role":"BR"})
        self.assertEqual(member_identity("BRACE","CO")["prefix"],"CO")
        self.assertEqual(member_identity("BEAM","BT")["brace_role"],"BT")
        self.assertEqual(member_identity("BEAM")["family"],"BEAM")
        self.assertEqual(member_identity("BELT TRUSS")["brace_role"],"BT")
        self.assertEqual(member_identity("CAP TRUSS")["brace_role"],"CT")
        self.assertEqual(display_label("CT",25,1),"CT2501")

    def test_no_geometry_only_fvd_or_outrigger_guessing(self):
        for category, role in (("COLUMN","CT"),("FLOOR","CO"),
                               ("BRACE","FVD"),("CAP TRUSS","CO")):
            with self.subTest(category=category,role=role):
                with self.assertRaises(ValueError):
                    member_identity(category,role)
        self.assertEqual(member_identity("FVD")["prefix"],"FVD")
        self.assertEqual(member_identity("BRB")["prefix"],"BRB")
        # The source must explicitly classify the device. Neither LINK nor
        # an ordinary BRACE silently becomes FVD or BRB.
        with self.assertRaisesRegex(ValueError,"Unclassified"):
            member_identity("LINK")

    def test_canonical_stage_scoped_finds_and_no_false_completion(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            config=root/"OpenSees_Complete_Model_Config_V118.json"
            config.write_text("{}",encoding="utf-8")
            src=root/"OpenSees_Complete_Export_Report_V118.json"
            src.write_text('{"analysis_ready": false}',encoding="utf-8")
            modal=root/"04_MODAL"/"RUNS"/"ULS"/"02_RESULTS"
            modal.mkdir(parents=True)
            (modal/"NBC105_Modal_V111.json").write_text(
                '{"status":"failed"}',encoding="utf-8")
            mrsm=root/"05_MRSM"/"RUNS"/"ULS"
            mrsm.mkdir(parents=True)
            (mrsm/"MRSM_ULS_Summary.json").write_text(
                '{"status":"TRUNCATED"}',encoding="utf-8")
            false_candidate=root/"07_NONLINEAR_TIME_HISTORY"
            false_candidate.mkdir()
            (false_candidate/"NLTH_Fake_Summary.json.processing.json").write_text("{}")
            statuses=workflow_status(root)
            self.assertEqual(len(statuses),9)
            self.assertIn("CANDIDATE",statuses[0][0])
            self.assertIn("CANDIDATE",statuses[3][0])
            self.assertIn("CANDIDATE",statuses[5][0])
            self.assertIn("NO FILE",statuses[8][0])
            self.assertIn("NOT checked",statuses[3][1])
            self.assertNotIn("COMPLETED",statuses[3][0])

    def test_other_stage_sources_do_not_create_false_modal_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            unrelated=root/"03_ESM"/"RUNS"
            unrelated.mkdir(parents=True)
            (unrelated/"NBC105_Modal_V111.json").write_text("{}")
            statuses=workflow_status(root)
            self.assertIn("NO FILE",statuses[3][0])


if __name__=="__main__":
    unittest.main()

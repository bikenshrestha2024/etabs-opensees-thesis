"""Filesystem-only tests for saved stiffness and modal autofill paths."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from components.validation.saved_stiffness import merge_saved_stiffness
from components.inputs.analysis_autofill import matching_modal_reference


class LegacyReaderMigrationTests(unittest.TestCase):
    def test_irregularity_reader_accepts_canonical_source_match_not_review_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            model=root/"OpenSees_Complete_Model_Data_V118.json"
            model.write_text('{"nodes":{}}',encoding="utf-8")
            digest=hashlib.sha256(model.read_bytes()).hexdigest()
            case=root/"05_MRSM"/"RUNS"/"ULS"/"test"/"run1"/"02_RESULTS"
            case.mkdir(parents=True)
            doc={"model_sha256":digest,"limit_state":"ULS",
                 "response_case":"X_E0","checks":[{
                     "check":"Soft story stiffness","value":0.73,"storey":2,
                     "status":"IRREGULAR","clause":"5.4.1.2"}]}
            (case/"Irregularity_X_E0_V132.json").write_text(json.dumps(doc))
            snap=root/"05_MRSM"/"REVIEW_SNAPSHOTS"/"copy"
            snap.mkdir(parents=True)
            doc["checks"][0]["value"]=0.22
            (snap/"Irregularity_X_E0_V132.json").write_text(json.dumps(doc))
            result={"checks":[{"clause":"5.4.1.2","check":"old",
                                "status":"NOT EVALUATED"}]}
            found=merge_saved_stiffness(root,result)
            values=[x.get("value") for x in found["checks"] if x.get("value") is not None]
            self.assertEqual(values,[0.73])
            self.assertEqual(found["overall"],"IRREGULAR")
            self.assertIn(["ULS","X"],found["stiffness_import_coverage"])

    def test_modal_source_must_match_state_and_sha(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            modern=root/"04_MODAL"/"RUNS"/"ULS"/"source"/"r1"/"02_RESULTS"
            modern.mkdir(parents=True)
            saved=modern/"NBC105_Modal_V111.json"
            saved.write_text(json.dumps({
                "model_sha256":"a"*64,"limit_state":"ULS",
                "rows":[{"mode":1,"period_s":3.0}]}))
            self.assertEqual(matching_modal_reference(root,"ULS","a"*64),saved)
            self.assertIsNone(matching_modal_reference(root,"SLS","a"*64))
            self.assertIsNone(matching_modal_reference(root,"ULS","b"*64))
            self.assertIsNone(matching_modal_reference(root,"ULS",None))
            # A stale older file with different model SHA must not be used.
            old=root/"OpenSees_Analysis_Results"/"Modal_ULS"
            old.mkdir(parents=True)
            (old/"NBC105_Modal_V111.json").write_text(json.dumps({
                "model_sha256":"b"*64,"limit_state":"ULS",
                "rows":[{"mode":1,"period_s":7.0}]}))
            self.assertEqual(matching_modal_reference(root,"ULS","a"*64),saved)
            self.assertEqual(matching_modal_reference(root,"ULS","b"*64),
                             old/"NBC105_Modal_V111.json")


if __name__=="__main__":
    unittest.main()

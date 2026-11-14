"""Canonical modal producer/consumer file-contract regression (no solver)."""
import json
import tempfile
import unittest
from pathlib import Path

from components.modal.gui_and_reports import prepare_canonical_modal_run
from components.ui.results import saved_modal_result
from components.inputs.output_contract import record_case_status


class ModalLiveMigrationTests(unittest.TestCase):
    def test_new_modal_case_is_independent_and_discoverable(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            model=root/"OpenSees_Complete_Linear_Model.py"
            model.write_text("MODEL_READY=True\n",encoding="utf-8")
            a=prepare_canonical_modal_run(root,"ULS",model)
            b=prepare_canonical_modal_run(root,"ULS",model)
            self.assertNotEqual(a,b)
            self.assertTrue(a.is_relative_to(root/"04_MODAL"/"RUNS"/"ULS"))
            for run in (a,b):
                evidence=json.loads((run/"00_INPUT_SOURCE"/"MODAL_INPUT_PROVENANCE.json").read_text())
                self.assertEqual(evidence["limit_state"],"ULS")
                self.assertIsNone(evidence["assembled_model_sha256"])
                self.assertFalse((run/"02_RESULTS"/"NBC105_Modal_V111.json").exists())
            record_case_status(a,"COMPLETED_SOLVER_ONLY")
            (a/"02_RESULTS"/"NBC105_Modal_V111.json").write_text(json.dumps({
                "limit_state":"ULS","rows":[{"mode":1,"period_s":1.2}]
            }))
            self.assertEqual(saved_modal_result(root,"ULS"),
                             a/"02_RESULTS"/"NBC105_Modal_V111.json")
            self.assertIsNone(saved_modal_result(root,"SLS"))
            self.assertEqual(model.read_text(),"MODEL_READY=True\n")
            with self.assertRaises(ValueError):
                prepare_canonical_modal_run(root,"BOTH",model)

    def test_legacy_modal_and_unrelated_review_copies_not_selected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            old=root/"OpenSees_Analysis_Results"/"ULS_case"/"Modal_ULS"
            old.mkdir(parents=True)
            oldfile=old/"NBC105_Modal_V111.json"
            oldfile.write_text(json.dumps({"limit_state":"ULS","rows":[{"mode":1,"period_s":3.8}]}))
            copy=root/"04_MODAL"/"REVIEW_SNAPSHOTS"/"ULS"
            copy.mkdir(parents=True)
            (copy/oldfile.name).write_bytes(oldfile.read_bytes())
            self.assertEqual(saved_modal_result(root,"ULS"),oldfile)
            self.assertIsNone(saved_modal_result(root,"SLS"))


if __name__=="__main__":
    unittest.main()

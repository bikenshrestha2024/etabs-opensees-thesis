"""Cross-module modal → Linear TH reference policy identity regression.

Synthetic saved files only: no private EDB, Tk display or OpenSees solver.
[REF docs/source/components/inputs/analysis_autofill.py.md]
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from components.inputs.analysis_autofill import matching_modal_reference


class ModalToHistoryPolicyTests(unittest.TestCase):
    def _fixture(self, root, *, support="PHYSICAL_32", mass="SOURCE_DISTRIBUTED"):
        model_sha=hashlib.sha256(b"source-matched-model").hexdigest()
        folder=root/"04_MODAL"/"RUNS"/"ULS"/"synthetic_case"/"01_RESULTS"
        folder.mkdir(parents=True)
        output=folder/"NBC105_Modal_V111.json"
        output.write_text(json.dumps({
            "model_sha256": model_sha, "limit_state":"ULS",
            "selected_support_case_verification":{
                "status":"MATCHED_SELECTED_CASE_NOT_NATIVE_EQUIVALENT",
                "selected_profile": support, "actual_supports": 32 if support=="PHYSICAL_32" else 76,
            },
            "seismic_mass_policy": mass,
            "rows":[{"mode":1,"period_s":2.4,"UX_cumulative_percent":42.0,
                     "UY_cumulative_percent":33.0}],
        }),encoding="utf-8")
        return model_sha,output

    def test_selected_support_and_mass_must_both_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);sha,path=self._fixture(root,support="SOURCE_76",mass="STORY_LUMPED_NBC")
            with patch("components.inputs.output_layout.result_roots",return_value=[root/"04_MODAL"]):
                self.assertIsNone(matching_modal_reference(
                    root,"ULS",sha,support_case="PHYSICAL_32",
                    seismic_mass_policy="SOURCE_DISTRIBUTED"))
                self.assertEqual(path,matching_modal_reference(
                    root,"ULS",sha,support_case="SOURCE_76",
                    seismic_mass_policy="STORY_LUMPED_NBC"))

    def test_missing_policy_metadata_is_not_trusted_as_matching(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);sha,path=self._fixture(root)
            payload=json.loads(path.read_text())
            payload.pop("selected_support_case_verification")
            path.write_text(json.dumps(payload))
            with patch("components.inputs.output_layout.result_roots",return_value=[root/"04_MODAL"]):
                self.assertIsNone(matching_modal_reference(
                    root,"ULS",sha,support_case="PHYSICAL_32",
                    seismic_mass_policy="SOURCE_DISTRIBUTED"))

    def test_wrong_limit_state_or_model_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);sha,_=self._fixture(root)
            with patch("components.inputs.output_layout.result_roots",return_value=[root/"04_MODAL"]):
                self.assertIsNone(matching_modal_reference(
                    root,"SLS",sha,support_case="PHYSICAL_32",
                    seismic_mass_policy="SOURCE_DISTRIBUTED"))
                self.assertIsNone(matching_modal_reference(
                    root,"ULS","wrong-model",support_case="PHYSICAL_32",
                    seismic_mass_policy="SOURCE_DISTRIBUTED"))


if __name__=="__main__":
    unittest.main()

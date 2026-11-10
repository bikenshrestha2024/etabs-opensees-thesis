"""Offline synthetic evidence bundler tests: no ETABS, no solver."""
from __future__ import annotations
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from components.equivalent_static.evidence_bundle import (
    bundle_esm_validation,REQUIRED_SOURCE)

class EvidenceBundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source=self.root/"model";self.source.mkdir()
        self.output=self.root/"esm";self.output.mkdir()
        for name in REQUIRED_SOURCE:
            (self.source/name).write_text("{}",encoding="utf-8")
        (self.source/"OpenSees_Complete_Model_Config_V118.json").write_text(
            json.dumps({"etabs_beam_weight_policy":"ETABS_BEAM_CLEAR_LENGTH"}),
            encoding="utf-8")
        self.native=self.root/"native";self.native.mkdir()
        (self.native/"ETABS_EQ_PDELTA_NATIVE_INDEX.json").write_text(
            json.dumps({"actual_test_case":"EQX"}),encoding="utf-8")
        self.provenance={
            "status":"RESEARCH COMPARISON ONLY; NOT NBC DESIGN ACCEPTANCE",
            "source_excel":"C:/private/reference.xlsx",
            "source_excel_sha256":"a"*64,
            "source_edb":"C:/private/model.EDB",
            "source_edb_sha256":"b"*64,
            "coefficients":{"X":{"Aw_m2":1.9582936288088642,
                                 "T1_s":2.03856740011866},
                            "Y":{"Aw_m2":2.2030803324099724,
                                 "T1_s":1.9219797767063125}}
        }
        (self.source/"source_A_ETABS_LINKED_ESM.provenance.json").write_text(
            json.dumps(self.provenance),encoding="utf-8")
        (self.output/"NBC105_ESM_OpenSees_Response_ULS_X+_E0.json").write_text(
            "[]",encoding="utf-8")

    def test_all_inputs_one_zip_and_native_source(self):
        report=bundle_esm_validation(
            self.source,self.output,self.root/"packages",
            native_etabs_evidence=self.native)
        manifest=report["manifest"]
        self.assertEqual(manifest["status"],"EVIDENCE_COMPLETE_FOR_REVIEW")
        self.assertFalse(manifest["missing_required"])
        with zipfile.ZipFile(report["upload_zip"]) as z:
            paths=z.namelist()
            self.assertIn("source/OpenSees_Complete_Model_Config_V118.json",paths)
            self.assertIn("native_etabs/ETABS_EQ_PDELTA_NATIVE_INDEX.json",paths)
            self.assertIn("ETABS_Linked_Original_Excel_Aw_T1_Audit.json",paths)
            self.assertIn("READ_FIRST_ESM_VALIDATION.txt",paths)
            values=json.loads(z.read("ETABS_Linked_Original_Excel_Aw_T1_Audit.json"))
            self.assertEqual(values["linked_source_count"],1)
            self.assertFalse(values["coefficient_disagreement"])

    def test_runner_scripts_are_included_but_not_claimed_executed(self):
        name="OpenSees_NBC105_ESM_Load_And_Static_Analysis_ULS_X+_E0_V111.py"
        (self.output/name).write_text(
            "# Synthetic script; not an executed analysis\\n",
            encoding="utf-8")
        report=bundle_esm_validation(
            self.source,self.output,self.root/"packages",
            native_etabs_evidence=self.native)
        self.assertEqual(report["manifest"]["generated_runner_count"],1)
        self.assertEqual(report["manifest"]["generated_runner_execution_status"],
                         "NOT_INFERRED_FROM_SCRIPT_EXISTENCE")
        self.assertEqual(report["manifest"]["story_shear_plot_type"],
                         "SUM_OF_APPLIED_FORCES_NOT_SOLVED_SECTION_CUT")
        with zipfile.ZipFile(report["upload_zip"]) as archive:
            self.assertIn("generated_runners/esm/"+name,archive.namelist())

    def test_source_generated_runners_still_do_not_satisfy_response_gate(self):
        (self.output/"NBC105_ESM_OpenSees_Response_ULS_X+_E0.json").unlink()
        (self.source/"OpenSees_NBC105_ESM_Load_And_Static_Analysis_ULS_X+_E0_V111.py").write_text(
            "# A generated runner is not a solved response\\n",encoding="utf-8")
        report=bundle_esm_validation(
            self.source,self.output,self.root/"packages",
            native_etabs_evidence=self.native)
        self.assertEqual(report["manifest"]["generated_runner_count"],1)
        self.assertTrue(any("response profiles absent" in item
                            for item in report["manifest"]["missing_required"]))

    def test_gross_source_is_never_declared_complete(self):
        (self.source/"OpenSees_Complete_Model_Config_V118.json").write_text(
            json.dumps({"etabs_beam_weight_policy":"GROSS_SECTION_LENGTH"}),
            encoding="utf-8")
        report=bundle_esm_validation(self.source,self.output,
                                     self.root/"packages")
        self.assertEqual(report["manifest"]["status"],
                         "INCOMPLETE_MISSING_EVIDENCE")
        self.assertTrue(any("CORRECTED_BEAM_POLICY" in m
                            for m in report["manifest"]["missing_required"]))

    def test_conflicting_excel_calculation_blocks(self):
        mismatch=dict(self.provenance)
        mismatch["coefficients"]={
            "X":{"Aw_m2":1.9306371},"Y":{"Aw_m2":2.2030803324099724}}
        (self.source/"source_B_ETABS_LINKED_ESM.provenance.json").write_text(
            json.dumps(mismatch),encoding="utf-8")
        report=bundle_esm_validation(self.source,self.output,
                                     self.root/"packages",
                                     native_etabs_evidence=self.native)
        self.assertEqual(report["manifest"]["status"],
                         "INCOMPLETE_MISSING_EVIDENCE")
        self.assertTrue(any("calculation sources disagree" in v
                            for v in report["manifest"]["missing_required"]))

if __name__=="__main__":
    unittest.main()

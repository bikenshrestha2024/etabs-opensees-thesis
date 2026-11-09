"""No false P-Delta PASS from names or files; purely synthetic tests."""
import json
import tempfile
import unittest
from pathlib import Path
from components.validation.eq_pdelta_evidence import verify_eq_pdelta_evidence

class EQPDeltaEvidenceTests(unittest.TestCase):
    def test_missing_source_cases_block_both_directions(self):
        with tempfile.TemporaryDirectory() as tmp:
            index=Path(tmp)/"cases.json"
            index.write_text(json.dumps({"X":{"axis":"X","etabs_case_name":"EQX P Delta"},
                                         "Y":{"axis":"Y","etabs_case_name":"EQY P Delta"}}),
                             encoding="utf-8")
            result=verify_eq_pdelta_evidence(index,Path(tmp)/"output")
            self.assertEqual(len(result["cases"]),2)
            for c in result["cases"]:
                self.assertEqual(c["status"],"BLOCKED_MISSING_OR_INCOMPATIBLE_EVIDENCE")
                self.assertTrue(any("MISSING_FIELDS" in issue for issue in c["missing_or_blocked"]))
            self.assertTrue((Path(tmp)/"output/EQX_EQY_PDelta_Evidence_Gates.json").is_file())

    def test_inconsistent_axis_and_pdelta_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"proof.json"
            file.write_text('{"case":"synthetic"}',encoding="utf-8")
            sample=lambda axis:dict(
                axis=axis,etabs_case_name="EQ"+axis+" P Delta",
                etabs_analysis_type="Linear Static",
                etabs_pdelta_enabled=True,
                etabs_combination_or_case_definition="synthetic source",
                etabs_evidence_path=str(file),opensees_result_path=str(file),
                opensees_preload_evidence_path=str(file),
                opensees_source_model_sha256="a"*64,
                limit_state="ULS",pdelta_method="PDelta geometric transformation",
                gravity_factors={"Self Weight":1.2},
                lateral_action_factors={"EQ"+axis:1.0})
            data={"X":sample("X"),"Y":sample("Y")}
            data["Y"]["axis"]="X"
            data["Y"]["etabs_pdelta_enabled"]=False
            idx=Path(tmp)/"cases.json"
            idx.write_text(json.dumps(data),encoding="utf-8")
            result=verify_eq_pdelta_evidence(idx,Path(tmp)/"output")
            self.assertEqual(result["cases"][0]["status"],
                             "BLOCKED_MISSING_OR_INCOMPATIBLE_EVIDENCE")
            self.assertIn("INCOMPLETE_RESPONSE_PAIRS",result["cases"][0]["missing_or_blocked"])
            self.assertIn("AXIS_MISMATCH",result["cases"][1]["missing_or_blocked"])
            self.assertIn("NATIVE_ETABS_PDELTA_NOT_CONFIRMED",
                          result["cases"][1]["missing_or_blocked"])

if __name__=="__main__":
    unittest.main()

"""ESM combined export and GUI safety (synthetic files, no ETABS/solver)."""
import ast
import json
from pathlib import Path
import tempfile
import unittest

from components.equivalent_static.organized_exports import build_combined_esm_export
from components.validation.etabs_direct_api import validate_mapping

ROOT = Path(__file__).resolve().parents[1]


class ESMCombinedExportTests(unittest.TestCase):
    def _make_case(self, root):
        filename="NBC105_ESM_Calculation_ULS_X+_E0_V111.json"
        payload={
            "response_case":"ULS_X+_E0","limit_state":"ULS",
            "period_s":1.98128089,"zoning_factor_Z":0.35,
            "soil_type":"C","period_exponent_k":1.7406,
            "site_subsoil_status":"NOT VERIFIED",
            "total_seismic_weight_kN":210000,
            "base_shear_kN":25659.046,
            "total_floor_force_kN":25659.046,
            "code_eligible":False,
            "esm_eligibility":"High-rise ULS comparison only",
            "period_selection":{"empirical_Aw_X_m2":"2.07317452"},
            "stories":[{"story_name":"1F","story_number":1,"height_m":3.8,
                        "seismic_weight_kN":9000,
                        "lateral_force_kN":200,"master_node_tag":1001}]
        }
        (root/filename).write_text(json.dumps(payload),encoding="utf-8")
        (root/"NBC105_ESM_Storey_Forces_ULS_X+_E0_V111.csv").write_text(
            "story_number,story_name,floor_force_kN\n1,1F,200\n",encoding="utf-8")
        (root/"OpenSees_NBC105_ESM_Load_And_Static_Analysis_ULS_X+_E0_V111.py").write_text(
            "# Synthetic runner; DO NOT EXECUTE\n",encoding="utf-8")
        etabs=root/"ETABS_Linked_ESM"
        etabs.mkdir()
        (etabs/"original_20261112_ETABS_LINKED_ESM.provenance.json").write_text(
            '{"source_edb":"C:/original.edb","assumptions_verified":false}',
            encoding="utf-8")
        return root/filename

    def test_copy_only_separated_modules_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            source=self._make_case(root)
            original=source.read_bytes()
            result=build_combined_esm_export(root)
            self.assertEqual(source.read_bytes(),original)
            self.assertEqual(result["cases"],1)
            index=json.loads(Path(result["manifest"]).read_text(encoding="utf-8"))
            self.assertEqual(index["acceptance"],
                             "COMPARISON_ONLY_NOT_NATIVE_ETABS_OR_NBC_CERTIFICATION")
            self.assertFalse(index["original_outputs_modified"])
            categories={r["module"] for r in index["files"]}
            self.assertIn("ETABS_Linked_Equivalent_Static",categories)
            self.assertIn("OpenSees_Direct_Equivalent_Static",categories)
            self.assertTrue(any("/JSON/" in r["snapshot_path"] for r in index["files"]))
            self.assertTrue(any("/CSV/" in r["snapshot_path"] for r in index["files"]))
            from openpyxl import load_workbook
            wb=load_workbook(result["workbook"],read_only=True,data_only=True)
            self.assertIn("Case Summary",wb.sheetnames)
            self.assertIn("Storey Forces",wb.sheetnames)
            self.assertIn("Validation Gates",wb.sheetnames)
            self.assertIn("REQUIRES",str(tuple(wb["Validation Gates"].values)))
            self.assertTrue(Path(result["zip"]).is_file())

    def test_no_input_case_does_not_invent_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"NBC105_ESM_Storey_Forces_ULS_X+_E0_V111.csv").write_text(
                "story,force\n1,0\n",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"no calculation JSON"):
                build_combined_esm_export(root)

    def test_bad_json_is_reported_as_invalid_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            file=root/"NBC105_ESM_Calculation_ULS_X+_E0_V111.json"
            file.write_text("[]",encoding="utf-8")
            result=build_combined_esm_export(root)
            from openpyxl import load_workbook
            wb=load_workbook(result["workbook"],read_only=True,data_only=True)
            rows=list(wb["Case Summary"].values)
            self.assertIn("INVALID SOURCE",str(rows))
            self.assertNotIn("VERIFIED NATIVE ETABS",str(rows))


class ESMGuiSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code=(ROOT/"components/equivalent_static/calculation_and_gui.py").read_text(
            encoding="utf-8")
        ast.parse(cls.code)

    def test_actions_grouped_and_export_visible(self):
        for text in ("ETABS comparison","Wall / period sources",
                     "Plots, reports and files","Export combined Excel + ZIP",
                     "Stop running batch","ESM_Organized"):
            if text == "ESM_Organized":
                self.assertIn(text,(ROOT/"components/equivalent_static/organized_exports.py").read_text())
            else:
                self.assertIn(text,self.code)
        self.assertNotIn("for button in footer.winfo_children():button.pack_forget()",self.code)

    def test_color_coded_status_and_cancel(self):
        for state in ('"RUNNING"','"FINISHED"','"BLOCKED"','"CANCELLED"','"EXPORTED"'):
            self.assertIn(state,self.code)
        self.assertIn("PROCESS ONLY",self.code)
        self.assertIn("self._esm_cancel_requested",self.code)

    def test_wrong_json_type_explained(self):
        with self.assertRaisesRegex(ValueError,"not an ETABS case-and-story mapping"):
            validate_mapping([{"source_edb":"C:/source.EDB"}])


if __name__=="__main__":
    unittest.main()

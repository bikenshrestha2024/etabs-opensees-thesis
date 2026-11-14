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
            self.assertTrue(Path(result["folder"]).is_relative_to(root / "03_ESM" / "REVIEW_SNAPSHOTS"))
            self.assertEqual(result["solver_batch_status"], "NOT_RUN")
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
            self.assertIn("Solver Batch Status",wb.sheetnames)
            self.assertIn("REQUIRES",str(tuple(wb["Validation Gates"].values)))
            self.assertTrue(Path(result["zip"]).is_file())

    def test_running_batch_not_misreported_as_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_case(root)
            status_dir = root / "ESM_Runner_Status" / "20261114_110851"
            status_dir.mkdir(parents=True)
            (status_dir / "CASE_STATUS.json").write_text(json.dumps([
                {"case":"OpenSees_NBC105_ESM_Load_And_Static_Analysis_ULS_X+_E0_V111.py",
                 "status":"RUNNING","return_code":None}]))
            result = build_combined_esm_export(root)
            self.assertEqual(result["solver_batch_status"], "PARTIAL_OR_FAILED")
            metadata = json.loads(Path(result["manifest"]).read_text())
            self.assertEqual(metadata["snapshot_status"], "PARTIAL_OR_UNVERIFIED")

    def test_exact_solver_identity_required_for_complete_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_case(root)
            run_name = "OpenSees_NBC105_ESM_Load_And_Static_Analysis_ULS_X+_E0_V111.py"
            status_dir = root / "ESM_Runner_Status" / "20261114_110851"
            status_dir.mkdir(parents=True)
            path = status_dir / "CASE_STATUS.json"
            def export_with(rows):
                path.write_text(json.dumps(rows), encoding="utf-8")
                return build_combined_esm_export(root)
            success = {"case": run_name, "status": "SUCCESS",
                       "return_code": 0, "elapsed_s": 140.0}
            result = export_with([success])
            self.assertEqual(result["solver_batch_status"], "COMPLETE_SOLVER_ONLY")
            result = export_with([success, success])
            self.assertEqual(result["solver_batch_status"], "PARTIAL_OR_FAILED")
            manifest = json.loads(Path(result["manifest"]).read_text())
            self.assertEqual(manifest["solver_batch"]["duplicate_cases"], [run_name])
            result = export_with([{"case": "OTHER_CASE.py", "status": "SUCCESS",
                                   "return_code": 0}])
            self.assertEqual(result["solver_batch_status"], "PARTIAL_OR_FAILED")
            manifest = json.loads(Path(result["manifest"]).read_text())
            self.assertEqual(manifest["solver_batch"]["missing_cases"], [run_name])
            self.assertEqual(manifest["solver_batch"]["unexpected_cases"], ["OTHER_CASE.py"])

    def test_stale_success_cannot_cover_missing_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_case(root)
            second = "OpenSees_NBC105_ESM_Load_And_Static_Analysis_ULS_Y+_E0_V111.py"
            (root / second).write_text("# Synthetic", encoding="utf-8")
            status_dir = root / "ESM_Runner_Status" / "20261114_110851"
            status_dir.mkdir(parents=True)
            first = "OpenSees_NBC105_ESM_Load_And_Static_Analysis_ULS_X+_E0_V111.py"
            (status_dir / "CASE_STATUS.json").write_text(json.dumps([
                {"case": first, "status": "SUCCESS", "return_code": 0}
            ]), encoding="utf-8")
            result = build_combined_esm_export(root)
            self.assertEqual(result["solver_batch_status"], "PARTIAL_OR_FAILED")
            overview = json.loads(Path(result["manifest"]).read_text())
            self.assertEqual(overview["solver_batch"]["missing_cases"], [second])

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
                     "Stop running batch","REVIEW_SNAPSHOTS"):
            if text == "REVIEW_SNAPSHOTS":
                # Canonical path literal is in the single shared source of truth,
                # not repeated in each stage exporter.
                self.assertIn(text, (ROOT/"components/inputs/output_layout.py").read_text())
                self.assertIn("review_snapshots_for",
                              (ROOT/"components/equivalent_static/organized_exports.py").read_text())
            else:
                self.assertIn(text,self.code)
        self.assertNotIn("for button in footer.winfo_children():button.pack_forget()",self.code)

    def test_color_coded_status_and_cancel(self):
        for state in ('"RUNNING"','"FINISHED"','"BLOCKED"','"CANCELLED"','"EXPORTED"'):
            self.assertIn(state,self.code)
        self.assertIn("PROCESS ONLY",self.code)
        self.assertIn("self._esm_cancel_requested",self.code)

    def test_shared_log_has_independent_scroll_actions(self):
        source=(ROOT/"components/ui/plot_utilities.py").read_text(encoding="utf-8")
        self.assertIn("Scroll to start",source)
        self.assertIn("Scroll to latest",source)
        self.assertIn("orient='vertical',command=text.yview",source)
        self.assertIn("orient='horizontal',command=text.xview",source)
        self.assertIn("current.winfo_class() in ('Text','Treeview','Listbox')",source)

    def test_wrong_json_type_explained(self):
        with self.assertRaisesRegex(ValueError,"not an ETABS case-and-story mapping"):
            validate_mapping([{"source_edb":"C:/source.EDB"}])


if __name__=="__main__":
    unittest.main()

"""Non-native categorised evidence export tests."""
from __future__ import annotations
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from components.ui.organized_results import classify, publish_organized_results, sha256


class OrganizedReviewTests(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(classify("MRSM_Results_V134.xlsx"), "MRSM")
        self.assertEqual(classify("NBC105_ESM_Force_Profile_ULS_X.png"), "ESM")
        self.assertEqual(classify("Gravity_Result_V110.json"), "Gravity")
        self.assertEqual(classify("Modal_ULS/mode_shapes.json"), "Modal")
        self.assertEqual(classify("ETABS_Comparison_V148/Comparison.csv"), "Comparisons")

    def test_classify_time_histories_separately(self):
        self.assertEqual(classify("06_LINEAR_TIME_HISTORY/RUNS/ULS/XY/Deformation.json"),"LinearTH")
        self.assertEqual(classify("07_NONLINEAR_TIME_HISTORY/RUNS/M0/XY/Response.json"),"NonlinearTH")
        self.assertEqual(classify("06_LINEAR_TH/ULS/Linear_Time_History.csv"),"LinearTH")
        self.assertEqual(classify("07_NONLINEAR_TH/NLTHA_XY_Result.json"),"NonlinearTH")
        self.assertEqual(classify("OpenSees_NLTHA_XY_Results.json"),"NonlinearTH")

    def test_time_history_files_get_dedicated_review_zip(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"case"
            root.mkdir()
            linear=root/"06_LINEAR_TIME_HISTORY"/"RUNS"/"ULS"/"LTH_XY.json"
            nonlinear=root/"07_NONLINEAR_TIME_HISTORY"/"RUNS"/"M0"/"NLTHA_XY.json"
            for file in (linear,nonlinear):
                file.parent.mkdir(parents=True,exist_ok=True)
                file.write_text('{"solver_status":"INCOMPLETE"}')
            pack=publish_organized_results(root)
            self.assertIn("LinearTH",pack["zip_files"])
            self.assertIn("NonlinearTH",pack["zip_files"])
            self.assertEqual(pack["status"],"OUTPUT_INDEX_NOT_ENGINEERING_ACCEPTANCE")
            for stage in ("LinearTH","NonlinearTH"):
                with zipfile.ZipFile(pack["zip_files"][stage]) as archive:
                    self.assertIn("EVIDENCE_MANIFEST.json",archive.namelist())

    def test_preserves_sources_exports_distinct_zip_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "ULS_MODEL_A"
            root.mkdir()
            files = {
                "MRSM_ULS/MRSM_Results_V132.json": b'{"completed":true}',
                "Gravity_Result_V110.json": b'{"ok":true}',
                "NBC105_ESM_Force_Profile_ULS_X.png": b"test illustration",
                "Modal_ULS/Modal_Periods.csv": b"mode,T\n1,2.38",
                "ETABS_Comparison_V148/Comparison.csv": b"status\nMISSING_ETABS",
                "RUN_NOTES.txt": b"test notes",
                "SourceModel.EDB": b"PRIVATE EDB",
                "Seismic_Review_Packages/OLD_UPLOAD.zip": b"archived prior run",
            }
            for name, data in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            original_hash = sha256(root / "MRSM_ULS/MRSM_Results_V132.json")
            result = publish_organized_results(root)
            self.assertEqual(result["status"], "OUTPUT_INDEX_NOT_ENGINEERING_ACCEPTANCE")
            self.assertEqual(result["file_count"], 6)
            archive = Path(result["zip_files"]["ALL_MODULES"])
            with zipfile.ZipFile(archive) as z:
                names = set(z.namelist())
                self.assertIn("MRSM/Analysis/MRSM_ULS/MRSM_Results_V132.json", names)
                self.assertIn("Unclassified/Analysis/RUN_NOTES.txt", names)
                self.assertIn("EVIDENCE_MANIFEST.json", names)
                self.assertFalse(any(x.endswith(".EDB") for x in names))
                self.assertFalse(any("OLD_UPLOAD.zip" in x for x in names))
            self.assertEqual(sha256(root / "MRSM_ULS/MRSM_Results_V132.json"), original_hash)
            manifest = json.loads(Path(result["manifest"]).read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["entries"]), 6)
            again = publish_organized_results(root)
            self.assertEqual(again["file_count"], 6)
            self.assertNotEqual(result["folder"], again["folder"])

    def test_gravity_review_under_export_02_gravity_isolated(self):
        with tempfile.TemporaryDirectory() as tmp:
            export = Path(tmp) / "Export_02"
            root = export / "OpenSees_Analysis_Results" / "ULS_Model"
            gravity = export / "02_GRAVITY" / "SOURCE_RUNS"
            root.mkdir(parents=True)
            gravity.mkdir(parents=True)
            (root / "Gravity_Result_V110.json").write_text('{"ok":true}')
            (root / "Modal_Results.json").write_text('{"modal":true}')
            (root / "ETABS_Comparison.csv").write_text("source,open\\n1,1\\n")
            (gravity / "Gravity_Run_V110.log").write_text("gravity log")
            home = export / "02_GRAVITY" / "REVIEW_SNAPSHOTS"
            first = publish_organized_results(
                root, gravity_root=gravity, destination_parent=home,
                selected_modules=("Gravity", "Comparisons"),
                bundle_name="GRAVITY_REVIEW")
            self.assertTrue(Path(first["folder"]).is_relative_to(home))
            self.assertIn("GRAVITY_REVIEW", first["zip_files"])
            with zipfile.ZipFile(first["zip_files"]["GRAVITY_REVIEW"]) as z:
                entries = z.namelist()
                self.assertTrue(any("Gravity_Result_V110.json" in n for n in entries))
                self.assertTrue(any("ETABS_Comparison.csv" in n for n in entries))
                self.assertFalse(any("Modal_Results.json" in n for n in entries))
            self.assertTrue((root / "Gravity_Result_V110.json").exists())
            # A second snapshot must not recursively copy the first review.
            second = publish_organized_results(
                root, gravity_root=gravity, destination_parent=home,
                selected_modules=("Gravity", "Comparisons"),
                bundle_name="GRAVITY_REVIEW")
            self.assertEqual(first["file_count"], second["file_count"])

    def test_separate_gravity_output_can_be_packaged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "analysis"
            gravity = Path(tmp) / "gravity_gui"
            root.mkdir()
            gravity.mkdir()
            (root / "MRSM_Results_V134.json").write_text("{}")
            (gravity / "Gravity_Result_V110.json").write_text('{"ok":true}')
            result = publish_organized_results(root, gravity_root=gravity)
            self.assertIn("Gravity", result["zip_files"])
            manifest = json.loads(Path(result["manifest"]).read_text())
            self.assertTrue(any(row["source_root"] == str(gravity.resolve())
                                for row in manifest["entries"]))


if __name__ == "__main__":
    unittest.main()

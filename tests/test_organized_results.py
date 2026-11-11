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

"""Regression: gravity review evidence has one compressed copy and no redundant tree."""
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from components.ui.organized_results import publish_organized_results


class GravityArchiveOnlyTests(unittest.TestCase):
    def test_one_zip_no_extracted_duplicates_and_verified_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"selected_export";root.mkdir()
            report=root/"Gravity_Run_V110.log";report.write_text("Gravity PASS",encoding="utf-8")
            chart=root/"Gravity_Deformation_V123.png";chart.write_bytes(b"synthetic-figure")
            dest_parent=root.parent/"reviews"
            result=publish_organized_results(root,destination_parent=dest_parent,
                selected_modules=("Gravity",),bundle_name="GRAVITY_REVIEW",
                archive_only=True)
            folder=Path(result["folder"])
            items=list(folder.iterdir())
            self.assertEqual({x.name for x in items},
                {"EVIDENCE_MANIFEST.json","README_FIRST.txt"})
            self.assertEqual(Path(result["zip_files"]["GRAVITY_REVIEW"]).parent,
                             root/"07_EXPORT_ZIP")
            self.assertEqual(set(result["zip_files"]),{"GRAVITY_REVIEW"})
            manifest=json.loads((folder/"EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertTrue(manifest["archive_only_no_extracted_copies"])
            self.assertEqual(manifest["file_count"],2)
            zipfile_path=Path(result["zip_files"]["GRAVITY_REVIEW"])
            with zipfile.ZipFile(zipfile_path) as z:
                for entry in manifest["entries"]:
                    self.assertFalse((folder/entry["snapshot"]).exists())
                    raw=z.read(entry["snapshot"])
                    self.assertEqual(hashlib.sha256(raw).hexdigest(),entry["sha256"])
                archive_manifest=json.loads(z.read("EVIDENCE_MANIFEST.json"))
                self.assertTrue(all(x["source"]=="<REDACTED_LOCAL_PATH>"
                                    for x in archive_manifest["entries"]))
            self.assertEqual(report.read_text(encoding="utf-8"),"Gravity PASS")
            self.assertEqual(chart.read_bytes(),b"synthetic-figure")

    def test_default_snapshot_behavior_remains_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"source";root.mkdir()
            (root/"Gravity_Result_V110.json").write_text('{"ok":true}',encoding="utf-8")
            result=publish_organized_results(root,destination_parent=Path(td)/"reviews",
                selected_modules=("Gravity",),bundle_name="GRAVITY_REVIEW")
            folder=Path(result["folder"])
            self.assertTrue(any(x.name=="Gravity_Result_V110.json"
                                for x in folder.rglob("Gravity_Result_V110.json")))
            self.assertIn("Gravity",result["zip_files"])


if __name__=="__main__":
    unittest.main()

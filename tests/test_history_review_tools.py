"""Deterministic tests for local ZIP evidence exports; no Tk/OpenSees needed."""
import json
import tempfile
import unittest
from pathlib import Path

from components.ui.history_review_tools import export_review_zip
from zipfile import ZipFile


class HistoryReviewExportTests(unittest.TestCase):
    def test_preserves_originals_and_excludes_archives(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "case").mkdir()
            (root / "case" / "response.csv").write_text("time_s,ux_m\n0,0\n")
            (root / "case" / "run.log").write_text("TRUNCATED_DIAGNOSTIC_NOT_CODE_ACCEPTANCE")
            (root / "private.pem").write_text("not-an-actual-key")
            (root / "old.zip").write_bytes(b"dummy")
            zip_path, manifest = export_review_zip(root, "linear")
            self.assertTrue(zip_path.is_file())
            self.assertTrue((root / "case" / "response.csv").is_file())
            self.assertEqual(manifest["status"], "REVIEW_EVIDENCE_NOT_ENGINEERING_ACCEPTANCE")
            with ZipFile(zip_path) as z:
                self.assertIn("case/response.csv", z.namelist())
                self.assertIn("case/run.log", z.namelist())
                self.assertNotIn("private.pem", z.namelist())
                self.assertNotIn("old.zip", z.namelist())
                details = json.loads(z.read("REVIEW_EVIDENCE_MANIFEST.json"))
                self.assertEqual(len(details["files"]), 2)
                self.assertEqual(len(details["excluded"]), 2)
            newer, _ = export_review_zip(root, "linear")
            self.assertNotEqual(newer, zip_path)
            with ZipFile(newer) as z:
                self.assertNotIn(zip_path.name, z.namelist())

    def test_rejects_unrecognized_module(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(KeyError):
                export_review_zip(folder, "unknown")


if __name__ == "__main__":
    unittest.main()

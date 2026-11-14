"""Test private literature hash audit without exposing or uploading PDF content."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "LITERATURE" / "tools" / "audit_private_pdf_uploads.py"
spec = importlib.util.spec_from_file_location("audit_private_pdf_uploads", SOURCE)
pdf_audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pdf_audit)


class LiteraturePdfAuditTests(unittest.TestCase):
    def test_duplicate_hash_groups_and_non_destructive_behavior(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "PRIVATE_PDFS"
            root.mkdir()
            a = root / "first.pdf"
            b = root / "second.pdf"
            c = root / "not_a_pdf.txt"
            a.write_bytes(b"%PDF-1.7\nsynthetic")
            b.write_bytes(a.read_bytes())
            c.write_bytes(b"%PDF-1.7\nsynthetic")
            report = pdf_audit.inventory(root)
            self.assertEqual(report["file_count"], 2)
            self.assertEqual(len(report["duplicate_sha256_groups"]), 1)
            self.assertEqual(set(report["duplicate_sha256_groups"][0]["filenames"]),
                             {"first.pdf", "second.pdf"})
            self.assertTrue(all(record["is_pdf_signature"] for record in report["files"]))
            target = Path(td) / "PRIVATE_AUDIT" / "inventory.json"
            pdf_audit.save_private_json(report, target)
            self.assertTrue(target.is_file())
            self.assertEqual(json.loads(target.read_text())["file_count"], 2)
            self.assertEqual(a.read_bytes(), b"%PDF-1.7\nsynthetic")
            self.assertEqual(b.read_bytes(), a.read_bytes())

    def test_non_pdf_signature_is_explicitly_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "fake.pdf").write_bytes(b"not a real PDF")
            report = pdf_audit.inventory(root)
            self.assertEqual(report["file_count"], 1)
            self.assertFalse(report["files"][0]["is_pdf_signature"])


if __name__ == "__main__":
    unittest.main()

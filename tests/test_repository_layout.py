"""Repository-layout inventory regression tests (stdlib; no ETABS required)."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from tools.audit_repository_layout import audit


class LayoutAuditTests(unittest.TestCase):
    def test_rejects_tracked_symlink_without_reading_external_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            external = Path(tmp) / "private.txt"
            root.mkdir()
            external.write_text("SECRET OUTSIDE CHECKOUT", encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            link = root / "external.txt"
            try:
                link.symlink_to(external)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation unavailable")
            (root / "OLD_NOTE.md").write_text("history", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            report = audit(root)
            self.assertIn("external.txt", report["skipped_text_files"])
            note = next(x for x in report["root_files"] if x["path"] == "OLD_NOTE.md")
            self.assertEqual(note["relocation_status"], "HOLD_REVIEW_REQUIRED")
            self.assertEqual(external.read_text(), "SECRET OUTSIDE CHECKOUT")

    def test_malformed_tracked_utf8_blocks_relocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "BROKEN.md").write_bytes(bytes((0xff, 0xfe)))
            (root / "OLD_NOTE.md").write_text("history", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            report = audit(root)
            self.assertIn("BROKEN.md", report["skipped_text_files"])
            note = next(x for x in report["root_files"] if x["path"] == "OLD_NOTE.md")
            self.assertEqual(note["relocation_status"], "HOLD_REVIEW_REQUIRED")

    def test_inventory_is_read_only_and_blocks_referenced_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "01_MAIN.py").write_text("print('one')\n", encoding="utf-8")
            (root / "01_OLD.py").write_text("print('two')\n", encoding="utf-8")
            (root / "OLD_NOTE.md").write_text("history\n", encoding="utf-8")
            (root / "README.md").write_text("See OLD_NOTE.md\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            before = {p.name: p.read_bytes() for p in root.iterdir() if p.is_file()}
            report = audit(root)
            after = {p.name: p.read_bytes() for p in root.iterdir() if p.is_file()}
            self.assertEqual(before, after)
            self.assertFalse(report["source_changes_performed"])
            self.assertEqual(report["total_tracked_files"], 4)
            self.assertIn("01", report["duplicate_numbered_prefixes"])
            note = next(x for x in report["root_files"] if x["path"] == "OLD_NOTE.md")
            self.assertEqual(note["relocation_status"], "HOLD_REVIEW_REQUIRED")
            self.assertEqual(note["reference_files"], ["README.md"])
            self.assertEqual(next(x for x in report["root_files"]
                                  if x["path"] == "01_MAIN.py")["relocation_status"],
                             "PINNED")


if __name__ == "__main__":
    unittest.main()

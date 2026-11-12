"""Non-native regression tests for nondestructive Windows output auditing."""
import tempfile
import unittest
from pathlib import Path

from tools.audit_output_storage import scan_output, write_report


class OutputStorageAuditTests(unittest.TestCase):
    def test_exact_bytes_only_and_never_change_sources(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "project"
            root.mkdir()
            (root / "02_GRAVITY").mkdir()
            (root / "OpenSees_Analysis_Results").mkdir()
            a = root / "02_GRAVITY" / "same.txt"
            b = root / "OpenSees_Analysis_Results" / "duplicate.txt"
            c = root / "02_GRAVITY" / "different.txt"
            a.write_bytes(b"same source evidence")
            b.write_bytes(b"same source evidence")
            c.write_bytes(b"another solver case")
            before = {p: p.read_bytes() for p in (a, b, c)}
            audit = scan_output(root)
            self.assertEqual(audit["total_files"], 3)
            self.assertEqual(audit["total_bytes"],
                             sum(len(x) for x in before.values()))
            self.assertEqual(len(audit["exact_duplicate_groups"]), 1)
            group = audit["exact_duplicate_groups"][0]
            self.assertEqual(group["repeat_count"], 2)
            self.assertEqual(group["redundant_bytes"], len(before[a]))
            self.assertTrue(group["review_only"])
            dest = Path(td) / "disk_report"
            write_report(audit, dest)
            self.assertTrue((dest / "READ_FIRST.md").is_file())
            self.assertTrue((dest / "DISK_AUDIT.json").is_file())
            self.assertTrue((dest / "EXACT_DUPLICATES.csv").is_file())
            with self.assertRaises(FileExistsError):
                write_report(audit, dest)
            self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_no_hash_does_not_infer_duplicate_from_equal_size(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.txt").write_bytes(b"aaaa")
            (root / "b.txt").write_bytes(b"bbbb")
            audit = scan_output(root, hash_duplicates=False)
            self.assertEqual(audit["exact_duplicate_groups"], [])
            self.assertEqual(audit["total_bytes"], 8)
            self.assertFalse(audit["hash_duplicates"])


if __name__ == "__main__":
    unittest.main()

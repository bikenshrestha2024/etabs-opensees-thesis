"""Confirm the three historical-note relocations are byte-identical Git objects.

This is a navigation/provenance test, NOT an engineering solver validation.
"""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
MOVED = {
    "00_V165_LAUNCHER_FIX.md": (
        "archive/previous_versions/HISTORICAL_NOTES/00_V165_LAUNCHER_FIX.md",
        "193b11611fd2057ad21b8b858e8a12f5fe3dcf6f",
    ),
    "EXPORT_HOTFIX_V142.md": (
        "archive/previous_versions/HISTORICAL_NOTES/EXPORT_HOTFIX_V142.md",
        "be5ea40470a054942434e6432b41821c7eff7ad0",
    ),
    "PACKAGE_CONTENTS_V141.md": (
        "archive/previous_versions/HISTORICAL_NOTES/PACKAGE_CONTENTS_V141.md",
        "d5943dd2fe781e77bedbcdb2e61f888da44ccab4",
    ),
}


class HistoricalNoteArchiveTests(unittest.TestCase):
    def test_preserved_git_blob_identity_and_root_reduction(self):
        for old_path, (new_path, expected_sha) in MOVED.items():
            with self.subTest(old_path=old_path):
                self.assertFalse((ROOT / old_path).exists())
                current = ROOT / new_path
                self.assertTrue(current.is_file())
                sha = subprocess.run(
                    ["git", "hash-object", str(current)],
                    cwd=ROOT, capture_output=True, text=True, check=True,
                ).stdout.strip()
                self.assertEqual(sha, expected_sha)


if __name__ == "__main__":
    unittest.main()

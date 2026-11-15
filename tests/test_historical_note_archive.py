"""Confirm all historical-note relocations are byte-identical Git objects.

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
    "00_V163_NONLINEAR_DIAGNOSTIC.md": (
        "archive/previous_versions/HISTORICAL_NOTES/RESEARCH_DIAGNOSTICS/00_V163_NONLINEAR_DIAGNOSTIC.md",
        "b1e40a3ddf98080f43d3a186dd424f4b6d75815d",
    ),
    "00_V164_LOAD_AND_NONLINEAR_REVIEW.md": (
        "archive/previous_versions/HISTORICAL_NOTES/RESEARCH_DIAGNOSTICS/00_V164_LOAD_AND_NONLINEAR_REVIEW.md",
        "60ef574573750b982f7516fcb8b9ca8f8448bf4a",
    ),
    "CHANGES_AND_LIMITS_V138.md": (
        "archive/previous_versions/HISTORICAL_NOTES/RELEASE_CHANGELOGS/CHANGES_AND_LIMITS_V138.md",
        "b0b115dbae34f392cd6a819f4ad741b56ce09b29",
    ),
    "MATERIAL_SETUP_V156.md": (
        "archive/previous_versions/HISTORICAL_NOTES/MATERIAL_RESEARCH/MATERIAL_SETUP_V156.md",
        "2900b16301cd959d47d1c10f0bfed75db6cc59cc",
    ),
    "VISUAL_VALIDATION_V149.md": (
        "archive/previous_versions/HISTORICAL_NOTES/MATERIAL_RESEARCH/VISUAL_VALIDATION_V149.md",
        "da1807066784aece769b06a2a4b251c0f9efc8af",
    ),
    "LITERATURE_REVIEW_AND_DECISION_V137.md": (
        "archive/previous_versions/HISTORICAL_NOTES/RESEARCH_DIAGNOSTICS/LITERATURE_REVIEW_AND_DECISION_V137.md",
        "ebe43db247ecfafa6ecf634d523377f8ea4d1beb",
    ),
    "REVIEW_V151.md": (
        "archive/previous_versions/HISTORICAL_NOTES/RESEARCH_DIAGNOSTICS/REVIEW_V151.md",
        "855376641abc6352943db336f6324f47c60c3814",
    ),
    "CHANGES_V136.md": (
        "archive/previous_versions/HISTORICAL_NOTES/RELEASE_CHANGELOGS/CHANGES_V136.md",
        "32d0d43caad07f733c893d178b5a026d5e21f9f7",
    ),
    "CAPABILITIES_AND_LIMITS_V134.md": (
        "archive/previous_versions/HISTORICAL_NOTES/RELEASE_CHANGELOGS/CAPABILITIES_AND_LIMITS_V134.md",
        "b913cfdf0e6a10c0e5d123043b6d0fe39d7cf3c6",
    ),
    "DESIGN_CHECKS_V135.md": (
        "archive/previous_versions/HISTORICAL_NOTES/RESEARCH_DIAGNOSTICS/DESIGN_CHECKS_V135.md",
        "a328c08916b5574e8ad6fc68cca7012175e9f8ba",
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

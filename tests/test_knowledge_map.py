"""Offline tests for canonical 5W1H knowledge-card navigation integrity."""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.audit_knowledge_map import audit_knowledge_cards, MANDATORY, CARD_FILE


class KnowledgeMapTests(unittest.TestCase):
    def write_fixture(self, root, rows):
        root = Path(root)
        file = root / CARD_FILE
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=MANDATORY)
            writer.writeheader()
            writer.writerows(rows)

    def row(self, **override):
        values = {
            "ID": "TEST", "Title": "Demo", "When": "Before running",
            "Why": "Reduce mistakes", "How": "Verify source and guide",
            "Where_Canonical_Source": "components/model/example.py",
            "Which_Inputs": "Verified inputs",
            "Who_Accountable_Roles": "Engineer and maintainer",
            "Acceptance_Gate": "Not physical acceptance",
            "Guide": "docs/source/example.md", "Priority": "P0",
        }
        values.update(override)
        return values

    def test_valid_source_and_guide_pass_navigation_only(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for path in ("components/model/example.py", "docs/source/example.md"):
                file = root / path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("fixture only", encoding="utf-8")
            self.write_fixture(root, [self.row()])
            result = audit_knowledge_cards(root)
            self.assertEqual(result["status"], "PASS_NAVIGATION_ONLY")
            self.assertEqual(result["cards"], 1)
            self.assertIn("not", result["limitations"].lower())

    def test_missing_guide_and_empty_owner_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.write_fixture(root, [self.row(Who_Accountable_Roles="")])
            result = audit_knowledge_cards(root)
            self.assertEqual(result["status"], "INVALID")
            self.assertTrue(any("Who_Accountable_Roles" in x for x in result["errors"]))
            self.assertTrue(any("Guide" in x for x in result["errors"]))

    def test_duplicate_ids_and_parent_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.write_fixture(root, [self.row(), self.row(Guide="../private.txt")])
            result = audit_knowledge_cards(root)
            self.assertEqual(result["status"], "INVALID")
            self.assertTrue(any("Duplicate" in x for x in result["errors"]))
            self.assertTrue(any("Unsafe" in x for x in result["errors"]))


if __name__ == "__main__":
    unittest.main()

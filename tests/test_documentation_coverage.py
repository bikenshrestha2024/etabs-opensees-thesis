"""Tests for path-only source-guide coverage reporting."""
import tempfile
import unittest
from pathlib import Path

from tools.audit_documentation_coverage import audit_guides


class DocumentationCoverageTests(unittest.TestCase):
    def test_guide_presence_is_separate_from_test_guide_gaps(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            module = root / "components" / "example.py"
            module.parent.mkdir(parents=True)
            module.write_text("pass\n", encoding="utf-8")
            guide = root / "docs" / "source" / "components" / "example.py.md"
            guide.parent.mkdir(parents=True)
            guide.write_text("Source guide (unverified content)\n", encoding="utf-8")
            tests = root / "tests" / "test_example.py"
            tests.parent.mkdir()
            tests.write_text("pass\n", encoding="utf-8")
            result = audit_guides(root)
            self.assertEqual(result["status"], "COMPONENT_GUIDE_PATHS_COMPLETE")
            self.assertEqual(result["groups"]["components"]["guides_present_nonempty"], 1)
            self.assertEqual(result["groups"]["tests"]["guides_missing_or_empty"], 1)
            self.assertIn("require human", result["limitations"])

    def test_empty_and_missing_guides_are_not_complete(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            source = root / "components" / "wall" / "model.py"
            source.parent.mkdir(parents=True)
            source.write_text("pass\n", encoding="utf-8")
            result = audit_guides(root)
            self.assertEqual(result["status"], "COMPONENT_GUIDE_PATHS_INCOMPLETE")
            self.assertEqual(result["groups"]["components"]["missing_paths"],
                             ["components/wall/model.py"])
            guide = root / "docs" / "source" / "components" / "wall" / "model.py.md"
            guide.parent.mkdir(parents=True)
            guide.write_text("", encoding="utf-8")
            self.assertEqual(audit_guides(root)["status"], "COMPONENT_GUIDE_PATHS_INCOMPLETE")


if __name__ == "__main__":
    unittest.main()

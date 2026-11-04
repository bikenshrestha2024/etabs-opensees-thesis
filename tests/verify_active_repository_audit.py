"""Run-order and static-source audits; solver-free, no model data."""
import tempfile
import unittest
from pathlib import Path
from tools.audit_active_repository import inventory, inspect_one_python, CANONICAL

class AuditTests(unittest.TestCase):
    def test_project_launchers_present(self):
        result=inventory()
        self.assertFalse(result["canonical_missing"])
        self.assertEqual(len(CANONICAL),29)
        self.assertGreater(len(result["active_python_modules"]),50)
        self.assertEqual(result["kind"],"STATIC_REPOSITORY_REVIEW_NOT_NATIVE_ENGINEERING_VALIDATION")
    def test_legacy_number_collisions_are_exposed(self):
        result=inventory()
        self.assertIn("01", result["numbered_alias_conflicts"])
        self.assertIn("17", result["numbered_alias_conflicts"])
        self.assertIn("01_WORKFLOW_START.py", result["numbered_alias_conflicts"]["01"])
    def test_syntax_error_is_evidence_not_silent_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            p=root/"broken.py"
            p.write_text("def fail(:\n    pass\n",encoding="utf8")
            record=inspect_one_python(p,root)
            self.assertEqual(record["parse_status"],"SYNTAX_ERROR")
            self.assertEqual(record["syntax_line"],1)

if __name__ == "__main__":
    unittest.main()

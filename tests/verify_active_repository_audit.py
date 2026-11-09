"""Run-order and static-source audits; solver-free, no model data."""
import tempfile
import unittest
import re
from pathlib import Path
from tools.audit_active_repository import inventory, inspect_one_python, CANONICAL

class AuditTests(unittest.TestCase):
    def test_project_launchers_present(self):
        result=inventory()
        self.assertFalse(result["canonical_missing"])
        self.assertEqual(CANONICAL[22], "22_NBC105_INPUT_SYNC.py")
        self.assertEqual(CANONICAL[37], "37_THESIS_EVIDENCE_DASHBOARD.py")
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

    def test_compiler_only_syntax_error_is_detected_without_execution(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            p=root/"broken.py"
            p.write_text("raise RuntimeError('must not execute')\nf(text='hover', text='label')\n", encoding="utf8")
            record=inspect_one_python(p,root)
            self.assertEqual(record["parse_status"], "SYNTAX_ERROR")
            self.assertEqual(record["syntax_line"], 2)

    def test_inventory_checks_root_launchers_and_runtime_facades(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"01_WORKFLOW_START.py").write_text("break\n", encoding="utf8")
            (root/"OpenSees_Runtime.py").write_text("f(x=1,x=2)\n", encoding="utf8")
            result=inventory(root)
            self.assertEqual({e["path"] for e in result["syntax_errors"]},
                             {"01_WORKFLOW_START.py", "OpenSees_Runtime.py"})
            self.assertIn("22_NBC105_INPUT_SYNC.py", result["canonical_missing"])
            self.assertIn("37_THESIS_EVIDENCE_DASHBOARD.py", result["canonical_missing"])

    def test_current_navigation_matches_canonical_tools_and_links(self):
        root=Path(__file__).resolve().parents[1]
        index=root/"docs/programs/00_PROGRAM_INDEX.md"
        content=index.read_text(encoding="utf8")
        rows=re.findall(r"^\| (\d{2}) \| \[`([^`]+)`\]", content, re.M)
        self.assertEqual(rows, [(f"{i:02d}", name) for i,name in sorted(CANONICAL.items())])
        for guide in (index, root/"00_READ_FIRST_RUN_ORDER.md",
                      root/"docs/00_REPOSITORY_ORGANIZATION.md",
                      root/"docs/review/00_CANONICAL_RUN_ORDER_AND_NAMING.md"):
            for link in re.findall(r"\]\(([^)]+)\)", guide.read_text(encoding="utf8")):
                if "://" in link or link.startswith("#"):
                    continue
                self.assertTrue((guide.parent/link.split("#")[0]).is_file(),
                                f"Broken navigation link: {guide.name}: {link}")

if __name__ == "__main__":
    unittest.main()

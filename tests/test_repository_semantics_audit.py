"""Synthetic regression for repo-wide semantic discovery, not engineering approval."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.audit_repository_semantics import audit_repository


class SemanticRepositoryInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def add(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        subprocess.run(["git", "-C", str(self.root), "add", "--", rel], check=True)

    def test_nested_import_and_missing_local_dependency_are_visible(self):
        self.add("components/__init__.py", "")
        self.add("components/ok.py", "def ok(): return 1\n")
        self.add("components/worker.py", (
            "from components.ok import ok\n"
            "def launch():\n"
            "    import components.missing\n"
            "    from components.no_such import nonexistent\n"
            "    import importlib\n"
            "    x=importlib.import_module('components.ok')\n"
            "    return ok()\n"))
        report = audit_repository(self.root)
        paths = {x["path"] for x in report["tracked_files"]}
        self.assertIn("components/worker.py", paths)
        unresolved = report["unresolved_local_dependencies"]
        self.assertTrue(any(x["imported"] == "components.missing" for x in unresolved))
        self.assertTrue(any(x["imported"] == "components.no_such" for x in unresolved))
        self.assertFalse(any(x["imported"] == "components.ok" for x in unresolved))
        edges = report["local_dependency_edges"]
        self.assertTrue(any(x["source"] == "components/worker.py" and
                            x["target"] == "components/ok.py" for x in edges))
        self.assertGreaterEqual(report["summary"]["runtime_python"], 3)
        self.assertEqual(report["status"], "BLOCKED_STATIC")

    def test_archive_not_parsed_as_live_module(self):
        self.add("components/main.py", "def run(): return 1\n")
        self.add("Saved_Project_V156/invalid.py", "def broken(:\n")
        self.add("archive/old.py", "def broken(:\n")
        report = audit_repository(self.root)
        self.assertFalse(report["active_source_errors"])
        historical = {x["path"]: x for x in report["tracked_files"]
                      if x["category"] == "HISTORICAL_SNAPSHOT"}
        self.assertIn("Saved_Project_V156/invalid.py", historical)
        self.assertIn("archive/old.py", historical)
        self.assertEqual(report["status"], "STATIC_TRIAGE_ONLY")

    def test_missing_import_not_confused_with_external_dependency(self):
        self.add("components/__init__.py", "")
        self.add("components/main.py", (
            "import os\nimport numpy as np\n"
            "from components import absent\n"
            "def run(): return np.pi\n"))
        report = audit_repository(self.root)
        self.assertFalse(any(x["imported"] == "numpy" for x in
                             report["unresolved_local_dependencies"]))
        # Missing imported symbol is ambiguous: it might be a runtime package
        # member, therefore not a definitive missing local module.
        self.assertFalse(any(x["imported"] == "components.absent" for x in
                             report["unresolved_local_dependencies"]))
        self.assertEqual(report["status"], "STATIC_TRIAGE_ONLY")

    def test_nested_namespace_package_and_package_relative_import(self):
        self.add("components/model/assembly.py", "VALUE=7\n")
        self.add("components/worker.py",
                 "from components.model import assembly\n"
                 "def run(): return assembly.VALUE\n")
        self.add("src/thesis_core/__init__.py",
                 "from .neutral_model import MODEL\n")
        self.add("src/thesis_core/neutral_model.py", "MODEL=5\n")
        report=audit_repository(self.root)
        self.assertEqual(report["status"],"STATIC_TRIAGE_ONLY")
        self.assertFalse(report["unresolved_local_dependencies"])
        targets={(x["source"],x["target"]) for x in report["local_dependency_edges"]}
        self.assertIn(("src/thesis_core/__init__.py",
                       "src/thesis_core/neutral_model.py"),targets)

    def test_unsafe_patterns_are_review_candidates_not_false_certificates(self):
        self.add("tools/runtime.py", (
            "def launch(command):\n"
            "    import subprocess\n"
            "    try:\n"
            "        return subprocess.run(command, shell=True)\n"
            "    except Exception:\n"
            "        pass\n"))
        report = audit_repository(self.root)
        codes = {x["code"] for x in report["review_candidates"]}
        self.assertIn("SHELL_TRUE_SUBPROCESS", codes)
        self.assertIn("SWALLOWED_EXCEPTION", codes)
        self.assertEqual(report["status"], "STATIC_TRIAGE_ONLY")
        self.assertIn("NOT_NATIVE_ENGINEERING_VALIDATION", report["scope"])

    def test_critical_review_queue_exposes_dependency_concentration(self):
        self.add("components/__init__.py", "")
        self.add("components/core.py", "def calculate(): return 42\n")
        self.add("components/a.py", "from components.core import calculate\n")
        self.add("components/b.py",
                 "import components.core\n"
                 "def run():\n"
                 "    try:\n"
                 "        return components.core.calculate()\n"
                 "    except Exception:\n"
                 "        pass\n")
        report=audit_repository(self.root)
        self.assertEqual(report["review_candidate_counts"]["SWALLOWED_EXCEPTION"],1)
        self.assertEqual(report["dependency_in_degree"]["components/core.py"],2)
        queue={row["path"]:row for row in report["priority_review_queue"]}
        self.assertEqual(queue["components/core.py"]["incoming_local_dependencies"],2)
        self.assertEqual(queue["components/b.py"]["advisory_count"],1)

    def test_legacy_names_and_directory_counts_are_reproducible(self):
        self.add("01_MAIN_GUI.py", "import components.core\n")
        self.add("components/__init__.py", "")
        self.add("components/core.py", "VALUE=1\n")
        self.add("tests/test_unit.py", "assert True\n")
        self.add("REVIEW_MAIN/note.md", "# reviewed\n")
        report = audit_repository(self.root)
        self.assertEqual(report["summary"]["tracked_files"], 5)
        self.assertEqual(report["summary"]["test_python"], 1)
        self.assertEqual(report["summary"]["runtime_python"], 3)
        self.assertIn("REVIEW_MAIN", report["top_level_counts"])
        self.assertFalse(report["unresolved_local_dependencies"])
        self.assertFalse(report["active_source_errors"])


if __name__ == "__main__":
    unittest.main()

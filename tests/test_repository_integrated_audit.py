"""Synthetic, solver-free regression tests for the integrated repository audit."""
import csv
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.audit_active_repository import inventory
from tools.audit_repository_integrated import (
    SCHEMA, audit, classify_file, import_graph, save,
)


class IntegratedAuditTests(unittest.TestCase):
    def test_every_tracked_file_is_classified_without_declaring_review(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(["git", "init", "-q", str(root)], check=True,
                           capture_output=True)
            files = {
                "src/thesis_core/__init__.py": "from .neutral_model import f\n",
                "src/thesis_core/neutral_model.py": "def f(): return 3\n",
                "components/gravity/solver.py": "from src.thesis_core.neutral_model import f\n",
                "README.md": "# guide\n",
                "archive/previous_versions/old.py": "broken code not runnable\n",
                "docs/overview.md": "Report\n",
                "research_model.bin": "opaque archive",
            }
            for name, source in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source, encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "-A"],
                           check=True, capture_output=True)
            result = audit(root)
            self.assertEqual(result["schema"], SCHEMA)
            self.assertEqual(result["tracked_file_count"], len(files))
            self.assertEqual(len(result["file_register"]), len(files))
            self.assertEqual(result["active_python_count"], 3)
            records = {item["path"]: item for item in result["file_register"]}
            self.assertEqual(records["archive/previous_versions/old.py"]["audit_state"],
                             "METADATA_INVENTORIED_NOT_SEMANTICALLY_REVIEWED")
            self.assertEqual(records["src/thesis_core/neutral_model.py"]["parse_status"],
                             "OK")
            self.assertEqual(result["acceptance"]["etabs_opensees_equivalence"],
                             "NOT_VERIFIED")
            self.assertNotIn("archive/previous_versions/old.py",
                             {x["path"] for x in result["active_source_parse_failures"]})
            out = root / "audit" / "integrated"
            summary, register = save(result, out)
            self.assertEqual(json.loads(summary.read_text())["tracked_file_count"],
                             len(files))
            with register.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), len(files))
            self.assertEqual(summary.relative_to(out).as_posix(),
                             "00_OVERVIEW/integrated_audit.json")
            self.assertEqual(register.relative_to(out).as_posix(),
                             "01_TRACKED_FILES/tracked_file_register.csv")
            sections = (
                "02_DEPENDENCIES/import_graph.json",
                "03_FINDINGS/consolidated_findings.json",
                "04_ACCEPTANCE/acceptance_gates.json",
                "05_OUTPUT_WRITERS/writer_summary.json",
                "06_SECURITY/secret_scan_summary.json",
            )
            for rel in sections:
                with self.subTest(section=rel):
                    data = json.loads((out/rel).read_text(encoding="utf-8"))
                    self.assertIsInstance(data,dict)
            self.assertEqual(
                json.loads((out/"04_ACCEPTANCE"/"acceptance_gates.json").read_text())
                ["acceptance"]["etabs_opensees_equivalence"], "NOT_VERIFIED")
            self.assertTrue((out/"README.md").is_file())
            self.assertFalse((root/"09_SOFTWARE_DIAGNOSTICS").exists())

    def test_local_edges_relative_imports_cycles_and_dynamic_import_review(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = root / "components" / "audit_fixture"
            pkg.mkdir(parents=True)
            (pkg / "__init__.py").write_text("from . import left\n",
                                              encoding="utf-8")
            (pkg / "left.py").write_text(
                "from .right import helper\n"
                "import importlib\n"
                "def late(x): return importlib.import_module(x)\n",
                encoding="utf-8")
            (pkg / "right.py").write_text("from components.audit_fixture.left import late\n"
                                          "def helper(): return 2\n", encoding="utf-8")
            (pkg / "missing.py").write_text(
                "import components.audit_fixture.does_not_exist\n",
                encoding="utf-8")
            entries = inventory(root)["active_python_modules"]
            report = import_graph(root, entries)
            self.assertIn(["components/audit_fixture/left.py",
                           "components/audit_fixture/right.py"],
                          report["potential_import_cycles"])
            self.assertIn(["components/audit_fixture/left.py",
                           "components/audit_fixture/right.py"],
                          report["eager_import_cycles"])
            self.assertEqual(report["unresolved_explicit_local_imports"][0]["import"],
                             "components.audit_fixture.does_not_exist")
            self.assertEqual(report["dynamic_import_review"][0]["kind"],
                             "DYNAMIC_IMPORT_REVIEW")
            edges = {(item["from"], item["to"])
                     for item in report["direct_local_edges"]}
            self.assertIn(("components/audit_fixture/left.py",
                           "components/audit_fixture/right.py"), edges)

    def test_function_scoped_mutual_import_is_not_eager_cycle(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            pkg=root/"components"/"deferred"
            pkg.mkdir(parents=True)
            (pkg/"left.py").write_text(
                "def work():\n    from components.deferred.right import solve\n"
                "    return solve()\n",encoding="utf-8")
            (pkg/"right.py").write_text(
                "def solve():\n    from components.deferred.left import work\n"
                "    return work\n",encoding="utf-8")
            graph=import_graph(root,inventory(root)["active_python_modules"])
            self.assertEqual(len(graph["potential_import_cycles"]),1)
            self.assertEqual(graph["eager_import_cycles"],[])
            self.assertEqual(graph["eager_import_edges"],0)
            self.assertEqual(graph["deferred_import_edges"],2)

    def test_missing_root_canonical_is_not_mislabeled_as_equivalence_failure(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(["git", "init", "-q", str(root)], check=True,
                           capture_output=True)
            (root/"README.md").write_text("empty fixture\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "-A"],
                           check=True, capture_output=True)
            output = audit(root)
            self.assertEqual(output["acceptance"]["static_audit"], "BLOCKED")
            self.assertEqual(output["acceptance"]["nonlinear_full_record"],
                             "NOT_VERIFIED")
            self.assertIn("P0_MISSING_CANONICAL_LAUNCHER",
                          {x["id"] for x in output["findings"]})

    def test_metadata_classifier_excludes_archived_python_from_active_set(self):
        self.assertEqual(classify_file("Saved_Project_V156/frozen.py"),
                         "ARCHIVE_OR_RESEARCH_SNAPSHOT_METADATA_ONLY")
        self.assertEqual(classify_file("src/opensees_engine/standalone.py"),
                         "ACTIVE_SOURCE_OR_TEST")
        self.assertEqual(classify_file("17_BUILDING_FULL_NONLINEAR.py"),
                         "ACTIVE_ROOT_LAUNCHER_OR_HELPER")


if __name__ == "__main__":
    unittest.main()

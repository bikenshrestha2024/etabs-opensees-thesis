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
                "archive/previous_versions/old_copy.py": "broken code not runnable\n",
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
            self.assertEqual(result["git_identity_scope"],
                             "TRACKED_INDEX_OBJECTS_NOT_DIRTY_WORKTREE")
            self.assertEqual(result["git_revision"],"UNBORN_HEAD")
            self.assertEqual(
                records["archive/previous_versions/old.py"]["git_blob_sha"],
                records["archive/previous_versions/old_copy.py"]["git_blob_sha"])
            self.assertEqual(records["archive/previous_versions/old.py"]["git_mode"],
                             "100644")
            duplicates=[x for x in result["exact_duplicate_git_blob_groups"]
                        if "archive/previous_versions/old.py" in x["paths"]]
            self.assertEqual(len(duplicates),1)
            self.assertTrue(duplicates[0]["contains_historical_snapshot"])
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
            self.assertTrue(all(len(row["git_blob_sha"])==40 for row in rows))
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
                "07_ARCHIVE_PROVENANCE/exact_blob_duplicates.json",
            )
            for rel in sections:
                with self.subTest(section=rel):
                    data = json.loads((out/rel).read_text(encoding="utf-8"))
                    self.assertIsInstance(data,dict)
            self.assertEqual(
                json.loads((out/"04_ACCEPTANCE"/"acceptance_gates.json").read_text())
                ["acceptance"]["etabs_opensees_equivalence"], "NOT_VERIFIED")
            provenance=json.loads(
                (out/"07_ARCHIVE_PROVENANCE"/"exact_blob_duplicates.json").read_text())
            self.assertTrue(any(group["contains_historical_snapshot"]
                                for group in provenance["duplicate_groups"]))
            semantic=out/"08_SEMANTIC_REVIEW"/"function_review_register.csv"
            with semantic.open(encoding="utf-8", newline="") as stream:
                units=list(csv.DictReader(stream))
            self.assertEqual(len(units),result["semantic_review_unit_count"])
            self.assertGreater(len(units),result["active_python_count"])
            self.assertTrue(all(unit["semantic_review_status"]=="NOT_REVIEWED"
                                for unit in units))
            self.assertEqual(result["semantic_review_completed_count"],0)
            self.assertTrue((out/"09_FACADE_COMPATIBILITY"/"facade_source_context.csv").is_file())
            self.assertIn("src/thesis_core/neutral_model.py",
                          {unit["path"] for unit in units})
            index = (out / "README.md").read_text(encoding="utf-8")
            artifacts = {p.relative_to(out).as_posix() for p in out.rglob("*")
                         if p.is_file() and p.name != "README.md"}
            for relative in artifacts:
                self.assertIn(f"]({relative})", index)
            self.assertFalse((root/"09_SOFTWARE_DIAGNOSTICS").exists())

    def test_exec_facade_inventory_marks_real_source_context_risk(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            target=root/"components"/"calculations.py"
            target.parent.mkdir(parents=True)
            target.write_text(
                "from pathlib import Path\n"
                "def root_for_calculation():\n"
                "    return Path(__file__).parents[2]\n",
                encoding="utf-8")
            facade=root/"OpenSees_Calculations.py"
            facade.write_text(
                "from pathlib import Path\n"
                "_component_source=Path(__file__).parent/'components/calculations.py'\n"
                "exec(compile(_component_source.read_text(),str(_component_source),'exec'),globals(),globals())\n",
                encoding="utf-8")
            from tools.audit_repository_integrated import inspect_exec_facades
            rows=inspect_exec_facades(
                root,inventory(root)["active_python_modules"],{
                    "OpenSees_Calculations.py":{"git_blob_sha":"a"*40},
                    "components/calculations.py":{"git_blob_sha":"b"*40}})
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]["implementation"],"components/calculations.py")
            self.assertTrue(rows[0]["target_present"])
            self.assertIn("CONTEXT_DEPENDENT",rows[0]["review_status"])
            self.assertIn("3",rows[0]["implementation_file_context_lines"])
            self.assertEqual(rows[0]["implementation_git_blob_sha"],"b"*40)

    def test_function_review_register_exposes_methods_nested_functions_and_risk(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            source=root/"components"/"study.py"
            source.parent.mkdir()
            source.write_text(
                "class Assembly:\n"
                "    def run(self, p):\n"
                "        def publish():\n"
                "            p.write_text('review')\n"
                "        return publish()\n",
                encoding="utf-8")
            from tools.audit_repository_integrated import inspect_semantic_review_units
            items=inspect_semantic_review_units(
                root,inventory(root)["active_python_modules"],
                {"components/study.py":{"git_blob_sha":"f"*40}})
            keys={(unit["symbol"],unit["kind"]) for unit in items}
            self.assertIn(("<module>","MODULE"),keys)
            self.assertIn(("Assembly","CLASS"),keys)
            self.assertIn(("Assembly.run","FUNCTION"),keys)
            self.assertIn(("Assembly.run.publish","FUNCTION"),keys)
            self.assertTrue(any("CALL_WRITE_TEXT" in unit["risk_signals"]
                                for unit in items))
            self.assertTrue(all(unit["git_blob_sha"]=="f"*40 for unit in items))
            self.assertTrue(all(unit["semantic_review_status"]=="NOT_REVIEWED"
                                for unit in items))

    def test_review_register_includes_defs_in_match_and_conditional_branches(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            mod=root/"components"/"nested.py"
            mod.parent.mkdir()
            mod.write_text(
                "match 1:\n"
                "    case 1:\n"
                "        def matching(): return 1\n"
                "if True:\n"
                "    def conditional(): return 2\n",
                encoding="utf-8")
            from tools.audit_repository_integrated import inspect_semantic_review_units
            items=inspect_semantic_review_units(
                root,inventory(root)["active_python_modules"],
                {"components/nested.py":{"git_blob_sha":"e"*40}})
            self.assertIn("matching",{x["symbol"] for x in items})
            self.assertIn("conditional",{x["symbol"] for x in items})

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
            # An ImportFrom(module=None) must create an actual package-init
            # dependency on its tracked child, not an ignored self-edge.
            self.assertIn(("components/audit_fixture/__init__.py",
                           "components/audit_fixture/left.py"), edges)

    def test_literal_dynamic_import_resolves_real_local_target_without_runtime_execution(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            pkg=root/"components"/"dynamic_case"
            pkg.mkdir(parents=True)
            (pkg/"target.py").write_text("VALUE=1\n",encoding="utf-8")
            (pkg/"lazy.py").write_text(
                "import importlib\n"
                "def later():\n"
                "    return importlib.import_module('components.dynamic_case.target')\n"
                "def missing():\n"
                "    return __import__('components.dynamic_case.absent')\n",
                encoding="utf-8")
            graph=import_graph(root, inventory(root)["active_python_modules"])
            edges={(x["from"],x["to"]) for x in graph["direct_local_edges"]}
            self.assertIn(("components/dynamic_case/lazy.py",
                           "components/dynamic_case/target.py"),edges)
            self.assertTrue(any(x["import"]=="components.dynamic_case.absent"
                                for x in graph["unresolved_explicit_local_imports"]))
            self.assertGreater(graph["deferred_import_edges"],0)
            self.assertTrue(any(x["kind"]=="LITERAL_DYNAMIC_IMPORT"
                                for x in graph["dynamic_import_review"]))

    def test_from_package_import_tracked_submodule_and_exported_symbol(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            pkg=root/"components"/"package_case"
            pkg.mkdir(parents=True)
            (pkg/"__init__.py").write_text(
                "EXPORTED_CONSTANT = 17\n", encoding="utf-8")
            (pkg/"submodule.py").write_text("VALUE = 3\n", encoding="utf-8")
            (pkg/"caller.py").write_text(
                "from components.package_case import submodule, EXPORTED_CONSTANT\n"
                "def use(): return submodule.VALUE + EXPORTED_CONSTANT\n",
                encoding="utf-8")
            graph=import_graph(root,inventory(root)["active_python_modules"])
            edges={(edge["from"],edge["to"])
                   for edge in graph["direct_local_edges"]}
            self.assertIn(("components/package_case/caller.py",
                           "components/package_case/submodule.py"),edges)
            self.assertEqual(graph["unresolved_explicit_local_imports"],[])

    def test_relative_from_import_exposes_real_eager_dependency_cycle(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            pkg=root/"components"/"relative_cycle"
            pkg.mkdir(parents=True)
            (pkg/"__init__.py").write_text(
                "from . import child\n",encoding="utf-8")
            (pkg/"child.py").write_text(
                "from components.relative_cycle import main\n",encoding="utf-8")
            # Referencing a package symbol called main is not necessarily an
            # actual submodule, unless a tracked module at that path exists.
            (pkg/"main.py").write_text(
                "from components.relative_cycle import child\n",encoding="utf-8")
            graph=import_graph(root,inventory(root)["active_python_modules"])
            edges={(edge["from"],edge["to"])
                   for edge in graph["direct_local_edges"]}
            self.assertIn(("components/relative_cycle/__init__.py",
                           "components/relative_cycle/child.py"),edges)
            self.assertIn(("components/relative_cycle/main.py",
                           "components/relative_cycle/child.py"),edges)
            self.assertEqual(graph["unresolved_explicit_local_imports"],[])

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

    def test_missing_facade_target_blocks_audit(self):
        from tools.audit_active_repository import CANONICAL

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(["git", "init", "-q", str(root)], check=True,
                           capture_output=True)
            for name in CANONICAL.values():
                (root / name).write_text("pass\n", encoding="utf-8")
            (root / "OpenSees_Calculations.py").write_text(
                "from pathlib import Path\n"
                "_component_source = Path(__file__).parent / 'components/missing.py'\n"
                "exec(compile(_component_source.read_text(), str(_component_source), 'exec'))\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "-C", str(root), "add", "-A"],
                           check=True, capture_output=True)

            output = audit(root)

            self.assertIn("P0_MISSING_EXEC_FACADE_TARGET",
                          {finding["id"] for finding in output["findings"]})
            self.assertEqual(output["acceptance"]["static_audit"], "BLOCKED")

    def test_metadata_classifier_excludes_archived_python_from_active_set(self):
        self.assertEqual(classify_file("Saved_Project_V156/frozen.py"),
                         "ARCHIVE_OR_RESEARCH_SNAPSHOT_METADATA_ONLY")
        self.assertEqual(classify_file("src/opensees_engine/standalone.py"),
                         "ACTIVE_SOURCE_OR_TEST")
        self.assertEqual(classify_file("17_BUILDING_FULL_NONLINEAR.py"),
                         "ACTIVE_ROOT_LAUNCHER_OR_HELPER")


if __name__ == "__main__":
    unittest.main()

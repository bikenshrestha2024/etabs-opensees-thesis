"""Run-order and static-source audits; solver-free, no model data."""
import importlib
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
import re
from pathlib import Path
from unittest.mock import patch
from tools.audit_active_repository import inventory, inspect_one_python, CANONICAL

ROOT = Path(__file__).resolve().parents[1]


class NumberedLauncherTests(unittest.TestCase):
    def test_gui_launchers_and_legacy_aliases_do_not_open_windows_on_import(self):
        names = (
            "02_INPUT_READINESS", "02_MODEL_INPUTS_AND_READINESS",
            "03_GRAVITY", "04_MODAL_ULS_SLS", "05_EQUIVALENT_STATIC",
            "06_RESPONSE_SPECTRUM", "07_LINEAR_TIME_HISTORY", "07_WALL_VALIDATION",
            "08_BUILDING_NONLINEAR_TRIAL", "09_NONLINEAR_REVIEWED_MODEL",
            "10_GRAVITY", "10_WALL_VALIDATION", "11_MODAL_ULS_SLS",
            "12_EQUIVALENT_STATIC", "13_RESPONSE_SPECTRUM", "14_LINEAR_TIME_HISTORY",
            "15_BUILDING_NONLINEAR_TRIAL", "16_NONLINEAR_REVIEWED_MODEL",
            "17_BUILDING_FULL_NONLINEAR", "18_BUILDING_FULL_NONLINEAR",
        )
        load = runpy.run_path
        facade_calls = []

        def record_facade(path, *, run_name):
            if Path(path).name.startswith("OpenSees_"):
                facade_calls.append((Path(path).name, run_name))
                return {}
            return load(path, run_name=run_name)

        for name in names:
            with self.subTest(name=name), \
                 patch.object(sys, "path", sys.path.copy()), \
                 patch("runpy.run_path", side_effect=record_facade), \
                 patch("OpenSees_Workflow_V144.launch") as readiness, \
                 patch("tkinter.Tk") as window, \
                 patch("tkinter.filedialog.askdirectory", return_value=""):
                facade_calls.clear()
                load(str(ROOT / (name + ".py")), run_name="review_import")
                self.assertEqual(facade_calls, [])
                readiness.assert_not_called()
                window.assert_not_called()

    def test_connectivity_audit_usage_names_the_invoked_launcher(self):
        for name in ("19_AUDIT_LOAD_CONNECTIONS.py", "20_AUDIT_LOAD_CONNECTIONS.py"):
            with self.subTest(name=name):
                result = subprocess.run(
                    [sys.executable, "-B", str(ROOT / name)],
                    capture_output=True, text=True, check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(f"python {name} <export folder>", result.stderr)

    def test_explicit_execution_preserves_compatibility_facade_routes(self):
        facade_launchers = {
            "07_WALL_VALIDATION": "OpenSees_Wall_Validation_V147.py",
            "03_GRAVITY": "OpenSees_Gravity_GUI_V110.py",
            "11_MODAL_ULS_SLS": "OpenSees_Modal_GUI_NBC105_V111.py",
            "12_EQUIVALENT_STATIC": "OpenSees_Earthquake_Analysis_NBC105_V111.py",
            "14_LINEAR_TIME_HISTORY": "OpenSees_Linear_Time_History_NBC105_V115.py",
            "16_NONLINEAR_REVIEWED_MODEL": "OpenSees_Nonlinear_Time_History_NBC105_V116.py",
        }
        load = runpy.run_path
        facade_calls = []

        def record_facade(path, *, run_name):
            name = Path(path).name
            if name in facade_launchers.values():
                facade_calls.append((name, run_name))
                return {}
            return load(path, run_name=run_name)

        for name, facade in facade_launchers.items():
            with self.subTest(name=name), \
                 patch.object(sys, "path", sys.path.copy()), \
                 patch("runpy.run_path", side_effect=record_facade):
                facade_calls.clear()
                load(str(ROOT / (name + ".py")), run_name="__main__")
                self.assertEqual(facade_calls, [(facade, "__main__")])

    def test_element_trace_selects_the_mapped_cell_of_a_meshed_area(self):
        trace_module = importlib.import_module("20_TRACE_FAILED_ELEMENT")
        with tempfile.TemporaryDirectory() as folder:
            model = Path(folder)
            (model / trace_module.MAP_FILE).write_text(
                json.dumps({"AREA:wall-7": [100001, 100002]}), encoding="utf-8"
            )
            (model / trace_module.DATA_FILE).write_text(json.dumps({
                "frames": [],
                "nodes": {str(i): [i, 0, 0] for i in range(1, 9)},
                "shells": [
                    {"object": "wall-7", "category": "SHEAR WALL", "nodes": [1, 2, 3, 4]},
                    {"object": "wall-7", "category": "SHEAR WALL", "nodes": [5, 6, 7, 8]},
                ],
            }), encoding="utf-8")
            result = trace_module.trace(model, 100002)
            self.assertEqual(result["matches"][0]["node_tags"], [5, 6, 7, 8])
            self.assertEqual(result["matches"][0]["node_coordinates"]["5"], [5, 0, 0])

            (model / trace_module.MAP_FILE).write_text(
                json.dumps({"AREA:wall-7": [100002]}), encoding="utf-8"
            )
            result = trace_module.trace(model, 100002)
            match = result["matches"][0]
            self.assertEqual(match["source_key"], "AREA:wall-7")
            self.assertEqual(match["metadata_status"], "MAP_AND_MODEL_SEGMENTS_DISAGREE")
            self.assertNotIn("node_tags", match)

    def test_element_trace_does_not_infer_tag_omitted_from_existing_map(self):
        trace_module = importlib.import_module("20_TRACE_FAILED_ELEMENT")
        with tempfile.TemporaryDirectory() as folder:
            model = Path(folder)
            (model / trace_module.MAP_FILE).write_text("{}", encoding="utf-8")
            (model / trace_module.DATA_FILE).write_text(json.dumps({
                "frames": [{"object": "beam-1", "category": "BEAM", "nodes": [1, 2]}],
            }), encoding="utf-8")
            result = trace_module.trace(model, 100001)
            self.assertEqual(result["mapping_method"], "element_map")
            self.assertEqual(result["matches"], [])

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

    def test_new_src_packages_are_inventoried_and_invalid_utf8_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            pkg=root/"src"/"opensees_engine"
            pkg.mkdir(parents=True)
            good=pkg/"standalone.py"
            good.write_text("def build():\n    return 42\n",encoding="utf-8")
            bad=pkg/"unreadable.py"
            bad.write_bytes(b"\xff\xfe\xf0")
            report=inventory(root)
            paths={entry["path"]:entry for entry in report["active_python_modules"]}
            self.assertIn("src/opensees_engine/standalone.py",paths)
            self.assertEqual(paths["src/opensees_engine/standalone.py"]["parse_status"],"OK")
            self.assertEqual(paths["src/opensees_engine/unreadable.py"]["parse_status"],"SOURCE_READ_ERROR")
            self.assertIn("src/opensees_engine/unreadable.py",
                          {x["path"] for x in report["syntax_errors"]})

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

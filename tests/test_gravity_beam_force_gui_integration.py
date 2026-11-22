"""Regression gates for the active Gravity GUI ETABS beam-force workflow.

The GUI is parsed, not launched: safe on headless CI without ETABS/OpenSeesPy.
Numerical integration and native solver equivalence remain separate gates.
"""
import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "components" / "gravity" / "gui_and_reports.py"


class GravityBeamForceGuiTests(unittest.TestCase):
    def test_gui_picker_and_consolidator_are_wired(self):
        code = TARGET.read_text(encoding="utf-8-sig")
        tree = ast.parse(code, filename=str(TARGET))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                   and n.name == "GravityAnalysisGUI")
        methods = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
        self.assertIn("_select_all_etabs_beam_force_workbooks", methods)
        self.assertIn("_audit_all_etabs_beam_force_workbooks", methods)
        self.assertIn("_build", methods)
        picker = ast.get_source_segment(code, methods["_select_all_etabs_beam_force_workbooks"])
        audit = ast.get_source_segment(code, methods["_audit_all_etabs_beam_force_workbooks"])
        build = ast.get_source_segment(code, methods["_build"])
        self.assertIn("askopenfilenames", picker)
        self.assertIn("register_current_etabs_tables", audit)
        self.assertIn("consolidate(", audit)
        self.assertIn("create_case_run", audit)
        self.assertIn("SOURCE_ONLY", audit)
        self.assertIn('stage/"02_RESULTS"', audit)
        self.assertIn("record_case_status", audit)
        self.assertIn("source_edb_sha256=edb_digest", audit)
        self.assertIn("registry[\"source_edb_sha256\"] != edb_digest", audit)
        self.assertIn('record_case_status(stage,"FAILED"', audit)
        self.assertIn('record_case_status(stage,"INCOMPLETE"', audit)
        self.assertIn("source_root", audit)
        self.assertIn("_select_all_etabs_beam_force_workbooks", build)
        self.assertIn("_audit_all_etabs_beam_force_workbooks", build)
        self.assertIn("reaction equivalence NOT VERIFIED", audit)


if __name__ == "__main__":
    unittest.main()

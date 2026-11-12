"""Offline safety tests for V4 primary-32 label and adopted-period GUI.

These checks inspect source without importing Tk, ETABS COM, or OpenSeesPy.
They are intentionally not substitutes for native Windows or numerical checks.
"""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8-sig")


class V4PrimaryGravityAndESMDisplayTests(unittest.TestCase):
    def test_active_gui_modules_compile(self):
        for path in ("components/gravity/gui_and_reports.py",
                     "components/equivalent_static/calculation_and_gui.py"):
            with self.subTest(path=path):
                ast.parse(read(path), filename=path)

    def test_primary_32_is_diagnostic_and_legacy_case_id_preserved(self):
        s = read("components/gravity/gui_and_reports.py")
        self.assertIn('tk.StringVar(value="32 nonzero-reaction nodes (diagnostic)")', s)
        self.assertIn('self.wall_support_strategy_var.set("32 nonzero-reaction nodes (diagnostic)")', s)
        self.assertIn('"32 nonzero-reaction nodes (diagnostic)": "ETABS_NONZERO_REACTION_DIAGNOSTIC"', s)
        self.assertIn('"ETABS Reaction Validation (32 nodes)": "ETABS_NONZERO_REACTION_DIAGNOSTIC"', s)
        self.assertIn('"ETABS Node Position (76 nodes)"', s)
        self.assertIn('"Continuous Wall Base (97 nodes)"', s)
        self.assertIn("releases 44 source restraints", s)
        self.assertIn("NOT certified", s)
        self.assertIn("def _view_saved_case(self):", s)

    def test_workbook_design_periods_not_mislabeled_eigenperiods(self):
        s = read("components/equivalent_static/calculation_and_gui.py")
        self.assertIn('text="Historical Excel adopted T1-X (s) — reference only"', s)
        self.assertIn('text="Historical Excel adopted T1-Y (s) — reference only"', s)
        self.assertIn('textvariable=self.excel_tx,state="readonly"', s)
        self.assertIn('textvariable=self.excel_ty,state="readonly"', s)
        self.assertIn("measured ETABS modal reference (separate)", s)
        self.assertIn('"Rayleigh T1-X (s)"', s)
        self.assertIn('"Rayleigh T1-Y (s)"', s)
        self.assertIn('self.excel_tx.set(str(reference[\'values\'].get(\'workbook_adopted_tx\',\'\')))', s)
        self.assertIn('self.excel_ty.set(str(reference[\'values\'].get(\'workbook_adopted_ty\',\'\')))', s)
        self.assertIn("self.adopted_tx", s)
        self.assertIn("self.adopted_ty", s)

    def test_ordered_launcher_is_primary_and_legacy_is_retained(self):
        self.assertTrue((ROOT / "01_WORKFLOW_START.py").is_file())
        self.assertTrue((ROOT / "01.py").is_file())
        self.assertTrue((ROOT / "RUN_ETABS_TO_OPENSEES.py").is_file())
        self.assertIn("01_WORKFLOW_START.py", read("00_READ_FIRST_RUN_ORDER.md"))
        self.assertIn("01_WORKFLOW_START.py", read("docs/programs/00_PROGRAM_INDEX.md"))


if __name__ == "__main__":
    unittest.main()

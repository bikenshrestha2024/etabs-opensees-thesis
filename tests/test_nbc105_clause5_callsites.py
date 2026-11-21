"""Call-site routing through components/modal/nbc105_clause5.py.

[REF NBC105-2025 §5, printed pp. 28-30] Unit tests only; no ETABS/OpenSees/tkinter.
"""
import json
import math
import re
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from components.modal import nbc105_clause5 as c5
from components.modal.analysis import nbc105_period_estimate

ROOT = Path(__file__).resolve().parents[1]
ROUTED_FILES = [
    "components/modal/analysis.py",
    "components/modal/rayleigh.py",
    "components/inputs/analysis_autofill.py",
    "components/equivalent_static/calculation_and_gui.py",
]


class EstimateMatchesModule(unittest.TestCase):
    def test_estimate_matches_clause5_module(self):
        h, aw_x, aw_y = 94.5, 18.7, 21.3
        out = nbc105_period_estimate(height_m=h, system_type="Concrete Shear-Wall",
                                     wall_aw_x_m2=aw_x, wall_aw_y_m2=aw_y,
                                     rayleigh_x_s=2.5, rayleigh_y_s=9.0)
        for axis, aw, ray in (("X", aw_x, 2.5), ("Y", aw_y, 9.0)):
            emp = c5.empirical_period_s(h, "concrete shear-wall", aw)
            self.assertEqual(out[f"empirical_{axis}_s"], emp)
            self.assertEqual(out[f"amplified_empirical_{axis}_s"], c5.amplified_period_s(emp))
            adopted = c5.adopted_period_s(emp, ray)
            self.assertEqual(out[f"adopted_design_period_{axis}_s"], adopted["adopted_s"])
        self.assertEqual(out["adopted_design_period_Y_s"], c5.amplified_period_s(out["empirical_Y_s"]))

    def test_mrf_matches_module_and_missing_wall_aw_is_incomplete(self):
        out = nbc105_period_estimate(height_m=25, system_type="steel moment-resisting frame")
        self.assertEqual(out["empirical_X_s"], c5.empirical_period_s(25, "steel moment-resisting frame"))
        self.assertIsNone(out["adopted_design_period_X_s"])
        wall = nbc105_period_estimate(height_m=25, system_type="concrete shear-wall")
        self.assertIsNone(wall["empirical_X_s"])
        self.assertIn("INCOMPLETE", wall["adopted_period_status_X"])


class AutofillDeviation(unittest.TestCase):
    def test_helper_applies_lesser_of_at_1_25(self):
        from components.inputs.analysis_autofill import workbook_adopted_period
        emp = c5.empirical_period_s(60.0, "concrete shear-wall", 12.0)
        period, note = workbook_adopted_period(60.0, 12.0, 99.0, 1.25)
        self.assertIsNone(note)
        self.assertEqual(period, c5.amplified_period_s(emp))
        period, _ = workbook_adopted_period(60.0, 12.0, 0.5, 1.25)
        self.assertEqual(period, 0.5)

    def test_autofill_reports_deviation_for_factor_1_5(self):
        from components.inputs.analysis_autofill import populate_linear, workbook_adopted_period
        period, note = workbook_adopted_period(60.0, 12.0, 0.5, 1.5)
        self.assertIsNone(period)
        self.assertIn("DEVIATION", note)

        class Field:
            def __init__(self): self.value = ""
            def get(self): return self.value
            def set(self, v): self.value = str(v)
        gui = SimpleNamespace(**{k: Field() for k in ("t1x", "t1y", "p1", "p2", "tnx", "tny")},
                              ls=SimpleNamespace(get=lambda: "ULS"))
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "OpenSees_Complete_Model_Data_V118.json").write_text(
                json.dumps({"nodes": {"1": [0, 0, 0], "2": [0, 0, 60]}, "base_z_m": 0}),
                encoding="utf-8")
            imported = {"values": {"awx": 12.0, "awy": 12.0, "rayleigh_tx": 0.5,
                                   "rayleigh_ty": 0.5, "period_factor": 1.5},
                        "notes": []}
            with patch("OpenSees_Project_Inputs_V123.import_project_inputs", return_value=imported):
                try:
                    populate_linear(gui, folder)
                except Exception:
                    pass  # later blocks need unrelated fixtures; notes are filled first
        text = " ".join(imported["notes"])
        self.assertIn("DEVIATION", text)


class NoLiteralFormulaLeft(unittest.TestCase):
    PATTERNS = [re.compile(r"\.075\s*\*\s*H\s*\*\*\s*\.?0?\.75\s*/\s*math\.sqrt"),
                re.compile(r"0?\.075\s*/\s*math\.sqrt\([^)]*\)\s*\*\s*H\s*\*\*"),
                re.compile(r"0?\.075\s*\*\s*h\s*\*\*\s*0?\.75\s*/\s*math\.sqrt"),
                re.compile(r"factor\s*\*\s*\.075\s*\*\s*H")]

    def test_no_literal_0_075_wall_formula_left_in_call_sites(self):
        for rel in ROUTED_FILES:
            text = (ROOT / rel).read_text(encoding="utf-8")
            for pat in self.PATTERNS:
                self.assertIsNone(pat.search(text), f"{rel}: {pat.pattern}")
            self.assertNotRegex(text, r"1\.25\s*\*\s*empirical")


if __name__ == "__main__":
    unittest.main()

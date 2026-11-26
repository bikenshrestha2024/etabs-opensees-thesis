"""Owner ruling 3: ETABS_COMPARISON (design-scaled) vs OPENSEES_ACTUAL drift, never mixed.

Printed 5.5.1.1 and 5.5.1.2 (p.36), 5.5.3 (p.37). Unit tests only.
"""
import csv
import tempfile
import unittest
from pathlib import Path

from components.nbc105 import clause_05_dynamic_characteristics as c5
from components.validation import response_checks


class DriftBases(unittest.TestCase):
    def test_etabs_comparison_uls_is_rmu_scaled_5_5_1_1(self):
        r = c5.etabs_comparison_drift(0.008, 4.0, "ULS", 3.5)   # 0.002 elastic ratio
        self.assertEqual(r["drift_basis"], "ETABS_COMPARISON")
        self.assertAlmostEqual(r["design_relative_deflection_m"], 0.028)
        self.assertAlmostEqual(r["ratio"], 0.007)
        self.assertAlmostEqual(r["elastic_ratio"], 0.002)
        self.assertTrue(r["pass"]); self.assertTrue(r["scaled_by_Rmu"])

    def test_etabs_comparison_uls_fails_when_scaled_exceeds_limit(self):
        # elastic 0.0075 ratio x Rmu 3.5 = 0.02625 > 0.025
        r = c5.etabs_comparison_drift(0.03, 4.0, "ULS", 3.5)
        self.assertFalse(r["pass"]); self.assertAlmostEqual(r["ratio"], 0.02625)

    def test_etabs_comparison_sls_is_elastic_5_5_1_2(self):
        r = c5.etabs_comparison_drift(0.024, 4.0, "SLS", None)
        self.assertAlmostEqual(r["ratio"], 0.006); self.assertTrue(r["pass"])   # exactly the limit
        self.assertFalse(r["scaled_by_Rmu"])
        r = c5.etabs_comparison_drift(0.0241, 4.0, "SLS", 3.5)                  # Rmu ignored at SLS
        self.assertFalse(r["pass"])

    def test_uls_requires_rmu(self):
        with self.assertRaises(ValueError):
            c5.etabs_comparison_drift(0.01, 4.0, "ULS")

    def test_opensees_actual_is_unscaled(self):
        r = c5.opensees_actual_drift(0.08, 4.0, "ULS")
        self.assertEqual(r["drift_basis"], "OPENSEES_ACTUAL")
        self.assertAlmostEqual(r["ratio"], 0.02); self.assertTrue(r["pass"])
        self.assertFalse(r["scaled_by_Rmu"])
        with self.assertRaises(TypeError):
            c5.opensees_actual_drift(0.08, 4.0, "ULS", 3.5)  # no scaling argument exists

    def test_same_inputs_give_different_separate_outputs(self):
        out = c5.separate_drift_outputs(limit_state="ULS", storey_height_m=4.0,
              elastic_relative_deflection_m=0.008, ductility_factor=3.5,
              opensees_relative_deflection_m=0.008)
        self.assertAlmostEqual(out["ETABS_COMPARISON"]["ratio"], 0.007)
        self.assertAlmostEqual(out["OPENSEES_ACTUAL"]["ratio"], 0.002)
        self.assertIsNone(out["combined_pass"]); self.assertFalse(out["mixing_allowed"])
        only = c5.separate_drift_outputs(limit_state="SLS", storey_height_m=4.0, opensees_relative_deflection_m=0.01)
        self.assertIsNone(only["ETABS_COMPARISON"])

    def test_mixing_refused(self):
        a = c5.etabs_comparison_drift(0.008, 4.0, "SLS")
        b = c5.opensees_actual_drift(0.008, 4.0, "SLS")
        with self.assertRaises(ValueError):
            c5.require_same_drift_basis(a, b)
        self.assertEqual(c5.require_same_drift_basis(a, a), "ETABS_COMPARISON")
        with self.assertRaises(ValueError):
            c5.drift_basis("DESIGN")

    def test_report_rows_carry_label(self):
        rows = response_checks.drift_check([{"design_drift_ratio": 0.01}], "ULS", "OPENSEES_ACTUAL")
        self.assertEqual(rows[0]["drift_basis"], "OPENSEES_ACTUAL")
        rows = response_checks.drift_check([{"design_drift_ratio": 0.01}], "ULS", "ETABS_COMPARISON")
        self.assertEqual(rows[0]["drift_basis"], "ETABS_COMPARISON")
        self.assertEqual(response_checks.drift_check([{"design_drift_ratio": 0.01}], "ULS")[0]["drift_basis"],
                         "UNLABELLED_LEGACY")
        with self.assertRaises(ValueError):
            response_checks.drift_check([{"design_drift_ratio": 0.01}], "ULS", "ACTUAL")

    def test_production_paths_label_their_basis(self):
        root = Path(__file__).resolve().parents[1]
        for rel, label in (("components/response_spectrum/model_analysis.py", "ETABS_COMPARISON"),
                           ("components/linear_time_history/runner_and_gui.py", "OPENSEES_ACTUAL"),
                           ("components/nonlinear_time_history/runner_and_gui.py", "OPENSEES_ACTUAL"),
                           ("components/equivalent_static/calculation_and_gui.py", "ETABS_COMPARISON"),
                           ("components/response_spectrum/reports.py", "ETABS_COMPARISON")):
            text = (root / rel).read_text(encoding="utf-8")
            self.assertIn(label, text, rel)
        text = (root / "components/validation/response_checks.py").read_text(encoding="utf-8")
        self.assertIn("'OPENSEES_ACTUAL'", text); self.assertIn("'ETABS_COMPARISON'", text)


if __name__ == "__main__":
    unittest.main()

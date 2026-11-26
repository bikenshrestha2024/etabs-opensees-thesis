"""Owner ruling 9a: clause 7.3 missing-mass correction for modes >= 33 Hz (printed p.41)."""
import math
import unittest
from components.nbc105 import clause_07_missing_mass as M


class MissingMass(unittest.TestCase):
    W = [100.0, 100.0, 100.0]
    PHI1 = [0.4, 0.75, 1.0]

    def test_cutoff_split_strict_less_than_33(self):
        inc, miss = M.split_modes_by_cutoff([0.5, 32.999, 33.0, 40.0])
        self.assertEqual((inc, miss), ([0, 1], [2, 3]))
        self.assertAlmostEqual(M.zpa_period_s(), 1 / 33)

    def test_residual_mass_percent_excludes_high_modes(self):
        # modes: 70 % at 1 Hz, 25 % at 20 Hz, 5 % at 40 Hz -> residual = 100 - 95
        self.assertAlmostEqual(M.residual_mass_percent([70, 25, 5], [1, 20, 40]), 5.0)
        self.assertAlmostEqual(M.residual_mass_percent([70, 25], [1, 20]), 5.0)
        self.assertEqual(M.residual_mass_percent([60, 40], [1, 20]), 0.0)
        with self.assertRaises(ValueError):
            M.residual_mass_percent([70, 40], [1, 20])

    def test_residual_weights_identity_hand_case(self):
        # Gamma = sum(w phi)/sum(w phi^2); sum of residual = W - effective modal weight (Eq. 7.1(2))
        res = M.residual_story_weights(self.W, [self.PHI1])
        num = 100 * (0.4 + 0.75 + 1.0)
        den = 100 * (0.16 + 0.5625 + 1.0)
        eff = num * num / den
        self.assertAlmostEqual(math.fsum(res), 300.0 - eff, places=9)
        gamma = num / den
        self.assertAlmostEqual(res[0], 100 * (1 - gamma * 0.4), places=9)
        # a complete mode set leaves nothing: three orthogonal modes of a 3-storey equal-weight system
        modes = [[1, 1, 1], [1, 0, -1], [1, -2, 1]]
        res = M.residual_story_weights(self.W, modes)
        self.assertTrue(all(abs(v) < 1e-9 for v in res))

    def test_residual_forces_and_inputs(self):
        out = M.missing_mass_correction_inputs(self.W, [self.PHI1], 0.2, modal_mass_percent=[90.0, 10.0], frequencies_hz=[1.0, 40.0])
        eff = (100 * 2.15) ** 2 / (100 * 1.7225)
        self.assertAlmostEqual(out["residual_base_shear"], 0.2 * (300 - eff), places=9)
        self.assertAlmostEqual(out["residual_weight_percent"], 100 * (300 - eff) / 300, places=9)
        self.assertAlmostEqual(out["residual_mass_percent_from_modes"], 10.0)
        self.assertAlmostEqual(out["zpa_period_s"], 1 / 33)
        with self.assertRaises(ValueError):
            M.residual_static_forces([1.0], -0.1)

    def test_combine_srss(self):
        self.assertAlmostEqual(M.combine_modal_and_residual(3.0, 4.0), 5.0)
        with self.assertRaises(ValueError):
            M.combine_modal_and_residual(float("nan"), 1.0)

    def test_gate_statuses(self):
        g = M.missing_mass_gate([1.0, 20.0], [60.0, 40.0])
        self.assertEqual(g["status"], "NOT_REQUIRED_ALL_MASS_COVERED")
        g = M.missing_mass_gate([1.0, 20.0, 40.0], [60.0, 35.0, 5.0])
        self.assertEqual(g["status"], "BLOCKED_CORRECTION_INPUTS_MISSING")
        self.assertEqual(g["exclude_from_combination"], [2])
        self.assertIn("ZPA_DESIGN_COEFFICIENT_AT_T_1_OVER_33_S", g["missing"])
        g = M.missing_mass_gate([1.0, 20.0, 40.0], [60.0, 35.0, 5.0], correction_inputs_supplied=True)
        self.assertEqual((g["status"], g["missing"]), ("CORRECTION_INPUTS_SUPPLIED", []))
        g = M.missing_mass_gate([1.0, 20.0], [60.0, 35.0])        # all modes < 33 Hz, 5 % unextracted mass: reported, not blocked
        self.assertEqual(g["status"], "NOT_REQUIRED_NO_MODE_AT_OR_ABOVE_33_HZ")
        self.assertAlmostEqual(g["residual_mass_percent"], 5.0)
        with self.assertRaises(ValueError):
            M.missing_mass_gate([1.0], [100.0], correction_inputs_supplied="yes")

    def test_production_paths_use_the_gate(self):
        import pathlib
        root = pathlib.Path(__file__).resolve().parents[1]
        for rel in ("components/modal/analysis.py", "components/response_spectrum/model_analysis.py"):
            self.assertIn("missing_mass_gate", (root / rel).read_text(encoding="utf-8"), rel)


if __name__ == "__main__":
    unittest.main()

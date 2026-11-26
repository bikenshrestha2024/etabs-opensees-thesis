"""Owner ruling 9b: 10 percent rigid-diaphragm criterion (printed 2.2.4 D, p.14)."""
import unittest
from components.nbc105.clause_02_general_principles import rigid_diaphragm_check as R, RIGID_DIAPHRAGM_TOLERANCE


class RigidDiaphragm(unittest.TestCase):
    def test_exactly_ten_percent_passes_and_above_flags(self):
        self.assertEqual(RIGID_DIAPHRAGM_TOLERANCE, 0.10)
        self.assertTrue(R([0.110, 0.05], [0.100, 0.05])["rigid_assumption_supported"])    # +10 % exactly (0.11-0.10 = 0.1 * 0.10 up to rounding)
        r = R([0.1101, 0.05], [0.100, 0.05])
        self.assertFalse(r["rigid_assumption_supported"]); self.assertEqual(r["flagged_points"], [0])
        self.assertEqual(r["status"], "FLAG_DIAPHRAGM_NOT_RIGID_MODEL_AS_FLEXIBLE")

    def test_flexible_below_rigid_is_not_an_exceedance(self):
        self.assertTrue(R([0.05], [0.10])["rigid_assumption_supported"])

    def test_uses_absolute_displacements(self):
        self.assertTrue(R([-0.105], [-0.100])["rigid_assumption_supported"])
        self.assertFalse(R([-0.120], [-0.100])["rigid_assumption_supported"])
        self.assertFalse(R([-0.120], [0.100])["rigid_assumption_supported"])

    def test_nowhere_means_every_point(self):
        r = R([0.1, 0.1, 0.1, 0.13], [0.1, 0.1, 0.1, 0.1])
        self.assertEqual(r["flagged_points"], [3])

    def test_zero_rigid_displacement(self):
        self.assertTrue(R([0.0], [0.0])["rigid_assumption_supported"])
        r = R([0.001], [0.0]); self.assertFalse(r["rigid_assumption_supported"])
        self.assertEqual(r["points"][0]["excess_over_rigid"], float("inf"))

    def test_rejections(self):
        for a, b in (([], []), ([1.0], [1.0, 2.0]), ([float("nan")], [1.0]), ([1.0], [float("inf")])):
            with self.assertRaises(ValueError):
                R(a, b)


if __name__ == "__main__":
    unittest.main()

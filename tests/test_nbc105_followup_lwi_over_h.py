"""Owner ruling 4: Lwi/H > 0.9 is a flagged limit exceedance, not a silent clamp (printed 5.1.2, p.29-30)."""
import unittest
from components.nbc105 import clause_05_dynamic_characteristics as c5


class LwiOverH(unittest.TestCase):
    def test_within_limit_and_equality(self):
        r = c5.effective_wall_area_result([(2.0, 5.0), (1.0, 9.0)], 10.0)
        self.assertEqual(r["status"], "WITHIN_LIMIT")
        self.assertAlmostEqual(r["aw_m2"], 2 * 0.45 + 1 * 1.01, places=12)
        self.assertEqual(r["exceeding_walls"], [])
        self.assertFalse(r["flags"][1]["exceeds_limit"])   # 0.9 exactly: "should not exceed"

    def test_exceedance_flagged_and_fail_closed(self):
        r = c5.effective_wall_area_result([(2.0, 5.0), (3.0, 20.0)], 10.0)   # ratio 2.0
        self.assertEqual(r["status"], "LIMIT_EXCEEDED_LWI_OVER_H_GT_0_9")
        self.assertIsNone(r["aw_m2"])
        self.assertEqual(r["exceeding_walls"], [1])
        self.assertAlmostEqual(r["aw_m2_formula_uncapped"], 0.9 + 3 * (0.2 + 4.0), places=12)
        self.assertAlmostEqual(r["aw_m2_if_ratio_limited_to_0_9"], 0.9 + 3.03, places=12)
        with self.assertRaises(c5.LwiOverHExceeded):
            c5.effective_wall_area_m2([(3.0, 9.0000001)], 10.0)

    def test_exception_is_a_valueerror_for_existing_callers(self):
        self.assertTrue(issubclass(c5.LwiOverHExceeded, ValueError))

    def test_empirical_period_inputs_are_not_clamped(self):
        # a wall at 0.95 H must not silently give the same Aw as a wall at 0.9 H
        with self.assertRaises(ValueError):
            c5.empirical_period_s(10.0, "concrete shear-wall building", c5.effective_wall_area_m2([(1.0, 9.5)], 10.0))

    def test_workbook_segments_carry_the_flag(self):
        from components.inputs import project_workbooks as pw
        aw, segs = pw._wall_aw_from_lines(10.0, {("X", 0.0, 0.3): [(0.0, 5.0)], ("Y", 0.0, 0.3): [(0.0, 9.5)]})
        by_axis = {s["axis"]: s for s in segs}
        self.assertFalse(by_axis["X"]["lwi_over_h_exceeds_limit"])
        self.assertTrue(by_axis["Y"]["lwi_over_h_exceeds_limit"])
        self.assertAlmostEqual(by_axis["Y"]["lwi_over_h"], 0.95)
        self.assertAlmostEqual(aw["X"], 0.3 * 5.0 * 0.45)


if __name__ == "__main__":
    unittest.main()

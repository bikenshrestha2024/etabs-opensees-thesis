"""Owner ruling 9c: input-driven irregularity checks 5.4.1.4, 5.4.2.3, 5.4.2.4, 5.4.2.5.

Unit tests of the printed thresholds only; not engineering acceptance of any model.
"""
import unittest

from components.nbc105 import clause_05_dynamic_characteristics as c5
from components.validation import response_checks as rc


class InPlane(unittest.TestCase):
    def test_offset_needs_overturning_demand(self):
        self.assertEqual(c5.in_plane_discontinuity_irregularity([(0.5, False)])["status"], "PASS")
        r = c5.in_plane_discontinuity_irregularity([(0.0, True), (0.5, True)])
        self.assertEqual(r["irregular_elements"], [1])
        self.assertEqual(r["status"], "IRREGULAR")

    def test_empty_and_bad_flag_rejected(self):
        with self.assertRaises(ValueError):
            c5.in_plane_discontinuity_irregularity([])
        with self.assertRaises(ValueError):
            c5.in_plane_discontinuity_irregularity([(1.0, 1)])


class Reentrant(unittest.TestCase):
    def test_strict_15_percent(self):
        self.assertEqual(c5.reentrant_corner_check(1.5, 10.0, 1.5, 10.0)["overall"], "PASS")
        r = c5.reentrant_corner_check(1.51, 10.0, 0.0, 10.0)
        self.assertEqual(r["X"]["status"], "IRREGULAR")
        self.assertEqual(r["overall"], "IRREGULAR")

    def test_missing_direction_not_evaluated(self):
        r = c5.reentrant_corner_check(1.0, 10.0)
        self.assertEqual(r["Y"]["status"], "NOT_EVALUATED")
        self.assertEqual(r["overall"], "PASS_EVALUATED_DIRECTIONS_ONLY")
        self.assertEqual(c5.reentrant_corner_check()["overall"], "NOT_EVALUATED")


class Diaphragm(unittest.TestCase):
    def test_cutout_strict_50_percent(self):
        self.assertEqual(c5.diaphragm_discontinuity_irregularity(50, 100)["cutout"]["status"], "PASS")
        self.assertEqual(c5.diaphragm_discontinuity_irregularity(50.1, 100)["cutout"]["status"], "IRREGULAR")

    def test_stiffness_both_readings(self):
        r = c5.diaphragm_discontinuity_irregularity(stiffness_this_storey=100, stiffness_adjacent_storey=160)["stiffness"]
        self.assertTrue(r["irregular"])            # 60 / 100 > 0.5
        self.assertFalse(r["irregular_vs_higher"])  # 60 / 160 < 0.5
        r = c5.diaphragm_discontinuity_irregularity(stiffness_this_storey=100, stiffness_adjacent_storey=150)["stiffness"]
        self.assertFalse(r["irregular"])            # exactly 50 percent is not exceeded

    def test_missing_inputs_listed(self):
        r = c5.diaphragm_discontinuity_irregularity()
        self.assertEqual(r["overall"], "NOT_EVALUATED")
        self.assertIn("CUTOUT_AREA", r["cutout"]["missing"])

    def test_cutout_larger_than_gross_rejected(self):
        with self.assertRaises(ValueError):
            c5.diaphragm_discontinuity_irregularity(120, 100)


class OutOfPlane(unittest.TestCase):
    def test_any_offset_flags_by_default(self):
        self.assertEqual(c5.out_of_plane_offset_irregularity([0.0, 0.0])["status"], "PASS")
        self.assertEqual(c5.out_of_plane_offset_irregularity([0.0, 0.01])["irregular_elements"], [1])

    def test_declared_tolerance(self):
        self.assertEqual(c5.out_of_plane_offset_irregularity([0.05], tolerance_m=0.05)["status"], "PASS")

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            c5.out_of_plane_offset_irregularity([])


class Wiring(unittest.TestCase):
    def _rows(self, **plan):
        out = rc.irregularity({"nodes": {}, "diaphragms": [], "base_z_m": 0.0}, plan_inputs=plan or None)
        rows = out["checks"]
        return {r["clause"]: r for r in rows if r["clause"] in ("5.4.1.4", "5.4.2.3", "5.4.2.4", "5.4.2.5")}

    def test_without_inputs_not_evaluated_with_missing_list(self):
        rows = self._rows()
        self.assertEqual(len(rows), 4)
        for r in rows.values():
            self.assertEqual(r["status"], "NOT EVALUATED")
            self.assertIn("Missing input", r["note"])

    def test_with_inputs_evaluated(self):
        rows = self._rows(in_plane_offsets=[(0.4, True)], reentrant_projection_x_m=2.0, overall_x_m=10.0,
                          reentrant_projection_y_m=1.0, overall_y_m=10.0, diaphragm_cutout_area_m2=10.0,
                          diaphragm_gross_area_m2=100.0, diaphragm_stiffness_this_storey=1.0,
                          diaphragm_stiffness_adjacent_storey=1.2, out_of_plane_offsets_m=[0.0])
        self.assertEqual(rows["5.4.1.4"]["status"], "IRREGULAR")
        self.assertEqual(rows["5.4.2.3"]["status"], "IRREGULAR")
        self.assertEqual(rows["5.4.2.5"]["status"], "PASS")

    def test_partial_inputs_never_pass(self):
        rows = self._rows(reentrant_projection_x_m=1.0, overall_x_m=10.0)
        self.assertEqual(rows["5.4.2.3"]["status"], "NOT EVALUATED")


if __name__ == "__main__":
    unittest.main()

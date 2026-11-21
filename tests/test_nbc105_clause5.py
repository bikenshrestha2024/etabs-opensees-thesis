"""Tests for components/modal/nbc105_clause5.py. [REF NBC105-2025 §5, printed pp. 28-30]"""
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'components' / 'modal'))
import nbc105_clause5 as c5  # noqa: E402


class Clause5Tests(unittest.TestCase):
    def test_kt_table(self):
        self.assertEqual(c5.KT_BY_SYSTEM["concrete moment-resisting frame"], 0.075)
        self.assertEqual(c5.KT_BY_SYSTEM["steel moment-resisting frame"], 0.085)
        self.assertEqual(c5.KT_BY_SYSTEM["steel eccentrically braced frame"], 0.075)
        self.assertEqual(c5.KT_BY_SYSTEM["other structural system"], 0.05)
        self.assertEqual(c5.SHEAR_WALL_KT_NUMERATOR, 0.075)

    def test_empirical_concrete_mrf(self):
        # H=25: 25**0.75 = 11.1803398875 (5**1.5); T = 0.075*11.1803398875 = 0.83852549
        self.assertAlmostEqual(c5.empirical_period_s(25, "Concrete Moment-Resisting Frame"),
                               0.075 * 5 ** 1.5, places=9)
        self.assertAlmostEqual(c5.empirical_period_s(25, "concrete moment-resisting frame"), 0.8385254916, places=8)
        self.assertAlmostEqual(c5.empirical_period_s(16, "steel moment-resisting frame"), 0.085 * 8.0, places=9)  # 16**0.75=8

    def test_empirical_shear_wall_uses_aw(self):
        # H=16 -> H**0.75=8; Aw=4 -> kt=0.075/2=0.0375; T=0.3
        self.assertAlmostEqual(c5.empirical_period_s(16, "concrete shear-wall building", aw_m2=4.0), 0.3, places=12)
        with self.assertRaises(ValueError):
            c5.empirical_period_s(16, "concrete shear-wall building")
        with self.assertRaises(ValueError):
            c5.empirical_period_s(16, "timber")

    def test_aw_clamps_lwi_over_h_at_0_9(self):
        # H=10. Wall A: Awi=2, Lwi=5 -> 2*(0.2+0.25)=0.9. Wall B: Awi=3, Lwi=20 (ratio 2 -> 0.9) -> 3*(0.2+0.81)=3.03
        self.assertAlmostEqual(c5.effective_wall_area_m2([(2.0, 5.0), (3.0, 20.0)], 10.0), 0.9 + 3.03, places=12)
        self.assertAlmostEqual(c5.effective_wall_area_m2([(1.0, 9.0)], 10.0), 1.0 * (0.2 + 0.81), places=12)

    def test_aw_rejects_nonpositive(self):
        for walls, h in (([(0.0, 3.0)], 10.0), ([(1.0, -3.0)], 10.0), ([(1.0, 3.0)], 0.0), ([(1.0, 3.0)], -5.0), ([], 10.0)):
            with self.assertRaises(ValueError):
                c5.effective_wall_area_m2(walls, h)

    def test_amplification_is_1_25_and_other_rejected(self):
        self.assertEqual(c5.AMPLIFICATION_FACTOR, 1.25)
        self.assertAlmostEqual(c5.amplified_period_s(0.8), 1.0, places=12)
        with self.assertRaises(ValueError):
            c5.amplified_period_s(0.8, factor=1.5)

    def test_adopted_is_lesser_of_rayleigh_and_amplified(self):
        # empirical 0.8 -> amplified 1.0
        low = c5.adopted_period_s(0.8, rayleigh_s=0.9)
        self.assertEqual(low["adopted_s"], 0.9)
        high = c5.adopted_period_s(0.8, rayleigh_s=1.4)
        self.assertAlmostEqual(high["adopted_s"], 1.0, places=12)
        self.assertTrue(high["status"].startswith("READY"))

    def test_adopted_none_without_rayleigh(self):
        out = c5.adopted_period_s(0.8)
        self.assertIsNone(out["adopted_s"])
        self.assertIsNone(out["rayleigh_s"])
        self.assertTrue(out["status"].startswith("INCOMPLETE"))
        self.assertAlmostEqual(out["amplified_s"], 1.0, places=12)

    def test_rayleigh_single_dof_equals_2pi_sqrt_m_over_k(self):
        m, k, d, g = 200.0, 5000.0, 0.02, 9.81  # W=m*g, F=k*d
        expected = 2 * math.pi * math.sqrt(m / k)  # 2*pi*0.2 = 1.2566370614
        self.assertAlmostEqual(c5.rayleigh_period_s([m * g], [d], [k * d], g=g), expected, places=10)
        self.assertAlmostEqual(expected, 1.2566370614, places=9)
        with self.assertRaises(ValueError):
            c5.rayleigh_period_s([1.0, 2.0], [0.1], [1.0])
        with self.assertRaises(ValueError):
            c5.rayleigh_period_s([1.0], [0.1], [-1.0])

    def test_seismic_weight_table_5_1_roof_zero(self):
        # 1000 + 0.6*200 + 0.3*100 + 0*500 = 1000+120+30 = 1150
        self.assertAlmostEqual(c5.seismic_weight_kN(1000, 200, 100, 500), 1150.0, places=12)
        self.assertEqual(c5.seismic_weight_kN(1000, roof_live_kN=9999), 1000.0)
        self.assertEqual(c5.LIVE_LOAD_FACTORS, {"storage": 0.60, "other": 0.30, "roof": 0.0})

    def test_building_height_basement_rules(self):
        self.assertEqual(c5.building_height_m(30.0, -3.0), 33.0)  # default includes basement
        self.assertEqual(c5.building_height_m(30.0, -3.0, basement_height_m=3.0), 33.0)  # not declared excluded
        self.assertEqual(c5.building_height_m(30.0, -3.0, basement_height_m=3.0, basement_excluded=True), 30.0)
        self.assertEqual(c5.building_height_m(30.0, 0.0, basement_excluded=True), 30.0)
        with self.assertRaises(ValueError):
            c5.building_height_m(3.0, 0.0, basement_height_m=3.0, basement_excluded=True)

    def test_period_factor_deviation_message(self):
        self.assertIsNone(c5.period_factor_deviation(1.25))
        msg = c5.period_factor_deviation(1.5)
        self.assertIn("DEVIATION", msg)
        self.assertIn("1.5", msg)
        self.assertIn("1.25", msg)


class StoreyIndexTests(unittest.TestCase):
    """[REF NBC105-2025 §5.2, printed p. 30] mid-height tributary rule."""
    E = [3.0, 6.0, 9.0]

    def test_below_first_and_on_floors(self):
        self.assertEqual(c5.storey_index_for_elevation(0.0, self.E), 0)
        self.assertEqual(c5.storey_index_for_elevation(1.5, self.E), 0)
        for i, z in enumerate(self.E):
            self.assertEqual(c5.storey_index_for_elevation(z, self.E), i)
            self.assertEqual(c5.storey_index_for_elevation(z + 5e-8, self.E), i)
            self.assertEqual(c5.storey_index_for_elevation(z - 5e-8, self.E), i)

    def test_midpoint_boundaries(self):
        # midpoint of 3 and 6 is 4.5
        self.assertEqual(c5.storey_index_for_elevation(4.4, self.E), 0)
        self.assertEqual(c5.storey_index_for_elevation(4.5 - 1e-6, self.E), 0)
        self.assertEqual(c5.storey_index_for_elevation(4.5, self.E), 1)
        self.assertEqual(c5.storey_index_for_elevation(4.6, self.E), 1)
        self.assertEqual(c5.storey_index_for_elevation(7.4, self.E), 1)
        self.assertEqual(c5.storey_index_for_elevation(7.5, self.E), 2)

    def test_above_roof(self):
        self.assertEqual(c5.storey_index_for_elevation(9.0, self.E), 2)
        self.assertEqual(c5.storey_index_for_elevation(12.0, self.E), 2)

    def test_two_floor_and_uneven(self):
        self.assertEqual(c5.storey_index_for_elevation(3.9, [3.0, 4.0]), 1)
        self.assertEqual(c5.storey_index_for_elevation(3.4, [3.0, 4.0]), 0)
        # uneven: floors 4, 7, 15 -> mids 5.5 and 11
        e = [4.0, 7.0, 15.0]
        self.assertEqual(c5.storey_index_for_elevation(5.4, e), 0)
        self.assertEqual(c5.storey_index_for_elevation(5.5, e), 1)
        self.assertEqual(c5.storey_index_for_elevation(10.9, e), 1)
        self.assertEqual(c5.storey_index_for_elevation(11.0, e), 2)
        self.assertEqual(c5.storey_index_for_elevation(1.0, [5.0]), 0)

    def test_total_weight_preserved(self):
        zs = [0.0, 1.0, 3.0, 4.4, 4.5, 5.9, 6.0, 7.49, 7.5, 8.9, 9.0, 10.0]
        w = [1.0 + 0.5 * k for k in range(len(zs))]
        buckets = [0.0] * len(self.E)
        for z, wi in zip(zs, w):
            buckets[c5.storey_index_for_elevation(z, self.E)] += wi
        self.assertAlmostEqual(sum(buckets), sum(w), places=12)
        self.assertEqual(buckets[0], sum(wi for z, wi in zip(zs, w) if z < 4.5))

    def test_nan_and_infinite_elevation_rejected(self):
        for bad in (float('nan'), float('inf'), -float('inf')):
            with self.assertRaises(ValueError):
                c5.storey_index_for_elevation(bad, self.E)

    def test_invalid_floors(self):
        for bad in ([], [3.0, 3.0], [6.0, 3.0]):
            with self.assertRaises(ValueError):
                c5.storey_index_for_elevation(1.0, bad)


if __name__ == '__main__':
    unittest.main()

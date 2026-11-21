"""Hand-computed tests for NBC 105:2025 clause 4 (printed pp. 22-27)."""
import math
import unittest

from components.nbc105 import clause_04_seismic_hazard as c4

ESM, DYN = "equivalent_static", "dynamic"


class SpectralShapeTests(unittest.TestCase):
    def test_table_4_1_transcription(self):
        # Read from the printed page 24 image.
        self.assertEqual(set(c4.TABLE_4_1), {"A", "B", "C", "D"})
        # Full table literally as printed (p. 24): Ta, Tc, Td, alpha.
        printed = {
            "A": {"Ta": 0.1, "Tc": 0.5, "Td": 4.0, "alpha": 2.5},
            "B": {"Ta": 0.1, "Tc": 0.7, "Td": 4.0, "alpha": 2.5},
            "C": {"Ta": 0.1, "Tc": 1.0, "Td": 4.0, "alpha": 2.5},
            "D": {"Ta": 0.5, "Tc": 2.0, "Td": 5.0, "alpha": 2.25},
        }
        self.assertEqual(c4.TABLE_4_1, printed)
        self.assertEqual([c4.TABLE_4_1[s]["Tc"] for s in "ABCD"],
                         [0.5, 0.7, 1.0, 2.0])
        self.assertEqual(c4.T_MAX_S, 6.0)

    def test_hand_values(self):
        # Soil C, T=2.0: 2.5*1.0/2.0 = 1.25
        self.assertAlmostEqual(c4.spectral_shape_factor(2.0, "C", method=DYN), 1.25)
        # Soil D, T=5: Td=5 so 2.25*2*5/25 = 0.9 (also 2.25*2/5 = 0.9)
        self.assertAlmostEqual(c4.spectral_shape_factor(5.0, "D", method=DYN), 0.9)
        # Soil B, T=4: 2.5*0.7/4 = 0.4375 and 2.5*0.7*4/16 = 0.4375
        self.assertAlmostEqual(c4.spectral_shape_factor(4.0, "B", method=DYN), 0.4375)
        self.assertAlmostEqual(2.5 * 0.7 * 4.0 / 16.0, 0.4375)
        # Soil D, T=6: 2.25*2*5/36 = 0.625
        self.assertAlmostEqual(c4.spectral_shape_factor(6.0, "D", method=DYN), 0.625)

    def test_ramp(self):
        # Soil D, T=0.25, Ta=0.5: 1 + (2.25-1)*0.25/0.5 = 1.625
        self.assertAlmostEqual(c4.spectral_shape_factor(0.25, "D", method=DYN), 1.625)
        # Soil A, T=0.05, Ta=0.1: 1 + 1.5*0.5 = 1.75
        self.assertAlmostEqual(c4.spectral_shape_factor(0.05, "A", method=DYN), 1.75)
        self.assertAlmostEqual(c4.spectral_shape_factor(0.0, "C", method=DYN), 1.0)

    def test_esm_ta_zero(self):
        # Ta = 0: alpha from T = 0 up to Tc.
        self.assertAlmostEqual(c4.spectral_shape_factor(0.0, "D", method=ESM), 2.25)
        self.assertAlmostEqual(c4.spectral_shape_factor(0.25, "D", method=ESM), 2.25)
        self.assertAlmostEqual(c4.spectral_shape_factor(0.0, "A", method=ESM), 2.5)
        # Beyond Tc ESM equals dynamic: soil A, T=1: 2.5*0.5/1 = 1.25
        self.assertAlmostEqual(c4.spectral_shape_factor(1.0, "A", method=ESM), 1.25)

    def test_continuity_all_soils(self):
        eps = 1e-9
        for soil, p in c4.TABLE_4_1.items():
            for t in (p["Ta"], p["Tc"], p["Td"]):
                lo = c4.spectral_shape_factor(t - eps, soil, method=DYN)
                at = c4.spectral_shape_factor(t, soil, method=DYN)
                hi = c4.spectral_shape_factor(t + eps, soil, method=DYN)
                self.assertAlmostEqual(lo, at, places=6)
                self.assertAlmostEqual(hi, at, places=6)
            # plateau value at Ta and Tc equals alpha; at Td alpha*Tc/Td
            self.assertAlmostEqual(
                c4.spectral_shape_factor(p["Ta"], soil, method=DYN), p["alpha"])
            self.assertAlmostEqual(
                c4.spectral_shape_factor(p["Td"], soil, method=DYN),
                p["alpha"] * p["Tc"] / p["Td"])

    def test_rejections(self):
        for bad in (-0.001, float("nan"), 6.0001, float("inf")):
            with self.assertRaises(ValueError):
                c4.spectral_shape_factor(bad, "C", method=DYN)
        with self.assertRaises(ValueError):
            c4.spectral_shape_factor(1.0, "E", method=DYN)
        with self.assertRaises(ValueError):
            c4.spectral_shape_factor(1.0, "C", method="static")


class SpectrumTests(unittest.TestCase):
    def test_importance(self):
        self.assertEqual(c4.importance_factor(1), 1.0)
        self.assertEqual(c4.importance_factor(2), 1.25)
        self.assertEqual(c4.importance_factor(2, disaster_shelter=True), 1.5)
        self.assertEqual(c4.importance_factor(3), 1.5)
        for bad in (0, 4, True, 2.5):
            with self.assertRaises(ValueError):
                c4.importance_factor(bad)
        with self.assertRaises(ValueError):
            c4.importance_factor(1, disaster_shelter=True)

    def test_c_and_cs(self):
        # Soil C, T=2, Z=0.35, I=1.25: 1.25*0.35*1.25 = 0.546875
        c = c4.elastic_site_spectrum(2.0, "C", 0.35, 1.25, method=DYN)
        self.assertAlmostEqual(c, 1.25 * 0.35 * 1.25)
        self.assertAlmostEqual(c, 0.546875)
        # Cs = 0.20 * 0.546875 = 0.109375
        cs = c4.serviceability_spectrum(2.0, "C", 0.35, 1.25, method=DYN)
        self.assertAlmostEqual(cs, 0.109375)

    def test_vertical(self):
        # 2/3 * 0.3 = 0.2 ; 2/3 * 0.4 = 0.266666...
        self.assertAlmostEqual(c4.vertical_spectrum_coefficient(0.3), 0.2)
        self.assertAlmostEqual(c4.vertical_spectrum_coefficient(0.4), 0.4 * 2 / 3)
        self.assertEqual(len(c4.VERTICAL_LOADING_CASES), 5)
        self.assertIn("20 m", c4.VERTICAL_LOADING_CASES[0])
        self.assertIn("5 m", c4.VERTICAL_LOADING_CASES[1])

    def test_zoning_validation(self):
        self.assertEqual(c4.validate_zoning_factor(0.4), 0.4)
        self.assertEqual(c4.validate_zoning_factor(0.25), 0.25)
        for bad in (0.0, -0.1, 0.4001, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                c4.validate_zoning_factor(bad)
        with self.assertRaises(ValueError):
            c4.elastic_site_spectrum(1.0, "C", 0.5, 1.0, method=DYN)
        with self.assertRaises(ValueError):
            c4.elastic_site_spectrum(1.0, "C", 0.3, 0.0, method=DYN)


class SoilTests(unittest.TestCase):
    def test_vs30_formula(self):
        # 30/(10/200 + 20/400) = 30/(0.05+0.05) = 300
        self.assertAlmostEqual(c4.vs30_from_layers([(10, 200), (20, 400)]), 300.0)
        for bad in ([], [(10, 200)], [(10, 0), (20, 400)], [(-10, 200), (40, 400)]):
            with self.assertRaises(ValueError):
                c4.vs30_from_layers(bad)

    def test_vs30_boundaries(self):
        cases = [(800.001, "A"), (800.0, "B"), (350.001, "B"), (350.0, "C"),
                 (150.001, "C"), (150.0, "D"), (149.999, "D")]
        for v, soil in cases:
            self.assertEqual(c4.soil_type_from_vs30(v), soil, v)
        with self.assertRaises(ValueError):
            c4.soil_type_from_vs30(float("nan"))

    def test_nspt_cu_boundaries(self):
        for n, soil in [(50.1, "B"), (50.0, "C"), (10.0, "C"), (9.9, "D")]:
            self.assertEqual(c4.soil_type_from_n_spt(n), soil, n)
        for cu, soil in [(250.1, "B"), (250.0, "C"), (25.0, "C"), (24.9, "D")]:
            self.assertEqual(c4.soil_type_from_cu(cu), soil, cu)

    def test_select_soil_type(self):
        r = c4.select_soil_type(height_m=30, vs30=300, n_spt=60)
        self.assertEqual((r["soil"], r["basis"]), ("C", "Vs30"))
        self.assertTrue(r["issues"])  # N_SPT says B, Vs,30 governs
        r = c4.select_soil_type(height_m=30, n_spt=5)
        self.assertEqual((r["soil"], r["basis"], r["issues"]), ("D", "N_SPT", []))
        r = c4.select_soil_type(height_m=40, n_spt=5)  # 40 m is not "more than 40"
        self.assertEqual(r["soil"], "D")
        # Above 40 m Vs,30 is optional for this thesis (USER_DECLARED 2026-11-21)
        # but the clause 4.1.3.1 requirement is reported, never raised.
        r = c4.select_soil_type(height_m=95, vs30=None, n_spt=20)
        self.assertEqual((r["soil"], r["basis"]), ("C", "N_SPT"))
        self.assertEqual(len(r["issues"]), 1)
        self.assertIn("VS30_REQUIRED_ABOVE_40M_NOT_SUPPLIED", r["issues"][0])
        self.assertIn("4.1.3.1", r["issues"][0])
        self.assertIn("optional for this thesis, USER_DECLARED 2026-11-21", r["issues"][0])
        self.assertEqual(c4.VS30_REQUIRED_ISSUE_CODE, "VS30_REQUIRED_ABOVE_40M_NOT_SUPPLIED")
        r = c4.select_soil_type(height_m=95)  # no basis at all: soil None plus both issues
        self.assertIsNone(r["soil"])
        self.assertEqual(r["issues"], [c4.VS30_REQUIRED_ISSUE, "neither Vs,30 nor N_SPT was provided"])
        r = c4.select_soil_type(height_m=95, vs30=300)
        self.assertEqual((r["soil"], r["basis"], r["issues"]), ("C", "Vs30", []))
        self.assertEqual(c4.select_soil_type(height_m=40, n_spt=20)["issues"], [])  # 40 m is not above 40
        self.assertIsNone(c4.select_soil_type(height_m=20)["soil"])


class KathmanduTable43Tests(unittest.TestCase):
    def test_transcription_check(self):
        # Pinned from the printed page 26 image: 21 rows (10 + 7 + 4).
        sites = c4.KATHMANDU_VALLEY_SOIL_D_SITES
        self.assertEqual(len(sites), 21)
        by_district = {}
        for district, _ in sites:
            by_district[district] = by_district.get(district, 0) + 1
        self.assertEqual(by_district, {"Kathmandu": 10, "Lalitpur": 7, "Bhaktapur": 4})
        kmc = sites[("Kathmandu", "Kathmandu Metropolitan City")]
        # 1,2,5 + 9..30 (22 wards) + 32 (printed twice) = 26 distinct wards
        self.assertEqual(len(kmc), 3 + 22 + 1)
        self.assertEqual(sorted(kmc)[:4], [1, 2, 5, 9])
        self.assertEqual(max(kmc), 32)
        self.assertFalse({3, 4, 6, 7, 8, 31} & kmc)
        lal = sites[("Lalitpur", "Lalitpur Metropolitan City")]
        self.assertEqual(sorted(lal),
                         [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 19, 20])
        self.assertEqual(sites[("Kathmandu", "Tokha Municipality")], frozenset(range(4, 12)))
        self.assertEqual(sites[("Kathmandu", "Tarakeswor Municipality")],
                         frozenset({4, 8, 9, 10, 11}))
        self.assertEqual(sites[("Lalitpur", "Mahalaxmi Municipality")],
                         frozenset({1, 2, 3, 4, 5, 7}))
        self.assertEqual(sites[("Bhaktapur", "Suryabinayak Municipality")],
                         frozenset({2, 3, 5, 6}))
        self.assertEqual(sites[("Bhaktapur", "Bhaktapur Municipality")], "ALL")
        nil = [k for k, v in sites.items() if v == frozenset()]
        self.assertEqual(len(nil), 9)

    def test_lookups(self):
        f = c4.default_soil_type_d
        self.assertTrue(f("Bhaktapur", "Madhyapur Thimi Municipality", 7))
        self.assertTrue(f("Bhaktapur", "Madhyapur Thimi Municipality"))
        self.assertTrue(f("Kathmandu", "Kirtipur Municipality", 10))
        self.assertFalse(f("Kathmandu", "Kirtipur Municipality", 9))
        self.assertFalse(f("Kathmandu", "Budhanilkantha Municipality", 3))
        self.assertFalse(f("Kathmandu", "Budhanilkantha Municipality"))
        self.assertTrue(f("kathmandu", "kathmandu metropolitan city", 32))
        self.assertFalse(f("Kathmandu", "Kathmandu Metropolitan City", 31))
        self.assertFalse(f("Pokhara", "Pokhara Metropolitan City", 1))
        with self.assertRaises(ValueError):
            f("Kathmandu", "Kirtipur Municipality")

    def test_select_soil_type_rejects_nonpositive_height(self):
        for h in (0.0, -5.0):
            with self.assertRaises(ValueError):
                c4.select_soil_type(height_m=h, vs30=300)

    def test_short_names_case_and_whitespace(self):
        f = c4.default_soil_type_d
        self.assertTrue(f("Kathmandu", "Kirtipur", 10))
        self.assertFalse(f("Kathmandu", "Kirtipur", 9))
        self.assertTrue(f("  KATHMANDU ", "  kirtipur   municipality ", 10))
        self.assertTrue(f("Bhaktapur", "Madhyapur Thimi", 3))
        self.assertTrue(f("Bhaktapur", "bhaktapur"))
        self.assertTrue(f("Lalitpur", "Lalitpur", 1))
        self.assertFalse(f("Lalitpur", "Lalitpur", 5))
        self.assertTrue(f("Kathmandu", "Kathmandu", 32))
        self.assertTrue(f("Lalitpur", "Mahalaxmi", 7))
        self.assertFalse(f("Lalitpur", "Godawari", 1))
        with self.assertRaises(ValueError):
            f("Kathmandu", "Kirtipur")

    def test_unknown_names_still_false(self):
        f = c4.default_soil_type_d
        self.assertFalse(f("Kathmandu", "Kirtipurr", 10))
        self.assertFalse(f("Kathmandu", "Thimi", 1))
        self.assertFalse(f("Kathmandu", "", 10))
        self.assertFalse(f("Kathmandu", "Madhyapur Thimi", 1))  # wrong district
        self.assertFalse(f("Bhaktapur", "Kirtipur", 10))
        self.assertFalse(f("Pokhara", "Pokhara", 1))


if __name__ == "__main__":
    unittest.main()

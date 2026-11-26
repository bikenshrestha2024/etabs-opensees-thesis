"""Owner ruling 2: printed 5.4.1.5 (p.34), consecutive storeys, exemption, strictness."""
import unittest
from components.nbc105.clause_05_dynamic_characteristics import mass_irregularity
from components.validation import response_checks


class MassIrregularity(unittest.TestCase):
    def test_hand_cases_lighter_basis_is_strict(self):
        r = mass_irregularity([100.0, 150.0, 150.0])
        self.assertEqual([x["status"] for x in r], ["PASS", "PASS"])
        r = mass_irregularity([100.0, 150.1])
        self.assertEqual(r[0]["status"], "IRREGULAR")
        self.assertAlmostEqual(r[0]["difference_over_lighter"], 0.501)

    def test_both_percentage_bases_reported(self):
        r = mass_irregularity([100.0, 200.0])[0]          # diff = 100% of lighter, 50% of heavier
        self.assertTrue(r["irregular_vs_lighter"])
        self.assertFalse(r["irregular_vs_heavier"])      # exactly 50% of heavier: not "more than"
        r2 = mass_irregularity([100.0, 200.0], reference="HEAVIER_STOREY")[0]
        self.assertEqual(r2["status"], "PASS")
        r3 = mass_irregularity([100.0, 200.1], reference="HEAVIER_STOREY")[0]
        self.assertEqual(r3["status"], "IRREGULAR")

    def test_only_consecutive_pairs_compared(self):
        # 100 -> 140 -> 190: every consecutive step <= 50% of lighter, though 190/100 = 1.9
        r = mass_irregularity([100.0, 140.0, 190.0])
        self.assertEqual([x["status"] for x in r], ["PASS", "PASS"])

    def test_declared_exemption_only(self):
        r = mass_irregularity([100.0, 100.0, 40.0])
        self.assertEqual(r[1]["status"], "IRREGULAR")        # light roof NOT exempt by default
        r = mass_irregularity([100.0, 100.0, 40.0], exempt=[2])
        self.assertEqual(r[1]["status"], "EXEMPT_DECLARED")
        self.assertEqual(r[0]["status"], "PASS")

    def test_rejections(self):
        for bad in ([100.0], [100.0, 0.0], [100.0, float("nan")]):
            with self.assertRaises(ValueError):
                mass_irregularity(bad)
        with self.assertRaises(ValueError):
            mass_irregularity([1.0, 2.0], exempt=[5])
        with self.assertRaises(ValueError):
            mass_irregularity([1.0, 2.0], reference="MEAN")

    def test_production_screen_routes_through_clause_5(self):
        data = {"base_z_m": 0.0, "nodes": {"1": [0, 0, 3.0], "2": [0, 0, 6.0], "3": [0, 0, 9.0]},
                "nodal_mass": {"1": 100.0, "2": 100.0, "3": 40.0}, "frames": [], "shells": [],
                "diaphragms": [{"master_xyz": [0, 0, 3.0 * k], "storey_number": k} for k in (1, 2, 3)]}
        chk = [c for c in response_checks.irregularity(data)["checks"] if c["clause"] == "5.4.1.5"]
        self.assertEqual([c["status"] for c in chk], ["PASS", "IRREGULAR"])
        chk = [c for c in response_checks.irregularity(data, mass_exempt_storeys=[2])["checks"] if c["clause"] == "5.4.1.5"]
        self.assertEqual([c["status"] for c in chk], ["PASS", "EXEMPT_DECLARED"])


if __name__ == "__main__":
    unittest.main()

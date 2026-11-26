"""Owner ruling 5: printed ranges of ap, mu_p, Ip in component_design_force (clause 10, pp.49-51)."""
import unittest
from components.nbc105.clause_10_parts_and_components import (
    component_design_force as F, component_amplification_factor, IP_VALUES, AP_RANGE, MU_P_RANGE)

BASE = dict(z=0.35, hp=47.5, H=95.0, Wp=100.0)


class ComponentFactorRanges(unittest.TestCase):
    def test_printed_corner_values_accepted(self):
        # Fp = 0.35 * 1.5 * (ap/mu) * Ip * 100
        self.assertAlmostEqual(F(ap=2.5, mu_p=1.5, Ip=1.5, **BASE), 0.35 * 1.5 * (2.5 / 1.5) * 1.5 * 100)
        self.assertAlmostEqual(F(ap=1.0, mu_p=2.5, Ip=1.0, **BASE), 0.35 * 1.5 * (1.0 / 2.5) * 100)

    def test_ap_outside_1_to_2_5_rejected(self):
        for ap in (0.99, 2.51, 3.0):
            with self.assertRaises(ValueError):
                F(ap=ap, mu_p=2.5, Ip=1.0, **BASE)
        self.assertEqual(AP_RANGE, (1.0, 2.5))

    def test_ap_from_table_10_1_always_in_range(self):
        for tp in (1.0, 1.1, 1.25, 1.5, 3.0):
            ap = component_amplification_factor(1.0, tp)
            F(ap=ap, mu_p=2.5, Ip=1.0, **BASE)

    def test_mu_p_range_and_research_clause(self):
        with self.assertRaises(ValueError):
            F(ap=1.0, mu_p=1.49, Ip=1.0, **BASE)
        with self.assertRaises(ValueError):
            F(ap=1.0, mu_p=3.0, Ip=1.0, **BASE)          # above 2.5 without research support
        self.assertAlmostEqual(F(ap=1.0, mu_p=3.5, Ip=1.0, research_supported_mu_p=True, **BASE),
                               0.35 * 1.5 * (1.0 / 3.5) * 100)
        with self.assertRaises(ValueError):
            F(ap=1.0, mu_p=3.51, Ip=1.0, research_supported_mu_p=True, **BASE)   # never above 3.5
        with self.assertRaises(ValueError):
            F(ap=1.0, mu_p=2.5, Ip=1.0, research_supported_mu_p="yes", **BASE)
        self.assertEqual(MU_P_RANGE, (1.5, 2.5))

    def test_ip_only_table_10_3_values(self):
        for ip in (0.9, 1.2, 2.0):
            with self.assertRaises(ValueError):
                F(ap=1.0, mu_p=2.5, Ip=ip, **BASE)
        self.assertEqual(IP_VALUES, (1.0, 1.5))

    def test_location_table_names_every_page(self):
        from pathlib import Path
        text = (Path(__file__).resolve().parents[1] / "docs/nbc105/clause_10_component_factor_locations.md").read_text(encoding="utf-8")
        for needle in ("10.3.1", "Table 10-1", "10.3.2", "Table 10-2", "10.3.3", "Table 10-3", "p. 6", "p. 7", "p. 9", "p. 50", "p. 51", "p. 49"):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()

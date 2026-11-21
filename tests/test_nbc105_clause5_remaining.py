"""NBC 105:2025 Clause 5 §§5.3–5.6, pp.31–37; exact boundary tests."""
import math
import unittest
from components.nbc105.clause_05_dynamic_characteristics import (
  table_5_2_system_factors,weak_story,soft_story,torsion_irregularity,
  interstory_drift_check,separation_gap_m,accidental_eccentricities_m,
  reentrant_corner_irregularity,uls_design_deflection)


class FullClause5(unittest.TestCase):
    def test_table_5_2_has_all_21_unique_rows(self):
        for row in range(1,22):
            entry=table_5_2_system_factors(row)
            self.assertEqual(entry["row"],row)
            self.assertGreater(entry["Rmu"],0)
        self.assertEqual(tuple(table_5_2_system_factors(9)[k] for k in
            ("Rmu","Omega_u","Omega_s")),(3.,1.3,1.15))
        self.assertEqual(tuple(table_5_2_system_factors(19)[k] for k in
            ("Rmu","Omega_u","Omega_s")),(3.5,1.4,1.2))
        with self.assertRaises(ValueError):
            table_5_2_system_factors(22)

    def test_strict_irregularity_boundaries(self):
        self.assertFalse(weak_story(80,100))
        self.assertTrue(weak_story(79.999,100))
        self.assertFalse(soft_story(70,100,[100,100,100]))
        self.assertTrue(soft_story(69.9,100,[100,100,100]))
        self.assertTrue(soft_story(79,140,[100,100,100]))
        self.assertEqual(torsion_irregularity(1.5,.999999999999), "REGULAR")
        self.assertEqual(torsion_irregularity(1.5001,1),"TORSION_IRREGULAR")
        self.assertEqual(torsion_irregularity(2.501,1),"EXTREME_TORSION_PROHIBITED")
        self.assertFalse(reentrant_corner_irregularity(1.5,10))
        self.assertTrue(reentrant_corner_irregularity(1.51,10))

    def test_drift_and_separation(self):
        self.assertTrue(interstory_drift_check(.025,1.0,"ULS")["pass"])
        self.assertFalse(interstory_drift_check(.0251,1.0,"ULS")["pass"])
        self.assertTrue(interstory_drift_check(.006,1.0,"SLS")["pass"])
        self.assertAlmostEqual(separation_gap_m(.03,.04),.05)
        self.assertEqual(accidental_eccentricities_m(20),(-1.,1.))
        self.assertAlmostEqual(uls_design_deflection(.01,3.),.03)


if __name__=="__main__":
    unittest.main()

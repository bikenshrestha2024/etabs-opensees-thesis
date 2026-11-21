"""Printed NBC 105:2025 Clause 3 seismic load-combination coefficient cases."""
import unittest
from components.nbc105.clause_03_scope_of_analysis import (
    load_combination_coefficients,vertical_seismic_combination)

class Clause3Combinations(unittest.TestCase):
    def test_parallel_uls_uses_occupancy_live_fraction_and_both_signs(self):
        rows=load_combination_coefficients(system="parallel",method="LSM",occupancy="other")
        self.assertEqual(next(r for r in rows if r["name"]=="ULS_GRAVITY")["DL"],1.2)
        self.assertEqual(next(r for r in rows if r["name"]=="ULS_E_X_POS")["Ex"],1.0)
        self.assertEqual(next(r for r in rows if r["name"]=="ULS_E_X_POS")["LL"],.3)
        self.assertEqual(next(r for r in rows if r["name"]=="ULS_STABILITY_X_NEG")["DL"],.9)
        self.assertEqual(len([r for r in rows if "ULS_E_" in r["name"]]),4)
    def test_nonparallel_has_exact_thirty_percent_orthogonal(self):
        rows=load_combination_coefficients(system="nonparallel",method="LSM",occupancy="storage")
        case=next(r for r in rows if r["name"]=="ULS_E_XPOS_YPOS")
        self.assertEqual((case["DL"],case["LL"],case["Ex"],case["Ey"]),(1.,.6,1.,.3))
        case=next(r for r in rows if r["name"]=="ULS_E_YPOS_XNEG")
        self.assertEqual((case["Ex"],case["Ey"]),(-.3,1.))
    def test_wsm_and_vertical(self):
        rows=load_combination_coefficients(system="parallel",method="WSM",occupancy="other")
        x=next(r for r in rows if r["name"]=="WSM_E_X_NEG")
        self.assertEqual((x["DL"],x["LL"],x["Ex"]),(1.,.3,-.7))
        v=vertical_seismic_combination(z=.35,occupancy="other",earthquake_sign=-1)
        self.assertAlmostEqual(v["DL"],1.1+(2./3.)*.35)
        self.assertEqual((v["LL"],v["E"]),(.3,-1.))

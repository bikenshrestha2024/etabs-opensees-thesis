"""Parity gate: NBC Clause 6 source helpers vs active ESM production."""
import unittest
from components.equivalent_static import code_basis
from components.nbc105.clause_06_equivalent_static import (
    distribution_exponent,base_shear_coefficient,base_shear,
    distribute_forces,esm_deflection_factor)


class ESMPriorityParities(unittest.TestCase):
    def test_exact_boundaries_and_invalid_period(self):
        for t in (.1,.5,.500001,1.981280885026091,2.5,4.):
            self.assertAlmostEqual(code_basis.esm_period_exponent(t),
                                   distribution_exponent(t))
        for t in (-1.,0.,float("nan"),float("inf")):
            with self.assertRaises(ValueError):
                code_basis.esm_period_exponent(t)

    def test_production_matches_reference_uls_sls(self):
        rows=[
            {"height_m":3.,"dead_load_kN":1000.,"storage_live_load_kN":0.,"other_live_load_kN":0.},
            {"height_m":6.,"dead_load_kN":2000.,"storage_live_load_kN":0.,"other_live_load_kN":0.},
        ]
        for state in ("ULS","SLS"):
            result=code_basis.calculate_esm(rows,period_s=.6,soil_type="C",
                zoning_factor_z=.35,importance_factor_i=1.,limit_state=state,
                r_mu=3.5,omega_u=1.4,omega_s=1.2,
                irregular=False,vs30_m_s=220.)
            c=result["elastic_spectrum_C_k"]
            cd=base_shear_coefficient(c if state=="ULS" else .2*c,
                ductility=3.5 if state=="ULS" else None,
                overstrength=1.4 if state=="ULS" else 1.2,
                limit_state=state)
            self.assertAlmostEqual(result["design_coefficient_Cd"],cd)
            self.assertAlmostEqual(result["base_shear_kN"],
                                   base_shear(cd,3000.))
            v=distribute_forces(result["base_shear_kN"],[1000.,2000.],
                [3.,6.],distribution_exponent(.6))
            self.assertEqual(len(result["stories"]),2)
            for index,force in enumerate(v):
                self.assertAlmostEqual(result["stories"][index]["lateral_force_kN"],force)
            self.assertAlmostEqual(result["deflection_scale_factor_kd"],
                                   esm_deflection_factor(2))

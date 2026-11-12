"""Independent pure-math regression for NBC §4.1-§6 ESM calculations.

Small synthetic two-storey building, NEVER an ETABS physical model.
[REF REVIEW_MAIN/02_ESM/20261112_RAYLEIGH_PERIOD_AND_NBC_SECTION6_FULL_AUDIT.md]
"""
import math
import unittest

from components.equivalent_static.code_basis import calculate_esm


class NBCSection6TraceTests(unittest.TestCase):
    def setUp(self):
        self.ledger=[
            dict(height_m=4.0,story_number=1,story_name="S1",master_node_tag=101,
                 dead_load_kN=1000.0, storage_live_load_kN=100.0,
                 other_live_load_kN=200.0),
            dict(height_m=8.0,story_number=2,story_name="S2",master_node_tag=102,
                 dead_load_kN=500.0, storage_live_load_kN=0.0,
                 other_live_load_kN=100.0)]
        self.kw=dict(period_s=1.98,soil_type="C",zoning_factor_z=0.35,
                     importance_factor_i=1.0,r_mu=3.0,omega_u=1.3,
                     omega_s=1.15,diagnostic_reference=True)

    def test_uls_spectral_c_cd_v_and_each_floor_force(self):
        out=calculate_esm(self.ledger,limit_state="ULS",**self.kw)
        W1=1000.0+0.6*100.0+0.3*200.0
        W2=500.0+0.3*100.0
        W=W1+W2
        Ch=2.5/1.98
        C=Ch*0.35
        Cd=C/(3.0*1.3)
        V=Cd*W
        k=1+(1.98-0.5)/2
        expected1=V*W1*4.0**k/(W1*4.0**k+W2*8.0**k)
        self.assertAlmostEqual(out['total_seismic_weight_kN'],W)
        self.assertAlmostEqual(out['spectral_shape_Ch'],Ch)
        self.assertAlmostEqual(out['elastic_spectrum_C_k'],C)
        self.assertAlmostEqual(out['design_coefficient_Cd'],Cd)
        self.assertAlmostEqual(out['base_shear_kN'],V)
        self.assertAlmostEqual(out['period_exponent_k'],k)
        self.assertAlmostEqual(out['stories'][0]['lateral_force_kN'],expected1)
        self.assertAlmostEqual(out['total_floor_force_kN'],V)

    def test_sls_has_0_2_elastic_and_omega_s_only(self):
        out=calculate_esm(self.ledger,limit_state="SLS",**self.kw)
        C=2.5/1.98*0.35
        self.assertAlmostEqual(out['design_coefficient_Cd'],0.2*C/1.15)
        self.assertAlmostEqual(out['base_shear_kN'],
                               out['design_coefficient_Cd']*out['total_seismic_weight_kN'])


if __name__ == "__main__":
    unittest.main()

"""Source-grounded NBC 105 numerical boundary and production routing regressions.

§5.1.1/§5.2/§5.4/§5.5 use exact positive/strict comparisons.
§7.4 permits an established CQC modal combination; the correlation formula
below is the existing solver's established CQC method, not an NBC tabulated
numeric coefficient.
"""
import inspect
import math
import unittest

from components.nbc105 import clause_05_dynamic_characteristics as c5
from components.nbc105 import clause_07_modal_response_spectrum as c7


class StrictClause5Boundaries(unittest.TestCase):
    def test_exactly_at_threshold_passes_but_first_representable_exceedance_fails(self):
        exact=.025
        exceed=math.nextafter(exact,math.inf)
        self.assertTrue(c5.interstory_drift_check(exact,1.,'ULS')['pass'])
        self.assertFalse(c5.interstory_drift_check(exceed,1.,'ULS')['pass'])
        self.assertTrue(c5.interstory_drift_check(.006,1.,'SLS')['pass'])
        self.assertFalse(c5.interstory_drift_check(
            math.nextafter(.006,math.inf),1.,'SLS')['pass'])

    def test_weak_soft_torsion_exact_boundaries(self):
        self.assertFalse(c5.weak_story(80.,100.))
        self.assertTrue(c5.weak_story(math.nextafter(80.,-math.inf),100.))
        self.assertFalse(c5.soft_story(70.,100.))
        self.assertTrue(c5.soft_story(math.nextafter(70.,-math.inf),100.))
        self.assertEqual(c5.torsion_irregularity(1.5,1.),'REGULAR')
        self.assertEqual(c5.torsion_irregularity(
            math.nextafter(1.5,math.inf),1.),'TORSION_IRREGULAR')
        self.assertEqual(c5.torsion_irregularity(
            math.nextafter(2.5,math.inf),1.),'EXTREME_TORSION_PROHIBITED')

    def test_seismic_weight_rejects_nan_negative_and_infinity(self):
        for bad in (float('nan'),float('inf'),-100.):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                c5.seismic_weight_kN(dead_kN=500.,other_live_kN=bad)
        self.assertAlmostEqual(c5.seismic_weight_kN(500.,100.,200.,1000.),620.)

    def test_rayleigh_rejects_nonfinite_and_negative_weight(self):
        for weights,displacements,forces in [
            ([100.,-20.],[.1,.2],[1.,2.]),
            ([100.,float('nan')],[.1,.2],[1.,2.]),
            ([100.,100.],[.1,float('inf')],[1.,2.]),
            ([100.,100.],[.1,.2],[1.,float('nan')]),
        ]:
            with self.assertRaises(ValueError):
                c5.rayleigh_period_s(weights,displacements,forces)
        result=c5.rayleigh_period_s([100.],[.1],[10.])
        self.assertAlmostEqual(result,2*math.pi*math.sqrt(1./9.81),places=12)


class CanonicalCQC(unittest.TestCase):
    def test_numeric_kernel_symmetry_and_modal_correlations(self):
        rho=c7.cqc_correlation_matrix([1.,2.],.05)
        self.assertEqual(len(rho),2)
        self.assertAlmostEqual(rho[0][0],1.)
        self.assertAlmostEqual(rho[1][1],1.)
        expected=8*.05**2*(1+2)*2**1.5/(
            (1-2**2)**2+4*.05**2*2*(1+2)**2)
        self.assertAlmostEqual(rho[0][1],expected,places=13)
        self.assertAlmostEqual(rho[1][0],expected,places=13)
        self.assertEqual(c7.cqc_correlation_matrix([1.,1.])[0][1],1.)

    def test_invalid_omega_damping_fails_closed(self):
        for values,zeta in [([], .05),([0,1.],.05),([1.,-1.],.05),
                            ([1.,float('nan')],.05),([1.,2.],0),
                            ([1.,2.],float('nan'))]:
            with self.subTest(values=values,zeta=zeta),self.assertRaises(ValueError):
                c7.cqc_correlation_matrix(values,zeta)

    def test_active_mrsm_uses_same_correlation_implementation(self):
        import numpy as np
        from components.response_spectrum import model_analysis as active
        self.assertIn('cqc_correlation_matrix',inspect.getsource(active.cqc_matrix))
        for omega in ([1.],[1.,2.,3.],[1.,1.00001,2.4]):
            expected=np.asarray(c7.cqc_correlation_matrix(omega,.05))
            actual=active.cqc_matrix(omega,.05)
            np.testing.assert_allclose(actual,expected,rtol=1e-13,atol=1e-14)
            np.testing.assert_allclose(actual,actual.T,rtol=1e-13,atol=1e-14)

if __name__=="__main__":
    unittest.main()

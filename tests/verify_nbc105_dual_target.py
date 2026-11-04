"""Exact NBC 105:2025 soil C/D dual-system regression, no recorded-motion claims."""
import tempfile
import unittest
from pathlib import Path
from components.response_spectrum.nbc105_dual_target import (
    ch_modal_nltha,target_nltha_g,write_target_spectra,verify_target_csv,
    RC_DUAL_SHEAR_WALL)

class Targets(unittest.TestCase):
 def test_code_dual(self):
    self.assertEqual(RC_DUAL_SHEAR_WALL["R_mu_ULS"],3.5)
    self.assertEqual(RC_DUAL_SHEAR_WALL["omega_u_ULS"],1.4)
 def test_piecewise_soil_c(self):
    for T,y in [(0.,1.),(.1,2.5),(1.,2.5),(2.,1.25),(4.,.625),(6.,2.5*1*4/36)]:
        self.assertAlmostEqual(ch_modal_nltha(T,"C"),y)
 def test_piecewise_soil_d(self):
    for T,y in [(0.,1.),(.5,2.25),(2.,2.25),(4.,1.125),(5.,.9),(6.,2.25*2*5/36)]:
        self.assertAlmostEqual(ch_modal_nltha(T,"D"),y)
 def test_c_d_different_target(self):
    self.assertNotEqual(target_nltha_g(3,"C",zoning_Z=.35,importance_I=1),
                        target_nltha_g(3,"D",zoning_Z=.35,importance_I=1))
    self.assertAlmostEqual(target_nltha_g(1.5,"C",zoning_Z=.35,importance_I=1),2.5/1.5*.25)
    self.assertAlmostEqual(target_nltha_g(1.5,"D",zoning_Z=.35,importance_I=1),2.25*.25)
 def test_no_unreviewed_extrapolation(self):
    with self.assertRaises(ValueError):ch_modal_nltha(6.5,"D")
    with self.assertRaises(ValueError):ch_modal_nltha(1.,"B")
 def test_separate_csv_roundtrip(self):
    with tempfile.TemporaryDirectory() as root:
        data=write_target_spectra(root,zoning_Z=.35,importance_I=1,step_s=.05)
        self.assertEqual(len(data["target_files"]),2)
        for soil in ("C","D"):
            checked=verify_target_csv(data["target_files"][soil],soil,
                                      zoning_Z=.35,importance_I=1)
            self.assertEqual(checked["mismatch_count"],0)
            self.assertFalse(checked["matched_accelerogram_spectra_verified"])
        wrong=verify_target_csv(data["target_files"]["D"],"C",
                                 zoning_Z=.35,importance_I=1)
        self.assertGreater(wrong["mismatch_count"],0)

if __name__=="__main__":unittest.main()

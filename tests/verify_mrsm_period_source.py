"""MRSM adopted period uses source-matched Rayleigh and directional wall Aw."""
import json
import tempfile
import unittest
from pathlib import Path
from components.response_spectrum.model_analysis import mrsm_period_defaults


class PeriodDefaults(unittest.TestCase):
    def test_missing_verified_period_stays_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            values,why=mrsm_period_defaults(directory,
                {"awx":3.6779,"awy":0.8019,"workbook_adopted_tx":1.5,
                 "workbook_adopted_ty":3.5})
            self.assertEqual(values,{"T1_X":"","T1_Y":""})
            self.assertIn("rayleigh_tx",why)

    def test_uses_code_lesser_rayleigh_and_amplified_empirical(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"OpenSees_Complete_Model_Data_V118.json").write_text(json.dumps(
                {"base_z_m":0,"diaphragms":[{"master_xyz":[0,0,90]}]}))
            values,_=mrsm_period_defaults(root,
                {"awx":4.0,"awy":1.0,"rayleigh_tx":2.0,"rayleigh_ty":5.0,
                 "workbook_adopted_tx":100.,"workbook_adopted_ty":100.})
            empirical_x=0.075*90**0.75/(4.0**0.5)
            empirical_y=0.075*90**0.75
            self.assertAlmostEqual(values["T1_X"],min(2.,1.25*empirical_x))
            self.assertAlmostEqual(values["T1_Y"],min(5.,1.25*empirical_y))
            self.assertNotEqual(values["T1_X"],100.)

    def test_missing_model_geometry_never_imports_unverified_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            values,why=mrsm_period_defaults(directory,
                {"awx":4,"awy":1,"rayleigh_tx":2,"rayleigh_ty":5})
            self.assertEqual(values["T1_X"],"")
            self.assertIn("Missing assembled",why)


if __name__=="__main__":
    unittest.main(verbosity=2)

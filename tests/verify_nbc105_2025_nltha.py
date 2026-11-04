"""NBC105:2025 numerical screening; NOT a spectral matching or building design test."""
import unittest
from components.nonlinear_time_history.nbc105_2025_audit import (
 nbc105_time_step_limit,paired_ground_motion_scale,scaling_period_range,
 response_aggregation_rule,validate_nbc105_design_metadata,SCALING_TARGET)

def evidence():
    return dict(t1_x_s=3.6,t1_y_s=3.2,tn90_x_s=.15,tn90_y_s=.12,
     r_mu=4.0,omega_u=1.5,factor_x=1.8,factor_y=1.5,
     target_spectrum_kind=SCALING_TARGET,spectrum_match_evidence_sha256="a"*64,
     ground_motion_selection_reviewed=True)
def run(e=None,dt=.005,scale=1.5,orientations=None):
    return validate_nbc105_design_metadata(
        evidence() if e is None else e,record_dt_s=.01,
        integration_dt_s=dt,selected_scale=scale,
        orientations=["XY","YX"] if orientations is None else orientations)

class NBC105Tests(unittest.TestCase):
 def test_lower_pair_factor(self):
    self.assertEqual(paired_ground_motion_scale(2.4,1.2),1.2)
    with self.assertRaisesRegex(ValueError,"0.33"):paired_ground_motion_scale(.32,1.5)
    with self.assertRaisesRegex(ValueError,"0.33"):paired_ground_motion_scale(1.0,3.001)
 def test_time_step_all_bounds(self):
    self.assertAlmostEqual(nbc105_time_step_limit(record_dt_s=.02,
         t1_x_s=.5,t1_y_s=1.,tn90_x_s=.1,tn90_y_s=.2),.005)
    with self.assertRaisesRegex(ValueError,"Tn90"):nbc105_time_step_limit(
       record_dt_s=.01,t1_x_s=1.,t1_y_s=1.,tn90_x_s=1.2,tn90_y_s=.1)
 def test_draft_metadata_only(self):
    r=run()
    self.assertEqual(r["status"],"METADATA_SCREEN_ONLY_NOT_NBC_DESIGN_APPROVAL")
    self.assertFalse(r["independent_spectrum_reproduced"])
    self.assertAlmostEqual(r["matching_period_windows_s"]["x"][1],7.2)
 def test_wrong_scale_blocks(self):
    with self.assertRaisesRegex(ValueError,"lower"):run(scale=1.8)
 def test_exceed_dt_blocks(self):
    e=evidence();e["t1_x_s"]=.1;e["tn90_x_s"]=.03
    with self.assertRaisesRegex(ValueError,"exceeds"):run(e,dt=.005)
 def test_must_swap_xy(self):
    with self.assertRaisesRegex(ValueError,"XY"):run(orientations=["XY"])
 def test_spectrum_evidence_required(self):
    e=evidence();e["spectrum_match_evidence_sha256"]=""
    with self.assertRaisesRegex(ValueError,"SHA256"):run(e)
 def test_seven_is_explicit_code_gap(self):
    self.assertEqual(response_aggregation_rule(6),"MAXIMUM")
    self.assertEqual(response_aggregation_rule(8),"AVERAGE")
    self.assertIn("REVIEW_REQUIRED",response_aggregation_rule(7))
    with self.assertRaises(ValueError):response_aggregation_rule(2)
 def test_matching_window(self):
    self.assertEqual(scaling_period_range(.25,3,4),[.25,6.])

if __name__=="__main__":unittest.main()

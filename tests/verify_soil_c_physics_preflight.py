"""No external solver; check strict user target, modal and pair factors."""
import unittest
from components.nonlinear_time_history.soil_c_physics_preflight import (
    audit_soil_c_analysis_config, assess_modal_damping_and_time_step,
    evaluate_original_seismomatch_logs)

def cfg():
    return dict(soil_type="C",soil_c_primary_nltha=True,
        source_records_already_scaled=True,scale=1.0,
        diagnostic_excitation="XY",orientations=["XY","YX"],
        limit_state="ULS",analysis_intent="RESEARCH_DIAGNOSTIC",
        dt_s=.005,damping_reference_modes=[1,4])

class Tests(unittest.TestCase):
    def test_immutable_soil_c_input(self):
        self.assertEqual(audit_soil_c_analysis_config(cfg())["applied_path_acceleration_factor"],9.80665)
        d=cfg();d["scale"]=1.4
        with self.assertRaisesRegex(ValueError,"scale"):audit_soil_c_analysis_config(d)
        d=cfg();d["soil_type"]="D"
        with self.assertRaisesRegex(ValueError,"Soil C"):audit_soil_c_analysis_config(d)
    def test_sls_requires_its_input_basis_for_thesis(self):
        d=cfg();d.update(limit_state="SLS",analysis_intent="THESIS_NLTHA")
        with self.assertRaisesRegex(ValueError,"SLS"):audit_soil_c_analysis_config(d)
    def test_modal_dt_and_period_coverage(self):
        d=cfg();d["nbc105_2025_design_evidence"]=dict(
            t1_x_s=3.622,t1_y_s=3.0,tn90_x_s=.15,tn90_y_s=.15)
        r=assess_modal_damping_and_time_step(d,[3.622,2.,1.,.2],.01)
        self.assertFalse(r["previous_005_to_6_window_covers_both_axes"])
        self.assertTrue(r["dt_within_code_bound"])
        d["analysis_intent"]="THESIS_NLTHA"
        with self.assertRaisesRegex(ValueError,"fitting"):assess_modal_damping_and_time_step(d,[3.622,2.,1.,.2],.01)
        d["damping_reference_modes"]=[1,1]
        with self.assertRaisesRegex(ValueError,"distinct"):assess_modal_damping_and_time_step(d,[3.622,2.,1.,.2],.01)
    def test_original_matching_log_validation(self):
        p=dict(scale_log_sha256="a"*64,engineering_reviewer="Review engineer",
               factor_A=1.8,factor_B=1.4,adopted_common_pair_factor=1.4,
               matching_log_reviewed=True)
        self.assertEqual(evaluate_original_seismomatch_logs(p)["applied_extra_opensees_spectral_scale"],1.)
        p["adopted_common_pair_factor"]=1.8
        with self.assertRaisesRegex(ValueError,"min"):evaluate_original_seismomatch_logs(p)
        p["adopted_common_pair_factor"]=1.4;p["factor_A"]=3.1
        with self.assertRaisesRegex(ValueError,"0.33"):evaluate_original_seismomatch_logs(p)

if __name__=="__main__":unittest.main()

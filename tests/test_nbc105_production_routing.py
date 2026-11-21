"""NBC 105 2025: production numerical ownership and parity regression.

The source-level checks prevent a future copy-paste reintroduction of inline
NBC equations after their callsites have been migrated to clause modules.
"""
from __future__ import annotations
import inspect
import math
import unittest

from components.equivalent_static import code_basis
from components.nbc105.clause_03_scope_of_analysis import esm_applicability, cracked_flexural_factor
from components.nbc105.clause_05_dynamic_characteristics import interstory_drift_check
from components.nbc105.clause_07_modal_response_spectrum import (
    force_scale_factor, modal_design_coefficient
)
from components.nbc105.clause_08_elastic_time_history import record_response_aggregate
from components.nbc105.clause_09_nonlinear_analysis import (
    history_time_step_limit_s, target_spectrum_period_range, pair_scale_factor
)
from components.nonlinear_time_history import nbc105_2025_audit
from components.validation import response_checks


class CanonicalCallsiteParity(unittest.TestCase):
    def test_equivalent_static_delegates_method_eligibility_to_clause_3(self):
        self.assertIn("esm_applicability", inspect.getsource(code_basis.esm_eligibility))
        for h,t,irregular,limit in ((15,1,True,"ULS"),(40,1,False,"ULS"),
                                    (95,2,True,"ULS"),(95,2,True,"SLS"),
                                    (20,.49,True,"ULS")):
            actual=code_basis.esm_eligibility(h,t,limit,irregular)
            expected=esm_applicability(height_m=h,period_s=t,irregular=irregular,
                                      limit_state=limit)
            self.assertEqual(actual[0],expected["permitted"])

    def test_cracked_stiffness_delegates_to_clause_3(self):
        self.assertIn("cracked_flexural_factor", inspect.getsource(code_basis.flexural_stiffness_modifier))
        for stage,state in (("ultimate","ULS"),("serviceability","SLS")):
            self.assertEqual(code_basis.flexural_stiffness_modifier("beam",stage),
                             cracked_flexural_factor("beam",state))

    def test_mrsm_coefficient_and_force_only_scale(self):
        from components.response_spectrum import model_analysis
        self.assertIn("modal_design_coefficient",inspect.getsource(model_analysis.design_cd))
        cfg={"soil":"C","Z":.35,"I":1,"rmu":3.5,"omegau":1.4,
             "omegas":1.2,"limit_state":"ULS"}
        coeff=model_analysis.design_cd(1.2,cfg)
        self.assertTrue(math.isfinite(coeff) and coeff>0)
        self.assertAlmostEqual(force_scale_factor(100,50),2)
        self.assertEqual(force_scale_factor(50,100),1)
        self.assertAlmostEqual(modal_design_coefficient(.6,ductility=3,
                                     overstrength=1.5,limit_state="ULS"),.6/4.5)
        self.assertIn("force_scale_factor",inspect.getsource(model_analysis.run_model_spectrum))

    def test_nltha_reference_rules_delegate_to_clause_9(self):
        self.assertIn("history_time_step_limit_s",
                      inspect.getsource(nbc105_2025_audit.nbc105_time_step_limit))
        self.assertIn("target_spectrum_period_range",
                      inspect.getsource(nbc105_2025_audit.scaling_period_range))
        self.assertIn("pair_scale_factor",
                      inspect.getsource(nbc105_2025_audit.paired_ground_motion_scale))
        self.assertAlmostEqual(nbc105_2025_audit.nbc105_time_step_limit(
            record_dt_s=.025,t1_x_s=1,t1_y_s=.8,tn90_x_s=.03,tn90_y_s=.02),.008)
        self.assertEqual(nbc105_2025_audit.paired_ground_motion_scale(.5,.7),.5)
        self.assertEqual(pair_scale_factor(.5,.7),.5)
        self.assertEqual(nbc105_2025_audit.scaling_period_range(.5,2,4),[.5,4])

    def test_elastic_history_uses_clause_8_aggregation(self):
        from components.linear_time_history import runner_and_gui
        self.assertIn("record_response_aggregate",
                      inspect.getsource(runner_and_gui._run_analysis))
        self.assertEqual(record_response_aggregate([2,5,3]),5)
        self.assertAlmostEqual(record_response_aggregate([1,2,3,4,5,6,7,8]),4.5)

    def test_drift_reporting_uses_clause_5(self):
        self.assertIn("interstory_drift_check",
                      inspect.getsource(response_checks.drift_check))
        self.assertEqual(response_checks.drift_check(
            [{"design_drift_ratio":.025}],"ULS")[0]["status"],"PASS")
        self.assertEqual(response_checks.drift_check(
            [{"design_drift_ratio":.0251}],"ULS")[0]["status"],"EXCEEDS")
        self.assertTrue(interstory_drift_check(.006,1.,"SLS")["pass"])


if __name__ == "__main__":
    unittest.main()

"""Independent numerical and fail-closed NBC 105:2025 clause tests.

All source page numbers below are PRINTED (PDF pages +23 for clauses 2-10).
"""
import math
import unittest
from components.nbc105.clause_02_general_principles import verification_check
from components.nbc105.clause_03_scope_of_analysis import (
    esm_applicability, cracked_flexural_factor, bearing_pressure_limit)
from components.nbc105.clause_06_equivalent_static import (
    base_shear_coefficient, base_shear, distribution_exponent,
    distribute_forces, esm_deflection_factor)
from components.nbc105.clause_07_modal_response_spectrum import (
    modal_effective_weight, modal_story_forces, force_only_scale,
    modal_mass_coverage, srss)
from components.nbc105.clause_08_elastic_time_history import (
    elastic_model_prerequisites, record_response_aggregate)
from components.nbc105.clause_09_nonlinear_analysis import (
    history_time_step_limit_s, required_component_runs,
    motion_scale_factor, nonlinear_model_prerequisites)
from components.nbc105.clause_10_parts_and_components import (
    component_amplification_factor, component_design_force,
    component_ductility_factor, component_importance_factor,
    component_scope, friction_design_resistance)


class Clause02(unittest.TestCase):
    def test_both_limit_states_and_stability_required(self):
        s=verification_check(uls=True,sls=True,overturning=True,sliding=True,
                             foundation=True,evacuation_components=True)
        self.assertEqual(s["status"],"PASS_INPUT_DECLARATIONS_ONLY")
        self.assertEqual(verification_check(uls=True,sls=False,overturning=True,
            sliding=True,foundation=True,evacuation_components=True)["status"],
            "MISSING_REQUIRED_DECLARATIONS")


class Clause03(unittest.TestCase):
    def test_95m_ulS_esm_not_applicable(self):
        self.assertFalse(esm_applicability(height_m=95,period_s=1.98,
                            irregular=True,limit_state="ULS")["permitted"])
        self.assertTrue(esm_applicability(height_m=95,period_s=1.98,
                            irregular=True,limit_state="SLS")["permitted"])
        self.assertTrue(esm_applicability(height_m=15,period_s=4,
                            irregular=True,limit_state="ULS")["permitted"])
        self.assertTrue(esm_applicability(height_m=39,period_s=1,
                            irregular=False,limit_state="ULS")["permitted"])
    def test_stiffness_table_3_1(self):
        self.assertEqual(cracked_flexural_factor("flat slab","ULS"),.25)
        self.assertEqual(cracked_flexural_factor("flat slab","SLS"),.5)
        self.assertEqual(cracked_flexural_factor("cracked wall","ULS"),.5)
        self.assertEqual(cracked_flexural_factor("beam","SLS"),.7)
    def test_soil_bearing_upper_bound(self):
        self.assertEqual(bearing_pressure_limit(100,earthquake=True),150)
        self.assertEqual(bearing_pressure_limit(100,earthquake=False),100)


class Clause06(unittest.TestCase):
    def test_coefficients_and_distribution(self):
        self.assertAlmostEqual(base_shear_coefficient(0.5,ductility=2,
                               overstrength=1.25,limit_state="ULS"),.2)
        self.assertAlmostEqual(base_shear_coefficient(.4,
                               overstrength=1.25,limit_state="SLS"),.32)
        self.assertEqual(base_shear(.2,1000),200)
        self.assertAlmostEqual(distribution_exponent(1.5),1.5)
        self.assertEqual(distribution_exponent(.5),1)
        self.assertEqual(distribution_exponent(2.5),2)
        f=distribute_forces(100,[100,200],[3,6],1)
        self.assertAlmostEqual(sum(f),100)
        self.assertAlmostEqual(f[0],20)
        self.assertEqual([esm_deflection_factor(x) for x in range(1,7)],
                         [1,.97,.94,.91,.88,.85])


class Clause07(unittest.TestCase):
    def test_effective_modal_weight_and_signed_story_forces(self):
        self.assertAlmostEqual(modal_effective_weight([100,100],[1,2]),180)
        f=modal_story_forces([100,100],[1,2],90)
        self.assertEqual(f,[30,60])
    def test_force_only_scaling(self):
        r=force_only_scale(esm_shear=100,mrsm_shear=50,
                      member_forces=[10,-20],story_shears=[30],
                      base_reactions=[-50],drifts=[.003],displacements=[.2])
        self.assertEqual(r["member_forces"],[20,-40])
        self.assertEqual(r["base_reactions"],[-100])
        self.assertEqual(r["drifts"],[.003])
        self.assertEqual(r["displacements"],[.2])
        self.assertEqual(modal_mass_coverage([20,70]),90)
        self.assertAlmostEqual(srss([3,4]),5)


class Clause08(unittest.TestCase):
    def test_model_requirements(self):
        self.assertEqual(elastic_model_prerequisites(is_3d=True,gravity=True,
            p_delta=True,torsion=True,damping_ratio=.05)["status"],"PASS")
        with self.assertRaises(ValueError):
            elastic_model_prerequisites(is_3d=True,gravity=True,p_delta=True,
                torsion=True,damping_ratio=.05001)
    def test_exact_seven_records_ambiguous(self):
        self.assertEqual(record_response_aggregate([1,4,2]),4)
        self.assertAlmostEqual(record_response_aggregate([1,2,3,4,5,6,7,8]),4.5)
        with self.assertRaises(ValueError):
            record_response_aggregate([1,2,3,4,5,6,7])


class Clause09(unittest.TestCase):
    def test_ground_motion_bounds_and_steps(self):
        self.assertEqual(motion_scale_factor(2,.5),.5)
        with self.assertRaises(ValueError):
            motion_scale_factor(2,.2)
        self.assertAlmostEqual(history_time_step_limit_s(.8,.02,.025),.008)
        self.assertEqual(required_component_runs(3,is_3d=True),6)
        self.assertEqual(nonlinear_model_prerequisites(is_3d=True,gravity=True,
            p_delta=True,torsion=True,bilinear=True,hysteretic=True)["status"],"PASS")


class Clause10(unittest.TestCase):
    def test_table_10_1(self):
        self.assertAlmostEqual(component_amplification_factor(1,1),2.5)
        self.assertAlmostEqual(component_amplification_factor(1,1.25),1.75)
        self.assertAlmostEqual(component_amplification_factor(1,1.5),1)
        self.assertAlmostEqual(component_amplification_factor(1,2),1)
    def test_components_and_limits(self):
        self.assertEqual(component_ductility_factor("low"),1.5)
        self.assertEqual(component_ductility_factor("moderate"),2.5)
        self.assertEqual(component_importance_factor("hazardous"),1.5)
        self.assertEqual(component_importance_factor("other"),1.0)
        self.assertFalse(component_scope(100,25)["allowed"])
        self.assertTrue(component_scope(100,24.9)["allowed"])
        self.assertAlmostEqual(friction_design_resistance(20,.3),3)
        self.assertAlmostEqual(component_design_force(z=.35,hp=47.5,H=95,
            ap=2.5,mu_p=2.5,Ip=1.5,Wp=100),78.75)
    def test_invalid_period_rejected(self):
        with self.assertRaises(ValueError):
            component_amplification_factor(float("nan"),1)


if __name__=="__main__":
    unittest.main()

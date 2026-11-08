"""Native ETABS-shell modifier conversion tests; no external solver needed.

The OpenSees C++ ElasticMembranePlateSection has E_mem for membrane,
E_plate=E_mem*Ep_modifier for bending AND transverse shear. Tests ensure
we never claim ETABS v13=v23=1.0 when bending m=0.1.

[REF components/model/linear_shell_stiffness.py]
"""
import math
import unittest
from components.model.linear_shell_stiffness import (
    shell_section_parameters,section_command)


class LinearShellStiffnessTests(unittest.TestCase):
    def setUp(self):
        self.wall=dict(f11=.5,f22=.5,f12=.5,
                       m11=.1,m22=.1,m12=.1,
                       v13=1.,v23=1.,mass=1.,weight=1.)
    def test_actual_wall_section_preserves_thickness_and_required_membrane_and_bending(self):
        result=shell_section_parameters(30e6,.2,.6,self.wall,
            property_name="Wall 600",
            transverse_shear_policy="ALLOW_REVIEWED_THIN_SHELL_APPROX")
        self.assertAlmostEqual(result["E_membrane_kN_m2"],15e6)
        self.assertAlmostEqual(result["E_plate_kN_m2"],3e6)
        self.assertAlmostEqual(result["ep_modifier"],.2)
        self.assertEqual(result["physical_thickness_m"],.6)
        self.assertEqual(result["actual_inplane_modifier"],.5)
        self.assertEqual(result["actual_plate_modifier"],.1)
        self.assertEqual(result["actual_transverse_shear_modifier"],.1)
        self.assertFalse(result["transverse_shear_exact"])
        self.assertIn("NOT_FULL_ETABS_EQUIVALENCE",result["status"])
        class Ops:
            def section(self,*args): self.args=args
        ops=Ops()
        section_command(ops,1234,result)
        self.assertEqual(ops.args[0],"ElasticMembranePlateSection")
        self.assertEqual(ops.args[1],1234)
        self.assertEqual(len(ops.args),7)
        self.assertAlmostEqual(ops.args[2],15e6)
        self.assertAlmostEqual(ops.args[6],.2)
    def test_refuse_unreviewed_transverse_shear_difference(self):
        with self.assertRaisesRegex(ValueError,"cannot independently reproduce transverse shear"):
            shell_section_parameters(30e6,.2,.6,self.wall,property_name="Wall 600")
    def test_exact_when_bending_and_transverse_shear_modifiers_coincide(self):
        vals=dict(self.wall,v13=.1,v23=.1)
        r=shell_section_parameters(30e6,.2,.6,vals,
            property_name="Wall 600")
        self.assertTrue(r["transverse_shear_exact"])
        self.assertEqual(r["status"],"EXACT_UNIFORM_ELASTIC_SECTION")
    def test_anisotropic_modifiers_block(self):
        for key in ("f22","m22"):
            vals=dict(self.wall,v13=.1,v23=.1)
            vals[key]=.7
            with self.assertRaisesRegex(ValueError,"nonuniform"):
                shell_section_parameters(30e6,.2,.6,vals,property_name="Wall 600")
    def test_nonunity_mass_or_weight_block(self):
        for key in ("mass","weight"):
            vals=dict(self.wall,v13=.1,v23=.1)
            vals[key]=.9
            with self.assertRaisesRegex(ValueError,"mass/weight"):
                shell_section_parameters(30e6,.2,.6,vals,property_name="Wall 600")
    def test_slab_inplane_full_bending_quarter(self):
        slab=dict(f11=1.,f22=1.,f12=1.,
                  m11=.25,m22=.25,m12=.25,
                  v13=1.,v23=1.,mass=1.,weight=1.)
        x=shell_section_parameters(30e6,.2,.15,slab,
            property_name="Slab 150",
            transverse_shear_policy="ALLOW_REVIEWED_THIN_SHELL_APPROX")
        self.assertEqual(x["physical_thickness_m"],.15)
        self.assertEqual(x["actual_inplane_modifier"],1.)
        self.assertEqual(x["actual_plate_modifier"],.25)
        self.assertEqual(x["actual_transverse_shear_modifier"],.25)
    def test_partial_vector_or_invalid_inputs_block(self):
        vals=dict(self.wall);vals.pop("f11")
        with self.assertRaisesRegex(ValueError,"missing"):
            shell_section_parameters(30e6,.2,.6,vals,property_name="Wall 600")
        vals=dict(self.wall);vals["mass"]=float("nan")
        with self.assertRaisesRegex(ValueError,"Nonpositive/nonfinite"):
            shell_section_parameters(30e6,.2,.6,vals,property_name="Wall 600")
    def test_no_unintentional_mass_or_gravity_modification(self):
        x=shell_section_parameters(30e6,.2,.6,self.wall,
            property_name="Wall 600",transverse_shear_policy="ALLOW_REVIEWED_THIN_SHELL_APPROX")
        self.assertEqual(x["section_density"],0.)
        self.assertEqual(x["physical_thickness_m"],.6)


if __name__=="__main__":
    unittest.main()

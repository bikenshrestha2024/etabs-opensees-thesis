"""Test no duplicate self-weight sources and native rounded SHS area mapping."""
import unittest

from components.model.single_count_self_weight import audit_self_weight_patterns
from components.model.assembly import _frame_property

class CountWeightTests(unittest.TestCase):
    def args(self,patterns):
        return audit_self_weight_patterns(
            patterns,{"Self Weight":1.,"Dead":1.,"Live":.3},
            {"Self Weight":1.,"Dead":1.,"Live":.3},
            beam_weight_policy="GROSS_SECTION_LENGTH",
            joint_volume_policy="AUDIT_ONLY")
    def test_single_source_weight_from_volume_once(self):
        data=self.args([{"pattern":"Self Weight","multiplier":1.0},
                        {"pattern":"Live","multiplier":0.0}])
        self.assertEqual(data["full_DL_LL_physical_self_weight_coefficient"],1.)
        self.assertEqual(data["configured_gravity_self_weight_coefficient"],1.)
        self.assertIn("NOT_ESTABLISHED",data["geometric_joint_solid_ownership"])
    def test_two_nonzero_patterns_cannot_double_count_volume(self):
        with self.assertRaisesRegex(ValueError,"DOUBLE COUNT"):
            self.args([{"pattern":"Self Weight","multiplier":1.0},
                       {"pattern":"Dead","multiplier":1.0}])
    def test_duplicate_pattern_names_are_blocked(self):
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            self.args([{"pattern":"Dead","multiplier":.5},
                       {"pattern":"Dead","multiplier":.5}])
    def test_split_source_weight_total_one_is_allowed(self):
        data=self.args([{"pattern":"Self Weight","multiplier":.5},
                        {"pattern":"Dead","multiplier":.5}])
        self.assertEqual(data["full_DL_LL_physical_self_weight_coefficient"],1.)
    def test_beam_overlap_double_subtraction_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"DOUBLE SUBTRACTION"):
            audit_self_weight_patterns(
                [{"pattern":"Dead","multiplier":1.}],
                {"Dead":1.},{"Dead":1.},
                beam_weight_policy="ETABS_BEAM_CLEAR_LENGTH",
                joint_volume_policy="VERIFIED_SINGLE_OWNER")
    def test_native_shs_props_replace_sharp_corner_guess(self):
        row=dict(section_type="tube_square",
                 assigned_section="SHS 350 350 16",width_m=.35,depth_m=.35,
                 tube_flange_thickness_m=.016,tube_web_thickness_m=.016,
                 E_kN_m2=2e8,G_kN_m2=7.8e7,weight_per_volume=77.)
        nominal=_frame_property(row)
        native={"SHS 350 350 16":{"A":nominal["A"]*.979,
                                  "Iy":nominal["Iy"]*.99,
                                  "Iz":nominal["Iz"]*.99,
                                  "J":nominal["J"]*.99}}
        corrected=_frame_property(row,native)
        self.assertAlmostEqual(corrected["A"],native["SHS 350 350 16"]["A"])
        self.assertAlmostEqual(corrected["J"],native["SHS 350 350 16"]["J"])
        self.assertEqual(corrected["weight"],77.)
        self.assertLess(corrected["A"],nominal["A"])

if __name__=="__main__":
    unittest.main()

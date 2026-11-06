"""First-storey effective wall-area profile diagnostics.

A varying cross-sectional footprint across the storey must NEVER
silently become a single NBC 105 effective wall Aw, even when each
individual elevation slice has finite wall area.
"""
import unittest
from components.inputs.project_workbooks import (
    _wall_aw_profile,_wall_aw_from_patches)


class WallProfileRegression(unittest.TestCase):
    def test_opening_produces_two_slices_without_adopted_area(self):
        patches=[
            ("X",0.,.3,0.,2.,0.,1.5),
            ("X",0.,.3,0.,1.,1.5,3.0),
            ("Y",5.,.2,0.,2.,0.,3.0),
        ]
        profile=_wall_aw_profile(95,0,3,patches)
        self.assertFalse(profile["uniform_footprint"])
        self.assertEqual(len(profile["rows"]),2)
        self.assertGreater(profile["rows"][0]["aw_x_m2"],
                           profile["rows"][1]["aw_x_m2"])
        with self.assertRaisesRegex(ValueError,"footprint changes"):
            _wall_aw_from_patches(95,0,3,patches)

    def test_mesh_splits_at_midheight_do_not_change_footprint(self):
        patches=[
            ("X",0.,.3,0.,2.,0.,1.5),
            ("X",0.,.3,0.,1.,1.5,3.0),
            ("X",0.,.3,1.,2.,1.5,3.0),
            ("Y",5.,.2,0.,2.,0.,3.0),
        ]
        profile=_wall_aw_profile(95,0,3,patches)
        self.assertTrue(profile["uniform_footprint"])
        actual,_=_wall_aw_from_patches(95,0,3,patches)
        self.assertAlmostEqual(profile["rows"][0]["aw_x_m2"],actual["X"])
        self.assertAlmostEqual(profile["rows"][1]["aw_y_m2"],actual["Y"])

    def test_no_patches_is_not_accepted_as_zero(self):
        with self.assertRaisesRegex(ValueError,"No source first-storey"):
            _wall_aw_profile(95,0,3,[])


if __name__=="__main__":
    unittest.main(verbosity=2)

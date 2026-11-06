"""NBC ESM first-storey opening continuity: source geometry diagnostic tests.

A through-storey geometric projection can be used for a *diagnostic* Aw
candidate, but cannot certify code-required physical wall-pier grouping.
"""
import unittest
from components.inputs.project_workbooks import (
    _wall_aw_profile,_continuous_wall_pier_diagnostic,_wall_aw_from_lines)


class TestContinuousPierGeometry(unittest.TestCase):
    def test_partial_height_opening_keeps_only_full_height_material(self):
        patches=[
            ('X',0.,.3,0.,5.,0.,1.5),
            ('X',0.,.3,0.,2.,1.5,3.),
            ('X',0.,.3,4.,5.,1.5,3.),
            ('Y',10.,.25,0.,3.,0.,3.)
        ]
        profile=_wall_aw_profile(95.,0.,3.,patches)
        self.assertFalse(profile['uniform_footprint'])
        result=_continuous_wall_pier_diagnostic(95.,profile)
        self.assertEqual(result['status'],'PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC')
        x=result['aw_candidate_m2']['X']
        y=result['aw_candidate_m2']['Y']
        expected,_=_wall_aw_from_lines(95.,{
            ('X',0.,.3):[(0.,2.),(4.,5.)],
            ('Y',10.,.25):[(0.,3.)]})
        self.assertAlmostEqual(x,expected['X'])
        self.assertAlmostEqual(y,expected['Y'])
        self.assertLess(x,profile['rows'][0]['aw_x_m2'])
        self.assertTrue(any('not a code-approved' in v.lower() for v in result['warnings']))

    def test_mesh_splits_same_wall_merge_back_without_double_counting(self):
        patches=[
            ('X',0.,.3,0.,5.,0.,1.),
            ('X',0.,.3,0.,2.5,1.,3.),
            ('X',0.,.3,2.5,5.,1.,3.),
        ]
        profile=_wall_aw_profile(80.,0.,3.,patches)
        self.assertTrue(profile['uniform_footprint'])
        result=_continuous_wall_pier_diagnostic(80.,profile)
        self.assertEqual(len(result['continuous_segments']),1)
        self.assertAlmostEqual(result['continuous_segments'][0]['wall_length_m'],5.)

    def test_no_full_height_pier_does_not_fabricate_Aw(self):
        patches=[
            ('X',0.,.3,0.,2.,0.,1.5),
            ('X',0.,.3,3.,5.,1.5,3.),
        ]
        profile=_wall_aw_profile(80.,0.,3.,patches)
        result=_continuous_wall_pier_diagnostic(80.,profile)
        self.assertIsNone(result['aw_candidate_m2']['X'])
        self.assertEqual(result['status'],'NO_FULL_HEIGHT_CONTINUOUS_WALL_SEGMENTS')

    def test_missing_y_stays_missing_y(self):
        patches=[
            ('X',0.,.3,0.,5.,0.,1.),
            ('X',0.,.3,0.,3.,1.,3.)
        ]
        result=_continuous_wall_pier_diagnostic(
            80.,_wall_aw_profile(80.,0.,3.,patches))
        self.assertGreater(result['aw_candidate_m2']['X'],0)
        self.assertIsNone(result['aw_candidate_m2']['Y'])


if __name__=='__main__':
    unittest.main(verbosity=2)

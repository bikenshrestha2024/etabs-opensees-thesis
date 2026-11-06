"""Geometric crosscheck of first-storey opening deduction, synthetic only.

ETABS and OpenSees can have different shell mesh subdivisions. Equal area
totals alone are insufficient: projected piers/opening boundaries at each
elevation must match. These tests are NOT NBC acceptance.
"""
import unittest
from components.inputs.project_workbooks import _wall_aw_profile
from components.inputs.opensees_nbc_sync import (
    compare_wall_profiles,opening_reduction_audit)


def geometry(split=False,opening_end=4.0):
    # First-storey wall with a centered opening over upper half.
    patches=[
        ('X',0.,.3,0.,6.,0.,1.5),
        ('X',0.,.3,0.,2.,1.5,3.),
        ('X',0.,.3,opening_end,6.,1.5,3.),
        ('Y',10.,.3,0.,4.,0.,3.),
    ]
    if split:
        patches=[
            ('X',0.,.3,0.,3.,0.,1.5),
            ('X',0.,.3,3.,6.,0.,1.5),
            ('X',0.,.3,0.,1.,1.5,3.),
            ('X',0.,.3,1.,2.,1.5,3.),
            ('X',0.,.3,opening_end,5.,1.5,3.),
            ('X',0.,.3,5.,6.,1.5,3.),
            ('Y',10.,.3,0.,4.,0.,3.),
        ]
    return _wall_aw_profile(95.,0.,3.,patches)


class OpeningsAndETABSCrosscheck(unittest.TestCase):
    def test_reduced_pier_uses_actual_opening_boundaries(self):
        profile=geometry()
        report=opening_reduction_audit(profile,95.)
        x=report['axes']['X']
        self.assertGreater(x['gross_projected_Aw_m2'],x['continuous_pier_Aw_m2'])
        self.assertGreater(x['excluded_noncontinuous_Aw_m2'],0)
        self.assertGreater(x['excluded_fraction_of_gross'],0)
        self.assertAlmostEqual(report['axes']['Y']['excluded_noncontinuous_Aw_m2'],0)
        self.assertIn('not an NBC-certified',report['disclaimer'])

    def test_independent_mesh_split_same_geometry_matches(self):
        result=compare_wall_profiles(geometry(),geometry(split=True))
        self.assertEqual(result['status'],'GEOMETRY_MATCHED_REVIEW_REQUIRED')
        self.assertGreaterEqual(result['checked_slices'],2)
        self.assertEqual(result['total_mismatches'],0)

    def test_different_opening_width_detected(self):
        result=compare_wall_profiles(geometry(),geometry(opening_end=4.5))
        self.assertEqual(result['status'],'GEOMETRY_MISMATCH')
        self.assertGreater(result['total_mismatches'],0)

    def test_same_totals_but_different_wall_location_rejected(self):
        a=geometry()
        b=geometry()
        for row in b['rows']:
            for segment in row['segments']:
                if segment['axis']=='X':
                    segment['plane_m']=2.0
        self.assertEqual(compare_wall_profiles(a,b)['status'],'GEOMETRY_MISMATCH')

    def test_tolerance_does_not_enable_arbitrary_acceptance(self):
        with self.assertRaises(ValueError):
            compare_wall_profiles(geometry(),geometry(),tolerance_m=-1)
        result=compare_wall_profiles(geometry(),geometry(),tolerance_m=.001)
        self.assertEqual(result['status'],'GEOMETRY_MATCHED_REVIEW_REQUIRED')
        self.assertIn('does not establish code-effective',result['disclaimer'])

    def test_no_wall_segment_is_not_treated_as_zero_approved_aw(self):
        self.assertEqual(opening_reduction_audit({'rows':[]},95.)['status'],'NO_GEOMETRY')


if __name__=="__main__":
    unittest.main(verbosity=2)

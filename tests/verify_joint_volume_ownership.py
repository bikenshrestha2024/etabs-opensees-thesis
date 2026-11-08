"""Conservative volumetric overlap ownership and never-silent activation."""
import tempfile
import unittest
from pathlib import Path
from components.model.joint_volume_ownership import (
    _volume, _subtract, build_joint_volume_ledger, export_joint_volume_ledger)


class JointWeightTests(unittest.TestCase):
    def setUp(self):
        # Column owns intersection; slab owns beam/slab junction; beam gets
        # the remainder. Stiffness/section are unchanged.
        self.nodes={
            1:[0.,0.,0.],2:[0.,0.,6.],
            3:[0.,0.,3.],4:[6.,0.,3.],
            5:[0.,-1.,3.],6:[6.,-1.,3.],
            7:[6.,1.,3.],8:[0.,1.,3.]}
        self.frames=[
            dict(object="C1",category="COLUMN",nodes=[1,2],length=6.,
                 physical_width_m=1.,physical_depth_m=1.,
                 properties=dict(A=1.,weight=25.)),
            dict(object="B1",category="BEAM",nodes=[3,4],length=6.,
                 physical_width_m=.5,physical_depth_m=.6,
                 properties=dict(A=.3,weight=25.))]
        self.shells=[
            dict(object="S1",category="FLOOR",nodes=[5,6,7,8],
                 area=12.,properties=dict(thickness=.15,weight=25.))]
    def test_cuboid_subtraction_conserves_volume(self):
        cube=((0.,2.),(0.,2.),(0.,2.))
        cut=((1.,3.),(.5,1.5),(.5,1.5))
        residual=_subtract(cube,cut)
        self.assertAlmostEqual(sum(map(_volume,residual)),7.)
    def test_triple_overlap_single_owner(self):
        audit=build_joint_volume_ledger(self.frames,self.shells,self.nodes)
        rows={r['object']:r for r in audit['rows']}
        self.assertAlmostEqual(rows['C1']['net_m3'],6.)
        self.assertAlmostEqual(rows['S1']['net_m3'],1.725)
        self.assertAlmostEqual(rows['B1']['net_m3'],1.2375)
        self.assertAlmostEqual(audit['gross_RCC_weight_kN'],9.6*25)
        self.assertAlmostEqual(audit['net_RCC_weight_kN'],8.9625*25)
        self.assertAlmostEqual(audit['potentially_duplicated_RCC_weight_kN'],.6375*25)
        # Attribution is by the material removed from each later solid:
        # Column owns both slab/column and beam/column volume;
        # floor slab owns only the remaining beam/slab volume.
        pairs=audit['overlap_pair_volume_m3']
        self.assertAlmostEqual(pairs['FLOOR_OVERLAPS_COLUMN'],.075)
        self.assertAlmostEqual(pairs['BEAM_OVERLAPS_COLUMN'],.15)
        self.assertAlmostEqual(pairs['BEAM_OVERLAPS_FLOOR'],.4125)
        self.assertAlmostEqual(sum(pairs.values()),.6375)
        self.assertEqual(audit['physical_geometry_validation_status'],
                         'ASSUMED_CENTERED_SOLIDS_NOT_VERIFIED')
        beam=rows['B1']
        self.assertAlmostEqual(beam['overlap_with_COLUMN_m3'],.15)
        self.assertAlmostEqual(beam['overlap_with_FLOOR_m3'],.4125)
        self.assertAlmostEqual(sum(audit['overlap_pair_weight_kN'].values()),
                               audit['potentially_duplicated_RCC_weight_kN'])
        self.assertEqual(audit['policy'],'AUDIT_ONLY')
        with tempfile.TemporaryDirectory() as folder:
            export_joint_volume_ledger(folder,audit)
            self.assertTrue((Path(folder)/'OpenSees_Joint_Volume_Ownership_Audit.csv').is_file())
    def test_verified_mode_requires_reviewed_physical_geometry(self):
        with self.assertRaisesRegex(ValueError,'geometry/insertion-point'):
            build_joint_volume_ledger(self.frames,self.shells,self.nodes,
                policy='VERIFIED_SINGLE_OWNER')
        a=build_joint_volume_ledger(self.frames,self.shells,self.nodes,
            policy='VERIFIED_SINGLE_OWNER',geometry_verified=True)
        self.assertLess(a['rows'][-1]['retained_ratio'],1.)
    def test_unsupported_rotated_geometry_is_not_invented(self):
        frame=dict(self.frames[1]);frame['nodes']=[1,7]
        with self.assertRaisesRegex(ValueError,'not axis aligned'):
            build_joint_volume_ledger([frame],[],self.nodes,
                policy="VERIFIED_SINGLE_OWNER",geometry_verified=True)
    def test_etabs_offset_audit_keeps_auto_mode_unverified(self):
        from components.model.joint_volume_ownership import export_frame_offset_weight_audit
        children={"B1":[dict(object="B1",category="BEAM",end=6.,
                     properties=dict(A=.48,weight=25.))]}
        with tempfile.TemporaryDirectory() as folder:
            report=export_frame_offset_weight_audit(folder,children,{
                "B1":{"GetEndLengthOffset":[True,.55,.55,1.,0]}})
            text=report.read_text(encoding="utf-8-sig")
            self.assertIn("AUTO_OFFSET_NOT_WEIGHT_RULE",text)
            self.assertIn("13.2",text)
            self.assertIn("4.9",text)

    def test_invalid_policy_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'Unknown joint'):
            build_joint_volume_ledger(self.frames,self.shells,self.nodes,
                policy="CLEAR_ALL")

if __name__=='__main__':
    unittest.main()

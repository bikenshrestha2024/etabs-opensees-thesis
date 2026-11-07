"""Regression tests for geometry-gated ETABS/OpenSees gravity support audit."""
import tempfile
import unittest
from pathlib import Path

from components.validation.gravity_node_comparison import (
    compare_support_nodes,write_node_comparison
)


class GravityNodeAuditTests(unittest.TestCase):
    def setUp(self):
        self.os=dict(
            nodes=[dict(tag=1,x_m=0,y_m=0,z_m=0),
                   dict(tag=2,x_m=6,y_m=0,z_m=0),
                   dict(tag=3,x_m=12,y_m=0,z_m=0)],
            reactions=[dict(node_tag=1,rz_kN=100),
                       dict(node_tag=2,rz_kN=200),
                       dict(node_tag=3,rz_kN=300)])
        self.etabs=dict(joint_reactions=[
            dict(point='A',x_m=0,y_m=0,z_m=0,
                 rz_global_kN=105,global_z_basis='GLOBAL_Z_VERIFIED_DEFAULT_AXES'),
            dict(point='B',x_m=6,y_m=0,z_m=0,
                 rz_global_kN=220,global_z_basis='GLOBAL_Z_VERIFIED_DEFAULT_AXES'),
            dict(point='C',x_m=19,y_m=0,z_m=0,
                 rz_global_kN=70,global_z_basis='GLOBAL_Z_VERIFIED_DEFAULT_AXES')])
    def test_ranks_real_one_to_one_reaction_discrepancy(self):
        report=compare_support_nodes(self.etabs,self.os,tolerance_m=.01)
        self.assertEqual(report['valid_one_to_one_global_z_count'],2)
        self.assertEqual(report['etabs_unmatched_count'],1)
        self.assertEqual(report['opensees_unmatched_count'],1)
        self.assertEqual(report['top_discrepancies'][0]['etabs_point'],'B')
        self.assertAlmostEqual(report['top_discrepancies'][0]['abs_delta_kN'],20)
        self.assertEqual(report['matched_sum_difference_kN'],25)
        self.assertTrue(report['unmatched_reactions_not_zeroed'])
        with tempfile.TemporaryDirectory() as root:
            out=write_node_comparison(root,report)
            self.assertTrue(out.is_file())
            self.assertTrue((Path(root)/'Gravity_All_Support_Nodes.csv').exists())
            self.assertTrue((Path(root)/'Gravity_Top_Node_Discrepancies.csv').exists())
    def test_point_local_axis_not_mislabeled_as_global_z(self):
        self.etabs['joint_reactions'][0]['rz_global_kN']=None
        self.etabs['joint_reactions'][0]['global_z_basis']='POINT_LOCAL_ROTATED'
        report=compare_support_nodes(self.etabs,self.os)
        self.assertEqual(report['axis_unverified_count'],1)
        self.assertEqual(report['valid_one_to_one_global_z_count'],1)
        self.assertEqual(report['top_discrepancies'][0]['etabs_point'],'B')
    def test_multiple_coordinates_never_silently_aggregate(self):
        self.os['nodes'].append(dict(tag=4,x_m=0,y_m=0,z_m=0))
        self.os['reactions'].append(dict(node_tag=4,rz_kN=100))
        report=compare_support_nodes(self.etabs,self.os)
        self.assertGreater(report['ambiguous_count'],0)
        self.assertEqual(report['valid_one_to_one_global_z_count'],1)
    def test_far_supports_stay_unmatched(self):
        self.etabs['joint_reactions'][0]['x_m']=0.1
        report=compare_support_nodes(self.etabs,self.os,tolerance_m=.01)
        self.assertEqual(report['valid_one_to_one_global_z_count'],1)
        self.assertGreater(report['opensees_unmatched_count'],0)
    def test_disallows_unsupported_matching_tolerance(self):
        with self.assertRaises(ValueError):
            compare_support_nodes(self.etabs,self.os,tolerance_m=2)

if __name__=="__main__":
    unittest.main()

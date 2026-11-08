"""Regression tests for geometry-gated ETABS/OpenSees gravity support audit."""
import tempfile
import unittest
from pathlib import Path

from components.validation.gravity_node_comparison import (
    compare_support_nodes,write_node_comparison,
    export_fixed_source_support_reactions
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
    def test_all_node_excel_preserves_source_map_and_does_not_invent_etabs_reactions(self):
        from openpyxl import load_workbook
        from components.validation.gravity_node_comparison import all_model_node_rows
        report=compare_support_nodes(self.etabs,self.os)
        # Third source point exists but has no exported ETABS support reaction.
        self.os["nodes"].append(dict(
            tag=4,x_m=1,y_m=2,z_m=3,ux_m=.001,uy_m=0,uz_m=-.004))
        topo={"node_map":[
            {"etabs_point_name":"A","opensees_node_tag":1},
            {"etabs_point_name":"B","opensees_node_tag":2},
            {"etabs_point_name":"D","opensees_node_tag":4}]}
        inventory=all_model_node_rows(self.os,topo,self.etabs,report)
        self.assertEqual(len(inventory),4)
        node4=next(x for x in inventory if x["opensees_node_tag"]=="4")
        self.assertEqual(node4["etabs_point_id"],"D")
        self.assertIsNone(node4["etabs_support_Rz_kN"])
        self.assertIsNone(node4["etabs_U3_m"])
        self.assertEqual(node4["opensees_Uz_m"],-.004)
        with tempfile.TemporaryDirectory() as root:
            write_node_comparison(root,report,etabs=self.etabs,
                                  opensees=self.os,topology=topo)
            self.assertTrue((Path(root)/"Gravity_All_Model_Nodes.csv").exists())
            wb=load_workbook(Path(root)/"Gravity_Node_Reaction_Comparison.xlsx",
                             read_only=True)
            self.assertIn("All OpenSees nodes",wb.sheetnames)
            self.assertIn("ETABS ID mapping",wb.sheetnames)
            self.assertIn("Largest differences",wb.sheetnames)
            self.assertEqual(wb["All OpenSees nodes"].max_row,5)

    def test_exact_source_76_node_workbook_and_critical_ranking(self):
        from openpyxl import load_workbook
        os_data=dict(nodes=[dict(tag=1,x_m=0.,y_m=0.,z_m=0.),
                            dict(tag=2,x_m=6.,y_m=0.,z_m=0.),
                            dict(tag=3,x_m=12.,y_m=0.,z_m=0.)],
            reactions=[dict(node_tag=1,rz_kN=110.),
                       dict(node_tag=2,rz_kN=180.),
                       dict(node_tag=3,rz_kN=100.)])
        topo=dict(node_map=[
            dict(opensees_node_tag=1,etabs_point_name="A",coordinates_m=[0,0,0]),
            dict(opensees_node_tag=2,etabs_point_name="B",coordinates_m=[6,0,0]),
            dict(opensees_node_tag=3,etabs_point_name="C",coordinates_m=[12,0,0])])
        etabs=dict(joint_reactions=[
            dict(point="A",x_m=0,y_m=0,z_m=0,rz_global_kN=100.,
                 global_z_basis="GLOBAL_Z_VERIFIED_DEFAULT_AXES"),
            dict(point="B",x_m=6,y_m=0,z_m=0,rz_global_kN=220.,
                 global_z_basis="GLOBAL_Z_VERIFIED_DEFAULT_AXES"),
            dict(point="C",x_m=12,y_m=0,z_m=0,rz_global_kN=100.,
                 global_z_basis="GLOBAL_Z_VERIFIED_DEFAULT_AXES")])
        with tempfile.TemporaryDirectory() as root:
            report=export_fixed_source_support_reactions(root,os_data,topo,etabs,
                                                         expected_tags=[1,2,3])
            self.assertEqual(report["matched_count"],3)
            self.assertEqual([x["opensees_node"] for x in report["rows"]],[1,2,3])
            self.assertEqual(report["ranked"][0]["opensees_node"],2)
            self.assertAlmostEqual(report["ranked"][0]["abs_difference_kN"],40.)
            book=load_workbook(Path(root)/"Gravity_76_Source_Support_Reactions.xlsx")
            self.assertIn("Nodes 1-76",book.sheetnames)
            self.assertEqual(book["Nodes 1-76"].max_row,4)
            self.assertTrue((Path(root)/"Gravity_76_Critical_Reaction_Nodes.csv").exists())
            no_etabs=export_fixed_source_support_reactions(
                Path(root)/"no_etabs",os_data,topo,None,expected_tags=[1,2,3])
            self.assertEqual(no_etabs["matched_count"],0)
            self.assertEqual(no_etabs["missing_or_unverified"],3)
            self.assertTrue(all(x["etabs_Rz_kN"] is None for x in no_etabs["rows"]))
    def test_76_support_audit_cannot_hide_wrong_source_coordinates(self):
        os_data=dict(nodes=[dict(tag=1,x_m=0,y_m=0,z_m=0)],
                     reactions=[dict(node_tag=1,rz_kN=100.)])
        topo=dict(node_map=[dict(opensees_node_tag=1,etabs_point_name="A",
                                 coordinates_m=[0,0,0])])
        etabs=dict(joint_reactions=[dict(point="A",x_m=20,y_m=0,z_m=0,
                                          rz_global_kN=100.)])
        with tempfile.TemporaryDirectory() as root:
            report=export_fixed_source_support_reactions(
                root,os_data,topo,etabs,expected_tags=[1])
            self.assertEqual(report["matched_count"],0)
            self.assertEqual(report["rows"][0]["status"],
                             "ETABS_OPENSEES_COORDINATE_MISMATCH")

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
    def test_source_pattern_nodal_load_export_is_separate_from_reactions(self):
        import json
        from components.validation.gravity_node_comparison import export_opensees_applied_nodal_loads
        with tempfile.TemporaryDirectory() as root:
            folder=Path(root)
            data=dict(nodes={'1':[0,0,0],'2':[3,0,3]},
                unfactored_patterns={
                    'Self Weight':{'1':[0,0,-100,0,0,0]},
                    'Live':{'2':[0,0,-30,0,0,0]},
                    'Roof Live':{'2':[0,0,-10,0,0,0]}})
            source=folder/'model.json'
            source.write_text(json.dumps(data),encoding='utf8')
            summary=export_opensees_applied_nodal_loads(source,folder/'out')
            self.assertEqual(summary['vertical_applied_kN_by_pattern']['Live'],-30)
            self.assertEqual(summary['vertical_applied_kN_by_pattern']['Roof Live'],-10)
            self.assertEqual(summary['profile'],'GRAVITY_1.0D_1.0L')
            self.assertTrue((folder/'out'/'OpenSees_Applied_Nodal_Gravity_By_Pattern.csv').is_file())

    def test_disallows_unsupported_matching_tolerance(self):
        with self.assertRaises(ValueError):
            compare_support_nodes(self.etabs,self.os,tolerance_m=2)

if __name__=="__main__":
    unittest.main()

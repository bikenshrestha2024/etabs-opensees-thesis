"""Physical slab self-weight = original floor area × thickness × unit weight.

[REF docs/source/components/gravity/slab_self_weight_audit.py.md]
"""
import json
import tempfile
import unittest
from pathlib import Path
from components.gravity.slab_self_weight_audit import audit_slab_self_weight

class SlabWeightAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        # 6m x 6m, one original slab source, split into two equal shell cells.
        self.original_nodes={
            1:[0.,0.,3.],2:[6.,0.,3.],
            3:[6.,6.,3.],4:[0.,6.,3.]
        }
        self.records=[
            dict(dimension="area_polygon",category="FLOOR",
                 etabs_object="Slab-A",node_tags=[1,2,3,4])]
        self.mesh_nodes=dict(self.original_nodes,
                             **{}) # preserve original source coordinates
        self.mesh_nodes.update({5:[3.,0.,3.],6:[3.,6.,3.]})
        self.prop=dict(thickness=.15,weight=25.)
        self.cells=[
            dict(category="FLOOR",object="Slab-A",
                 area=18.,properties=self.prop,nodes=[1,5,6,4]),
            dict(category="FLOOR",object="Slab-A",
                 area=18.,properties=self.prop,nodes=[5,2,3,6])]
    def run_audit(self,ledger=None):
        return audit_slab_self_weight(
            self.cells,self.records,self.original_nodes,
            mesh_nodes=self.mesh_nodes,
            joint_volume_ledger=ledger,output_dir=self.root)

    def test_36m2_slab_weight_135kN_and_mesh_conserves(self):
        report=self.run_audit()
        self.assertEqual(report["total_source_floor_area_m2"],36.)
        self.assertAlmostEqual(report["gross_slab_self_weight_kN"],135.)
        self.assertAlmostEqual(report["equivalent_nodal_slab_self_weight_kN"],135.)
        self.assertEqual(report["slab_mesh_cell_count"],2)
        self.assertEqual(report["default_slab_weight_correction"],"NONE")
        self.assertEqual(report["hypothetical_full_overlap_net_beam_depth_m"],.65)
        self.assertTrue((self.root/"Gravity_Slab_Self_Weight_Audit.xlsx").is_file())
        self.assertTrue((self.root/"Gravity_Slab_Self_Weight_Audit.csv").is_file())

    def test_duplicate_child_polygon_same_total_area_fails(self):
        self.cells[1]["nodes"]=[1,5,6,4]
        with self.assertRaisesRegex(ValueError,"DUPLICATE/OVERLAPPING"):
            self.run_audit()

    def test_missing_floor_cell_area_fails_not_auto_fixes(self):
        self.cells[1]["area"]=17.
        with self.assertRaisesRegex(ValueError,"Mesh slab cell area differs"): 
            self.run_audit()

    def test_overlapping_two_source_slabs_blocks_single_count(self):
        ledger=dict(schema="joint-volume-ownership-v1",
            overlap_pair_weight_kN={"FLOOR_OVERLAPS_FLOOR":2.5},
            rows=[
                dict(kind="shell",index=0,category="FLOOR",
                     gross_weight_kN=67.5,net_weight_kN=67.5),
                dict(kind="shell",index=1,category="FLOOR",
                     gross_weight_kN=67.5,net_weight_kN=65.0)
            ])
        with self.assertRaisesRegex(ValueError,"OVERLAPPING source floor slabs"):
            self.run_audit(ledger)

    def test_floor_column_wall_intersections_are_recorded_not_deducted(self):
        ledger=dict(schema="joint-volume-ownership-v1",
            overlap_pair_weight_kN={},
            rows=[
                dict(kind="shell",index=0,category="FLOOR",
                     gross_weight_kN=67.5,net_weight_kN=62.5,
                     overlap_with_COLUMN_m3=.12,
                     **{"overlap_with_SHEAR WALL_m3":.08}),
                dict(kind="shell",index=1,category="FLOOR",
                     gross_weight_kN=67.5,net_weight_kN=67.5)
            ])
        report=self.run_audit(ledger)
        one=report["records"][0]
        self.assertEqual(one["gross_slab_self_weight_kN"],135.)
        self.assertAlmostEqual(one["joint_overlap_slab_net_hypothesis_kN"],130.)
        self.assertAlmostEqual(one["potential_slab_overlap_with_column_kN"],3.)
        self.assertAlmostEqual(one["potential_slab_overlap_with_wall_kN"],2.)
        self.assertEqual(report["default_slab_weight_correction"],"NONE")

    def test_unreconciled_original_object_is_error(self):
        self.records[0]["etabs_object"]="OTHER"
        with self.assertRaisesRegex(ValueError,"differ"):
            self.run_audit()

if __name__=="__main__":
    unittest.main()

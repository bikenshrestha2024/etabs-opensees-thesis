"""Regression for wall mesh supports: no false base fixity on generated nodes."""
import unittest
from components.model.assembly import _resolve_refined_wall_supports, _gravity_wall_support_strategy


class WallBaseSupportTests(unittest.TestCase):
    def setUp(self):
        # Horizontal base edge of a rectangular vertical wall, with 2 mesh-only nodes.
        self.source_nodes={1:[0.,0.,0.],2:[6.,0.,0.],3:[6.,0.,3.],4:[0.,0.,3.]}
        self.nodes={**self.source_nodes,101:[2.,0.,0.],102:[4.,0.,0.],
                    103:[3.,0.,1.5]}
        self.topology={"elements":[{"dimension":"area_polygon",
                                    "node_tags":[1,2,3,4]}]}
        self.source_supports={"1":[1]*6,"2":[1]*6}
    def test_source_only_does_not_fix_mesh_nodes(self):
        supports,added=_resolve_refined_wall_supports(
            self.source_supports,self.source_nodes,self.nodes,self.topology)
        self.assertEqual(set(supports),{"1","2"})
        self.assertEqual(added,[])
        self.assertNotIn("101",supports)
        self.assertNotIn("102",supports)
    def test_explicitly_confirmed_etabs_edge_extension(self):
        supports,added=_resolve_refined_wall_supports(
            self.source_supports,self.source_nodes,self.nodes,self.topology,
            policy="EDGE_PROPAGATE_CONFIRMED",confirmed_edge_extension=True)
        self.assertEqual(added,[101,102])
        self.assertEqual(set(supports),{"1","2","101","102"})
        self.assertNotIn("103",supports)
    def test_cannot_assume_etabs_wall_edge_option(self):
        with self.assertRaisesRegex(ValueError,"explicit ETABS confirmation"):
            _resolve_refined_wall_supports(
                self.source_supports,self.source_nodes,self.nodes,self.topology,
                policy="EDGE_PROPAGATE_CONFIRMED")
    def test_opening_edge_source_support_is_preserved(self):
        flags=[1,1,1,0,0,0]
        original=dict(self.source_supports)
        original["3"]=flags
        supported,added=_resolve_refined_wall_supports(
            original,self.source_nodes,self.nodes,self.topology)
        self.assertEqual(supported["3"],flags)
        self.assertEqual(added,[])
    def test_runtime_source_only_uses_exact_support_ids(self):
        data=dict(nodes={str(k):v for k,v in self.nodes.items()},
                  supports=dict(self.source_supports),
                  base_z_m=0.,added_wall_mesh_support_tags=[])
        mapping=dict(node_map=[
            dict(opensees_node_tag=tag,coordinates_m=loc)
            for tag,loc in self.source_nodes.items()],
            elements=self.topology["elements"])
        selected,added=_gravity_wall_support_strategy(
            data,mapping,"ETABS_SOURCE_SUPPORTS")
        self.assertEqual(set(selected),{"1","2"})
        self.assertEqual(added,[])
        self.assertEqual(data["supports"],self.source_supports)

    def test_continuous_fixed_base_only_adds_intermediate_wall_base(self):
        data=dict(nodes={str(k):v for k,v in self.nodes.items()},
                  supports=dict(self.source_supports),
                  base_z_m=0.,added_wall_mesh_support_tags=[])
        mapping=dict(node_map=[
            dict(opensees_node_tag=tag,coordinates_m=loc)
            for tag,loc in self.source_nodes.items()],
            elements=self.topology["elements"])
        selected,added=_gravity_wall_support_strategy(
            data,mapping,"CONTINUOUS_WALL_BASE_FIXED")
        self.assertEqual(added,[101,102])
        self.assertEqual(set(selected),{"1","2","101","102"})
        self.assertNotIn("103",selected)
        self.assertEqual(data["supports"],self.source_supports)

    def test_runtime_refuses_source_only_from_pre_extended_export(self):
        data=dict(nodes={str(k):v for k,v in self.nodes.items()},
                  supports=dict(self.source_supports),
                  base_z_m=0.,added_wall_mesh_support_tags=[101])
        mapping=dict(node_map=[],elements=[])
        with self.assertRaisesRegex(ValueError,"SOURCE_ONLY rebuilt export"):
            _gravity_wall_support_strategy(data,mapping,"ETABS_SOURCE_SUPPORTS")

    def test_unknown_policy_fails(self):
        with self.assertRaisesRegex(ValueError,"Unknown wall"):
            _resolve_refined_wall_supports(
                self.source_supports,self.source_nodes,self.nodes,self.topology,
                policy="ALL_FIXED")


if __name__=="__main__":
    unittest.main()

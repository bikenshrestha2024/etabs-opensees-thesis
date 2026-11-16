"""Regression: spatially indexed meshing retains source-floor geometry and off-panel cuts.

No ETABS API or OpenSees solver is required. These tests exercise the same
production _mesh_areas() and build_case progress contract used by the GUI.
"""
from pathlib import Path
import importlib.util
import math
import unittest
from unittest.mock import patch

from components.model.assembly import _mesh_areas


class IndexedShellMeshTests(unittest.TestCase):
    def test_coplanar_off_panel_node_still_adds_conforming_grid_line(self):
        # The node (2,9,0) lies OUTSIDE the 6x6 floor panel but is coplanar.
        # Original mesh semantics propagate its x=2 coordinate into that
        # panel, even though its y coordinate is outside the source polygon.
        nodes = {
            1: [0., 0., 0.], 2: [6., 0., 0.],
            3: [6., 6., 0.], 4: [0., 6., 0.],
            5: [2., 9., 0.],
            6: [2., 9., 4.],  # off the source plane, must not add a cut
        }
        records = [dict(dimension="area_polygon", category="FLOOR",
                        etabs_object="floorA", node_tags=[1, 2, 3, 4])]
        rows = {"floorA": dict(assigned_property="Slab 150",
                               property_type="slab", material_name="M30",
                               thickness_m=.15,
                               material_values={"E": 30e6, "nu": .2,
                                                "weight_per_volume": 25.})}
        _, shells, by_source = _mesh_areas(nodes, records, rows, {}, 4)
        self.assertEqual(len(shells), 20)
        self.assertEqual(len(by_source["floorA"]), 20)
        self.assertAlmostEqual(sum(cell["area"] for cell in shells), 36., places=9)
        self.assertTrue(any(math.isclose(p[0], 2., abs_tol=1e-9)
                            for p in _.values()))

    def test_base_mesh_preserves_area_at_4_8_16(self):
        nodes = {1:[0.,0.,0.],2:[6.,0.,0.],
                 3:[6.,6.,0.],4:[0.,6.,0.]}
        records=[dict(dimension="area_polygon",category="FLOOR",
                      etabs_object="A",node_tags=[1,2,3,4])]
        rows={"A":dict(assigned_property="Slab",property_type="slab",
                       material_name="M30",thickness_m=.15,
                       material_values={"E":30e6,"nu":.2,"weight_per_volume":25.})}
        for n in (4,8,16):
            with self.subTest(n=n):
                out,shells,_ = _mesh_areas(nodes,records,rows,{},n)
                self.assertEqual(len(shells),n*n)
                self.assertAlmostEqual(sum(x["area"] for x in shells),36.,places=9)
                self.assertEqual(len(out),len(nodes)+(n+1)**2-4)

    def test_mesh_build_progress_signature_backward_compatible(self):
        root=Path(__file__).resolve().parents[1]/"components/gravity/mesh_cases.py"
        spec=importlib.util.spec_from_file_location("mesh_case_perf_contract",root)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        import inspect
        parameters=inspect.signature(module.build_case).parameters
        self.assertIn("progress",parameters)
        self.assertIsNone(parameters["progress"].default)


if __name__ == "__main__":
    unittest.main(verbosity=2)

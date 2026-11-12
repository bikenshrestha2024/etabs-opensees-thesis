"""Deterministic uniform-pressure patch tests for floor quad nodal load vector."""
import json
import math
import tempfile
import unittest
from pathlib import Path
from tools.audit_shell_gravity_transfer import (
    quad_equivalent_nodal_forces, review_export)


class SlabLoadPatchTests(unittest.TestCase):
    def test_rectangle_has_exact_equal_four_node_loads(self):
        force,area = quad_equivalent_nodal_forces(
            [(0,0),(2,0),(2,3),(0,3)], pressure=5)
        self.assertAlmostEqual(area,6)
        for nodal in force:self.assertAlmostEqual(nodal,7.5)

    def test_trapezoid_has_equal_total_but_unequal_nodal_loads(self):
        forces,area = quad_equivalent_nodal_forces(
            [(0,0),(2,0),(1.5,1),(0,1)])
        self.assertAlmostEqual(area,1.75)
        self.assertAlmostEqual(sum(forces),area)
        self.assertAlmostEqual(forces[0],11/24)
        self.assertAlmostEqual(forces[2],5/12)
        self.assertNotAlmostEqual(forces[0],area/4)

    def test_inverted_cell_does_not_silently_change_normals(self):
        with self.assertRaisesRegex(ValueError, "inverted"):
            quad_equivalent_nodal_forces([(0,0),(0,1),(1,1),(1,0)])

    def test_read_only_model_export_audit(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/"model.json"
            model = {"nodes":{"1":[0,0,4],"2":[2,0,4],
                              "3":[1.5,1,4],"4":[0,1,4]},
                     "shells":[{"category":"FLOOR","object":"Area1",
                                "area":1.75,"nodes":[1,2,3,4]}]}
            original = json.dumps(model)
            path.write_text(original)
            audit = review_export(path)
            self.assertEqual(audit["nonuniform_nodal_share_cells"],1)
            self.assertEqual(audit["status"],"REVIEW_REQUIRED")
            self.assertEqual(path.read_text(),original)


if __name__=="__main__":
    unittest.main()

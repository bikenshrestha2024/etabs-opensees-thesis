"""Solver-free geometric regression checks, not physical wall-model validation."""
import unittest
from components.nonlinear_time_history.wall_diagnostics import inspect_wall_geometry

def quad(nodes, obj="354", thickness=0.4):
    return {"frames":[], "nodes":{str(i+1):list(p) for i,p in enumerate(nodes)},
            "shells":[{"object":obj,"category":"SHEAR WALL",
                       "nodes":[1,2,3,4],"properties":{"thickness":thickness}}]}

class WallGeometryAuditTests(unittest.TestCase):
    def test_vertical_panel(self):
        model=quad([(0,0,0),(2,0,0),(2,0,3),(0,0,3)])
        report=inspect_wall_geometry(model)
        self.assertEqual(report["panels"][0]["status"],"GEOMETRY_SCREEN_PASSED")
        self.assertEqual(report["panels"][0]["estimated_solver_tag"],100001)
        self.assertTrue(report["panels"][0]["suspected_from_v168"])
    def test_degenerate_panel(self):
        model=quad([(0,0,0),(0,0,0),(2,0,3),(0,0,3)])
        self.assertEqual(inspect_wall_geometry(model)["status"],"INVALID")
    def test_nonfinite_thickness(self):
        model=quad([(0,0,0),(2,0,0),(2,0,3),(0,0,3)],thickness=float("nan"))
        self.assertEqual(inspect_wall_geometry(model)["status"],"INVALID")
    def test_vertical_panel_with_wrong_esfi_node_orientation_is_blocked(self):
        # Geometrically valid vertical quad, but i-j represents panel HEIGHT,
        # causing wrong macrofiber widths if accepted by the solver mapping.
        model=quad([(0,0,0),(0,0,3),(2,0,3),(2,0,0)])
        report=inspect_wall_geometry(model)
        self.assertEqual(report["status"],"INVALID")
        self.assertIn("bottom width edge must be horizontal",
                      report["panels"][0]["errors"][0])

    def test_upside_down_esfi_panel_is_blocked(self):
        model=quad([(0,0,3),(2,0,3),(2,0,0),(0,0,0)])
        report=inspect_wall_geometry(model)
        self.assertEqual(report["status"],"INVALID")
        self.assertIn("must rise vertically",report["panels"][0]["errors"][0])

    def test_no_walls_is_not_a_pass(self):
        self.assertEqual(inspect_wall_geometry({"frames":[],"nodes":{},"shells":[]})["status"],"MISSING_WALLS")

if __name__=="__main__":
    unittest.main()

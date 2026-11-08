"""3D node focus and tag regression tests; no GUI display or OpenSees needed."""
import ast
import unittest
from pathlib import Path
from components.ui.view_controls import resolve_node_tag,center_camera_on_node


class Axis:
    def __init__(self):
        self.limits=[(-15.,30.),(-10.,20.),(0.,100.)]
        self.aspect=None
    def get_xlim(self):return self.limits[0]
    def get_ylim(self):return self.limits[1]
    def get_zlim(self):return self.limits[2]
    def set_xlim(self,a,b):self.limits[0]=(a,b)
    def set_ylim(self,a,b):self.limits[1]=(a,b)
    def set_zlim(self,a,b):self.limits[2]=(a,b)
    def set_box_aspect(self,value):self.aspect=value


class ViewFocusTests(unittest.TestCase):
    def test_etabs_integer_mapping_returns_string_tag(self):
        mapping={"264":41,"725":"9"}
        self.assertEqual(resolve_node_tag("ETABS point","264",mapping),"41")
        self.assertEqual(resolve_node_tag("ETABS point"," 725 ",mapping),"9")
        self.assertEqual(resolve_node_tag("OpenSees node"," 41 ",mapping),"41")
        self.assertEqual(resolve_node_tag("ETABS point","UNKNOWN",mapping),"")
    def test_focus_base_node_preserves_location_and_valid_extent(self):
        ax=Axis()
        span=center_camera_on_node(ax,[12.,12.,0.],span_fraction=.08)
        self.assertAlmostEqual(span,8.)
        self.assertEqual(ax.limits,[(8.,16.),(8.,16.),(-4.,4.)])
        self.assertEqual(ax.aspect,(1,1,1))
    def test_focus_validates_nan_and_rejects_invalid_fraction(self):
        ax=Axis()
        with self.assertRaisesRegex(ValueError,"finite"):
            center_camera_on_node(ax,[float("nan"),0,0])
        with self.assertRaisesRegex(ValueError,"span_fraction"):
            center_camera_on_node(ax,[0,0,0],span_fraction=1.4)
    def test_both_viewers_implement_shared_zoom_and_highlight(self):
        base=Path(__file__).resolve().parents[1]
        for file in ("components/ui/plot_utilities.py",
                     "components/ui/response_viewer.py",
                     "components/ui/view_controls.py"):
            ast.parse((base/file).read_text(encoding="utf8"),filename=file)
        for file in ("components/ui/plot_utilities.py",
                     "components/ui/response_viewer.py"):
            data=(base/file).read_text(encoding="utf8")
            self.assertIn("Zoom to Node",data)
            self.assertIn("node_selection_artists",data)
            self.assertIn("center_camera_on_node",data)


if __name__=="__main__":
    unittest.main()

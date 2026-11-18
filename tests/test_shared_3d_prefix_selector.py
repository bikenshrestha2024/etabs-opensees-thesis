"""All exported Plotly views share source-verified member-prefix selection.

Source display roles are not OpenSees solver tag renames. This test generates
the HTML without ETABS/solver and checks script parsing where Node is present.
"""
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from components.model.id_audit import export_id_audit


class Shared3DPrefixSelection(unittest.TestCase):
    def setUp(self):
        try:
            import openpyxl  # noqa: F401
        except ImportError:
            self.skipTest("Optional openpyxl required for ID audit generation")

    def make_fixture(self, folder):
        nodes=[]
        for i in range(1,23):
            nodes.append(dict(etabs_point_name=str(100+i),
                              opensees_node_tag=i,
                              etabs_storey_number=25,
                              coordinates_m=[float(i),float(i%4),95.0]))
        elements=[]
        types=["BEAM","COLUMN","BRACE","BRACE","BRACE","BRACE",
               "FVD","BRB","SHEAR WALL","FLOOR"]
        for i,cat in enumerate(types):
            obj=str(200+i)
            elements.append(dict(etabs_object=obj,dimension=(
                "area_polygon" if cat in ("FLOOR","SHEAR WALL") else "line_2_node"),
                category=cat,storey_number=25,
                assigned_section="example source section",
                element_tag=25001+i,
                node_tags=[i+1,i+2] if i<8 else [i+1,i+2,i+3,i+4],
                node_names=[str(101+i),str(102+i)]))
        (folder/"OpenSees_Element_Connectivity.json").write_text(
            json.dumps({"node_map":nodes,"elements":elements}),encoding="utf-8")
        (folder/"OpenSees_Complete_Model_Config_V118.json").write_text(
            json.dumps({"display_member_roles":{"203":"CO","204":"BT","205":"CT"}}),
            encoding="utf-8")
        (folder/"OpenSees_Source_Model_Metadata_V118.json").write_text(
            json.dumps({"supports":{}}),encoding="utf-8")
        for name in ("OpenSees_Structural_Elements_By_Storey.html",
                     "OpenSees_Load_Assignment_3D.html",
                     "OpenSees_Element_Connectivity_3D.html"):
            (folder/name).write_text(
                '<!doctype html><html><head><title>3D</title></head><body>'
                '<div class="plotly-graph-div"></div></body></html>',
                encoding="utf-8")

    def test_structural_source_filter_does_not_mutate_selection_overlay_trace(self):
        # Source postscript owns only the ORIGINAL Plotly traces. The shared
        # ID inspector adds a temporary trace; source filters must not index
        # original[i] for that new trace or hide it when filtering storeys.
        source=(Path(__file__).resolve().parents[1]/
                "components/ui/application.py").read_text(encoding="utf-8")
        self.assertIn('gd.data.slice(0,original.length).forEach',source)
        self.assertIn('Plotly.restyle(gd,{visible:vis},meta.map((_,i)=>i))',source)
        self.assertIn('class="source-3d-advanced"',source)
        self.assertIn('id="storyFilter"',source)
        self.assertIn('id="sectionFilter"',source)
        self.assertIn('id="opsIdFilter"',source)

    def test_prefix_selection_and_focus_shared_across_all_plotly_views(self):
        from openpyxl import load_workbook
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            self.make_fixture(root)
            export_id_audit(root)
            with (root/"OpenSees_ID_and_Support_Audit.xlsx").open("rb") as stream:
                workbook=load_workbook(stream,read_only=True,data_only=True)
                try:
                    rows=list(workbook["Elements"].values)
                finally:
                    workbook.close()
            self.assertEqual([r[9] for r in rows[1:]],
                ["B2501","C2501","BR2501","CO2501","BT2501",
                 "CT2501","FVD2501","BRB2501","SW2501","FL2501"])
            self.assertEqual([r[12] for r in rows[1:]],
                ["B","C","BR","CO","BT","CT","FVD","BRB","SW","FL"])
            for name in ("OpenSees_Structural_Elements_By_Storey.html",
                         "OpenSees_Load_Assignment_3D.html",
                         "OpenSees_Element_Connectivity_3D.html"):
                output=root/name
                markup=output.read_text(encoding="utf-8")
                for feature in ('id="memberPrefix"','id="memberStorey"',
                                'id="memberNumber"','id="memberHighlight"',
                                'id="memberFocus"','id="viewerAdvanced"',
                                'id="idKind"','id="viewZoomNode"',
                                'id="idResult"'):
                    self.assertIn(feature,markup,feature)
                for prefix in ("B","C","BR","CO","BT","CT","FVD","BRB"):
                    self.assertIn('value="'+prefix+'"',markup)
                self.assertIn("function refreshMemberNumbers()",markup)
                self.assertIn("function highlightMember()",markup)
                self.assertIn("source-verified members",markup)
                self.assertIn("not a solver tag",markup)
                self.assertIn("display_category",markup)
                self.assertIn("idKind",markup)
                self.assertEqual(markup.count('id="shared-3d-viewer-style-v162"'),1)
                self.assertEqual(markup.count('id="shared-id-selector-v121"'),1)
                self.assertIn("min-height:31px",markup)
                self.assertIn("@media(max-width:600px)",markup)
                self.assertIn("viewer-advanced",markup)
                if shutil.which("node"):
                    match=re.search(r'<script id="shared-id-selector-v121">(.*?)</script>',
                                    markup,re.S)
                    self.assertIsNotNone(match)
                    js=root/"selection-test.js"
                    js.write_text(match.group(1),encoding="utf-8")
                    result=subprocess.run(["node","--check",str(js)],
                                          capture_output=True,text=True,timeout=12)
                    self.assertEqual(result.returncode,0,result.stderr)
            export_id_audit(root)
            html=(root/"OpenSees_Structural_Elements_By_Storey.html").read_text()
            self.assertEqual(html.count('id="shared-id-selector-v121"'),1)
            self.assertEqual(html.count('id="shared-3d-viewer-style-v162"'),1)
            self.assertEqual(html.count('id="shared-id-controls-v122"'),1)


if __name__=="__main__":
    unittest.main()

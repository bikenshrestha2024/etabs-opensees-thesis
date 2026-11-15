"""Solver-free support topology check: original point != internal shell analysis node."""
import json
import tempfile
import unittest
from pathlib import Path

from components.gravity.etabs_reaction_support_filter import PROJECT_PRIMARY_32
from components.validation.gravity_native_equivalence_preflight import assess


class SupportTopologyEvidenceTests(unittest.TestCase):
    def fixture(self, root, *, include_assembled=True):
        folder=root/"source"
        folder.mkdir()
        primary=sorted(PROJECT_PRIMARY_32)
        extra=718
        src={
            "supports":{str(n):[1]*6 for n in primary+[extra]}
        }
        if include_assembled:
            src["frames"]=[{"object":"col","nodes":[primary[0],991]}]
            src["shells"]=[
                {"object":"wall","nodes":[extra,992,993,994]},
                {"object":"wall","nodes":[extra,994,995,996]}]
        (folder/"OpenSees_Complete_Model_Data_V118.json").write_text(
            json.dumps(src),encoding="utf-8")
        (folder/"OpenSees_Source_Model_Metadata_V118.json").write_text(
            json.dumps({"frames":{"923":{"GetEndLengthOffset":[True,0.,0.,1.,0]}},
                        "errors":[]}),encoding="utf-8")
        top={"node_map":[{"opensees_node_tag":n,"etabs_point_name":str(100+n)}
                         for n in primary+[extra]]}
        if include_assembled:
            top["elements"]=[
                {"category":"BEAM","node_tags":[extra,primary[0]],
                 "assigned_section":None},
                {"category":"BEAM","node_tags":[extra,primary[1]],
                 "assigned_section":None},
                {"category":"SHEAR WALL","node_tags":[primary[0],991,992,993]}
            ]
        (folder/"OpenSees_Element_Connectivity.json").write_text(
            json.dumps(top),encoding="utf-8")
        return folder

    def test_source_fixed_shell_only_support_is_marked_not_changed(self):
        with tempfile.TemporaryDirectory() as td:
            folder=self.fixture(Path(td))
            before=(folder/"OpenSees_Complete_Model_Data_V118.json").read_bytes()
            report=assess(folder)
            self.assertEqual(report["engineering_acceptance"],"NOT_VALIDATED")
            t=report["support_topology_summary"]
            self.assertEqual(t["released_original_restraints_count"],1)
            self.assertEqual(t["released_are_assembled_shell_only"],1)
            self.assertEqual(t["released_are_assembled_frame_connected"],0)
            self.assertEqual(t["released_incident_source_unassigned_frame_lines"],2)
            self.assertEqual(t["released_incident_assembled_shell_cells"],2)
            p=next(x for x in report["support_rows"] if x["opensees_node"]==718)
            self.assertEqual(p["assembled_support_class"],"SHELL_ONLY")
            self.assertEqual(p["source_unassigned_frame_incidence"],2)
            self.assertEqual(p["solver_shell_incidence"],2)
            self.assertEqual(p["solver_frame_incidence"],0)
            self.assertEqual((folder/"OpenSees_Complete_Model_Data_V118.json").read_bytes(),before)

    def test_missing_assembled_topology_is_not_silent_zero(self):
        with tempfile.TemporaryDirectory() as td:
            report=assess(self.fixture(Path(td),include_assembled=False))
            r=report["support_topology_summary"]
            self.assertEqual(r["status"],"ASSEMBLED_TOPOLOGY_NOT_AVAILABLE")
            self.assertIsNone(r["released_are_assembled_shell_only"])
            point=next(x for x in report["support_rows"] if x["opensees_node"]==718)
            self.assertIsNone(point["solver_shell_incidence"])
            self.assertEqual(point["assembled_support_class"],"CONNECTIVITY_NOT_IN_EXPORT")


if __name__=="__main__":
    unittest.main()

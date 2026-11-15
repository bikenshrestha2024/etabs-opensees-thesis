"""Optional XLSX/HTML integration: source ETABS IDs and reviewed brace roles."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from components.model.id_audit import export_id_audit


@unittest.skipUnless(importlib.util.find_spec("openpyxl"),"openpyxl not installed")
class DisplayRoleOutputTests(unittest.TestCase):
    def make_case(self, root, mappings):
        from openpyxl import load_workbook
        nodes=[{"etabs_point_name":"base","opensees_node_tag":1,
                "etabs_storey_number":0,"coordinates_m":[0,0,0]},
               {"etabs_point_name":"upper","opensees_node_tag":2,
                "etabs_storey_number":25,"coordinates_m":[0,0,96]}]
        elements=[]
        for index in range(4):
            elements.append({"etabs_object":str(1308+index),
              "dimension":"line_2_node","category":"BRACE","storey_number":25,
              "assigned_section":"350*350*16 SHS","element_tag":25049+index,
              "node_names":["base","upper"],"node_tags":[1,2]})
        (root/"OpenSees_Element_Connectivity.json").write_text(
            json.dumps({"node_map":nodes,"elements":elements}),encoding="utf-8")
        (root/"OpenSees_Complete_Model_Config_V118.json").write_text(
            json.dumps({"display_member_roles":mappings}),encoding="utf-8")
        return load_workbook

    def test_reviewed_co_bt_ct_are_prefixes_not_solver_tags(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            load_workbook=self.make_case(root,{"1308":"CO","1309":"BT","1310":"CT"})
            export_id_audit(root)
            wb=load_workbook(root/"OpenSees_ID_and_Support_Audit.xlsx",read_only=True)
            rows=list(wb["Elements"].values)
            self.assertEqual([r[9] for r in rows[1:]],["CO2501","BT2501","CT2501","BR2501"])
            self.assertEqual([r[10] for r in rows[1:]],["BRACE"]*4)
            self.assertEqual([r[11] for r in rows[1:]],["CO","BT","CT","BR"])
            self.assertEqual([r[5] for r in rows[1:]],list(range(25049,25053)))
            html=(root/"OpenSees_ID_Lookup.html").read_text(encoding="utf-8")
            self.assertIn("Brace role",html)
            self.assertIn("CO2501",html)

    def test_invalid_role_and_unknown_source_id_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            self.make_case(root,{"9999":"CT"})
            with self.assertRaisesRegex(ValueError,"absent ETABS IDs"):
                export_id_audit(root)
            self.make_case(root,{"1308":"FVD"})
            with self.assertRaisesRegex(ValueError,"Invalid display_member_roles"):
                export_id_audit(root)


if __name__=="__main__":
    unittest.main()

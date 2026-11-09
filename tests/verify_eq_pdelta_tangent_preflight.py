"""Synthetic preflight only; no real ETABS/OpenSees solver acceptance."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from components.model.eq_pdelta_initial_tangent import (
    audit_inputs, _read_force_rows)

class TangentPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.native={
            "opensees_beam_crosswalk_status":"SOURCE_IDS_OFFSETS_AND_TOTAL_MATCH",
            "clear_candidate_matches_native_quantity":True}
        self.config={"etabs_beam_weight_policy":"ETABS_BEAM_CLEAR_LENGTH",
                     "etabs_clear_beam_weight_confirmed":True,
                     "joint_volume_weight_policy":"AUDIT_ONLY"}
        self.data={"nodes":{"101":[0,0,4],"102":[0,0,8]},
                   "unfactored_patterns":{
                       name:{"101":[0,0,-10,0,0,0]}
                       for name in ("Self Weight","Floor Finish",
                                    "Partition","Wall","Live")}}
        self.save("ETABS_Native_Assignment_Gravity_Quantity_Audit.json",self.native)
        self.save("OpenSees_Complete_Model_Config_V118.json",self.config)
        self.save("OpenSees_Complete_Model_Data_V118.json",self.data)
        self.save("OpenSees_Element_Connectivity.json",{"node_map":[]})
        self.table=self.root/"etabs_supports.xlsx"
        self.table.write_bytes(b"placeholder path for preflight only")
        self.force=self.root/"force.csv"
        with self.force.open("w",newline="",encoding="utf-8") as f:
            w=csv.writer(f)
            w.writerow(["story_name","height_m","master_node_tag",
                        "lateral_force_kN","torsional_moment_kNm","limit_state"])
            w.writerow(["Story1",4,101,100,5,"ULS"])
            w.writerow(["Story2",8,102,50,2.5,"ULS"])
    def save(self,name,record):
        (self.root/name).write_text(json.dumps(record),encoding="utf-8")
    def test_verified_source_gate(self):
        a=audit_inputs(self.root,self.force,self.table,"X")
        self.assertEqual(a["axis"],"X")
        self.assertEqual(len(a["rows"]),2)
        self.assertEqual(a["rows"][0]["fx"],100)
    def test_unverified_gross_weight_blocks(self):
        self.config["etabs_beam_weight_policy"]="GROSS_SECTION_LENGTH"
        self.save("OpenSees_Complete_Model_Config_V118.json",self.config)
        with self.assertRaisesRegex(ValueError,"Re-export verified"):
            audit_inputs(self.root,self.force,self.table,"X")
    def test_unclassified_source_load_blocks(self):
        self.data["unfactored_patterns"]["Other"]={"101":[0,0,-1,0,0,0]}
        self.save("OpenSees_Complete_Model_Data_V118.json",self.data)
        with self.assertRaisesRegex(ValueError,"Unclassified"):
            audit_inputs(self.root,self.force,self.table,"Y")
    def test_unordered_stories_block(self):
        rows=list(csv.reader(self.force.open()))
        rows[1],rows[2]=rows[2],rows[1]
        with self.force.open("w",newline="",encoding="utf-8") as f:
            csv.writer(f).writerows(rows)
        with self.assertRaisesRegex(ValueError,"bottom-to-top"):
            _read_force_rows(self.force,"X")

if __name__=="__main__":
    unittest.main()

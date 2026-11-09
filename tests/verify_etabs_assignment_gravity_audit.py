"""Native ETABS assignment workbook and beam policy gates; synthetic only."""
import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook
from components.validation.etabs_assignment_gravity_audit import (
    audit_native_assignment_workbook)


class NativeBeamQuantityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        book=Workbook()
        book.remove(book.active)
        tables={
            "Material List by Object Type":(
                ["Object Type","Material","Weight","Number Pieces"],
                [["Beam","M45",100.,1],["Column","M45",200.,1],
                 ["Wall","M45",300.,1],["Floor","M45",400.,1],
                 ["Brace","Fe345",20.,1]]),
            "Material List by Section Prop":(
                ["Section","Object Type","Weight"],
                [["Beam 1","Beam",100.]]),
            "Frame Assigns - Summary":(
                ["UniqueName","Design Type","Length"],
                [["B1","Beam",5.]]),
            "Frame Assigns - End Len Offsets":(
                ["UniqueName","Offset I","Offset J","Self Weight Option"],
                [["B1",500.,500.,"Auto"]]),
            "Frame Assigns - Insertion Point":(
                ["UniqueName","Cardinal Point"],
                [["B1","8 (Top Center)"]]),
            "Area Assigns - Insertion Point":(
                ["UniqueName","Cardinal Point"],
                [["F1","Top"]]),
            "Load Pattern Definitions":(
                ["Name","Self Weight Multiplier"],
                [["Self Weight",1.],["Live",0.]]),
            "Shell Uniform Load Sets":(
                ["Load Pattern","Load Value"],[["Live",4.]]),
        }
        for name,(header,rows) in tables.items():
            ws=book.create_sheet(name)
            ws.append(["TABLE: "+name])
            ws.append(header)
            ws.append([""]*len(header))
            for row in rows:ws.append(row)
        self.path=self.root/"source.xlsx"
        book.save(self.path)
        self.beam=self.root/"beam.json"
        self.beam.write_text(json.dumps({
            "schema":"beam-self-weight-end-offset-v1",
            "rows":[{"etabs_object":"B1","full_length_m":5.,
                     "end_i_m":.5,"end_j_m":.5}],
            "gross_beam_weight_kN":125.,
            "potential_offset_reduction_kN":25.,
            "selected_beam_weight_kN":125.,
        }),encoding="utf-8")

    def test_exact_native_beam_match_without_weight_change(self):
        r=audit_native_assignment_workbook(
            self.path,self.root/"out",self.beam)
        self.assertEqual(r["opensees_beam_crosswalk_status"],
                         "SOURCE_IDS_OFFSETS_AND_TOTAL_MATCH")
        self.assertTrue(r["clear_candidate_matches_native_quantity"])
        self.assertEqual(r["native_beam_objects"],1)
        self.assertFalse(r["physical_correction_activated"])

    def test_wrong_native_beam_offset_blocks(self):
        data=json.loads(self.beam.read_text())
        data["rows"][0]["end_j_m"]=.3
        self.beam.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,"offset disagrees"):
            audit_native_assignment_workbook(
                self.path,self.root/"out",self.beam)

    def test_unmatched_native_beam_length_blocks(self):
        data=json.loads(self.beam.read_text())
        data["rows"][0]["full_length_m"]=6.
        self.beam.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,"length disagrees"):
            audit_native_assignment_workbook(
                self.path,self.root/"out",self.beam)


if __name__=="__main__":
    unittest.main()

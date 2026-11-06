"""Reproduce the 2026-11-06 blank Aw fields with source-attributed Excel.

Synthetic fixture only. A workbook text label is never an NBC wall index,
ETABS modal T1 or calculated Rayleigh result.
"""
import json
import tempfile
import unittest
from pathlib import Path
from openpyxl import Workbook
from components.inputs.project_workbooks import (
    import_project_inputs, source_workbooks, scaling_workbook_diagnostics)


class ESMBlankAwRegression(unittest.TestCase):
    def fixture(self,root,awx="3.6779",awy="0.8019",same=True,
                adjacent=False,only_scaling=False):
        export=root/"export";export.mkdir()
        model=r"D:\Models\ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS, OUTRIGGER CAP TRUSS.EDB"
        (export/"OpenSees_Element_Connectivity.json").write_text(
            json.dumps({"source_edb":model}),encoding="utf-8")
        workbook_root=root if adjacent else export
        w=Workbook();ws=w.active;ws.title="SCALING SUMMARY"
        ws["B4"]=model if same else r"D:\Models\SERVICE LOAD - NEPAL - 3 - BELT TRUSS.EDB"
        ws["B14"]=awx;ws["B15"]=awy;ws["C14"]=1.5;ws["C15"]=2.2
        scale=workbook_root/"scaling.xlsx";w.save(scale)
        calculator=None
        if not only_scaling:
            w=Workbook();ws=w.active;ws.title="NBC Calculator"
            ws["B9"]="C";ws["B10"]=0.35;ws["B11"]=1.;ws["B15"]=1.25
            calculator=export/"calculator.xlsx";w.save(calculator)
        return export,scale,calculator

    def test_valid_adjacent_scaling_fills_both_aw_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);export,scale,calc=self.fixture(root,adjacent=True)
            books=source_workbooks(root,export,"ULS")
            self.assertEqual(books,[calc,scale])
            imported=import_project_inputs(root,export,"ULS")
            self.assertAlmostEqual(imported["values"]["awx"],3.6779)
            self.assertAlmostEqual(imported["values"]["awy"],0.8019)

    def test_aw_label_is_rejected_not_written_into_gui_numeric_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);export,_,_=self.fixture(root,awx="Aw (m²)",awy="Aw (m²)")
            inputs=import_project_inputs(root,export,"ULS")
            self.assertNotIn("awx",inputs["values"])
            self.assertNotIn("awy",inputs["values"])
            self.assertTrue(any("Invalid awx" in note for note in inputs["notes"]))
            self.assertTrue(any("Invalid awy" in note for note in inputs["notes"]))

    def test_mismatched_source_remains_rejected_with_explicit_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);export,scale,_=self.fixture(root,same=False)
            self.assertIsNone(source_workbooks(root,export,"ULS")[1])
            infos=scaling_workbook_diagnostics(root,export,"ULS")
            self.assertTrue(any("B14 Aw-X=" in note and str(scale) in note
                                for note in infos))
            self.assertTrue(any("source EDB differs" in note for note in infos))

    def test_explicit_scaling_selection_does_not_hide_calculator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);export,scale,calc=self.fixture(root)
            (export/"NBC105_Workbook_Source.json").write_text(json.dumps(
                {"workbooks":[str(scale)]}),encoding="utf8")
            self.assertEqual(source_workbooks(root,export,"ULS"),[calc,scale])

    def test_source_matches_but_formula_error_is_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);export,_,_=self.fixture(root,awx="#VALUE!",awy="0.8019")
            imported=import_project_inputs(root,export,"ULS")
            self.assertNotIn("awx",imported["values"])
            self.assertAlmostEqual(imported["values"]["awy"],.8019)


if __name__=="__main__":
    unittest.main(verbosity=2)

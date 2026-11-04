"""Regression checks for NBC 105 ESM area/workbook/period provenance.

No ETABS COM or native OpenSees solver required. Synthetic data only.
"""
import json
import math
import tempfile
import unittest
from pathlib import Path
from openpyxl import Workbook
from components.inputs.project_workbooks import source_workbooks
from components.equivalent_static.calculation_and_gui import ESMGui, resolve_esm_state_periods


class Value:
    def __init__(self, value=""):
        self.value = str(value)
    def get(self):
        return self.value
    def set(self, value):
        self.value = str(value)


class ESMProvenanceTests(unittest.TestCase):
    def _workbook(self, path, edb):
        wb = Workbook()
        ws = wb.active
        ws.title = "SCALING SUMMARY"
        ws["B4"] = edb
        ws["B14"] = 3.6779
        ws["B15"] = 0.8019
        ws["C14"] = 1.2
        ws["C15"] = 2.1
        wb.save(path)

    def test_windows_edb_identity_selects_correct_scaling_workbook(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            edb = r"D:\Thesis\3 - BELT TRUSS, OUTRIGGER CAP TRUSS.EDB"
            (folder/"OpenSees_Element_Connectivity.json").write_text(
                json.dumps({"source_edb": edb}), encoding="utf-8")
            incorrect = folder/"other.xlsx"
            correct = folder/"correct.xlsx"
            self._workbook(incorrect, r"D:\Thesis\3 - BELT TRUSS, DIFFERENT.EDB")
            self._workbook(correct, edb)
            selected = source_workbooks(folder,folder,"ULS")[1]
            self.assertEqual(selected,correct)

    def test_wrong_floor_default_workbook_is_not_silently_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = r"D:\Thesis\3 - BELT TRUSS, OUTRIGGER CAP TRUSS.EDB"
            (folder/"OpenSees_Element_Connectivity.json").write_text(
                json.dumps({"source_edb": source}), encoding="utf-8")
            wrong = folder/"SERVICE LOAD  - NEPAL - 3 - BELT TRUSS, OUTRIGGER CAP TRUSS_NBC105_RS_Scaling_2.xlsx"
            self._workbook(wrong, r"D:\Thesis\5 - BELT TRUSS, OUTRIGGER CAP TRUSS.EDB")
            self.assertIsNone(source_workbooks(folder,folder,"SLS")[1])

    def test_unverified_workbook_period_does_not_replace_rayleigh_by_default(self):
        gui=object.__new__(ESMGui)
        gui.awx=Value("3.6779")
        gui.awy=Value("0.8019")
        gui.period_factor=Value("1.25")
        gui.rayleigh_tx=Value("")
        gui.rayleigh_ty=Value("")
        gui.excel_tx=Value("1.2 s")
        gui.excel_ty=Value("2.1 s")
        gui.use_workbook_periods=Value(False)
        gui.period_sources={}
        gui.project_input_audit={"values":{"awx":3.6779, "awy":0.8019,
                                            "workbook_adopted_tx":1.2,
                                            "workbook_adopted_ty":2.1}}
        with self.assertRaisesRegex(ValueError,"Rayleigh"):
            gui._adopted_axis_period("X",95)

    def test_reference_rejected_if_aw_changed_after_workbook_import(self):
        gui=object.__new__(ESMGui)
        gui.awx=Value("4.0")
        gui.awy=Value("0.8019")
        gui.period_factor=Value("1.25")
        gui.rayleigh_tx=Value("")
        gui.rayleigh_ty=Value("")
        gui.excel_tx=Value("1.2 s")
        gui.excel_ty=Value("2.1 s")
        gui.use_workbook_periods=Value(True)
        gui.period_sources={}
        gui.project_input_audit={"values":{"awx":3.6779,"awy":0.8019,
                                            "workbook_adopted_tx":1.2,
                                            "workbook_adopted_ty":2.1}}
        with self.assertRaisesRegex(ValueError,"Aw"):
            gui._adopted_axis_period("X",95)

    def test_uls_sls_periods_are_not_shared(self):
        periods=resolve_esm_state_periods(
            height_m=95,aw_by_axis={"X":3.6779,"Y":0.8019},
            factor=1.25,states=("ULS","SLS"),
            rayleigh_by_state={"ULS":{"X":1.5,"Y":2.4},
                               "SLS":{"X":2.2,"Y":3.3}})
        self.assertAlmostEqual(periods["ULS"]["X"],1.5)
        self.assertAlmostEqual(periods["SLS"]["X"],min(
            2.2,1.25*0.075*95**0.75/math.sqrt(3.6779)))
        self.assertNotEqual(periods["ULS"]["X"],periods["SLS"]["X"])

    def test_combined_state_missing_sls_rayleigh_is_blocked(self):
        with self.assertRaisesRegex(ValueError,"SLS"):
            resolve_esm_state_periods(
                height_m=95,aw_by_axis={"X":3.6779,"Y":0.8019},
                factor=1.25,states=("ULS","SLS"),
                rayleigh_by_state={"ULS":{"X":1.5,"Y":2.4}, "SLS":{}})


if __name__=="__main__":
    unittest.main(verbosity=2)

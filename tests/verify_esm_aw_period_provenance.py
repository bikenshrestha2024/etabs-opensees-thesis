"""Regression checks for NBC 105 ESM area/workbook/period provenance.

No ETABS COM or native OpenSees solver required. Synthetic data only.
"""
import json
import math
import tempfile
import unittest
from pathlib import Path
from openpyxl import Workbook
from components.inputs.project_workbooks import source_workbooks, _wall_aw_from_patches
from components.equivalent_static.calculation_and_gui import ESMGui, resolve_esm_state_periods


class Value:
    def __init__(self, value=""):
        self.value = value
    def get(self):
        return self.value
    def set(self, value):
        self.value = value


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

    def test_shifted_scaling_summary_uses_labelled_rows(self):
        from components.inputs.project_workbooks import import_project_inputs
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            edb=r"D:\\Thesis\\NBC Ultimate\\ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS, OUTRIGGER CAP TRUSS.EDB"
            (folder/"OpenSees_Element_Connectivity.json").write_text(
                json.dumps({"source_edb":edb}),encoding="utf-8")
            from openpyxl import Workbook
            wb=Workbook();ws=wb.active;ws.title="SCALING SUMMARY"
            ws["A5"]="Source EDB";ws["B5"]=edb
            ws["B15"]="Aw (m²)";ws["C15"]="Adopted T1 (s)"
            ws["A16"]="X";ws["B16"]=1.9582936288;ws["C16"]=2.0385674001
            ws["A17"]="Y";ws["B17"]=2.2030803324;ws["C17"]=1.9219797767
            source=folder/"shifted.xlsx";wb.save(source)
            chosen=source_workbooks(folder,folder,"ULS")
            self.assertEqual(chosen[1],source)
            data=import_project_inputs(folder,folder,"ULS")
            for key,value in {"awx":1.9582936288,"awy":2.2030803324,
                              "workbook_adopted_tx":2.0385674001,
                              "workbook_adopted_ty":1.9219797767}.items():
                self.assertAlmostEqual(data["values"][key],value)
            self.assertEqual(next(x["cell"] for x in data["audit"]
                                  if x["field"]=="awy"),"B17")

    def test_wrong_copy_source_identity_blocks_shifted_aw(self):
        from components.inputs.project_workbooks import import_project_inputs
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            selected=r"D:\\Thesis\\NBC Ultimate\\ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS, OUTRIGGER CAP TRUSS - Copy.EDB"
            original=r"D:\\Thesis\\NBC Ultimate\\ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS, OUTRIGGER CAP TRUSS.EDB"
            (folder/"OpenSees_Element_Connectivity.json").write_text(
                json.dumps({"source_edb":selected}),encoding="utf-8")
            from openpyxl import Workbook
            wb=Workbook();ws=wb.active;ws.title="SCALING SUMMARY"
            ws["A5"]="Source EDB";ws["B5"]=original
            ws["B15"]="Aw (m²)";ws["C15"]="Adopted T1 (s)"
            ws["A16"]="X";ws["B16"]=1.9583;ws["C16"]=2.0385
            ws["A17"]="Y";ws["B17"]=2.2031;ws["C17"]=1.922
            wb.save(folder/"unmatched.xlsx")
            self.assertIsNone(source_workbooks(folder,folder,"ULS")[1])
            data=import_project_inputs(folder,folder,"ULS")
            self.assertNotIn("awx",data["values"])
            self.assertNotIn("awy",data["values"])

    def test_calculator_scaling_tab_cannot_bypass_edb_identity(self):
        from components.inputs.project_workbooks import import_project_inputs
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            selected=r"D:\\Models\\ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS - Copy.EDB"
            original=r"D:\\Models\\ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS.EDB"
            (folder/"OpenSees_Element_Connectivity.json").write_text(
                json.dumps({"source_edb":selected}),encoding="utf-8")
            from openpyxl import Workbook
            wb=Workbook();wb.active.title="NBC Calculator"
            wb.active["B9"]="C";wb.active["B10"]=.35;wb.active["B11"]=1
            ws=wb.create_sheet("SCALING SUMMARY")
            ws["A5"]="Source EDB";ws["B5"]=original
            ws["A16"]="X";ws["B16"]=4.3;ws["C16"]=2.1
            ws["A17"]="Y";ws["B17"]=3.8;ws["C17"]=2.2
            wb.save(folder/"calculator_with_wrong_scaling.xlsx")
            data=import_project_inputs(folder,folder,"ULS")
            self.assertNotIn("awx",data["values"])
            self.assertNotIn("awy",data["values"])
            self.assertEqual(data["values"].get("soil"),"C")

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

    def test_partial_height_wall_opening_does_not_overstate_aw(self):
        walls=[
            ("X",0.,.3,0.,2.,0.,1.5),
            ("X",0.,.3,0.,1.,1.5,3.),
            ("Y",5.,.2,0.,2.,0.,3.),
        ]
        with self.assertRaisesRegex(ValueError,"footprint changes"):
            _wall_aw_from_patches(95.,0.,3.,walls)

    def test_vertically_meshed_wall_preserves_consistent_aw(self):
        walls=[
            ("X",0.,.3,0.,2.,0.,1.5),
            ("X",0.,.3,0.,1.,1.5,3.),
            ("X",0.,.3,1.,2.,1.5,3.),
            ("Y",5.,.2,0.,2.,0.,3.),
        ]
        area,segments=_wall_aw_from_patches(95.,0.,3.,walls)
        expected_x=.3*2.*(.2+(2./95.)**2)
        self.assertAlmostEqual(area["X"],expected_x)
        self.assertEqual(len(segments),2)

    def test_uls_sls_periods_are_not_shared(self):
        periods=resolve_esm_state_periods(
            height_m=95,aw_by_axis={"X":3.6779,"Y":0.8019},
            factor=1.25,states=("ULS","SLS"),
            rayleigh_by_state={"ULS":{"X":1.0,"Y":2.4},
                               "SLS":{"X":2.2,"Y":3.3}})
        self.assertAlmostEqual(periods["ULS"]["X"],1.0)
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

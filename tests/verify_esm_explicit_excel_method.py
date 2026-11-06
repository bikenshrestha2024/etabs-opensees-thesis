"""Explicit original Excel method integration, not calculated geometry fallback.

Source checks: source EDB, ULS/SLS, actual numeric labelled cells,
workbook SHA; a different EDB may be used only by direct user selection
as research reference, never as automatically qualified design values.
"""
import json
import tempfile
import unittest
from pathlib import Path
from openpyxl import Workbook
from components.inputs.project_workbooks import read_explicit_excel_calculation
from components.equivalent_static.calculation_and_gui import ESMGui


class Value:
    def __init__(self,x):self.x=x
    def get(self):return self.x


def prepared(root,state="ULS",source=None):
    if source is None:
        source=r"D:\\Thesis\\NBC Ultimate\\ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS.EDB"
    (root/"OpenSees_Element_Connectivity.json").write_text(
        json.dumps({"source_edb":source}),encoding="utf8")
    wb=Workbook();ws=wb.active;ws.title="SCALING SUMMARY"
    ws["A5"]="Source EDB"
    original=r"D:\\Thesis\\NBC Ultimate\\ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS.EDB"
    ws["B5"]=original
    ws["B15"]="Aw (m²)";ws["C15"]="Adopted T1 (s)"
    ws["A16"]="X";ws["B16"]=1.9582936288;ws["C16"]=2.0385674001
    ws["A17"]="Y";ws["B17"]=2.2030803324;ws["C17"]=1.9219797767
    path=root/"actual_ETABS_scaling.xlsx"
    wb.save(path)
    return path


class TestDirectExcelReference(unittest.TestCase):
    def test_reads_actual_shifted_workbook_cells_and_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);path=prepared(root)
            ref=read_explicit_excel_calculation(path,root,"ULS")
            self.assertAlmostEqual(ref['values']['awx'],1.9582936288)
            self.assertAlmostEqual(ref['values']['awy'],2.2030803324)
            self.assertEqual(ref['cells']['awx'],'B16')
            self.assertEqual(ref['cells']['awy'],'B17')
            self.assertEqual(ref['cells']['workbook_adopted_ty'],'C17')
            self.assertEqual(len(ref['workbook_sha256']),64)
            self.assertEqual(ref['source_identity'],'SAME_EDB_PATH_REFERENCE')
            self.assertFalse(ref['code_accepted'])

    def test_explicit_different_copy_edb_is_diagnostic_only(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            path=prepared(root,source=r"D:\\Thesis\\NBC Ultimate\\ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS - Copy.EDB")
            ref=read_explicit_excel_calculation(path,root,"ULS")
            self.assertEqual(ref['source_identity'],
                             'DIFFERENT_EDB_RESEARCH_REFERENCE_ONLY')
            self.assertFalse(ref['code_accepted'])

    def test_service_workbook_rejected_for_uls(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            path=prepared(root)
            wb=Workbook();ws=wb.active;ws.title="SCALING SUMMARY"
            ws['A5']='Source EDB'
            ws['B5']=r"D:\\Models\\SERVICE LOAD - NEPAL - 3.EDB"
            ws['A16']='X';ws['B16']=1.5;ws['C16']=1.0
            ws['A17']='Y';ws['B17']=1.6;ws['C17']=1.2
            wb.save(path)
            with self.assertRaisesRegex(ValueError,'Service/SLS'):
                read_explicit_excel_calculation(path,root,'ULS')

    def test_nonnumeric_headers_cannot_become_wall_area(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);path=prepared(root)
            wb=Workbook();ws=wb.active;ws.title="SCALING SUMMARY"
            ws['A5']='Source EDB'
            ws['B5']=r"D:\\Thesis\\NBC Ultimate\\ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS.EDB"
            ws['A16']='X';ws['B16']='Aw (m²)';ws['C16']='Adopted T1 (s)'
            ws['A17']='Y';ws['B17']=2.2;ws['C17']=1.9
            wb.save(path)
            with self.assertRaisesRegex(ValueError,'no numeric Aw-X'):
                read_explicit_excel_calculation(path,root,'ULS')

    def test_excel_reference_adopted_t_requires_matching_aw_and_bound(self):
        gui=object.__new__(ESMGui)
        gui.awx=Value(str(1.9582936288));gui.awy=Value(str(2.2030803324))
        gui.period_factor=Value("1.25")
        gui.rayleigh_tx=Value("");gui.rayleigh_ty=Value("")
        gui.use_workbook_periods=Value(True);gui.state=Value("ULS")
        gui.period_sources={}
        gui.excel_direct_reference={
            'limit_state':'ULS','source_identity':'DIFFERENT_EDB_RESEARCH_REFERENCE_ONLY',
            'values':{'awx':1.9582936288,'awy':2.2030803324,
                      'workbook_adopted_tx':2.0385674001,
                      'workbook_adopted_ty':1.9219797767}}
        # Current model height must make the workbook adopted references
        # compatible with the amplified empirical upper bound.
        self.assertAlmostEqual(gui._adopted_axis_period("X",95.),2.0385674001)
        self.assertIn('NOT ETABS EIGEN',gui.period_sources['X'])
        gui.awx=Value("2.000")
        with self.assertRaisesRegex(ValueError,'differs'):
            gui._adopted_axis_period("X",95.)

if __name__=="__main__":
    unittest.main(verbosity=2)

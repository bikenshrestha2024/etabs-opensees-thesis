"""ESM malformed workbook isolation: screenshot regression.

The XLSX suffix is not proof of OOXML ZIP bytes. An invalid workbook
must not block valid workbooks or model geometry. Original bytes unchanged.
"""
import json
import tempfile
import unittest
from pathlib import Path
from openpyxl import Workbook
from components.inputs.project_workbooks import (
    source_workbooks, import_project_inputs)


class InvalidXlsxIsolation(unittest.TestCase):
    def fixture(self,root):
        export=root/"export";export.mkdir()
        model=r"D:\Models\ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS.EDB"
        (export/"OpenSees_Element_Connectivity.json").write_text(
            json.dumps({"source_edb":model}),encoding="utf8")
        calc=Workbook();calc.active.title="NBC Calculator"
        calc.active['B9']="C";calc.active['B10']=.35;calc.active['B11']=1.
        calc.active['B15']=1.25
        valid=export/"good_calculator.xlsx";calc.save(valid)
        return export,model,valid

    def test_bad_zip_does_not_block_valid_calculator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);export,model,valid=self.fixture(root)
            bad=export/"00_invalid.xlsx"
            payload=b'This is an Excel text export, NOT an XLSX ZIP archive!'
            bad.write_bytes(payload)
            self.assertEqual(source_workbooks(root,export,'ULS'),[valid,None])
            result=import_project_inputs(root,export,'ULS')
            self.assertEqual(result['values']['soil'],'C')
            self.assertEqual(result['values']['Z'],.35)
            self.assertTrue(any('INVALID_XLSX_SKIPPED' in note and
                                bad.name in note for note in result['notes']))
            self.assertEqual(bad.read_bytes(),payload)

    def test_explicit_bad_selection_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);export,_,valid=self.fixture(root)
            bad=export/'chosen_scaling.xlsx';bad.write_bytes(b'not a zip file')
            (export/'NBC105_Workbook_Source.json').write_text(json.dumps(
                {'workbooks':[str(bad)]}),encoding='utf8')
            self.assertEqual(source_workbooks(root,export,'ULS'),[valid,None])
            result=import_project_inputs(root,export,'ULS')
            self.assertTrue(any('INVALID_XLSX_SKIPPED' in note and bad.name in note
                                for note in result['notes']))

    def test_all_invalid_leave_source_reader_operable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);export,_,valid=self.fixture(root);valid.unlink()
            (export/'bad.xlsx').write_bytes(b'bad')
            self.assertEqual(source_workbooks(root,export,'ULS'),[None,None])
            result=import_project_inputs(root,export,'ULS')
            self.assertTrue(any('No NBC Calculator' in note for note in result['notes']))
            self.assertTrue(any('INVALID_XLSX_SKIPPED' in note
                                for note in result['notes']))

    def test_valid_scaling_coexists_with_corrupt_sibling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);export,model,calc=self.fixture(root)
            (export/'bad.xlsx').write_bytes(b'broken')
            w=Workbook();w.active.title='SCALING SUMMARY'
            w.active['B4']=model;w.active['B14']=2.2;w.active['B15']=1.7
            scaling=export/'valid_scaling.xlsx';w.save(scaling)
            self.assertEqual(source_workbooks(root,export,'ULS'),[calc,scaling])
            inputs=import_project_inputs(root,export,'ULS')
            self.assertAlmostEqual(inputs['values']['awx'],2.2)
            self.assertAlmostEqual(inputs['values']['awy'],1.7)


if __name__=='__main__':
    unittest.main(verbosity=2)

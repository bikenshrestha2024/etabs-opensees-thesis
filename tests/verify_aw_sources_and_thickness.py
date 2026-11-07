"""Direct ETABS wall thickness, labelled Aw sources and shared GUI helpers.

[REF NBC105-2025 §5.1.2 (Awi uses actual wall thickness)]
[REF CSI ETABS OAPI cAreaObj / cPropArea.GetWall]
Solver-free and ETABS-free: the ETABS API is a fake object; no claim about
the live ETABS model is made by these tests.
"""
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from components.equivalent_static.etabs_linked_excel import (
    check_excel_wall_thickness, direct_wall_thickness_inventory)
from components.inputs import aw_sources
from components.ui.output_folder import resolve_folder

ROOT = Path(__file__).resolve().parents[1]


class FakeSap:
    """Section NAMED 250 but with a real numeric thickness of 0.600 m."""

    def __init__(self):
        areas = {'W1': (1, 'Outrigger Wall 250'), 'W2': (1, 'Outrigger Wall 250'),
                 'W3': (1, 'Core 300'), 'F1': (2, 'Slab 200')}
        thickness = {'Outrigger Wall 250': 0.600, 'Core 300': 0.300}
        self.AreaObj = mock.Mock()
        self.AreaObj.GetNameList.return_value = [len(areas), list(areas), 0]
        self.AreaObj.GetDesignOrientation.side_effect = lambda n: [areas[n][0], 0]
        self.AreaObj.GetProperty.side_effect = lambda n: [areas[n][1], 0]
        self.PropArea = mock.Mock()
        self.PropArea.GetWall.side_effect = (
            lambda p: [1, 1, 'C40', thickness[p], 0, '', '', 0] if p in thickness else [0, 0, '', 0., 0, '', '', 1])


def calculator(path, thicknesses_mm):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = 'NBC Calculator'
    for i, t in enumerate(thicknesses_mm, 10):
        ws[f'G{i}'] = t
    wb.save(path)
    return list(range(10, 10 + len(thicknesses_mm)))


class DirectThickness(unittest.TestCase):
    def test_numeric_thickness_not_section_name(self):
        inv = direct_wall_thickness_inventory(FakeSap())
        self.assertEqual(inv['properties'], {'Outrigger Wall 250': 0.6, 'Core 300': 0.3})
        self.assertEqual(inv['wall_areas'], {'Outrigger Wall 250': 2, 'Core 300': 1})
        self.assertNotIn('Slab 200', inv['properties'])          # floors excluded

    def test_excel_g_column_against_direct_values(self):
        inv = direct_wall_thickness_inventory(FakeSap())
        with tempfile.TemporaryDirectory() as tmp:
            ok = Path(tmp) / 'ok.xlsx'
            rows = calculator(ok, [600., 600., 300.])
            self.assertEqual(check_excel_wall_thickness(ok, rows, inv)['status'], 'MATCHED')
            bad = Path(tmp) / 'bad.xlsx'
            rows = calculator(bad, [600., 250.])                 # 250 taken from a NAME
            rep = check_excel_wall_thickness(bad, rows, inv)
            self.assertEqual(rep['status'], 'MISMATCH')
            self.assertIn('G11=250', rep['mismatches'][0])
            self.assertEqual(check_excel_wall_thickness(ok, rows, {'properties': {}})['status'],
                             'UNAVAILABLE')


def audit(edb='D:/Etabs/ULTIMATE LOAD - Copy.EDB', condition='Ultimate', thickness='MATCHED'):
    return dict(source_edb=edb, output_excel='x.xlsx',
                direct_thickness_check=dict(status=thickness, mismatches=['G11=250']),
                coefficients={a: dict(Aw_m2=aw, T1_s=t, condition=condition)
                              for a, aw, t in (('X', 1.9582936, 2.0385674), ('Y', 2.2030803, 1.9219798))})


class LinkedReference(unittest.TestCase):
    def test_reference_shape_identity_and_gates(self):
        edb = 'D:\\Etabs\\ULTIMATE LOAD - Copy.EDB'
        ref = aw_sources.linked_reference_from_audit(audit(), 'p.json', state='ULS', current_edb=edb)
        self.assertEqual(ref['source_identity'], 'SAME_EDB_PATH_REFERENCE')
        self.assertAlmostEqual(ref['values']['awx'], 1.9582936)
        self.assertAlmostEqual(ref['values']['workbook_adopted_ty'], 1.9219798)
        self.assertFalse(ref['code_accepted'])
        other = aw_sources.linked_reference_from_audit(audit(), 'p.json', state='ULS',
                                                       current_edb='D:/Etabs/SERVICE LOAD.EDB')
        self.assertEqual(other['source_identity'], 'DIFFERENT_EDB_RESEARCH_REFERENCE_ONLY')
        with self.assertRaisesRegex(ValueError, 'does not match'):
            aw_sources.linked_reference_from_audit(audit(condition='Service'), 'p', state='ULS', current_edb=edb)
        with self.assertRaisesRegex(ValueError, 'thickness'):
            aw_sources.linked_reference_from_audit(audit(thickness='MISMATCH'), 'p', state='ULS', current_edb=edb)

    def test_resolve_prefers_same_edb_excel_method_then_geometry(self):
        with tempfile.TemporaryDirectory() as tmp:
            export, results = Path(tmp) / 'export', Path(tmp) / 'results'
            export.mkdir()
            results.mkdir()
            edb = 'D:/Etabs/ULTIMATE LOAD - Copy.EDB'
            snapshot = dict(aw_candidate_m2={'X': 1.9306371, 'Y': None},
                            aw_evidence={'X': {'status': 'PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC'},
                                         'Y': {'status': 'NO_CONTINUOUS_PIER_IN_THIS_AXIS'}},
                            assembled_model_sha256='abc')
            with mock.patch('components.inputs.project_workbooks.analysis_output_folder', return_value=results), \
                 mock.patch('components.inputs.project_workbooks._source_edb_path', return_value=edb), \
                 mock.patch('components.inputs.opensees_nbc_sync._source_snapshot', return_value=snapshot):
                out = aw_sources.resolve_aw(export, 'ULS')               # nothing linked yet
                self.assertEqual(out['method'], 'OPEN_SEES_GEOMETRY_CANDIDATE')
                self.assertAlmostEqual(out['X'], 1.9306371)
                self.assertIsNone(out['Y'])
                self.assertIn('not NBC accepted', out['labels']['X'])
                (results / 'a_ETABS_LINKED_ESM.provenance.json').write_text(
                    json.dumps(audit(edb='D:/Etabs/SERVICE LOAD.EDB')))
                self.assertEqual(aw_sources.resolve_aw(export, 'ULS')['method'],
                                 'OPEN_SEES_GEOMETRY_CANDIDATE')   # different EDB is not auto-filled
                (results / 'b_ETABS_LINKED_ESM.provenance.json').write_text(json.dumps(audit(edb=edb)))
                out = aw_sources.resolve_aw(export, 'Both')
                self.assertEqual(out['method'], 'ORIGINAL_EXCEL_METHOD_ETABS_LINKED')
                self.assertAlmostEqual(out['X'], 1.9582936)
                self.assertAlmostEqual(out['Y'], 2.2030803)


class GuiHelpers(unittest.TestCase):
    def test_resolve_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / 'a.txt'
            f.write_text('x')
            var = mock.Mock()
            var.get.return_value = str(f)
            self.assertEqual(resolve_folder(var), Path(tmp))
            self.assertEqual(resolve_folder(lambda: tmp), Path(tmp))
            self.assertIsNone(resolve_folder(str(Path(tmp) / 'missing')))
            self.assertIsNone(resolve_folder(''))

    def test_no_literal_backslash_n_in_dialog_text(self):
        pattern = re.compile(r"messagebox\.\w+\(.*\\\\n")
        hits = [f'{p.relative_to(ROOT)}:{i}' for p in (ROOT / 'components').rglob('*.py')
                for i, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1)
                if pattern.search(line)]
        esm = (ROOT / 'components/equivalent_static/calculation_and_gui.py').read_text(encoding='utf-8')
        self.assertEqual(hits, [])
        self.assertNotIn("'\\\\n", esm)

    def test_every_analysis_window_offers_output_folder(self):
        for name in ('components/modal/gui_and_reports.py', 'components/linear_time_history/runner_and_gui.py',
                     'components/nonlinear_time_history/runner_and_gui.py',
                     'components/response_spectrum/model_analysis.py',
                     'components/validation/irregularity_review.py', 'components/ui/literature_demo_gui.py'):
            self.assertIn('add_open_output_button', (ROOT / name).read_text(encoding='utf-8'), name)


if __name__ == '__main__':
    unittest.main()

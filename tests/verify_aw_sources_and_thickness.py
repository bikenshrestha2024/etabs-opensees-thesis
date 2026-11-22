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
    _read_reviewed_first_storey, check_excel_wall_thickness, direct_wall_thickness_inventory)
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


class LinkedFirstStorey(unittest.TestCase):
    def test_lintel_is_only_excluded_if_its_vertices_clear_the_door_head(self):
        engine = mock.Mock()
        sap = object()
        stories = [{'name': 'Storey 1', 'height': 3.8, 'elevation': 3.8}]
        engine.audit_open_sap.return_value = {'reference_story': 'Storey 1'}
        engine.geometry_bays_from_direct_preflight.return_value = (
            [{'wall_y_m': 6., 'opening_intervals_m': [(8., 10.)]}], [])
        engine.area_points.return_value = [1, 2, 3, 4]
        with tempfile.TemporaryDirectory() as tmp:
            audit_dir = Path(tmp)
            (audit_dir / 'wall_panels.json').write_text(
                json.dumps({'spandrel_areas': [{'area': 'shell over the door'}]}))
            points = {1: (8, 6, 2.3), 2: (10, 6, 2.3),
                      3: (10, 6, 3.8), 4: (8, 6, 3.8)}
            engine.point_xyz.side_effect = lambda _sap, tag: points[tag]
            _, _, _, proof = _read_reviewed_first_storey(
                engine, sap, stories, audit_dir, lambda _msg: None)
            self.assertEqual(proof['checked_lintel_shells'][0]['bottom_m'], 2.3)
            engine.read_etabs_walls.assert_not_called()
            points[1] = (8, 6, 2.1)
            with self.assertRaisesRegex(ValueError, 'crosses a door below its head'):
                _read_reviewed_first_storey(engine, sap, stories, audit_dir, lambda _msg: None)


def audit(edb='D:/Etabs/ULTIMATE LOAD - Copy.EDB', condition='Ultimate',
          thickness='MATCHED', sha=None):
    return dict(source_edb=str(edb),source_edb_sha256=sha, output_excel='x.xlsx',
                direct_thickness_check=dict(status=thickness, mismatches=['G11=250']),
                coefficients={a: dict(Aw_m2=aw, T1_s=t, condition=condition)
                              for a, aw, t in (('X', 1.9582936, 2.0385674), ('Y', 2.2030803, 1.9219798))})


class LinkedReference(unittest.TestCase):
    def test_reference_shape_identity_and_gates(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            edb=Path(tmp)/"ULTIMATE LOAD - Copy.EDB"
            edb.write_bytes(b"verified unique ETABS source model")
            sha=hashlib.sha256(edb.read_bytes()).hexdigest()
            reference=audit(edb=edb,sha=sha)
            ref=aw_sources.linked_reference_from_audit(
                reference,'p.json',state='ULS',current_edb=str(edb))
            self.assertEqual(ref['source_identity'],'SAME_EDB_PATH_REFERENCE')
            self.assertAlmostEqual(ref['values']['awx'],1.9582936)
            self.assertAlmostEqual(ref['values']['workbook_adopted_ty'],1.9219798)
            self.assertFalse(ref['code_accepted'])
            other=Path(tmp)/"SERVICE LOAD.EDB"
            other.write_bytes(b"different ETABS source")
            changed=aw_sources.linked_reference_from_audit(
                reference,'p.json',state='ULS',current_edb=str(other))
            self.assertEqual(changed['source_identity'],
                             'DIFFERENT_EDB_RESEARCH_REFERENCE_ONLY')
            # Identical real EDB bytes may be deliberately copied to a new
            # path; identity requires SHA and must be labelled as such.
            other.write_bytes(edb.read_bytes())
            copied=aw_sources.linked_reference_from_audit(
                reference,'p.json',state='ULS',current_edb=str(other))
            self.assertEqual(copied['source_identity'],
                             'BYTE_IDENTICAL_EDB_REFERENCE')
            with self.assertRaisesRegex(ValueError,'does not match'):
                aw_sources.linked_reference_from_audit(
                    audit(edb=edb,condition='Service',sha=sha),
                    'p',state='ULS',current_edb=str(edb))
            with self.assertRaisesRegex(ValueError,'thickness'):
                aw_sources.linked_reference_from_audit(
                    audit(edb=edb,thickness='MISMATCH',sha=sha),
                    'p',state='ULS',current_edb=str(edb))

    def test_matching_name_without_source_file_and_digest_never_auto_qualifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            edb=Path(tmp)/"same_name.EDB"
            edb.write_bytes(b"changed model")
            missing_hash=aw_sources.linked_reference_from_audit(
                audit(edb=edb),'p.json',state='ULS',current_edb=str(edb))
            self.assertEqual(missing_hash['source_identity'],
                             'DIFFERENT_EDB_RESEARCH_REFERENCE_ONLY')
            wrong_hash=aw_sources.linked_reference_from_audit(
                audit(edb=edb,sha='0'*64),'p.json',state='ULS',
                current_edb=str(edb))
            self.assertEqual(wrong_hash['source_identity'],
                             'DIFFERENT_EDB_RESEARCH_REFERENCE_ONLY')
            edb.unlink()
            self.assertEqual(aw_sources.edb_identity(str(edb),
                             audit(edb=edb,sha='0'*64)),
                             'CURRENT_EDB_NOT_ACCESSIBLE')

    def test_resolve_prefers_same_edb_excel_method_then_geometry(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            export,results=Path(tmp)/'export',Path(tmp)/'results'
            export.mkdir();results.mkdir()
            edb=Path(tmp)/'ULTIMATE LOAD - Copy.EDB'
            edb.write_bytes(b"verified ETABS EDB bytes")
            sha=hashlib.sha256(edb.read_bytes()).hexdigest()
            snapshot=dict(aw_candidate_m2={'X':1.9306371,'Y':None},
                          aw_evidence={
                              'X':{'status':'PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC'},
                              'Y':{'status':'NO_CONTINUOUS_PIER_IN_THIS_AXIS'}},
                          assembled_model_sha256='abc')
            with mock.patch('components.inputs.project_workbooks.analysis_output_folder',
                            return_value=results), \
                 mock.patch('components.inputs.project_workbooks._source_edb_path',
                            return_value=str(edb)), \
                 mock.patch('components.inputs.opensees_nbc_sync._source_snapshot',
                            return_value=snapshot):
                out=aw_sources.resolve_aw(export,'ULS')
                self.assertEqual(out['method'],'OPEN_SEES_GEOMETRY_CANDIDATE')
                self.assertAlmostEqual(out['X'],1.9306371)
                self.assertIsNone(out['Y'])
                self.assertIn('not NBC accepted',out['labels']['X'])
                (results/'a_ETABS_LINKED_ESM.provenance.json').write_text(
                    json.dumps(audit(edb=Path(tmp)/'SERVICE LOAD.EDB',sha='f'*64)))
                self.assertEqual(aw_sources.resolve_aw(export,'ULS')['method'],
                                 'OPEN_SEES_GEOMETRY_CANDIDATE')
                # A same-path record lacking hash also remains diagnostic.
                same=results/'b_ETABS_LINKED_ESM.provenance.json'
                same.write_text(json.dumps(audit(edb=edb)))
                self.assertEqual(aw_sources.resolve_aw(export,'ULS')['method'],
                                 'OPEN_SEES_GEOMETRY_CANDIDATE')
                same.write_text(json.dumps(audit(edb=edb,sha=sha)))
                out=aw_sources.resolve_aw(export,'Both')
                self.assertEqual(out['method'],'ORIGINAL_EXCEL_METHOD_ETABS_LINKED')
                self.assertAlmostEqual(out['X'],1.9582936)
                self.assertAlmostEqual(out['Y'],2.2030803)


    def test_explicitly_registered_provenance_takes_priority_over_newer_file(self):
        import hashlib
        import os
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);results=root/'results';results.mkdir()
            edb=root/'current.EDB';edb.write_bytes(b"source edb")
            sha=hashlib.sha256(edb.read_bytes()).hexdigest()
            older=results/'old_ETABS_LINKED_ESM.provenance.json'
            newer=results/'new_ETABS_LINKED_ESM.provenance.json'
            old=audit(edb=edb,sha=sha);old['coefficients']['X']['Aw_m2']=4.8
            fresh=audit(edb=edb,sha=sha);fresh['coefficients']['X']['Aw_m2']=9.6
            older.write_text(json.dumps(old),encoding="utf-8")
            newer.write_text(json.dumps(fresh),encoding="utf-8")
            os.utime(older,(1_600_000_000,1_600_000_000))
            os.utime(newer,(1_700_000_000,1_700_000_000))
            with mock.patch('components.inputs.project_workbooks.analysis_output_folder',
                            return_value=results), \
                 mock.patch('components.inputs.project_workbooks._source_edb_path',
                            return_value=str(edb)), \
                 mock.patch('components.inputs.project_workbooks.registered_project_source',
                            return_value=str(older)):
                ref,reason=aw_sources.latest_linked_reference(root,'ULS')
            self.assertEqual(reason,'OK')
            self.assertEqual(ref['values']['awx'],4.8)
            self.assertEqual(Path(ref['provenance_json']),older)



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

"""Stage 02 Model: source-only area inventory and mesh file identity tests.

No real ETABS files, solver or user source workbooks are imported.
"""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import unittest
from openpyxl import load_workbook
from components.sections.area_elements import (export_area_integration_inventory, default_area_integration_script_path, model_area_directory)


class AreaInventoryTests(unittest.TestCase):
    def test_excel_and_json_inventory_from_small_source(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            topology=root/'topo.json'
            topology.write_text(json.dumps({
                'node_map':[
                    {'opensees_node_tag':i,'coordinates_m':xy}
                    for i,xy in enumerate([(0,0,3),(2,0,3),(2,2,3),(0,2,3)],1)
                ],
                'elements':[{'dimension':'area_polygon','category':'FLOOR','etabs_object':'F01',
                             'opensees_element_tag':10001,'node_tags':[1,2,3,4]}]
            }),encoding='utf-8')
            assignments=root/'assignments.csv'
            assignments.write_text('etabs_area_object,assigned_property\nF01,SLAB150\n',encoding='utf-8')
            config=root/'config.json'
            config.write_text(json.dumps({'source_reviewed_by_user':False}),encoding='utf-8')
            workbook,manifest=export_area_integration_inventory(
                topology_json=topology,area_assignment_csv=assignments,
                config_json=config,output_dir=root)
            self.assertIn('/02_MODEL/AREA_INTEGRATION/excel/',workbook.as_posix())
            self.assertTrue(workbook.exists())
            m=json.loads(manifest.read_text(encoding='utf-8'))
            self.assertEqual(m['source_quad_counts']['FLOOR'],1)
            self.assertEqual(m['sha256']['topology'],hashlib.sha256(topology.read_bytes()).hexdigest())
            self.assertFalse(m['analysis_ready'])
            archived=root/'02_MODEL'/'AREA_INTEGRATION'/'07_EXPORT_ZIP'/(workbook.stem+'.zip')
            self.assertTrue(archived.is_file(), 'Area inventory must publish a real ZIP')
            with ZipFile(archived) as archive:
                self.assertIsNone(archive.testzip())
                self.assertIn('00_INPUT_SOURCE/OpenSees_Element_Connectivity.json',archive.namelist())
                self.assertIn('02_MODEL/AREA_INTEGRATION/excel/'+workbook.name,archive.namelist())
                zip_manifest=json.loads(archive.read('EVIDENCE_MANIFEST.json'))
                self.assertEqual(zip_manifest['engineering_acceptance'],'NOT_VERIFIED')
            wb=load_workbook(workbook,read_only=True,data_only=False)
            self.assertEqual(wb['Area objects']['D2'].value,'SLAB150')
            self.assertEqual(wb['Area objects']['F2'].value,4.0)
            self.assertIn('NOT VERIFIED',wb['Summary']['B3'].value)
            wb.close()

    def test_repeated_selection_of_model_stage_never_creates_nested_stage(self):
        with TemporaryDirectory() as td:
            root=Path(td).resolve()
            expected=root/'02_MODEL'/'AREA_INTEGRATION'
            for selected in (root,root/'02_MODEL', expected,
                             root/'02_MODEL'/'07_EXPORT_ZIP',
                             expected/'07_EXPORT_ZIP'):
                self.assertEqual(model_area_directory(selected),expected)
                self.assertEqual(default_area_integration_script_path(selected).parent,
                                 expected/'PYTHON')
            self.assertFalse(expected.exists(), 'Resolver must be read-only')

    def test_invalid_geometry_is_not_auto_approved(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            (root/'topo.json').write_text(json.dumps({'node_map':[
                {'opensees_node_tag':i,'coordinates_m':[0,0,0]} for i in range(1,5)],
                'elements':[{'dimension':'area_polygon','category':'FLOOR','etabs_object':'F1',
                             'node_tags':[1,2,3,4]}]}),encoding='utf-8')
            (root/'a.csv').write_text('etabs_area_object,assigned_property\nF1,SLAB\n')
            (root/'c.json').write_text('{}')
            _,manifest=export_area_integration_inventory(topology_json=root/'topo.json',
                area_assignment_csv=root/'a.csv',config_json=root/'c.json',output_dir=root)
            self.assertEqual(len(json.loads(manifest.read_text())['geometry_errors']),1)

    def test_area_python_default_is_inside_selected_export(self):
        with TemporaryDirectory() as td:
            root=Path(td).resolve()
            target=default_area_integration_script_path(root)
            self.assertEqual(target,root/"02_MODEL"/"AREA_INTEGRATION"/
                             "PYTHON"/"OpenSees_Area_Integration_Call_V116.py")
            self.assertFalse(target.exists())
            self.assertFalse((root/"02_MODEL").exists())

    def test_04_08_16_names_and_hash_guard_present(self):
        # After the established module split, mesh-case preparation belongs
        # to mesh_cases.py; load_path_formulas.py owns the formula exporter.
        base=Path(__file__).parents[1]/'components/gravity'
        mesh=(base/'mesh_cases.py').read_text(encoding='utf-8')
        formula=(base/'load_path_formulas.py').read_text(encoding='utf-8')
        self.assertIn('MESH_SIZES = (4, 8, 16)',mesh)
        self.assertIn('PREPARED_CONFIGS',mesh)
        self.assertIn('for n in MESH_SIZES',mesh)
        for token in ('MESH_{n:02d}','config_sha256'):
            self.assertIn(token,mesh)
            self.assertIn(token,formula)
        self.assertIn('Slab_Load_Path_MESH_',formula)


if __name__=='__main__':
    unittest.main()

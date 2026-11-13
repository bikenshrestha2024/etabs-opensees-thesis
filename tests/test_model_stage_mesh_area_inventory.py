"""Stage 02 Model: source-only area inventory and mesh file identity tests.

No real ETABS files, solver or user source workbooks are imported.
"""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from openpyxl import load_workbook
from components.sections.area_elements import export_area_integration_inventory


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
            wb=load_workbook(workbook,read_only=True,data_only=False)
            self.assertEqual(wb['Area objects']['D2'].value,'SLAB150')
            self.assertEqual(wb['Area objects']['F2'].value,4.0)
            self.assertIn('NOT VERIFIED',wb['Summary']['B3'].value)
            wb.close()

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

    def test_04_08_16_names_and_hash_guard_present(self):
        src=(Path(__file__).parents[1]/'components/gravity/load_path_formulas.py').read_text()
        for token in ('MESH_{n:02d}','config_sha256','Slab_Load_Path_MESH_',
                      'PREPARED_CONFIGS','for n in (4,8,16)'):
            self.assertIn(token,src)


if __name__=='__main__':
    unittest.main()

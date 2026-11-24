"""Evidence ZIP for actual area-element instantiation is distinct from source inventory.

Synthetic shell panels only. No ETABS API, FSAM constitutive material or native
OpenSees gravity/analysis is exercised by these tests.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from zipfile import ZipFile

from components.sections.area_elements import (
    instantiate_area_elements, package_area_instantiation_audit,
    inspect_instantiated_area_evidence)


class FakeOps:
    def __init__(self):
        self.elements=[]
        self.sections=[]
    def getEleTags(self):
        return []
    def section(self,*args):
        self.sections.append(args)
    def element(self,*args):
        self.elements.append(args)


def inputs(root):
    topology=root/'OpenSees_Element_Connectivity.json'
    topology.write_text(json.dumps({
        'node_map':[{'opensees_node_tag':i,'coordinates_m':xyz} for i,xyz in enumerate(
            [(0,0,3),(2,0,3),(2,2,3),(0,2,3)],1)],
        'elements':[{'dimension':'area_polygon','category':'FLOOR','etabs_object':'F01',
                     'opensees_element_tag':10001,'node_tags':[1,2,3,4]}]
    }),encoding='utf-8')
    audit=root/'OpenSees_Area_Section_Assignment_Audit.csv'
    audit.write_text('etabs_area_object,assigned_property\nF01,SLAB150\n')
    config=root/'OpenSees_Area_Model_Config_V116.json'
    config.write_text(json.dumps({'coordinate_units':'m','force_units':'kN',
        'source_reviewed_by_user':True,
        'audit_output_json':'OpenSees_Area_Element_Integration_Audit_V116.json',
        'floor_sections':{'SLAB150':{'section_tag':920,'E_kN_m2':30000000.,
                      'poisson_ratio':.2,'thickness_m':.15}}}))
    return topology,audit,config


class InstantiatedAreaEvidenceTests(TestCase):
    def test_missing_saved_area_report_is_explained_not_fabricated(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            topology,audit,config=inputs(root)
            cfg=json.loads(config.read_text())
            cfg['source_reviewed_by_user']=False
            cfg['opensees_wall_sections']={
                'RC_WALL_600':{'fsam_material_tag':None}}
            config.write_text(json.dumps(cfg),encoding='utf-8')
            original=config.read_bytes()
            info=inspect_instantiated_area_evidence(config_json=config)
            self.assertEqual(info['status'],'SOURCE_ONLY_NO_INSTANTIATION_REPORT')
            self.assertFalse(info['saved_report_present'])
            self.assertFalse(info['analysis_ready'])
            self.assertFalse(info['source_reviewed_by_user'])
            self.assertEqual(info['missing_fsam_targets'],['RC_WALL_600'])
            self.assertIn('OpenSees_Area_Element_Integration_Audit_V116.json',
                          info['report_path'])
            self.assertIn('not automatically',info['guidance'].lower())
            self.assertEqual(config.read_bytes(),original)
            self.assertEqual(list(root.glob('*.zip')),[])
            self.assertFalse((root/cfg['audit_output_json']).exists())

    def test_saved_report_presence_is_not_approved_or_packaged_by_preflight(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            topology,audit,config=inputs(root)
            before=inspect_instantiated_area_evidence(config_json=config)
            self.assertFalse(before['saved_report_present'])
            report=root/'OpenSees_Area_Element_Integration_Audit_V116.json'
            report.write_text(json.dumps({'element_audit':[{'tag':1}],
                'floor_shell_count':1,'nonlinear_wall_panel_count':0}),
                encoding='utf-8')
            after=inspect_instantiated_area_evidence(config_json=config)
            self.assertEqual(after['status'],'SAVED_REPORT_PRESENT_NOT_VALIDATED')
            self.assertTrue(after['saved_report_present'])
            self.assertFalse(after['analysis_ready'])
            self.assertFalse(after['engineering_accepted'])
            with self.assertRaises(ValueError):
                package_area_instantiation_audit(
                    topology_json=topology,area_assignment_csv=audit,
                    config_json=config,output_dir=root)
            self.assertFalse((root/'02_MODEL').exists())

    def test_instantiation_preflight_rejects_parent_relative_output(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            _,_,config=inputs(root)
            cfg=json.loads(config.read_text())
            cfg['audit_output_json']='../OTHER/AUDIT.json'
            config.write_text(json.dumps(cfg))
            with self.assertRaises(ValueError):
                inspect_instantiated_area_evidence(config_json=config)

    def test_actual_element_report_is_source_local_and_zip_is_nonempty(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            topology,audit,config=inputs(root)
            ops=FakeOps()
            result=instantiate_area_elements(ops,topology_json=topology,
                area_assignment_csv=audit,config_json=config,
                floor_shells=True,nonlinear_wall_panels=False)
            self.assertEqual(result['floor_shell_count'],1)
            self.assertEqual(len(ops.elements),1)
            report=root/'OpenSees_Area_Element_Integration_Audit_V116.json'
            self.assertTrue(report.is_file(), 'Report must belong to selected source, not cwd')
            archive=package_area_instantiation_audit(topology_json=topology,
                area_assignment_csv=audit,config_json=config,output_dir=root)
            self.assertEqual(archive.parent,root/'02_MODEL'/'AREA_INTEGRATION'/'07_EXPORT_ZIP')
            with ZipFile(archive) as zipped:
                self.assertIsNone(zipped.testzip())
                self.assertIn('02_MODEL/AREA_INTEGRATION/INSTALLED_ELEMENTS/'+report.name,zipped.namelist())
                manifest=json.loads(zipped.read('EVIDENCE_MANIFEST.json'))
                self.assertGreaterEqual(manifest['file_count'],4)
                self.assertEqual(manifest['engineering_acceptance'],'NOT_VERIFIED')
                self.assertIn(b'"floor_shell_count": 1',zipped.read(
                    '02_MODEL/AREA_INTEGRATION/INSTALLED_ELEMENTS/'+report.name))
            self.assertFalse(result['analysis_ready'])

    def test_missing_or_noninstantiated_element_report_is_not_packaged(self):
        with TemporaryDirectory() as td:
            root=Path(td);topology,audit,config=inputs(root)
            def export():
                return package_area_instantiation_audit(topology_json=topology,
                    area_assignment_csv=audit,config_json=config,output_dir=root)
            with self.assertRaises(FileNotFoundError):
                export()
            (root/'OpenSees_Area_Element_Integration_Audit_V116.json').write_text(
                json.dumps({'source_topology':str(topology),'source_area_assignment_audit':str(audit),
                            'floor_shell_count':0,'nonlinear_wall_panel_count':0,'element_audit':[]}))
            with self.assertRaises(ValueError):
                export()

    def test_wrong_source_and_inconsistent_element_count_rejected(self):
        with TemporaryDirectory() as td:
            root=Path(td);topology,audit,config=inputs(root)
            report=root/'OpenSees_Area_Element_Integration_Audit_V116.json'
            record={'source_topology':str(root/'OTHER.json'),'source_area_assignment_audit':str(audit),
                    'floor_shell_count':1,'nonlinear_wall_panel_count':0,
                    'element_audit':[{'tag':10001,'category':'FLOOR'}]}
            report.write_text(json.dumps(record))
            def export():
                return package_area_instantiation_audit(topology_json=topology,
                    area_assignment_csv=audit,config_json=config,output_dir=root)
            with self.assertRaises(ValueError):
                export()
            record['source_topology']=str(topology)
            record['floor_shell_count']=2
            report.write_text(json.dumps(record))
            with self.assertRaises(ValueError):
                export()


if __name__=='__main__':
    import unittest
    unittest.main()

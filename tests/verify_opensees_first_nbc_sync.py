"""Regression for OpenSees-first NBC105 sync (synthetic data only).

Protects source/limit state, wall opening slice interpretation, workbook
preservation, no ETABS write or analysis, and tagged review status.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from openpyxl import Workbook,load_workbook

from components.inputs import opensees_nbc_sync as sync


def model_files(root):
    (root/'OpenSees_Complete_Model_Data_V118.json').write_text(json.dumps({
        'base_z_m':0,'diaphragms':[{'master_xyz':[0,0,3]},{'master_xyz':[0,0,90]}]}))
    (root/'NBC105_ESM_Story_Weights_Assembled_V118.csv').write_text(
        'story_number,story_name,height_m,dead_load_kN,storage_live_load_kN,other_live_load_kN\n'
        '1,Story1,3,100,0,0\n2,Story2,90,100,0,0\n')


def geometry(uniform):
    a={'X':2.1,'Y':1.7}
    row={'z_bottom_m':0.,'z_top_m':3.,'aw_x_m2':2.1,
         'aw_y_m2':1.7,'x_segment_count':1,'y_segment_count':1,'segments':[
             dict(axis='X',plane_m=0.,start_m=0.,end_m=3.,
                  thickness_m=.3,wall_length_m=3.,
                  Aw_contribution_m2=2.1)]}
    if not uniform:
        a=None
        row2=dict(row,z_bottom_m=1.5,aw_x_m2=1.4,z_top_m=3.,
                  segments=[dict(axis='X',plane_m=0.,start_m=0.,end_m=2.,
                                 thickness_m=.3,wall_length_m=2.,
                                 Aw_contribution_m2=1.4)])
        row=dict(row,z_top_m=1.5)
        return {'uniform_footprint':False,'rows':[row,row2]},a
    return {'uniform_footprint':True,'rows':[row]},a


class FakeSap:
    def __init__(self,edb):self.edb=edb;self.present=3;self.calls=[]
    def GetModelFilename(self):return str(self.edb)
    def GetPresentUnits(self):return self.present
    def SetPresentUnits(self,v):self.calls.append(('units',v));self.present=v;return 0
    @property
    def AreaObj(self):return self
    @property
    def PointObj(self):return self
    @property
    def PropArea(self):return self
    def GetNameList(self):return 2,['A','B'],0
    def GetProperty(self,name):return 'WALL_300',0
    def GetWall(self,prop):return 1,1,'M30',.3,0,'','','',0
    def GetPoints(self,name):
        return 4, ['a1','a2','a3','a4'] if name=='A' else ['b1','b2','b3','b4'],0
    def GetCoordCartesian(self,p):
        points={'a1':(0,0,0),'a2':(3,0,0),'a3':(3,0,3),'a4':(0,0,3),
                'b1':(4,0,0),'b2':(4,3,0),'b3':(4,3,3),'b4':(4,0,3)}
        return (*points[p],0)


class SyncTests(unittest.TestCase):
    def with_snapshot(self,root,uniform):
        model_files(root)
        profile,areas=geometry(uniform)
        values={'soil':'C','Z':.35,'I':1.,'period_factor':1.25,
                'wall_aw_profile':profile,'rayleigh_tx':3.1,'rayleigh_ty':2.8}
        if areas:
            values.update({'geometry_aw_x':areas['X'],'geometry_aw_y':areas['Y'],
                           'awx':areas['X'],'awy':areas['Y']})
        else:
            values.update({'awx':1.9582936,'awy':2.2030803})
        return {'values':values,'notes':['Synthetic mocked source'],
                'audit':[dict(field='awx',source='mocked',cell='B14')]}

    def test_uniform_opensees_candidate_is_primary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=self.with_snapshot(root,True)
            with patch.object(sync,'require_source_state'),patch.object(sync,'import_project_inputs',return_value=data),patch.object(sync,'_source_edb_path',return_value='D:/Models/ULTIMATE MODEL.EDB'):
                report=sync._source_snapshot(root,'ULS')
            self.assertEqual(report['aw_candidate_m2'],{'X':2.1,'Y':1.7})
            self.assertEqual(report['rayleigh_s']['X'],3.1)
            self.assertEqual(len(report['assembled_model_sha256']),64)

    def test_nonuniform_opening_fills_only_traceable_provisional_pier_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=self.with_snapshot(root,False)
            with patch.object(sync,'require_source_state'),patch.object(sync,'import_project_inputs',return_value=data),patch.object(sync,'_source_edb_path',return_value='D:/Models/ULTIMATE MODEL.EDB'):
                report=sync._source_snapshot(root,'ULS')
            self.assertIsNotNone(report['aw_candidate_m2']['X'])
            self.assertEqual(report['aw_evidence']['X']['status'],
                             'PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC')
            self.assertFalse(report['aw_evidence']['X']['code_accepted'])
            self.assertLess(report['aw_candidate_m2']['X'],2.1)
            self.assertEqual(len(report['continuous_pier_diagnostic']['continuous_segments']),1)

    def test_excel_template_preserved_new_sheet_and_new_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=self.with_snapshot(root,True)
            with patch.object(sync,'require_source_state'),patch.object(sync,'import_project_inputs',return_value=data),patch.object(sync,'_source_edb_path',return_value='D:/Models/ULTIMATE MODEL.EDB'):
                report=sync._source_snapshot(root,'ULS')
            template=root/'original.xlsx'
            wb=Workbook();ws=wb.active;ws.title='NBC Calculator'
            ws['B15']=1.25;ws['B14']='ORIGINAL_FORMULA';
            wb.save(template)
            json_file,xlsx_file=sync.export_sync_report(report,root/'audit',template)
            original=load_workbook(template)
            copy=load_workbook(xlsx_file)
            self.assertEqual(original['NBC Calculator']['B14'].value,'ORIGINAL_FORMULA')
            self.assertEqual(copy['NBC Calculator']['B14'].value,'ORIGINAL_FORMULA')
            self.assertIn('OpenSees Source Sync',copy.sheetnames)
            self.assertEqual(copy['OpenSees Source Sync']['B9'].value,2.1)
            self.assertTrue(json_file.is_file())
            with self.assertRaises(FileExistsError):
                sync.export_sync_report(report,root/'audit',template)

    def test_readonly_etabs_fallback_and_restored_units(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);model_files(root)
            edb=root/'ULTIMATE MODEL.EDB';edb.write_bytes(b'only for path verification')
            sap=FakeSap(edb)
            with patch.object(sync,'_source_edb_path',return_value=str(edb)):
                result=sync.read_etabs_wall_profile(root,sap=sap)
            self.assertEqual(result['source'],'READ_ONLY_ETABS_OAPI')
            self.assertEqual(sap.present,3)
            self.assertTrue(result['profile']['uniform_footprint'])
            self.assertEqual(sap.calls,[('units',6),('units',3)])
            self.assertFalse(any('Save' in str(x) for x in sap.calls))

    def test_other_edb_rejected_before_geometry_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);model_files(root)
            edb=root/'SERVICE.EDB';edb.write_bytes(b'other')
            sap=FakeSap(edb)
            with patch.object(sync,'_source_edb_path',return_value=str(root/'ULTIMATE.EDB')):
                with self.assertRaisesRegex(ValueError,'differs'):
                    sync.read_etabs_wall_profile(root,sap=sap)
            self.assertEqual(sap.calls,[])


if __name__=='__main__':
    unittest.main(verbosity=2)

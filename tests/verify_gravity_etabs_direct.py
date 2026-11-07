"""Synthetic API and result comparison tests. No ETABS binary is required."""
import unittest
from components.validation import gravity_etabs_direct as g

class GravityDirectAPITests(unittest.TestCase):
    def test_exact_combo_contract(self):
        class Combo:
            def GetTypeCombo(self,name):return (0,0)
            def GetCaseList(self,name):return (2,[0,0],['Dead','Live'],[1.,1.],0)
        class Sap:RespCombo=Combo()
        cases=g._combo(Sap(),'1. DL + LL')
        self.assertEqual([c['name'] for c in cases],['Dead','Live'])
        self.assertTrue(all(c['factor']==1 for c in cases))
    def test_wrong_live_multiplier_fails(self):
        class Combo:
            def GetTypeCombo(self,name):return (0,0)
            def GetCaseList(self,name):return (2,[0,0],['Dead','Live'],[1.,.3],0)
        class Sap:RespCombo=Combo()
        with self.assertRaisesRegex(ValueError,'factor'):
            g._combo(Sap(),'wrong')
    def test_comparison_needs_complete_full_gravity(self):
        e={'case':'1. DL + LL','summary':{'base_reaction_FZ_kN':319000.0},
           'matched_edb_identity':True}
        o={'ok':True,'gravity_profile':'GRAVITY_1.0D_1.0L',
           'report':{'applied_vertical_load_kN':320047.789,
                     'support_vertical_reaction_kN':320047.789}}
        v=g.compare_existing(e,o)
        self.assertAlmostEqual(v['difference_kN'],-1047.789,3)
        self.assertAlmostEqual(v['percent_difference'],1047.789/320047.789*100,7)
        o['gravity_profile']='AS_CONFIGURED'
        with self.assertRaisesRegex(ValueError,'full 1.0D'):
            g.compare_existing(e,o)
    def test_alternate_edb_requires_explicit_permission(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        with TemporaryDirectory() as d:
            source=Path(d)/'Original.EDB';source.write_bytes(b'original')
            alt=Path(d)/'Gravity.EDB';alt.write_bytes(b'copy')
            class Sap:
                def GetModelFilename(self):return str(alt)
            with self.assertRaisesRegex(ValueError,'diagnostic alternate-EDB mode'):
                g.extract_from_sap(Sap(),source_edb=source)
            # Guard is bypassed ONLY in explicit diagnostic mode; extractor
            # must continue to inspect real case/units rather than fabricate data.
            with patch.object(g,'_snapshot',side_effect=RuntimeError('session inspected')):
                with self.assertRaisesRegex(RuntimeError,'session inspected'):
                    g.extract_from_sap(Sap(),source_edb=source,allow_alternate_edb=True)

    def test_gui_protects_alternate_mode(self):
        from pathlib import Path
        src=(Path(__file__).resolve().parents[1]/
             'components/gravity/gui_and_reports.py').read_text('utf-8')
        self.assertIn('self.allow_alternate_edb',src)
        self.assertIn('messagebox.askyesno',src)

    def test_owned_etabs_new_instance_is_closed_on_success_and_failure(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        with TemporaryDirectory() as temp:
            edb=Path(temp)/'Gravity.EDB'
            edb.write_bytes(b'test model')
            events=[]
            class File:
                def OpenFile(self,path):
                    events.append(('open',path))
                    return 0
            class Sap:
                def GetModelFilename(self):return str(edb)
            Sap.File=File()
            class Etabs:
                SapModel=Sap()
                def ApplicationStart(self):events.append(('start',));return 0
                def ApplicationExit(self,save):events.append(('exit',save));return 0
            class Helper:
                def CreateObjectProgID(self,name):
                    events.append(('create',name));return Etabs()
            class Client:
                def CreateObject(self,name):
                    self.last=name
                    return Helper()
            import sys
            from types import ModuleType
            fake=ModuleType('comtypes')
            fake.client=Client()
            with patch.dict(sys.modules,{'comtypes':fake,'comtypes.client':fake.client}):
                instance=g._new_etabs_instance(edb)
                self.assertIsInstance(instance,Etabs)
                g._release_owned_instance(instance)
                self.assertEqual(events[-1],('exit',False))
            events.clear()
            class BadFile:
                def OpenFile(self,path):return 12
            Sap.File=BadFile()
            with patch.dict(sys.modules,{'comtypes':fake,'comtypes.client':fake.client}):
                with self.assertRaisesRegex(RuntimeError,'OpenFile'):
                    g._new_etabs_instance(edb)
                self.assertEqual(events[-1],('exit',False))

    def test_default_gui_uses_owned_process(self):
        from pathlib import Path
        gui=(Path(__file__).resolve().parents[1]/
             'components/gravity/gui_and_reports.py').read_text('utf-8')
        self.assertIn('self.launch_etabs_for_gravity = tk.BooleanVar(value=True)',gui)
        self.assertIn('launch_new_etabs=bool(self.launch_etabs_for_gravity.get())',gui)

    def test_nonfinished_api_status_does_not_preempt_actual_base_reaction(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        with TemporaryDirectory() as d:
            edb=Path(d)/'Gravity.EDB';edb.write_bytes(b'model')
            class Sap:
                def GetModelFilename(self):return str(edb)
                def SetPresentUnits(self,unit):return 0
            class Setup:
                def DeselectAllCasesAndCombosForOutput(self):return 0
                def SetComboSelectedForOutput(self,case):return 0
            sap=Sap()
            class Results:
                Setup=Setup() if False else None
            # Mock only the external CSI API; retain real decision logic.
            class Result:
                Setup=type('SetupMock',(),{
                    'DeselectAllCasesAndCombosForOutput':lambda self:0,
                    'SetComboSelectedForOutput':lambda self,x:0})()
            sap.Results=Result()
            events=[]
            initial={'units':6,'cases':[],'combos':[('1. DL + LL',False)]}
            with (patch.object(g,'_snapshot',return_value=initial), 
                 patch.object(g,'_restore',return_value=None), 
                 patch.object(g,'_combo',return_value=[
                     {'name':'Dead','factor':1.0},{'name':'Live','factor':1.0}]), 
                 patch.object(g,'_get_case_status',return_value={'Dead':1,'Live':1}), 
                 patch.object(g,'_base',side_effect=RuntimeError('No saved BaseReact rows'))):
                with self.assertRaisesRegex(RuntimeError,'no usable BaseReact'):
                    g.extract_from_sap(sap,source_edb=edb,
                        log=lambda stage,message,**kwargs:events.append(stage))
            self.assertIn('ETABS_CASE_STATUS',events)
            self.assertIn('ETABS_RESULTS',events)

    def test_auto_analysis_requires_source_copy_and_preserves_source_hash(self):
        import json
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        from hashlib import sha256
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            source=root/'Original.EDB'
            source.write_bytes(b'original source model')
            before=sha256(source.read_bytes()).hexdigest()
            gravity=root/'Gravity_Result_V110.json'
            gravity.write_text(json.dumps({'ok':True,
                'gravity_profile':'GRAVITY_1.0D_1.0L',
                'report':{'applied_vertical_load_kN':100.,
                          'support_vertical_reaction_kN':100.}}))
            calls=[]
            class Analyze:
                def RunAnalysis(self):
                    calls.append('run')
                    return 0
            class Sap:
                pass
            Sap.Analyze=Analyze()
            class App:
                pass
            App.SapModel=Sap()
            def fake_open(edb_path,exe_path=None):
                calls.append(('open',Path(edb_path)))
                return App()
            def fake_extract(sap,case,source_edb,allow_alternate_edb,log):
                calls.append(('extract',Path(source_edb)))
                if calls.count('run')==0:
                    raise RuntimeError('ETABS gravity combination has no usable BaseReact results')
                return {'summary':{'base_reaction_FZ_kN':101.},
                        'case':case,'model_identity_status':'SAME_EDB_PATH',
                        'joint_reactions':[],'base_reactions':[],
                        'support_displacements':[],
                        'source_case_base_reactions':[]}
            with (patch('components.inputs.project_workbooks._source_edb_path',
                       return_value=str(source)),
                 patch.object(g,'_new_etabs_instance',side_effect=fake_open),
                 patch.object(g,'_release_owned_instance',side_effect=lambda app:calls.append('closed')),
                 patch.object(g,'extract_from_sap',side_effect=fake_extract),
                 patch.object(g,'export_direct',return_value=root/'out')):
                comp,_=g.connect_and_compare(root,gravity,output_dir=root/'out',
                            launch_new_etabs=True,run_if_missing=True)
            self.assertEqual(before,sha256(source.read_bytes()).hexdigest())
            self.assertEqual(calls.count('run'),1)
            self.assertEqual(calls[-1],'closed')
            self.assertNotEqual(calls[0][1],source)
            self.assertEqual(comp['model_identity_status'],'WORKING_COPY_ANALYZED_FROM_SOURCE_EDB')
            self.assertFalse(comp['matched_edb_identity'])
            self.assertTrue((root/'out'/'ETABS_Gravity_Extraction.log').is_file())

    def test_gravity_gui_run_missing_is_consent_gated(self):
        from pathlib import Path
        src=(Path(__file__).resolve().parents[1]/
            'components/gravity/gui_and_reports.py').read_text('utf-8')
        self.assertIn('run_if_missing=bool(self.run_missing_etabs_results.get())',src)
        self.assertIn('messagebox.askyesno(',src)

    def test_exact_base_row_no_envelope(self):
        rows=[dict(LoadCase='X',StepType='',StepNum=0,FZ=40)]
        self.assertEqual(g._exact_one(rows,'X')['FZ'],40)
        with self.assertRaises(ValueError):
            g._exact_one(rows+rows,'X')
    def test_gravity_gui_has_direct_button(self):
        from pathlib import Path
        import ast
        src=(Path(__file__).resolve().parents[1]/
             'components/gravity/gui_and_reports.py').read_text('utf-8')
        ast.parse(src)
        self.assertIn('Extract ETABS + compare gravity',src)
        self.assertIn('connect_and_compare',src)
        self.assertIn('1. DL + LL',src)
if __name__=='__main__':unittest.main()

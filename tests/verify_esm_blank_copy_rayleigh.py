"""ESM blank-form regression: copied EDB provenance and Both Rayleigh states.

Synthetic only: no ETABS/Opensees native solver. Never infer that renamed
models are physically equivalent without two byte-identical source files.
"""
import json
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from openpyxl import Workbook
from components.inputs.project_workbooks import (
    _same_edb_file_content,source_workbooks,import_project_inputs,
)
from components.equivalent_static.calculation_and_gui import ESMGui


class Var:
    def __init__(self,v):self.v=v
    def get(self):return self.v
    def set(self,v):self.v=v


class ESMBlankRegression(unittest.TestCase):
    def files(self,folder,same=True):
        original=folder/'ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS, OUTRIGGER CAP TRUSS.EDB'
        copy=folder/'ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS, OUTRIGGER CAP TRUSS - Copy.EDB'
        original.write_bytes(b'confirmed model bytes')
        copy.write_bytes(original.read_bytes() if same else b'DIFFERENT model bytes')
        (folder/'OpenSees_Element_Connectivity.json').write_text(
            json.dumps({'source_edb':str(copy)}),encoding='utf-8')
        wb=Workbook();ws=wb.active;ws.title='SCALING SUMMARY'
        ws['B4']=str(original);ws['B14']=3.6779;ws['B15']=0.8019
        ws['C14']=1.1;ws['C15']=2.2
        file=folder/'ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS, OUTRIGGER CAP TRUSS_NBC105_RS_Scaling.xlsx'
        wb.save(file)
        return original,copy,file

    def test_true_renamed_copy_can_restore_aw_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);original,copy,book=self.files(folder,same=True)
            self.assertTrue(_same_edb_file_content(original,copy))
            self.assertEqual(source_workbooks(folder,folder,'ULS')[1],book)
            imported=import_project_inputs(folder,folder,'ULS')
            self.assertAlmostEqual(imported['values']['awx'],3.6779)
            self.assertAlmostEqual(imported['values']['awy'],0.8019)

    def test_different_model_named_copy_remains_blocked_with_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);original,copy,book=self.files(folder,same=False)
            self.assertFalse(_same_edb_file_content(original,copy))
            self.assertIsNone(source_workbooks(folder,folder,'ULS')[1])
            imported=import_project_inputs(folder,folder,'ULS')
            self.assertNotIn('awx',imported['values'])
            self.assertTrue(any('NO verified equality' in s for s in imported['notes']))

    def test_absent_original_file_never_trusts_copy_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);original,copy,book=self.files(folder,same=True)
            original.unlink()
            self.assertIsNone(source_workbooks(folder,folder,'ULS')[1])

    def test_both_runs_both_states_without_reusing_uls(self):
        gui=object.__new__(ESMGui)
        gui.awx=Var('3.6779');gui.awy=Var('0.8019')
        gui.state=Var('Both')
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            gui.outdir=Var(str(folder));gui.export_dir=folder
            (folder/'OpenSees_Complete_Model_Data_V118.json').write_text('{}')
            (folder/'NBC105_ESM_Story_Weights_Assembled_V118.csv').write_text(
                'story_number,story_name,height_m,dead_load_kN,storage_live_load_kN,other_live_load_kN\\n'
                '1,Story1,3,100,0,0\\n')
            gui.python_exe=Var('python')
            gui.status=Var('')
            gui.root=types.SimpleNamespace(after=lambda _ms,func:func())
            invoked=[]
            def run(command,**kw):
                invoked.append(command[-1])
                return types.SimpleNamespace(returncode=0,stdout='ok',stderr='')
            root=Path(__import__('components.equivalent_static.calculation_and_gui',
                                  fromlist=['HERE']).HERE)
            # Do not execute any native solver; mock process and thread start.
            with patch('components.equivalent_static.calculation_and_gui.subprocess.run',side_effect=run),\
                 patch('components.equivalent_static.calculation_and_gui.threading.Thread') as thread,\
                 patch('components.equivalent_static.calculation_and_gui.HERE',root),\
                 patch.object(gui,'_load_project_inputs',return_value=None):
                def start():
                    worker=thread.call_args.kwargs['target']
                    worker()
                thread.return_value.start.side_effect=start
                gui._run_rayleigh()
            self.assertEqual(invoked,['ULS','SLS'])
            self.assertTrue((folder/'NBC105_Rayleigh_Preliminary_V123_ULS.log').is_file())
            self.assertTrue((folder/'NBC105_Rayleigh_Preliminary_V123_SLS.log').is_file())


if __name__=='__main__':
    unittest.main(verbosity=2)

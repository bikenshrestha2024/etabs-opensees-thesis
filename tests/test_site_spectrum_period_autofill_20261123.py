"""Regression: site spectra must use the same source-matched adopted T1 as MRSM.

No Windows GUI or ETABS/OpenSees solver is required; a synthetic current-model
export is sufficient to prove input provenance and missing-source behavior.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from components.inputs.analysis_autofill import populate_site
from components.response_spectrum.model_analysis import mrsm_period_defaults


class Var:
    def __init__(self, value=''):
        self.value=str(value)
    def get(self):
        return self.value
    def set(self, value):
        self.value=str(value)


def fake_app():
    fields=('soil','z','imp','rmu','omega','omegas','t1x','t1y','tnx','tny','status')
    return SimpleNamespace(**{name:Var() for name in fields})


class SoilSpectrumSourcePeriodTests(TestCase):
    def test_site_adopted_periods_match_mrsm_for_same_model_and_state(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            (root/'OpenSees_Complete_Model_Data_V118.json').write_text(
                json.dumps({'base_z_m':0,'diaphragms':[{'master_xyz':[0,0,94.9999999]}]}),
                encoding='utf-8')
            values={'soil':'C','Z':.35,'I':1.,'rmu':3.5,'omegau':1.4,'omegas':1.2,
                    'awx':2.07317451,'awy':2.20308033,
                    'rayleigh_tx':1.7031298875501197,'rayleigh_ty':2.4009996958491655}
            expected,_=mrsm_period_defaults(root,values,'ULS')
            project={'values':values,'notes':[]}
            app=fake_app()
            with patch('OpenSees_Project_Inputs_V123.import_project_inputs',
                       return_value=project) as imported, \
                 patch('components.inputs.project_workbooks.source_limit_state',
                       return_value=('ULS','Synthetic source ULS')), \
                 patch('components.inputs.analysis_autofill.matching_modal_reference',
                       return_value=None):
                populate_site(app,root)
            self.assertAlmostEqual(float(app.t1x.get()),expected['T1_X'])
            self.assertAlmostEqual(float(app.t1y.get()),expected['T1_Y'])
            self.assertIn('NBC',app.status.get())
            self.assertIn('ULS',app.status.get())
            self.assertEqual(imported.call_args.args[-1],'ULS')

    def test_no_matching_period_source_does_not_reuse_old_workbook_fields(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            app=fake_app()
            app.t1x.set('STALE');app.t1y.set('STALE')
            values={'soil':'C','workbook_adopted_tx':99.,'workbook_adopted_ty':98.}
            with patch('OpenSees_Project_Inputs_V123.import_project_inputs',
                       return_value={'values':values,'notes':[]}), \
                 patch('components.inputs.project_workbooks.source_limit_state',
                       return_value=('ULS','Synthetic source ULS')), \
                 patch('components.inputs.analysis_autofill.matching_modal_reference',
                       return_value=None):
                populate_site(app,root)
            self.assertEqual(app.t1x.get(),'')
            self.assertEqual(app.t1y.get(),'')
            self.assertIn('unavailable',app.status.get().casefold())

    def test_source_state_propagates_to_spectrum_period_lookup(self):
        with TemporaryDirectory() as td:
            app=fake_app()
            vals={'Z':.35}
            with patch('OpenSees_Project_Inputs_V123.import_project_inputs',
                       return_value={'values':vals,'notes':[]}) as importer, \
                 patch('components.inputs.project_workbooks.source_limit_state',
                       return_value=('SLS','Synthetic SLS')), \
                 patch('components.response_spectrum.model_analysis.mrsm_period_defaults',
                       return_value=({'T1_X':1.4,'T1_Y':1.6},
                                     'Synthetic SLS adopted period source')) as periods, \
                 patch('components.inputs.analysis_autofill.matching_modal_reference',
                       return_value=None):
                populate_site(app,td)
            self.assertEqual(importer.call_args.args[-1],'SLS')
            self.assertEqual(periods.call_args.args[-1],'SLS')
            self.assertEqual(app.t1x.get(),'1.4')
            self.assertEqual(app.t1y.get(),'1.6')

    def test_main_launcher_passes_selected_export_before_loading(self):
        from components.ui.application import App
        with TemporaryDirectory() as td:
            root=Path(td).resolve()
            launcher=App.__new__(App)
            launcher.root=object()
            launcher.out=Var(root)
            with patch('NBC105_Spectrum_Scaling_V115.launch_spectrum_gui') as launch:
                self.assertIs(launcher._open_spectrum_diagnostics(),launch.return_value)
                launch.assert_called_once_with(launcher.root,str(root))

    def test_launcher_without_folder_does_not_import_from_legacy_fallback(self):
        from components.response_spectrum.site_spectrum_and_scaling import launch_spectrum_gui
        app=fake_app();app.win=object()
        with patch('components.response_spectrum.site_spectrum_and_scaling.SpectrumScalingGUI',
                   return_value=app), \
             patch('OpenSees_Linear_Autofill_V124.populate_site') as populate:
            launch_spectrum_gui(parent=object())
            populate.assert_not_called()


if __name__ == '__main__':
    import unittest
    unittest.main()

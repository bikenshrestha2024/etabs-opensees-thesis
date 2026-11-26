"""Synthetic regression for unique authoritative MRSM case report loading.

No ETABS model, private source files or OpenSees numerical solve required.
[REF docs/source/components/response_spectrum/reports.py.md]
"""
import json
import tempfile
import unittest
from pathlib import Path

from components.response_spectrum.reports import saved_cases


class TestMRSMReports(unittest.TestCase):
    def test_authoritative_result_preferred_over_copied_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            authoritative=root/'MRSM_ULS'
            duplicate=root/'Organized_Results'/'snapshot'/'MRSM_ULS'
            authoritative.mkdir(parents=True)
            duplicate.mkdir(parents=True)
            source={'X_E0':{'limit_state':'ULS','model_sha256':'model123',
                            'axis':'X','marker':'NATIVE_WORKING_COPY'}}
            (authoritative/'MRSM_Results_V132.json').write_text(json.dumps(source))
            (duplicate/'MRSM_Results_V132.json').write_text(json.dumps(source))
            cases=saved_cases(root)
            self.assertEqual(len(cases),1)
            self.assertEqual(cases[0][0],authoritative/'MRSM_Results_V132.json')
            self.assertEqual(cases[0][2]['marker'],'NATIVE_WORKING_COPY')

    def test_same_state_disjoint_cases_cannot_mix_different_models_or_policies(self):
        for different in ('model_sha256','support_case','seismic_mass_policy'):
            with self.subTest(field=different), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                path=root/'MRSM_ULS'
                path.mkdir()
                source={'limit_state':'ULS','model_sha256':'modelA',
                        'support_case':'PHYSICAL_32','seismic_mass_policy':'SOURCE_DISTRIBUTED'}
                second=dict(source)
                second[different]='different'
                (path/'MRSM_Results_V132.json').write_text(json.dumps({
                    'X_E0':source,'Y_E0':second}))
                with self.assertRaisesRegex(ValueError,'incompatible MRSM'):
                    saved_cases(root)

    def test_missing_sls_panels_are_explicitly_labeled(self):
        from components.response_spectrum.reports import figures
        case={'limit_state':'ULS','axis':'X','stories':[{
            'height_m':3.0,'scaled_story_shear_kN':10.0,'design_drift_ratio':.001}]}
        with tempfile.TemporaryDirectory() as tmp:
            result=figures([(Path(tmp)/'MRSM_Results_V132.json','X_E0',case)])
            combined=result[-1][1]
            for ax in (combined.axes[1],combined.axes[3],combined.axes[5]):
                self.assertTrue(any('No saved SLS' in label.get_text() for label in ax.texts))
                self.assertEqual(len(ax.lines),0)

    def test_source_different_state_is_not_silently_merged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for state in ('ULS','SLS'):
                path=root/('MRSM_'+state)
                path.mkdir()
                (path/'MRSM_Results_V132.json').write_text(json.dumps({
                    'X_E0':{'limit_state':state,'model_sha256':'state_'+state}}))
            cases=saved_cases(root)
            self.assertEqual(len(cases),2)
            self.assertEqual({case['limit_state'] for _,_,case in cases},
                             {'ULS','SLS'})


if __name__=='__main__':
    unittest.main()

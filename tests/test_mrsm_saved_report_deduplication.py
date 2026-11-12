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

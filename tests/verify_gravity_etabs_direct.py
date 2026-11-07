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

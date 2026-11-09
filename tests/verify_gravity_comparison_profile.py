"""Regression: comparison preload and seismic mass are independent."""
import copy
import unittest

from OpenSees_Complete_Export_V118 import apply_gravity_profile


class GravityComparisonProfileTests(unittest.TestCase):
    def test_full_dead_live_and_roof_leave_mass_unchanged(self):
        data = {'unfactored_patterns': {
            'Dead': {'1': [0, 0, -10, 0, 0, 0]},
            'Live': {'1': [0, 0, -4, 0, 0, 0]},
            'Roof Live': {'1': [0, 0, -2, 0, 0, 0]},
        }, 'nodal_mass': {'1': [2.0, 2.0, 2.0]}}
        cfg = {'gravity_factors': {'Dead': 1, 'Live': .3, 'Roof Live': 0},
               'mass_factors': {'Dead': 1, 'Live': .3, 'Roof Live': 0}}
        mass, factors = copy.deepcopy(data['nodal_mass']), copy.deepcopy(cfg)
        context = apply_gravity_profile(data, cfg, 'GRAVITY_1.0D_1.0L')
        self.assertEqual(data['total_downward_load_kN'], 16.0)
        self.assertEqual(context['factors'], {'Dead': 1.0, 'Live': 1.0, 'Roof Live': 1.0})
        self.assertEqual(data['nodal_mass'], mass)
        self.assertEqual(cfg, factors)

    def test_seismic_profile_remains_separate_from_full_roof_live_gravity(self):
        from components.model.assembly import apply_gravity_profile
        data={'unfactored_patterns':{
            'Dead':{'1':[0,0,-100,0,0,0]},
            'Live':{'1':[0,0,-30,0,0,0]},
            'Roof Live':{'1':[0,0,-20,0,0,0]}},
            'nodal_mass':{'1':10.0},
            'total_downward_load_kN':109.0}
        cfg={'gravity_factors':{'Dead':1.0,'Live':0.3,'Roof Live':0.0},
             'mass_factors':{'Dead':1.0,'Live':0.3,'Roof Live':0.0}}
        snapshot=copy.deepcopy(data)
        seismic=apply_gravity_profile(data,cfg,'AS_CONFIGURED')
        self.assertEqual(seismic['factors']['Live'],0.3)
        self.assertEqual(seismic['factors']['Roof Live'],0.0)
        self.assertEqual(data,snapshot)
        full=apply_gravity_profile(data,cfg,'GRAVITY_1.0D_1.0L')
        self.assertEqual(data['total_downward_load_kN'],150.0)
        self.assertEqual(full['factors']['Live'],1.0)
        self.assertEqual(full['factors']['Roof Live'],1.0)
        self.assertEqual(data['nodal_mass'],snapshot['nodal_mass'])
        self.assertEqual(cfg['mass_factors']['Roof Live'],0.0)

    def test_roof_live_defined_but_unassigned_is_zero_in_full_gravity(self):
        # A pattern definition alone creates no applied roof-live force.
        data={'unfactored_patterns':{
            'Dead':{'1':[0,0,-100,0,0,0]},
            'Live':{'1':[0,0,-20,0,0,0]},
            'Roof Live':{}},
            'nodal_mass':{'1':12.5}}
        cfg={'gravity_factors':{'Dead':1,'Live':.3,'Roof Live':0},
             'mass_factors':{'Dead':1,'Live':.3,'Roof Live':0}}
        before=copy.deepcopy(data['nodal_mass'])
        result=apply_gravity_profile(data,cfg,'GRAVITY_1.0D_1.0L')
        self.assertEqual(result['factors']['Roof Live'],1.)
        self.assertEqual(data['gravity_by_pattern_kN']['Roof Live'],0.)
        self.assertEqual(data['total_downward_load_kN'],120.)
        self.assertEqual(data['nodal_mass'],before)

    def test_no_roof_live_source_pattern_adds_no_roof_load(self):
        data={'unfactored_patterns':{
            'Dead':{'1':[0,0,-50,0,0,0]},
            'Live':{'1':[0,0,-10,0,0,0]}}}
        cfg={'gravity_factors':{'Dead':1,'Live':.3,'Roof Live':0},
             'mass_factors':{'Dead':1,'Live':.3,'Roof Live':0}}
        result=apply_gravity_profile(data,cfg,'GRAVITY_1.0D_1.0L')
        self.assertEqual(data['total_downward_load_kN'],60.)
        self.assertNotIn('Roof Live',result['factors'])

    def test_gravity_gui_explicit_profile_and_no_second_preload(self):
        import ast
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]
        source=(root/'components/gravity/gui_and_reports.py').read_text(encoding='utf-8')
        ast.parse(source)
        self.assertIn('tk.StringVar(value="GRAVITY_1.0D_1.0L")',source)
        self.assertIn("'OPENSEES_GRAVITY_PROFILE':profile",source)
        self.assertIn("model_report.get('preload_completed')",source)
        self.assertIn("self._selected_gravity_evidence(model)",source)
        self.assertIn("'gravity_profile':GRAVITY_PROFILE",source)

    def test_unknown_pattern_fails_closed(self):
        data = {'unfactored_patterns': {'mystery': {'1': [0, 0, -1]}}}
        with self.assertRaisesRegex(ValueError, 'unclassified'):
            apply_gravity_profile(data, {'gravity_factors': {}}, 'GRAVITY_1.0D_1.0L')


if __name__ == '__main__':
    unittest.main()

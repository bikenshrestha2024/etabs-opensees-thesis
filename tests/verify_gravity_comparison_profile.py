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

    def test_unknown_pattern_fails_closed(self):
        data = {'unfactored_patterns': {'mystery': {'1': [0, 0, -1]}}}
        with self.assertRaisesRegex(ValueError, 'unclassified'):
            apply_gravity_profile(data, {'gravity_factors': {}}, 'GRAVITY_1.0D_1.0L')


if __name__ == '__main__':
    unittest.main()

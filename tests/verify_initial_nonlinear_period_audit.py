"""Verify nonlinear initial modal T1/Tn90 source distinction offline.

[REF NBC 105:2025 §7.3; docs/source/components/nonlinear_time_history/building_exploratory.py.md]
"""
import unittest
from components.nonlinear_time_history.building_exploratory import (
    _initial_nonlinear_mode_audit,
)


class TestInitialNonlinearPeriods(unittest.TestCase):
    def test_90_percent_threshold_is_first_crossing_mode_not_last(self):
        periods=[2.21,1.54,1.02,0.51]
        props={'partiMassRatiosCumuMX':[42,75,91,93],
               'partiMassRatiosCumuMY':[33,68,82,90.1]}
        report=_initial_nonlinear_mode_audit(periods,props,model_sha256='abc')
        self.assertAlmostEqual(report['model_period_T1_s'],2.21)
        self.assertEqual(report['Tn90_X_mode'],3)
        self.assertAlmostEqual(report['Tn90_X_s'],1.02)
        self.assertEqual(report['Tn90_Y_mode'],4)
        self.assertTrue(report['ninety_percent_both_axes'])
        self.assertEqual(report['model_sha256'],'abc')

    def test_not_reaching_90_is_none_not_fictitious_last_mode(self):
        report=_initial_nonlinear_mode_audit([2.21,1.54],
            {'partiMassRatiosCumuMX':[60,89.9],
             'partiMassRatiosCumuMY':[80,93]})
        self.assertIsNone(report['Tn90_X_s'])
        self.assertEqual(report['Tn90_Y_mode'],2)
        self.assertFalse(report['ninety_percent_both_axes'])

    def test_bad_missing_mass_outputs_are_fail_closed(self):
        report=_initial_nonlinear_mode_audit([2.2,1.5],
            {'partiMassRatiosCumuMX':[float('nan'),5]})
        self.assertIsNone(report['Tn90_X_s'])
        self.assertIsNone(report['Tn90_Y_s'])


if __name__=='__main__':
    unittest.main()

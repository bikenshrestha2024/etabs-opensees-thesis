"""Exploratory window: probe, damping and case-identity options.

[REF V168_FIRST_STEP_DIAGNOSTICS.md; components/ui/exploratory_options.py]
Solver-free; the GUI check only builds the panel (no analysis is started).
"""
import os
import unittest
from pathlib import Path

from components.ui.exploratory_options import build_options, describe, event_name

ROOT = Path(__file__).resolve().parents[1]


class Options(unittest.TestCase):
    def test_documented_failing_probe(self):
        o = build_options(excitation='x', damping_mode='ZERO damping (diagnostic)',
                          pair_label='RSN1120_KOBE_TAK000', variant='M0')
        self.assertEqual(o['diagnostic_excitation'], 'X')
        self.assertTrue(o['diagnostic_zero_damping'])
        self.assertEqual((o['pair_id'], o['variant_id']), ('Kobe', 'M0'))
        self.assertIn('DIAGNOSTIC PROBE', describe(o))

    def test_thesis_style_case(self):
        o = build_options(reference_modes='1, 6', energy_balance=True, energy_tolerance='0.03',
                          variant='M3', pair_label='D:\\Thesis\\X Direction\\Matched_RSN1505_CHICHI_TCU068-E')
        self.assertEqual(o['damping_reference_modes'], [1, 6])
        self.assertEqual((o['energy_balance'], o['energy_balance_tolerance']), (True, 0.03))
        self.assertEqual(o['inherent_damping_ratio'], 0.025)
        self.assertNotIn('diagnostic_zero_damping', o)
        self.assertEqual(o['pair_id'], 'Chi-Chi')
        self.assertTrue(describe(o).startswith('case: Chi-Chi M3'))

    def test_rejections(self):
        bad = [dict(excitation='Z'), dict(ratio='0.05'), dict(ratio='5'), dict(reference_modes='1'),
               dict(reference_modes='3,3'), dict(reference_modes='1,21'), dict(reference_modes='a,b'),
               dict(energy_balance=True, energy_tolerance='2'), dict(variant='M7'),
               dict(damping_mode='half')]
        for kwargs in bad:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                build_options(**kwargs)
        self.assertEqual(build_options(ratio='0.05', allow_above_2_5=True)['inherent_damping_ratio'], 0.05)

    def test_event_names_cover_soil_c_suite(self):
        from components.nonlinear_time_history.soil_c_nltha_suite import EVENT_ORDER
        labels = ['KATNP.HNE.NQ.01_a_EW_PEER_Gorkha', 'RSN879_LANDERS_LCN260', 'RSN1086_NORTHR_SYL090',
                  'RSN1120_KOBE_TAK000', 'RSN1165_KOCAELI_IZT090', 'RSN1505_CHICHI_TCU068-E',
                  'RSN1787_HECTOR', 'RSN767_LOMAP']
        self.assertEqual([event_name(v) for v in labels], list(EVENT_ORDER))


@unittest.skipUnless(os.environ.get('DISPLAY'), 'no display: GUI panel not built (skipped, not passed)')
class Panel(unittest.TestCase):
    def test_panel_builds(self):
        import tkinter as tk
        from components.ui.building_exploratory_gui import launch
        root = tk.Tk()
        root.withdraw()
        try:
            launch(root, ROOT / 'Saved_Project_V156')
            win = [w for w in root.winfo_children() if isinstance(w, tk.Toplevel)][-1]
            texts, stack = [], [win]
            while stack:
                w = stack.pop()
                stack += w.winfo_children()
                try:
                    texts.append(str(w.cget('text')))
                except tk.TclError:
                    pass
            self.assertIn('Diagnostics, damping and case identity', texts)
            self.assertIn('Record energy balance', texts)
        finally:
            root.destroy()


if __name__ == '__main__':
    unittest.main()

"""Single-source material set, candidate defaults and MRSM blank-period handling.

[REF R01 PEER 2015/12 Appendix B.3; components/nonlinear_time_history/material_source_sets.py]
Solver-free. Native behaviour of the single-source basis is not tested here.
"""
import unittest

from components.nonlinear_time_history.material_source_sets import (
    BASES, SINGLE_SOURCE_BASIS, default_candidates, peer_single_source, source_table)
from components.nonlinear_time_history.research_building_materials import MATERIAL_OVERRIDE_BOUNDS

PEER = 'webpeer-2015-12-kristijan_kolozvari_kutay_orakcal_john_wallace.pdf'


class SingleSource(unittest.TestCase):
    def test_every_value_from_one_paper_or_labelled(self):
        s = peer_single_source()
        allowed = {'FROM_SOURCE', 'MODEL_ASSUMPTION_NOT_IN_SOURCE', 'PROVENANCE_NOT_RECORDED', 'NOT_IN_SOURCE'}
        self.assertTrue(all(r['status'] in allowed for r in s['rows']))
        self.assertTrue(all(r['source'].endswith(PEER) for r in s['rows'] if r['status'] == 'FROM_SOURCE'))
        self.assertTrue(all(r['source'] == '' for r in s['rows'] if r['status'] != 'FROM_SOURCE'))
        missing = {r['family'] for r in s['rows'] if r['status'] == 'NOT_IN_SOURCE'}
        self.assertEqual(missing, {'Ordinary SHS brace (Steel01)', 'Fluid viscous damper', 'Buckling-restrained brace'})

    def test_frame_uses_same_card_as_walls(self):
        s = peer_single_source()
        f = s['frame_section']
        self.assertAlmostEqual(f['cover_fc_mpa'], abs(s['wall_concrete']['fpcc']))
        self.assertAlmostEqual(f['fy_rebar_mpa'], s['wall_steel']['fyp'])
        self.assertEqual((f['steel_cR1'], f['steel_cR2']), (s['wall_steel']['cR1'], s['wall_steel']['cR2']))
        # printed Menegotto-Pinto a1=18.5 converted to the OpenSees ratio a1/R0
        self.assertAlmostEqual(s['wall_steel']['cR1'], 18.5 / 20.)
        self.assertTrue(any('converted: printed a1=18.5' in r['locator'] for r in s['rows']))

    def test_mixed_basis_is_labelled(self):
        self.assertIn('MIXED_SOURCES', {r['status'] for r in source_table('PUBLISHED_REFERENCE')})
        self.assertIn(SINGLE_SOURCE_BASIS, BASES)


class Candidates(unittest.TestCase):
    def test_every_parameter_has_values_or_a_reason(self):
        for basis in BASES:
            for key in MATERIAL_OVERRIDE_BOUNDS:
                with self.subTest(basis=basis, key=key):
                    text, why = default_candidates(key, basis)
                    self.assertTrue(text or why)
        self.assertEqual(default_candidates('brace.b', 'PUBLISHED_REFERENCE')[0], '0.009, 0.01, 0.011')
        self.assertEqual(default_candidates('brace.E_mpa', 'PUBLISHED_REFERENCE')[0], '')


class MrsmBlankPeriods(unittest.TestCase):
    def test_blank_inputs_named_not_float_error(self):
        from pathlib import Path
        src = (Path(__file__).resolve().parents[1] / 'components/response_spectrum/model_analysis.py').read_text(encoding='utf-8')
        i = src.index("blank=[k for k in ('Z','I','rmu','omegau','omegas','T1_X','T1_Y'")
        self.assertLess(i, src.index("for k in ['Z','I','rmu','omegau','omegas','T1_X','T1_Y','damping']:cfg[k]=float(cfg[k])"))


if __name__ == '__main__':
    unittest.main()

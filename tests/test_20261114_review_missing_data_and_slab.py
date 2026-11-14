"""Regression evidence for explicit missing seismic response and mandatory slab basis.

This test is source/static only; ETABS native runs and 0.25/0.35 physical
section equivalence are separate acceptance gates.
"""
import ast
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class TestCaseReviewAndSlabBasis(unittest.TestCase):
    def test_sources_parse(self):
        for rel in ('components/validation/case_review.py',
                    'components/model/analysis_basis.py'):
            ast.parse((ROOT/rel).read_text(encoding='utf-8'),filename=rel)

    def test_source_and_no_data_policy(self):
        s=(ROOT/'components/validation/case_review.py').read_text(encoding='utf-8')
        for item in ('export_root_for','03_ESM','05_MRSM',
                     'NO_SAVED_SEISMIC_DRIFT','NO_SAVED_LATERAL_DEFLECTION',
                     'Searched result paths','NOT ZERO DRIFT'):
            self.assertIn(item,s)

    def test_required_slab_basis_label(self):
        s=(ROOT/'components/model/analysis_basis.py').read_text(encoding='utf-8')
        self.assertIn('REQUIRED PROJECT ANALYSIS BASIS',s)
        self.assertIn('0.25 Ig (ULS/strength)',s)
        self.assertIn('0.35 Ig (SLS/serviceability)',s)
        self.assertNotIn('shown as a supplemental comparison for this conventional slab',s)


if __name__=='__main__':
    unittest.main()

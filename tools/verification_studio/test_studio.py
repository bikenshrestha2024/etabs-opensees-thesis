"""Offline regression of registry, metadata, analytical checks and reports."""
import json
import pathlib
import tempfile
import unittest

import ETABS_OpenSees_Verification_Studio as studio
import expanded_benchmarks as expanded


class TestStudio(unittest.TestCase):
    def test_registry(self):
        self.assertEqual(len(studio.CASES), 12)
        self.assertEqual([x[0] for x in studio.CASES], [f'B{i:02d}' for i in range(1, 13)])
        self.assertEqual(len(studio.REFERENCE_INDEX), 15)

    def test_metric_acceptance(self):
        self.assertTrue(studio._metric('exact', 10, 10, .01)['passed'])
        self.assertFalse(studio._metric('bad', 9, 10, .01)['passed'])
        with self.assertRaises(ValueError):
            studio._metric('bad', float('nan'), 10, .01)

    def test_analytical_damper_only(self):
        result = expanded.run('B12', None, .01)
        self.assertEqual(result['status'], 'ANALYTICAL_PASS')
        self.assertEqual(result['etabs_native_equivalence'], 'NOT_VERIFIED')
        self.assertEqual(len(result['metrics']), 7)
        self.assertTrue(all(m['passed'] for m in result['metrics']))

    def test_worker_isolated_output(self):
        with tempfile.TemporaryDirectory() as t:
            r = studio.run_worker('B12', .01, t)
            self.assertEqual(r['solver'], 'NONE_ANALYTICAL_ONLY')
            self.assertEqual(len(r['source_sha256']), 2)
            self.assertEqual(
                json.loads((pathlib.Path(t) / 'B12.json').read_text())['status'],
                'ANALYTICAL_PASS',
            )

    def test_no_solver_never_passes(self):
        with tempfile.TemporaryDirectory() as t:
            studio._write_reports(t, [
                {'case_id': 'B06', 'title': 'slab', 'status': 'BLOCKED', 'metrics': [], 'reason': 'not installed'}
            ], {'kind': 'test'})
            self.assertIn('BLOCKED', (pathlib.Path(t) / 'report.html').read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)

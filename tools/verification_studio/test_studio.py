"""Offline regression of registry, metadata, analytical checks and reports."""
import json
import pathlib
import importlib.util
import shutil
import subprocess
import sys
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

    def test_missing_companion_is_not_a_missing_openseespy_claim(self):
        # Regression for downloaded single-file GUI without its companion module.
        with tempfile.TemporaryDirectory() as t:
            folder = pathlib.Path(t)
            isolated = folder / 'ETABS_OpenSees_Verification_Studio.py'
            shutil.copyfile(pathlib.Path(studio.__file__), isolated)
            r = subprocess.run([sys.executable, str(isolated), '--worker', 'B12',
                                '--output', str(folder / 'run')],
                               capture_output=True, text=True, timeout=30)
            result = json.loads((folder / 'run' / 'B12.json').read_text())
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertEqual(result['missing_dependency'], 'expanded_benchmarks.py')
            self.assertIn('Copy expanded_benchmarks.py', result['reason'])
            self.assertNotIn('OpenSeesPy is not installed', result['reason'])

    def test_all_in_one_standalone(self):
        # Self-contained B01-B12 runner must work without importing the sibling.
        source = pathlib.Path(__file__).with_name(
            'ETABS_OpenSees_Verification_Studio_ALL_IN_ONE.py'
        )
        spec = importlib.util.spec_from_file_location('verification_single_file', source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(len(module.CASES), 12)
        self.assertEqual(len(module.REFERENCE_INDEX), 15)
        result = module._run_case(None, 'B12', .01)
        self.assertEqual(result['status'], 'ANALYTICAL_PASS')
        self.assertEqual(len(result['metrics']), 7)
        self.assertEqual(result['etabs_native_equivalence'], 'NOT_VERIFIED')
        with tempfile.TemporaryDirectory() as tempdir:
            isolated = pathlib.Path(tempdir) / source.name
            shutil.copyfile(source, isolated)
            output = pathlib.Path(tempdir) / 'run'
            run = subprocess.run(
                [sys.executable, str(isolated), '--worker', 'B12', '--output', str(output)],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            saved = json.loads((output / 'B12.json').read_text())
            self.assertEqual(saved['status'], 'ANALYTICAL_PASS')
            self.assertIn(source.name, saved['source_sha256'])
            self.assertEqual(len(saved['source_sha256']), 1)

    def test_no_solver_never_passes(self):
        with tempfile.TemporaryDirectory() as t:
            studio._write_reports(t, [
                {'case_id': 'B06', 'title': 'slab', 'status': 'BLOCKED', 'metrics': [], 'reason': 'not installed'}
            ], {'kind': 'test'})
            self.assertIn('BLOCKED', (pathlib.Path(t) / 'report.html').read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)

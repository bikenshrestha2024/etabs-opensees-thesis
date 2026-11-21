"""Tests for tools/analyze_run_log.py. [REF docs/source/tools/analyze_run_log.py.md]"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import analyze_run_log as arl  # noqa: E402

FIXTURE = ROOT / 'tests' / 'fixtures' / 'ltha_v115_prelim_log_excerpt.txt'
TEXT = FIXTURE.read_text(encoding='utf-8', errors='replace')


class AnalyzeRunLogTests(unittest.TestCase):
    def test_parse_counts_twelve_completed_of_sixteen(self):
        p = arl.parse_run_log(TEXT)
        self.assertEqual(p['workload']['cases'], 16)
        self.assertEqual(len(p['cases']), 12)
        self.assertEqual(p['started_unfinished'], ['RSN1787_HECTOR_XY'])

    def test_diagnostic_only_flag(self):
        self.assertTrue(arl.parse_run_log(TEXT)['diagnostic_only'])

    def test_stage_timings_present(self):
        for c in arl.parse_run_log(TEXT)['cases']:
            self.assertGreater(c['stages']['native_transient_solve'], 0)
            self.assertIsNotNone(c['full_record_s'])
            self.assertIsNotNone(c['dt_s'])

    def test_baseline_solver_count_twelve(self):
        self.assertEqual(arl.parse_run_log(TEXT)['solver_baseline_cases'], 12)

    def test_eigen_residual_is_5_36e_7(self):
        self.assertAlmostEqual(arl.parse_run_log(TEXT)['eigen_max_residual'], 5.36e-7, places=9)

    def test_projection_is_days_not_hours(self):
        proj = arl.project_full_run(arl.parse_run_log(TEXT))
        self.assertGreater(proj['total_projected_hours'], 100)
        self.assertEqual(len(proj['per_case']), 12)

    def test_projection_basis_wording(self):
        proj = arl.project_full_run(arl.parse_run_log(TEXT))
        self.assertIn('linear baseline, no factor reuse, lower bound for nonlinear', proj['basis'])

    def test_crlf_input_parses_same(self):
        self.assertEqual(arl.parse_run_log(TEXT), arl.parse_run_log(TEXT.replace('\n', '\r\n')))

    def test_empty_log(self):
        p = arl.parse_run_log('')
        self.assertEqual(p['cases'], [])
        proj = arl.project_full_run(p)
        self.assertEqual(proj['total_projected_hours'], 0.0)
        arl.render_markdown(p, proj, 'empty')

    def test_cli_writes_deterministic_files(self):
        blobs = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as d:
                r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'analyze_run_log.py'),
                                    str(FIXTURE), '--out-dir', d, '--stem', 'X'],
                                   capture_output=True, text=True, check=True)
                self.assertEqual(len(r.stdout.split()), 2)
                md = (Path(d) / 'X.md').read_bytes()
                js = (Path(d) / 'X.json').read_bytes()
                blobs.append((md, js))
        self.assertEqual(blobs[0], blobs[1])
        md = blobs[0][0].decode('utf-8')
        self.assertIn(arl.STATUS, md)
        self.assertIn(arl.STATUS, blobs[0][1].decode('utf-8'))
        self.assertNotIn('ACCEPTED', md)
        self.assertNotIn('ACCEPTED', blobs[0][1].decode('utf-8'))
        self.assertNotIn(b'\r', blobs[0][0])
        self.assertIn('lower bound for nonlinear', md)


if __name__ == '__main__':
    unittest.main()

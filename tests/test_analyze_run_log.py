"""Tests for tools/analyze_run_log.py. [REF docs/source/tools/analyze_run_log.py.md]"""
import json
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
                self.assertEqual(len(r.stdout.splitlines()), 2)
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

    def test_cli_prints_one_path_per_line_even_with_space_in_dir(self):
        with tempfile.TemporaryDirectory(prefix='run log ') as d:
            r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'analyze_run_log.py'),
                                str(FIXTURE), '--out-dir', d, '--stem', 'X'],
                               capture_output=True, text=True, check=True)
            lines = r.stdout.splitlines()
            self.assertEqual([Path(x).name for x in lines], ['X.md', 'X.json'])
            self.assertTrue(all(Path(x).is_file() for x in lines))


FAILED_LOG = (
    '[WORKLOAD] 2 cases | 20 requested steps\n'
    '[START] A_XY: rebuilding model\n'
    '[LINEAR TRIAL] A_XY: analyzed=0.5s; full_record=1.0s; TRUNCATED_DIAGNOSTIC_NOT_CODE_ACCEPTANCE\n'
    '[CASE TIMING] A_XY | failed | elapsed=5.0s | stages={"model_and_gravity": 5.0}\n'
    '[START] B_XY: rebuilding model\n'
    '[LINEAR TRIAL] B_XY: analyzed=0.5s; full_record=1.0s; TRUNCATED_DIAGNOSTIC_NOT_CODE_ACCEPTANCE\n'
    '[OK] B_XY: steps=10, dt=0.1s, peak drifts X/Y=0.001/0.002\n'
    '[CASE TIMING] B_XY | completed | elapsed=9.0s | stages={"native_transient_solve": 4.0, "x": null}\n'
)


class FailedCaseTests(unittest.TestCase):
    def test_failed_case_not_counted_completed(self):
        p = arl.parse_run_log(FAILED_LOG)
        self.assertEqual([c['name'] for c in p['cases']], ['B_XY'])
        self.assertEqual(p['cases'][0]['status'], 'completed')
        self.assertEqual([(c['name'], c['status']) for c in p['failed_cases']], [('A_XY', 'failed')])
        self.assertEqual(p['started_unfinished'], [])

    def test_failed_case_in_markdown_and_json(self):
        p = arl.parse_run_log(FAILED_LOG)
        proj = arl.project_full_run(p)
        md = arl.render_markdown(p, proj, 'probe')
        self.assertIn('Completed cases in log: 1.', md)
        self.assertIn('A_XY (failed)', md)
        self.assertEqual(proj['projected_case_count'], 1)
        self.assertEqual(proj['cases_not_projected'], 1)
        self.assertIn('1 of 2 declared cases were not run to completion', md)
        self.assertIn('failed_cases', json.dumps({'parsed': p}))

    def test_non_numeric_stage_value_does_not_raise(self):
        p = arl.parse_run_log(FAILED_LOG)
        self.assertEqual(p['cases'][0]['stages'], {'native_transient_solve': 4.0})
        q = arl.parse_run_log('[CASE TIMING] Z | completed | elapsed=1.0s | stages={"a": "x", "b": [1]}')
        self.assertEqual(q['cases'][0]['stages'], {})

    def test_fixture_report_states_partial_projection(self):
        p = arl.parse_run_log(TEXT)
        md = arl.render_markdown(p, arl.project_full_run(p), 'f')
        self.assertIn('4 of 16 declared cases were not run to completion', md)
        self.assertIn('0.5 s truncated diagnostic', arl.project_full_run(p)['basis'])
        self.assertEqual(p['failed_cases'], [])

    def test_truncation_wording_only_when_log_says_truncated(self):
        log = ('[WORKLOAD] 1 cases | 10 requested steps\n'
               '[LINEAR TRIAL] A_XY: analyzed=5s; full_record=5s\n'
               '[OK] A_XY: steps=10, dt=0.5s, peak drifts X/Y=0.1/0.1\n'
               '[CASE TIMING] A_XY | completed | elapsed=2.0s | stages={"native_transient_solve": 1.0}\n')
        p = arl.parse_run_log(log)
        proj = arl.project_full_run(p)
        md = arl.render_markdown(p, proj, 'full')
        self.assertNotIn('0.5 s', md)
        self.assertNotIn('truncated diagnostic', proj['basis'])
        self.assertNotIn('only 0.5 s', md)


if __name__ == '__main__':
    unittest.main()

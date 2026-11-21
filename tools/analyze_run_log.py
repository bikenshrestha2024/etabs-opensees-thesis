"""Parse a runner log from the preliminary linear LTHA setup check and project full-record cost.

[REF engineering/rules/CORE_RULES.md; docs/source/tools/analyze_run_log.py.md]
Reads bracket-tagged log lines only. Output is log evidence, never engineering acceptance.

    python tools/analyze_run_log.py LOG --out-dir docs/validation/run_findings --stem NAME
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

STATUS = 'SOLVER_OR_LOG_EVIDENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE'
BASIS = ('native_transient_solve seconds per step measured on the 0.5 s truncated diagnostic '
         '(linear baseline, no factor reuse, lower bound for nonlinear)')
DIAG_TAG = 'TRUNCATED_DIAGNOSTIC_NOT_CODE_ACCEPTANCE'

_WORKLOAD = re.compile(r'^\[WORKLOAD\]\s+(\d+)\s+cases\s*\|\s*(\d+)\s+requested steps')
_SCOPE = re.compile(r'^\[SCOPE\]\s*(.*)$')
_START = re.compile(r'^\[START\]\s+(\S+?):')
_TRIAL = re.compile(r'^\[LINEAR TRIAL\]\s+(\S+?):.*?full_record=([0-9.]+)s')
_TIMING = re.compile(r'^\[CASE TIMING\]\s+(\S+)\s*\|[^|]*\|\s*elapsed=([0-9.]+)s\s*\|\s*stages=(\{.*\})')
_OK = re.compile(r'^\[OK\]\s+(\S+?):\s*steps=(\d+),\s*dt=([0-9.eE+-]+)s,\s*peak drifts X/Y=([0-9.eE+-]+)/([0-9.eE+-]+)')
_BASE = re.compile(r'^\[SOLVER BASELINE\]\s+(\S+?):')
_EXP = re.compile(r'^\[SOLVER EXPERIMENTAL\]\s+(\S+?):')
_EIGEN = re.compile(r'^\[EIGEN COMPLETE\].*max relative residual=([0-9.eE+-]+)')


def parse_run_log(text):
    """Parse bracket-tagged runner log text into a dict of workload, per-case timing and flags.

    [REF docs/source/tools/analyze_run_log.py.md]
    """
    workload, scope = None, None
    starts, timings, trials, oks = [], [], {}, {}
    baseline, experimental, eigen, diag = set(), set(), None, False
    for raw in (text or '').splitlines():
        line = raw.strip()
        if DIAG_TAG in line:
            diag = True
        m = _WORKLOAD.match(line)
        if m:
            workload = {'cases': int(m.group(1)), 'requested_steps': int(m.group(2))}
            continue
        m = _SCOPE.match(line)
        if m:
            scope = m.group(1)
            continue
        m = _START.match(line)
        if m:
            starts.append(m.group(1))
            continue
        m = _TRIAL.match(line)
        if m:
            trials[m.group(1)] = (float(m.group(2)), DIAG_TAG in line)
            continue
        m = _TIMING.match(line)
        if m:
            try:
                stages = {k: float(v) for k, v in json.loads(m.group(3)).items()}
            except ValueError:
                stages = {}
            timings.append((m.group(1), float(m.group(2)), stages))
            continue
        m = _OK.match(line)
        if m:
            oks[m.group(1)] = (int(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)))
            continue
        m = _BASE.match(line)
        if m:
            baseline.add(m.group(1))
            continue
        m = _EXP.match(line)
        if m:
            experimental.add(m.group(1))
            continue
        m = _EIGEN.match(line)
        if m:
            value = float(m.group(1))
            eigen = value if eigen is None else max(eigen, value)
    cases = []
    for name, elapsed, stages in timings:
        steps, dt, dx, dy = oks.get(name, (None, None, None, None))
        full, trunc = trials.get(name, (None, False))
        cases.append({'name': name, 'elapsed_s': elapsed, 'stages': stages, 'steps': steps,
                      'dt_s': dt, 'peak_drift_x': dx, 'peak_drift_y': dy,
                      'full_record_s': full, 'truncated_diagnostic': trunc})
    done = {c['name'] for c in cases}
    unfinished = []
    for name in starts:
        if name not in done and name not in unfinished:
            unfinished.append(name)
    return {'workload': workload, 'scope': scope, 'cases': cases,
            'started_unfinished': unfinished, 'solver_baseline_cases': len(baseline),
            'solver_experimental_cases': len(experimental), 'eigen_max_residual': eigen,
            'diagnostic_only': diag}


def project_full_run(parsed, *, dt_by_case=None):
    """Project full-record hours from measured native solve seconds per step (linear lower bound).

    [REF docs/source/tools/analyze_run_log.py.md]
    """
    dt_by_case = dt_by_case or {}
    solve = sum(c['stages'].get('native_transient_solve', 0.0) for c in parsed['cases']
                if c['steps'])
    steps = sum(c['steps'] for c in parsed['cases'] if c['steps'])
    rate = solve / steps if steps else None
    per_case, total = [], 0.0
    for c in parsed['cases']:
        dt = dt_by_case.get(c['name'], c['dt_s'])
        full = c['full_record_s']
        if rate is None or not dt or not full:
            continue
        n = int(math.ceil(full / dt - 1e-9))
        hours = n * rate / 3600.0
        total += hours
        per_case.append({'name': c['name'], 'full_record_s': full, 'dt_s': dt, 'steps': n,
                         'projected_hours': hours})
    return {'measured_native_s_per_step': rate, 'per_case': per_case,
            'total_projected_hours': total, 'basis': BASIS}


def _f(value, fmt):
    return 'n/a' if value is None else format(value, fmt)


def render_markdown(parsed, projection, source_name):
    """Render the findings as deterministic Markdown with explicit non-evidence limits.

    [REF docs/source/tools/analyze_run_log.py.md]
    """
    w = parsed['workload']
    n_done = len(parsed['cases'])
    rate = projection['measured_native_s_per_step']
    out = ['# Run-log findings: %s' % source_name, '', 'Status: `%s`' % STATUS, '',
           '## What ran', '']
    if w:
        out.append('- Workload declared: %d cases, %d requested steps.' % (w['cases'], w['requested_steps']))
    out.append('- Completed cases in log: %d.' % n_done)
    out.append('- Started but unfinished: %s.' % (', '.join(parsed['started_unfinished']) or 'none'))
    out.append('- Linear baseline solver cases: %d; experimental solver cases: %d.'
               % (parsed['solver_baseline_cases'], parsed['solver_experimental_cases']))
    out.append('- Max eigen relative residual: %s.' % _f(parsed['eigen_max_residual'], '.3g'))
    out.append('- Truncated diagnostic only: %s.' % ('yes' if parsed['diagnostic_only'] else 'no'))
    if parsed['scope']:
        out.append('- Scope: %s' % parsed['scope'])
    out += ['', '## Timing (seconds)', '',
            '| case | elapsed | model_and_gravity | damping_eigenanalysis | native_transient_solve | steps | dt |',
            '|---|---|---|---|---|---|---|']
    for c in parsed['cases']:
        s = c['stages']
        out.append('| %s | %.1f | %.1f | %.1f | %.1f | %s | %s |' % (
            c['name'], c['elapsed_s'], s.get('model_and_gravity', 0.0),
            s.get('damping_eigenanalysis', 0.0), s.get('native_transient_solve', 0.0),
            c['steps'] if c['steps'] is not None else 'n/a', _f(c['dt_s'], 'g')))
    out += ['', '## Projection to full records', '',
            'Measured native solve: %s s/step.' % _f(rate, '.4f'),
            'Basis: %s.' % projection['basis'],
            'The projection is a lower bound for nonlinear analysis.', '',
            '| case | full record (s) | dt (s) | steps | projected hours |', '|---|---|---|---|---|']
    for p in projection['per_case']:
        out.append('| %s | %.2f | %g | %d | %.2f |' % (
            p['name'], p['full_record_s'], p['dt_s'], p['steps'], p['projected_hours']))
    out += ['', 'Total projected solve time for %d completed cases: %.1f hours (%.1f days).'
            % (len(projection['per_case']), projection['total_projected_hours'],
               projection['total_projected_hours'] / 24.0),
            '', '## Not evidence of', '',
            '- Engineering acceptance of any model, check or result.',
            '- Drift performance: peak drifts come from only 0.5 s of each record.',
            '- Nonlinear cost: nonlinear steps need re-factorisation and iteration, so cost is higher.',
            '']
    return '\n'.join(out)


def _write(path, text):
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('log')
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--stem', required=True)
    args = ap.parse_args(argv)
    text = Path(args.log).read_text(encoding='utf-8', errors='replace')
    parsed = parse_run_log(text)
    projection = project_full_run(parsed)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    md, js = out_dir / (args.stem + '.md'), out_dir / (args.stem + '.json')
    _write(md, render_markdown(parsed, projection, Path(args.log).name))
    payload = {'status': STATUS, 'source': Path(args.log).name, 'parsed': parsed,
               'projection': projection}
    _write(js, json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print(md)
    print(js)
    return 0


if __name__ == '__main__':
    sys.exit(main())

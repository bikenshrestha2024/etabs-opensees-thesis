"""Excel run-matrix tracker with pass/fail gates and summary sheets (openpyxl).

[REF R10 NBC105-2025 §5.5.3 (drift screen), §9.3.2.3 (XY and YX), §9.3.3 (mean of accepted responses)]
[REF docs/00_THESIS_ACCEPTANCE_GATES.md (gate vocabulary)]
[REF Uang & Bertero 1990 (energy balance closure)]

Usage (Anaconda prompt, env etabs_env312; openpyxl is already used by the repo):
    python tools/export_dashboard.py --run-root D:/Thesis/SoilC_Matrix --out D:/Thesis/NLTHA_Dashboard.xlsx

Sheets
  README          scope, gate definitions, references
  Run_Matrix      one row per planned config x orientation (from
                  00_SOIL_C_M0_M6_RUN_MATRIX.csv when present) joined to results
  Case_Results    every discovered case folder with peaks and gate outcome
  Summary_Variant mean of ACCEPTED cases per variant x limit state (§9.3.3)
  Gate_Counts     pass / fail / not-run counts per gate and variant
Gates are numerical screens. PASS never means NBC design acceptance.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.plot_results import (  # noqa: E402  (shared discovery / parsing)
    ACCEPTED_GATE, DRIFT_LIMIT, VARIANTS, _read_json, discover_cases, read_csv_columns, story_names)

GATES = (
    ('G_RUN', 'Case executed without FAILED.json', 'Runner'),
    ('G_COMPLETE', f'Accepted_History_Completion_Gate status = {ACCEPTED_GATE}', 'full_record_gate.py'),
    ('G_ENERGY', 'Energy balance error <= configured tolerance', 'Uang & Bertero 1990'),
    ('G_DRIFT', 'Peak storey drift <= NBC §5.5.3 screen (0.025 ULS / 0.006 SLS)', 'NBC 105:2025 §5.5.3'),
    ('G_DAMPING', 'Inherent ratio <= 0.025, or 0.05 with explicit flag; region scope', 'NBC §8.1.1 (repo); TBI 2017'),
)
FILL = {'PASS': 'C6EFCE', 'FAIL': 'FFC7CE', 'REVIEW': 'FFEB9C', 'NOT_RUN': 'D9D9D9', 'N/A': 'EDEDED'}


def case_row(c):
    """Peaks and gate outcomes for one discovered case.

    [REF R10 §5.5.3; full_record_gate.py; energy_balance.py] Output: dict.
    """
    row = dict(variant=c['variant'], limit_state=c['limit_state'], event=c['event'],
               orientation=c['orientation'], case_status=c['status'], completion_gate=c['gate'],
               folder=str(c['path']))
    row['G_RUN'] = 'FAIL' if c['failed'] else 'PASS'
    row['G_COMPLETE'] = 'PASS' if c['accepted'] else ('FAIL' if c['failed'] else 'REVIEW')
    energy = _read_json(c['path'] / 'Energy_Balance.json')
    if energy:
        row['energy_status'] = energy.get('status')
        row['energy_max_rel_error'] = energy.get('max_relative_error')
        fin = energy.get('final') or {}
        inp = (fin.get('input_kJ') or 0.) + (fin.get('gravity_work_kJ') or 0.)
        row['device_energy_share'] = (fin.get('device_kJ', 0.) / inp) if inp else None
        row['G_ENERGY'] = 'PASS' if energy.get('status') == 'PASS' else (
            'FAIL' if energy.get('status') == 'FAIL' else 'REVIEW')
    else:
        row['G_ENERGY'] = 'NOT_RUN'
    hist = c['path'] / 'Building_Nonlinear_history.csv'
    if hist.exists() and not c['failed']:
        cols = read_csv_columns(hist)
        names = story_names(cols)
        for ax in ('X', 'Y'):
            row['peak_drift_' + ax] = max((abs(v) for n in names for v in cols[n + '_drift_' + ax]), default=None)
            row['peak_base_shear_' + ax + '_kN'] = max((abs(v) for v in cols.get('base_shear_' + ax + '_kN', [])), default=None)
            roof = names[-1] if names else None
            row['peak_roof_U' + ax + '_m'] = max((abs(v) for v in cols.get(f'{roof}_U{ax}_m', [])), default=None)
        lim = DRIFT_LIMIT.get(c['limit_state'])
        peak = max(row.get('peak_drift_X') or 0., row.get('peak_drift_Y') or 0.)
        row['drift_limit'] = lim
        row['G_DRIFT'] = ('PASS' if peak <= lim else 'FAIL') if lim else 'N/A'
    else:
        row['G_DRIFT'] = 'NOT_RUN'
    modal = _read_json(c['path'] / 'Initial_Modal_Damping.json') or {}
    zeta = modal.get('inherent_damping_ratio')
    scope = modal.get('rayleigh_scope')
    row['inherent_damping_ratio'] = zeta
    row['rayleigh_scope'] = scope
    if zeta is None:
        row['G_DAMPING'] = 'REVIEW'   # pre-change run: fixed 5% global Rayleigh
    else:
        row['G_DAMPING'] = 'PASS' if (zeta <= 0.05 + 1e-12 and scope == 'STRUCTURAL_REGION') else 'REVIEW'
    row['T1_s'] = (modal.get('periods_s') or [None])[0]
    return row


def read_run_matrix(run_root):
    """Planned configurations from 00_SOIL_C_M0_M6_RUN_MATRIX.csv (if present).

    [REF components/nonlinear_time_history/soil_c_run_matrix.py]
    """
    path = Path(run_root) / '00_SOIL_C_M0_M6_RUN_MATRIX.csv'
    if not path.exists():
        return []
    with open(path, encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


def summarize(rows):
    """Mean of accepted cases per variant x limit state.

    [REF R10 NBC105-2025 §9.3.3; AGENTS.md: failed/nonconverged data excluded]
    """
    out = []
    for state in ('ULS', 'SLS'):
        for v in VARIANTS:
            sel = [r for r in rows if r['variant'] == v and r['limit_state'] == state]
            acc = [r for r in sel if r['G_COMPLETE'] == 'PASS']

            def mean(key):
                vals = [r[key] for r in acc if isinstance(r.get(key), (int, float))]
                return sum(vals) / len(vals) if vals else None
            out.append(dict(
                variant=v, limit_state=state, cases_found=len(sel), cases_accepted=len(acc),
                events_accepted=len({r['event'] for r in acc}),
                mean_peak_drift_X=mean('peak_drift_X'), mean_peak_drift_Y=mean('peak_drift_Y'),
                mean_peak_roof_UX_m=mean('peak_roof_UX_m'), mean_peak_roof_UY_m=mean('peak_roof_UY_m'),
                mean_peak_base_shear_X_kN=mean('peak_base_shear_X_kN'),
                mean_peak_base_shear_Y_kN=mean('peak_base_shear_Y_kN'),
                mean_device_energy_share=mean('device_energy_share'),
                drift_limit=DRIFT_LIMIT[state],
                aggregation='MEAN_OF_ACCEPTED' if acc else 'NO_ACCEPTED_CASES'))
    return out


def build_workbook(run_root, out_path):
    """Write the dashboard workbook; return a small JSON-able summary.

    [REF R10 NBC105-2025 §5.5.3, §9.3.3; docs/00_THESIS_ACCEPTANCE_GATES.md]
    """
    from openpyxl import Workbook
    from openpyxl.formatting.rule import CellIsRule
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    cases = discover_cases(run_root)
    rows = [case_row(c) for c in cases]
    planned = read_run_matrix(run_root)
    wb = Workbook()
    ws = wb.active
    ws.title = 'README'
    lines = [
        ['NLTHA run-matrix dashboard — damped-outrigger high-rise, NBC 105:2025'],
        ['Run root', str(Path(run_root).resolve())],
        ['Cases discovered', len(cases)], ['Planned configurations', len(planned)],
        ['Scope', 'Numerical screens only. PASS is NOT design acceptance or NBC compliance.'],
        [],
        ['Gate', 'Definition', 'Basis'],
        *[list(g) for g in GATES],
        [],
        ['Colours', 'PASS green, FAIL red, REVIEW amber, NOT_RUN grey'],
        ['Aggregation', 'Summary_Variant averages ACCEPTED cases only (NBC §9.3.3 as implemented in repo).'],
        ['Drift note', 'NBC §9.3.3.1 cites 5.6 although drift limits are in 5.5.3 (retained discrepancy, R10).'],
    ]
    for line in lines:
        ws.append(line)
    ws['A1'].font = Font(bold=True, size=13)
    for cell in ws[7]:
        cell.font = Font(bold=True)
    ws.column_dimensions['A'].width = 18
    ws.column_dimensions['B'].width = 80
    ws.column_dimensions['C'].width = 32

    def sheet(name, records, status_cols=()):
        sh = wb.create_sheet(name)
        if not records:
            sh.append(['No records found'])
            return sh
        headers = list(dict.fromkeys(k for r in records for k in r))
        sh.append(headers)
        for r in records:
            sh.append([r.get(h) for h in headers])
        for cell in sh[1]:
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill('solid', fgColor='2B4C7E')
            cell.alignment = Alignment(wrap_text=True, vertical='center')
        sh.freeze_panes = 'A2'
        sh.auto_filter.ref = sh.dimensions
        for i, h in enumerate(headers, 1):
            sh.column_dimensions[get_column_letter(i)].width = max(10, min(45, len(h) + 2))
            if h in status_cols:
                col = get_column_letter(i)
                rng = f'{col}2:{col}{len(records) + 1}'
                for value, color in FILL.items():
                    sh.conditional_formatting.add(rng, CellIsRule(
                        operator='equal', formula=[f'"{value}"'], fill=PatternFill('solid', fgColor=color)))
        return sh

    gate_cols = [g[0] for g in GATES]
    # Run matrix: planned config x orientation joined to the discovered result.
    index = {(r['variant'], r['limit_state'], r['event'].replace('_', ' '), r['orientation']): r for r in rows}
    matrix = []
    for p in planned:
        for orient in ('XY', 'YX'):
            key = (p['variant'], p['limit_state'], p['earthquake'], orient)
            r = index.get(key, {})
            matrix.append(dict(order=p['order'], variant=p['variant'], limit_state=p['limit_state'],
                               earthquake=p['earthquake'], orientation=orient,
                               field_group=p.get('study_field_group'),
                               blocking_review=p.get('blocking_review'),
                               result_found='YES' if r else 'NO',
                               **{g: r.get(g, 'NOT_RUN') for g in gate_cols},
                               peak_drift_X=r.get('peak_drift_X'), peak_drift_Y=r.get('peak_drift_Y')))
    sheet('Run_Matrix', matrix, gate_cols)
    sheet('Case_Results', rows, gate_cols)
    summary = summarize(rows)
    sheet('Summary_Variant', summary)
    counts = []
    for v in VARIANTS + ('UNASSIGNED',):
        sel = [r for r in rows if r['variant'] == v]
        if not sel and v == 'UNASSIGNED':
            continue
        for g in gate_cols:
            counts.append(dict(variant=v, gate=g, **{s: sum(r.get(g) == s for r in sel)
                                                    for s in ('PASS', 'FAIL', 'REVIEW', 'NOT_RUN')}))
    sheet('Gate_Counts', counts)
    if summary and any(s['mean_peak_drift_X'] is not None for s in summary):
        from openpyxl.chart import BarChart, Reference
        sh = wb['Summary_Variant']
        headers = [c.value for c in sh[1]]
        chart = BarChart()
        chart.title = 'Mean peak drift (accepted cases)'
        chart.y_axis.title = 'Drift ratio'
        for key in ('mean_peak_drift_X', 'mean_peak_drift_Y'):
            col = headers.index(key) + 1
            chart.add_data(Reference(sh, min_col=col, min_row=1, max_row=len(summary) + 1), titles_from_data=True)
        chart.set_categories(Reference(sh, min_col=1, min_row=2, max_row=len(summary) + 1))
        chart.width, chart.height = 22, 10
        sh.add_chart(chart, 'A' + str(len(summary) + 4))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)
    return dict(workbook=str(out_path), cases=len(rows), planned=len(planned),
                accepted=sum(r['G_COMPLETE'] == 'PASS' for r in rows))


def main(argv=None):
    """Command-line entry. [REF docs/source/tools/export_dashboard.py.md]"""
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--run-root', required=True)
    p.add_argument('--out', required=True, help='output .xlsx path')
    a = p.parse_args(argv)
    print(json.dumps(build_workbook(a.run_root, a.out), indent=2))


if __name__ == '__main__':
    main()

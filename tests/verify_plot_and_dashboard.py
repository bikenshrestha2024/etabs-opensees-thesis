"""tools/plot_results.py and tools/export_dashboard.py on a synthetic run tree.

[REF R10 NBC105-2025 §5.5.3 drift screen, §9.3.3 mean of accepted responses]
[REF Chopra (storey shear from storey mass x absolute acceleration)]
Solver-free: the synthetic numbers test parsing, aggregation and gate logic,
not any structural response of the thesis building.
"""
import csv
import json
import math
import tempfile
import unittest
from pathlib import Path

from tools.plot_results import case_envelopes, discover_cases, make_all, mean_envelope
from tools.export_dashboard import build_workbook, case_row


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def make_case(root, variant, state, event, orient, *, amp, accepted=True, failed=False):
    run = root / 'results' / variant / state / event
    case = run / orient
    case.mkdir(parents=True, exist_ok=True)
    (run / 'isolated_model').mkdir(exist_ok=True)
    (run / 'isolated_model' / 'OpenSees_Complete_Model_Data_V118.json').write_text(json.dumps(dict(
        base_z_m=0.,
        nodal_mass={'11': 100., '12': 100., '21': 80., '22': 80.},
        diaphragms=[dict(storey_number=1, master_tag=1001, master_xyz=[0, 0, 4.], slave_node_tags=[11, 12]),
                    dict(storey_number=2, master_tag=1002, master_xyz=[0, 0, 8.], slave_node_tags=[21, 22])])))
    rows = []
    for k in range(101):
        t = k * .01
        a1, a2 = amp * math.sin(6 * t), 2 * amp * math.sin(6 * t)
        row = dict(time_s=t, base_shear_X_kN=amp * 10 * math.sin(6 * t), base_shear_Y_kN=0.)
        for name, a, d in (('Storey_1', a1, .004), ('Storey_2', a2, .006)):
            row.update({f'{name}_UX_m': d * amp * math.sin(6 * t), f'{name}_UY_m': 0.,
                        f'{name}_drift_X': d * amp * math.sin(6 * t), f'{name}_drift_Y': d * amp * .5 * math.sin(6 * t),
                        f'{name}_UX_absolute_accel_m_s2': a, f'{name}_UY_absolute_accel_m_s2': .5 * a})
        rows.append(row)
    write_csv(case / 'Building_Nonlinear_history.csv', rows)
    (case / 'Case_Summary.json').write_text(json.dumps(dict(
        variant_id=variant, pair_id=event, limit_state=state, orientation=orient, status='COMPLETED')))
    (case / 'Accepted_History_Completion_Gate.json').write_text(json.dumps(dict(
        status='FULL_DURATION_NUMERIC_SCREEN' if accepted else 'TRUNCATED')))
    if failed:
        (case / 'FAILED.json').write_text('{}')
    (case / 'Initial_Modal_Damping.json').write_text(json.dumps(dict(
        eigenvalues=[39.48, 400.], periods_s=[1.0, .314], alphaM=.2, betaKcomm=.002,
        inherent_damping_ratio=.025, rayleigh_scope='STRUCTURAL_REGION')))
    erows = [dict(time_s=k * .1, input_kJ=k, gravity_work_kJ=0., kinetic_kJ=.1 * k, rayleigh_kJ=.3 * k,
                  strain_hysteretic_kJ=.3 * k, device_kJ=.3 * k, sum_kJ=k, error_kJ=0., relative_error=0.)
             for k in range(11)]
    write_csv(case / 'Energy_Balance.csv', erows)
    (case / 'Energy_Balance.json').write_text(json.dumps(dict(
        status='PASS', tolerance=.05, max_relative_error=0., final=erows[-1])))
    write_csv(case / 'Device_Accepted_Step_History.csv', [
        dict(time_s=k * .01, element_tag=900, device_kind='FVD', relative_displacement_m=.01 * math.sin(k / 5),
             signed_force_kN=100 * math.cos(k / 5)) for k in range(60)])
    return case


class Tools(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'run'
        make_case(self.root, 'M0', 'ULS', 'Kobe', 'XY', amp=1.)
        make_case(self.root, 'M0', 'ULS', 'Kobe', 'YX', amp=3.)
        make_case(self.root, 'M1', 'ULS', 'Kobe', 'XY', amp=1., accepted=False)
        make_case(self.root, 'M1', 'ULS', 'Kobe', 'YX', amp=9., failed=True, accepted=False)
        with open(self.root / '00_SOIL_C_M0_M6_RUN_MATRIX.csv', 'w', newline='', encoding='utf-8') as fh:
            w = csv.writer(fh)
            w.writerow(['order', 'variant', 'limit_state', 'earthquake', 'orientations', 'expected_analysis_count',
                        'study_field_group', 'config_file', 'output_directory', 'status', 'blocking_review'])
            w.writerow([1, 'M0', 'ULS', 'Kobe', 'XY + YX', 2, 'NEAR', 'c', 'o', 'NOT_EXECUTED', 'X'])
            w.writerow([2, 'M2', 'ULS', 'Kobe', 'XY + YX', 2, 'NEAR', 'c', 'o', 'NOT_EXECUTED', 'X'])

    def tearDown(self):
        self.tmp.cleanup()

    def test_storey_shear_from_inertia_matches_hand_calculation(self):
        case = next(c for c in discover_cases(self.root) if c['variant'] == 'M0' and c['orientation'] == 'XY')
        env = case_envelopes(case)
        a = max(abs(math.sin(6 * k * .01)) for k in range(101))
        # Storey 1 shear = 200 t*a1 + 160 t*a2 (a2 = 2 a1); storey 2 = 160*a2.
        self.assertAlmostEqual(env['shear']['X'][0], (200 + 160 * 2) * a, places=9)
        self.assertAlmostEqual(env['shear']['X'][1], 160 * 2 * a, places=9)
        # OTM about base: 200*a*4 + 320*a*8.
        self.assertAlmostEqual(env['overturning']['X'][0], (200 * 4 + 320 * 8) * a, places=9)
        self.assertAlmostEqual(env['roof']['height_m'], 8.)
        self.assertAlmostEqual(mean_envelope([[1, 2], [3, 4]])[1], 3)

    def test_figures_and_workbook(self):
        from openpyxl import load_workbook
        out = Path(self.tmp.name) / 'fig'
        res = make_all(self.root, out)
        self.assertEqual(res['cases_found'], 4)
        for key in ('workflow', 'envelopes_ULS', 'roof_drift', 'device_loops', 'energy', 'modal'):
            self.assertTrue(res[key], key)
            self.assertTrue(all(Path(p).exists() for p in res[key]), key)
        with open(out / 'Story_Envelopes_ULS.csv', encoding='utf-8-sig') as fh:
            env = list(csv.DictReader(fh))
        m0 = [r for r in env if r['variant'] == 'M0' and r['quantity'] == 'drift' and r['axis'] == 'X'
              and r['storey'] == 'Storey_2']
        self.assertAlmostEqual(float(m0[0]['mean_peak']), .006 * (1 + 3) / 2 * max(
            abs(math.sin(6 * k * .01)) for k in range(101)), places=12)
        xlsx = Path(self.tmp.name) / 'dash.xlsx'
        info = build_workbook(self.root, xlsx)
        self.assertEqual((info['cases'], info['planned'], info['accepted']), (4, 2, 2))
        wb = load_workbook(xlsx)
        self.assertEqual(wb.sheetnames, ['README', 'Run_Matrix', 'Case_Results', 'Summary_Variant', 'Gate_Counts'])
        summary = {(r[0].value, r[1].value): r for r in wb['Summary_Variant'].iter_rows(min_row=2)}
        headers = [c.value for c in wb['Summary_Variant'][1]]
        m1 = summary[('M1', 'ULS')]
        self.assertEqual(m1[headers.index('cases_accepted')].value, 0)
        self.assertEqual(m1[headers.index('aggregation')].value, 'NO_ACCEPTED_CASES')
        matrix = list(wb['Run_Matrix'].iter_rows(min_row=2, values_only=True))
        self.assertEqual(len(matrix), 4)          # 2 planned configs x XY/YX

    def test_gates(self):
        cases = {(c['variant'], c['orientation']): c for c in discover_cases(self.root)}
        ok = case_row(cases[('M0', 'XY')])
        self.assertEqual((ok['G_RUN'], ok['G_COMPLETE'], ok['G_ENERGY'], ok['G_DRIFT'], ok['G_DAMPING']),
                         ('PASS', 'PASS', 'PASS', 'PASS', 'PASS'))
        big = case_row(cases[('M0', 'YX')])        # drift 0.018 < 0.025 still PASS
        self.assertEqual(big['G_DRIFT'], 'PASS')
        failed = case_row(cases[('M1', 'YX')])
        self.assertEqual((failed['G_RUN'], failed['G_COMPLETE'], failed['G_DRIFT']), ('FAIL', 'FAIL', 'NOT_RUN'))


if __name__ == '__main__':
    unittest.main()

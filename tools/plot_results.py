"""Thesis figures from completed NLTHA output folders (matplotlib, read-only).

[REF R10 NBC105-2025 §5.5.3 (interstorey drift 0.025 ULS / 0.006 SLS screen), §9.3.3 (response aggregation)]
[REF Uang & Bertero 1990 (energy balance)]
[REF Chopra, Dynamics of Structures (storey shear from inertia forces; response spectrum)]

Usage (Anaconda prompt, env etabs_env312; no extra packages):
    python tools/plot_results.py --run-root D:/Thesis/SoilC_Matrix --out D:/Thesis/Figures
    python tools/plot_results.py --run-root ... --zone-Z 0.35 --importance-I 1.0   # adds NBC target
    python tools/plot_results.py --flowchart-only --out D:/Thesis/Figures

Reads only files the runners already write:
    <case>/Building_Nonlinear_history.csv     storey U, drift, abs. accel, base shear
    <case>/Case_Summary.json                  variant_id, pair_id, limit_state, status
    <case>/Accepted_History_Completion_Gate.json
    <case>/Device_Accepted_Step_History.csv   FVD/BRB force-displacement
    <case>/Energy_Balance.csv                 (energy_balance=true runs)
    <case>/Initial_Modal_Damping.json         periods and Rayleigh ratios
    <run>/isolated_model/OpenSees_Complete_Model_Data_V118.json  storey masses, heights
    <run>/RunConfig.json                      record paths for spectra
Nothing is re-analysed and nothing is approved. Cases whose completion gate is
not FULL_DURATION_NUMERIC_SCREEN are drawn dashed and labelled EXPLORATORY,
and are excluded from the §9.3.3 mean envelope.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

VARIANTS = ('M0', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6')
ACCEPTED_GATE = 'FULL_DURATION_NUMERIC_SCREEN'
# [REF R10 NBC105-2025 §5.5.3] drift screens; §9.3.3.1 cross-reference
# discrepancy (cites 5.6) is retained as documented in docs/00_RESEARCH_REFERENCES.md.
DRIFT_LIMIT = {'ULS': 0.025, 'SLS': 0.006}


# ---------------------------------------------------------------- discovery
def discover_cases(run_root):
    """Find every case folder containing Building_Nonlinear_history.csv.

    [REF components/nonlinear_time_history/soil_c_run_matrix.py layout]
    results/<variant>/<ULS|SLS>/<event>/<XY|YX>. Metadata are read from
    Case_Summary.json when present, else inferred from folder names.
    Output: list of dicts (path, run_dir, variant, limit_state, event,
    orientation, status, accepted).
    """
    cases = []
    for hist in sorted(Path(run_root).rglob('Building_Nonlinear_history.csv')):
        case = hist.parent
        summary = _read_json(case / 'Case_Summary.json') or {}
        gate = _read_json(case / 'Accepted_History_Completion_Gate.json') or {}
        parts = case.parts
        variant = summary.get('variant_id')
        if variant in (None, 'UNASSIGNED'):
            variant = next((p for p in parts if p in VARIANTS), 'UNASSIGNED')
        state = summary.get('limit_state') or next((p for p in parts if p in ('ULS', 'SLS')), 'ULS')
        gate_status = gate.get('status', 'NO_COMPLETION_GATE')
        cases.append(dict(
            path=case, run_dir=case.parent, variant=variant, limit_state=state,
            event=str(summary.get('pair_id') or (parts[-2] if len(parts) > 1 else '?')).replace('_', ' '),
            orientation=summary.get('orientation') or case.name,
            status=summary.get('status', 'NO_CASE_SUMMARY'), gate=gate_status,
            accepted=gate_status == ACCEPTED_GATE,
            failed=(case / 'FAILED.json').exists()))
    return cases


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError, ValueError):
        return None


def read_csv_columns(path):
    """Read a numeric CSV into {column: [float]} (non-numeric -> NaN).

    [REF components/shared/response_recorders.py column naming]
    """
    with open(path, encoding='utf-8-sig', newline='') as fh:
        rows = list(csv.DictReader(fh))
    cols = {}
    for r in rows:
        for k, v in r.items():
            try:
                x = float(v)
            except (TypeError, ValueError):
                x = float('nan')
            cols.setdefault(k, []).append(x)
    return cols


def story_names(columns):
    """Storey labels in elevation order from '<Storey_n>_drift_X' columns.

    [REF components/nonlinear_time_history/building_exploratory.py (Storey_<n> naming)]
    """
    names = [k[:-len('_drift_X')] for k in columns if k.endswith('_drift_X')]
    return sorted(names, key=lambda s: int(s.rsplit('_', 1)[1]) if s.rsplit('_', 1)[1].isdigit() else 0)


def story_masses_and_heights(run_dir):
    """Storey seismic mass (t) and elevation (m) from the isolated model export.

    [REF NBC105-2025 seismic weight per repo mass_factors; Chopra (lumped storey mass)]
    Sum of translational X nodal mass over each rigid-diaphragm group (master +
    slaves). Returns ({story_name: mass_t}, {story_name: z_m}, base_z_m) or None.
    """
    model = _read_json(Path(run_dir) / 'isolated_model' / 'OpenSees_Complete_Model_Data_V118.json')
    if model is None:
        model = _read_json(Path(run_dir).parent / 'isolated_model' / 'OpenSees_Complete_Model_Data_V118.json')
    if not model:
        return None
    nodal = model.get('nodal_mass', {})
    masses, heights = {}, {}
    for g in model.get('diaphragms', []):
        name = 'Storey_' + str(g['storey_number'])
        tags = [g['master_tag'], *g.get('slave_node_tags', [])]
        masses[name] = sum(float(nodal.get(str(t), 0.)) for t in tags)
        heights[name] = float(g['master_xyz'][2])
    return masses, heights, float(model.get('base_z_m', 0.))


def case_envelopes(case):
    """Peak |drift|, storey shear and overturning moment per storey and axis.

    [REF R10 §5.5.3 drift] drift from recorded '<storey>_drift_<axis>'.
    [REF Chopra; inertia-force method] V_i(t)=sum_{j>=i} m_j a_abs,j(t);
    M_i(t)=sum_{j>i} m_j a_abs,j(t)(z_j - z_i) about the storey-i floor;
    damping forces are neglected (stated on the figure).
    Output: dict with lists aligned to storey order, or None for drift only.
    """
    cols = read_csv_columns(case['path'] / 'Building_Nonlinear_history.csv')
    names = story_names(cols)
    out = dict(stories=names, drift={}, shear={}, overturning={}, roof=None)
    for ax in ('X', 'Y'):
        out['drift'][ax] = [max(abs(v) for v in cols[n + '_drift_' + ax]) for n in names]
    mh = story_masses_and_heights(case['run_dir'])
    if mh and all(n + '_UX_absolute_accel_m_s2' in cols for n in names):
        masses, heights, base = mh
        nt = len(cols['time_s'])
        for ax in ('X', 'Y'):
            acc = {n: cols[n + '_U' + ax + '_absolute_accel_m_s2'] for n in names}
            shear_env, mom_env = [], []
            for i, n in enumerate(names):
                above = names[i:]
                z0 = heights.get(names[i - 1], base) if i else base
                v_peak = m_peak = 0.
                for k in range(nt):
                    v = sum(masses.get(m, 0.) * acc[m][k] for m in above)
                    mo = sum(masses.get(m, 0.) * acc[m][k] * (heights.get(m, 0.) - z0) for m in above)
                    v_peak, m_peak = max(v_peak, abs(v)), max(m_peak, abs(mo))
                shear_env.append(v_peak)
                mom_env.append(m_peak)
            out['shear'][ax], out['overturning'][ax] = shear_env, mom_env
    roof = names[-1] if names else None
    if roof and mh:
        h = mh[1].get(roof, 0.) - mh[2]
        if h > 0:
            out['roof'] = dict(time=cols['time_s'],
                               X=[u / h for u in cols[roof + '_UX_m']],
                               Y=[u / h for u in cols[roof + '_UY_m']], height_m=h)
    return out


def mean_envelope(envs):
    """NBC 105 §9.3.3 aggregation used in this repo: mean of accepted peaks.

    [REF R10 NBC105-2025 §9.3.3; AGENTS.md (average of complete accepted responses)]
    """
    if not envs:
        return None
    n = len(envs[0])
    return [sum(e[i] for e in envs) / len(envs) for i in range(n)]


# ------------------------------------------------------------------ figures
def _plt():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    return plt


def _variant_colors():
    plt = _plt()
    cmap = plt.get_cmap('tab10')
    return {v: cmap(i) for i, v in enumerate(VARIANTS)}


def plot_story_envelopes(cases, out_dir, limit_state='ULS'):
    """Drift / shear / overturning envelopes per M0-M6 (mean of accepted cases).

    [REF R10 §5.5.3 drift limit line; §9.3.3 mean aggregation]
    Writes Story_Envelopes_<state>.png and .csv. Returns written paths.
    """
    plt = _plt()
    colors = _variant_colors()
    sel = [c for c in cases if c['limit_state'] == limit_state and not c['failed']]
    if not sel:
        return []
    fig, axes = plt.subplots(2, 3, figsize=(15, 10), sharey=True)
    rows = []
    for v in VARIANTS + ('UNASSIGNED',):
        vc = [c for c in sel if c['variant'] == v]
        if not vc:
            continue
        envs = [(c, case_envelopes(c)) for c in vc]
        accepted = [e for c, e in envs if c['accepted']]
        source, style, label = (accepted, '-', v) if accepted else ([e for _, e in envs], '--', v + ' EXPLORATORY')
        names = source[0]['stories']
        levels = list(range(1, len(names) + 1))
        for r, ax_name in enumerate(('X', 'Y')):
            for col, (key, scale, unit) in enumerate((('drift', 100., '%'), ('shear', 1e-3, 'MN'),
                                                     ('overturning', 1e-3, 'MN·m'))):
                data = [e[key].get(ax_name) for e in source if e[key].get(ax_name)]
                m = mean_envelope(data)
                if not m:
                    continue
                axes[r][col].plot([x * scale for x in m], levels, style, marker='o', ms=3,
                                  color=colors.get(v, 'k'), label=label + f' (n={len(data)})')
                for lvl, name, val in zip(levels, names, m):
                    rows.append(dict(limit_state=limit_state, variant=v, accepted_only=bool(accepted),
                                     cases=len(data), axis=ax_name, quantity=key, storey=name,
                                     level=lvl, mean_peak=val))
    for r, ax_name in enumerate(('X', 'Y')):
        lim = DRIFT_LIMIT.get(limit_state)
        if lim:
            axes[r][0].axvline(lim * 100, color='r', lw=1, ls=':', label=f'NBC §5.5.3 {limit_state} screen')
        axes[r][0].set_xlabel(f'Peak interstorey drift {ax_name} (%)')
        axes[r][1].set_xlabel(f'Peak storey shear {ax_name} (MN, inertia-force method)')
        axes[r][2].set_xlabel(f'Peak overturning moment {ax_name} (MN·m)')
        axes[r][0].set_ylabel('Storey level')
        for a in axes[r]:
            a.grid(alpha=.3)
    axes[0][0].legend(fontsize=7)
    fig.suptitle(f'{limit_state} storey envelopes — mean of accepted cases per variant '
                 '(dashed = exploratory, not accepted)\nShear/OTM from storey mass × absolute '
                 'acceleration; damping forces neglected')
    fig.tight_layout()
    out = Path(out_dir)
    png = out / f'Story_Envelopes_{limit_state}.png'
    fig.savefig(png, dpi=150)
    plt.close(fig)
    csv_path = _write_rows(out / f'Story_Envelopes_{limit_state}.csv', rows)
    return [png, csv_path]


def plot_roof_drift(cases, out_dir, max_cases=8):
    """Roof drift ratio histories (roof displacement / building height).

    [REF R10 §5.5.3 context; recorded storey master displacement]
    """
    plt = _plt()
    written = []
    sel = [c for c in cases if not c['failed']][:max_cases]
    if not sel:
        return written
    fig, axes = plt.subplots(len(sel), 1, figsize=(12, 2.4 * len(sel)), sharex=True, squeeze=False)
    for ax, c in zip(axes[:, 0], sel):
        env = case_envelopes(c)
        if not env['roof']:
            ax.text(.5, .5, 'No model export beside this run: height unknown', ha='center',
                    transform=ax.transAxes)
            continue
        r = env['roof']
        ax.plot(r['time'], [x * 100 for x in r['X']], lw=.8, label='X')
        ax.plot(r['time'], [x * 100 for x in r['Y']], lw=.8, label='Y')
        tag = '' if c['accepted'] else '  [EXPLORATORY]'
        ax.set_title(f"{c['variant']} {c['limit_state']} {c['event']} {c['orientation']}{tag}", fontsize=9)
        ax.set_ylabel('Roof drift (%)')
        ax.grid(alpha=.3)
        ax.legend(fontsize=7, loc='upper right')
    axes[-1, 0].set_xlabel('Time (s)')
    fig.tight_layout()
    png = Path(out_dir) / 'Roof_Drift_Histories.png'
    fig.savefig(png, dpi=150)
    plt.close(fig)
    return [png]


def plot_device_loops(cases, out_dir, per_case=6):
    """Force-displacement loops of the most loaded FVD/BRB devices per case.

    [REF Constantinou, Soong & Dargush 1998 (FVD loops); Black, Makris & Aiken 2004 (BRB)]
    Sign convention is reported UNVERIFIED by device_recording.py.
    """
    plt = _plt()
    written = []
    for c in cases:
        path = c['path'] / 'Device_Accepted_Step_History.csv'
        if not path.exists():
            continue
        with open(path, encoding='utf-8-sig', newline='') as fh:
            rows = list(csv.DictReader(fh))
        by = {}
        for r in rows:
            by.setdefault((r['element_tag'], r.get('device_kind', '?')), []).append(r)
        top = sorted(by.items(), key=lambda kv: -max(abs(float(r['signed_force_kN'])) for r in kv[1]))[:per_case]
        n = len(top)
        fig, axes = plt.subplots(1, n, figsize=(3.4 * n, 3.4), squeeze=False)
        for ax, ((tag, kind), rs) in zip(axes[0], top):
            ax.plot([float(r['relative_displacement_m']) * 1000 for r in rs],
                    [float(r['signed_force_kN']) for r in rs], lw=.7)
            ax.set_title(f'{kind} {tag}', fontsize=9)
            ax.set_xlabel('Deformation (mm)')
            ax.grid(alpha=.3)
        axes[0][0].set_ylabel('Force (kN)')
        fig.suptitle(f"Device loops — {c['variant']} {c['limit_state']} {c['event']} {c['orientation']} "
                     '(sign convention UNVERIFIED; demand only)', fontsize=10)
        fig.tight_layout()
        png = Path(out_dir) / f"Device_Loops_{_slug(c)}.png"
        fig.savefig(png, dpi=150)
        plt.close(fig)
        written.append(png)
    return written


def plot_energy(cases, out_dir):
    """Stacked energy components with input energy and balance error.

    [REF Uang & Bertero 1990; Christopoulos & Filiatrault 2006]
    """
    plt = _plt()
    written = []
    for c in cases:
        path = c['path'] / 'Energy_Balance.csv'
        if not path.exists():
            continue
        e = read_csv_columns(path)
        t = e['time_s']
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True,
                                     gridspec_kw=dict(height_ratios=[3, 1]))
        comps = [('kinetic_kJ', 'Kinetic'), ('strain_hysteretic_kJ', 'Strain + hysteretic (frame/core/slab)'),
                 ('device_kJ', 'Devices / braces'), ('rayleigh_kJ', 'Rayleigh (inherent)')]
        a1.stackplot(t, *[e[k] for k, _ in comps], labels=[l for _, l in comps], alpha=.8)
        total_in = [i + g for i, g in zip(e['input_kJ'], e.get('gravity_work_kJ', [0.] * len(t)))]
        a1.plot(t, total_in, 'k', lw=1.2, label='Input + gravity work')
        a1.set_ylabel('Energy (kJ)')
        a1.legend(fontsize=8, loc='upper left')
        a1.grid(alpha=.3)
        a2.plot(t, [x * 100 for x in e['relative_error']], 'r', lw=.8)
        summary = _read_json(c['path'] / 'Energy_Balance.json') or {}
        tol = summary.get('tolerance')
        if tol:
            a2.axhline(tol * 100, color='k', ls=':', lw=.8)
        a2.set_ylabel('Balance error (%)')
        a2.set_xlabel('Time (s)')
        a2.grid(alpha=.3)
        fig.suptitle(f"Energy balance — {c['variant']} {c['event']} {c['orientation']} "
                     f"[{summary.get('status', 'NO SUMMARY')}]")
        fig.tight_layout()
        png = Path(out_dir) / f"Energy_Balance_{_slug(c)}.png"
        fig.savefig(png, dpi=150)
        plt.close(fig)
        written.append(png)
    return written


def plot_modal_table(cases, out_dir):
    """Period and initial Rayleigh damping-ratio table per variant.

    [REF Chopra Ch. 11 (Rayleigh ratio = aM/2w + bK w/2); NBC105-2025 §8.1.1 (repo citation)]
    Mass participation is NOT recorded by the runner and is not shown.
    """
    plt = _plt()
    seen, rows = set(), []
    for c in cases:
        if c['variant'] in seen:
            continue
        m = _read_json(c['path'] / 'Initial_Modal_Damping.json')
        if not m:
            continue
        seen.add(c['variant'])
        ratios = m.get('initial_modal_damping_ratios') or [
            m['alphaM'] / (2 * math.sqrt(v)) + m['betaKcomm'] * math.sqrt(v) / 2
            for v in m['eigenvalues'] if v > 0]
        for i, (T, z) in enumerate(zip(m['periods_s'], ratios), 1):
            rows.append(dict(variant=c['variant'], mode=i, period_s=T, rayleigh_ratio_pct=100 * z,
                             inherent_target_pct=100 * m.get('inherent_damping_ratio', float('nan'))))
    if not rows:
        return []
    variants = sorted({r['variant'] for r in rows})
    modes = sorted({r['mode'] for r in rows})[:12]
    cell = [[f"{next((r['period_s'] for r in rows if r['variant'] == v and r['mode'] == k), float('nan')):.3f} s / "
             f"{next((r['rayleigh_ratio_pct'] for r in rows if r['variant'] == v and r['mode'] == k), float('nan')):.2f}%"
             for v in variants] for k in modes]
    fig, ax = plt.subplots(figsize=(2.2 + 2.0 * len(variants), .45 * len(modes) + 1.5))
    ax.axis('off')
    table = ax.table(cellText=cell, rowLabels=[f'Mode {k}' for k in modes], colLabels=variants, loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.3)
    ax.set_title('Initial-stiffness periods / Rayleigh damping ratio (post-gravity eigen)\n'
                 'Mass participation not recorded here — verify Tn90 separately', fontsize=10)
    fig.tight_layout()
    png = Path(out_dir) / 'Modal_Table.png'
    fig.savefig(png, dpi=150)
    plt.close(fig)
    return [png, _write_rows(Path(out_dir) / 'Modal_Table.csv', rows)]


def plot_spectra(cases, out_dir, *, soil='C', zone_Z=None, importance_I=None, target_csv=None):
    """5%-damped spectra of each record pair vs the NBC C(T)/Omega_u target.

    [REF R10 NBC105-2025 §4.1.2 Eq. 4.1(2) Fig. 4-2; §9.3.2.2 (0.33-3 factor, lower of two)]
    Target from components/response_spectrum/nbc105_dual_target.target_nltha_g
    ONLY when Z and I are given explicitly (no project value is assumed), or
    from a user target CSV (period_s, Sa_g). Records are read unchanged.
    """
    plt = _plt()
    import numpy as np
    from components.inputs.records import _read_peer_text_record
    from components.response_spectrum.site_spectrum_and_scaling import response_spectrum_5pct
    periods = np.round(np.geomspace(.05, 6., 80), 4)
    target = None
    if target_csv:
        t = read_csv_columns(target_csv)
        target = (t['period_s'], t['Sa_g'], 'Target CSV')
    elif zone_Z is not None and importance_I is not None:
        from components.response_spectrum.nbc105_dual_target import target_nltha_g
        target = (periods, [target_nltha_g(T, soil, zoning_Z=zone_Z, importance_I=importance_I)
                            for T in periods], f'NBC C(T)/Ωu soil {soil}, Z={zone_Z}, I={importance_I}')
    runs, written = {}, []
    for c in cases:
        cfg = _read_json(c['run_dir'] / 'RunConfig.json')
        if cfg and cfg.get('x_path'):
            runs.setdefault((c['event'], cfg['x_path'], cfg['y_path']), cfg)
    for (event, xp, yp), cfg in runs.items():
        fig, ax = plt.subplots(figsize=(8, 5))
        for label, path in (('A (X in XY)', xp), ('B (Y in XY)', yp)):
            try:
                values, dt, units = _read_peer_text_record(path)[:3]
            except Exception as exc:  # record not on this machine
                ax.text(.02, .9, f'{label}: {exc}', transform=ax.transAxes, fontsize=7)
                continue
            if str(units).lower() not in ('g', 'acc(g)'):
                values = [v / 9.80665 for v in values]
            sa = response_spectrum_5pct(values, dt, periods)
            ax.loglog(periods, sa, lw=1, label=label)
        if target:
            ax.loglog(target[0], target[1], 'k', lw=2, label=target[2])
        ax.set_xlabel('Period (s)')
        ax.set_ylabel('Sa (g), 5% damped')
        ax.set_title(f'{event}: matched record pair vs target (records unchanged, scale 1.0)')
        ax.grid(which='both', alpha=.3)
        ax.legend(fontsize=8)
        fig.tight_layout()
        png = Path(out_dir) / f"Spectra_{event.replace(' ', '_')}.png"
        fig.savefig(png, dpi=150)
        plt.close(fig)
        written.append(png)
    return written


WORKFLOW = [
    ('00 Provenance', 'Soil C target, record SHA,\n8 A/B pairs, Gorkha/Loma notes', '34_, 35_'),
    ('01 Import / geometry', 'ETABS export, openings,\ndiaphragms, mass, sections', '01_, 02_, 19_'),
    ('02 Materials', 'Wall/frame/FVD/BRB cards,\nnative device checks', '03_ – 09_'),
    ('03 Gravity + P-Δ', 'LoadControl → loadConst(0)\nreaction = weight', '10_, 20_'),
    ('04 Modal / dt', 'T1, Tn90 X/Y, damping modes,\ndt ≤ min(rec dt, T1/100, 0.01)', '11_, 32_'),
    ('05 Damping', 'Region Rayleigh 2.5% on frame/\ncore/slab; devices excluded', 'damping_regions'),
    ('06 Recorders', 'Rel. + abs. accel, drift, devices,\nenergy balance', 'energy_balance'),
    ('07 Excitation', 'UniformExcitation XY & YX,\nPath factor 9.80665, scale 1.0', '17_, 36_'),
    ('08 Transient', 'Newmark avg. accel., Newton →\nKrylov fallbacks, dt bisection', '15_, 21_'),
    ('09 Post-process', 'Energy closure → §9.3.3 mean →\n§5.5.3 drift, devices, M0–M6', '18_, 27_, tools/'),
]


def plot_workflow(out_dir):
    """Order-of-operations flowchart for the OpenSeesPy NLTHA workflow.

    [REF docs/review/00_CANONICAL_RUN_ORDER_AND_NAMING.md; R10 NBC105-2025 §9.3.1-9.3.3]
    Damping (05) is set AFTER the post-gravity eigen analysis (04).
    """
    plt = _plt()
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 2.3)
    ax.axis('off')
    pos = [(i % 5, 1.35 if i < 5 else .25) for i in range(len(WORKFLOW))]
    for i, ((title, body, entry), (x, y)) in enumerate(zip(WORKFLOW, pos)):
        box = FancyBboxPatch((x + .06, y), .88, .7, boxstyle='round,pad=0.02',
                             fc='#e8f0fb' if i < 5 else '#eaf6ea', ec='#2b4c7e', lw=1.2)
        ax.add_patch(box)
        ax.text(x + .5, y + .58, title, ha='center', va='center', fontsize=10, weight='bold')
        ax.text(x + .5, y + .33, body, ha='center', va='center', fontsize=7.5)
        ax.text(x + .5, y + .07, entry, ha='center', va='center', fontsize=7, color='#555')
        if i < len(WORKFLOW) - 1:
            nx, ny = pos[i + 1]
            if ny == y:
                ax.annotate('', (nx + .06, y + .35), (x + .94, y + .35),
                            arrowprops=dict(arrowstyle='->', lw=1.2))
            else:
                ax.annotate('', (nx + .5, ny + .72), (x + .5, y - .02),
                            arrowprops=dict(arrowstyle='->', lw=1.2, connectionstyle='arc3,rad=0'))
    ax.text(2.5, 2.22, 'OpenSeesPy NLTHA order of operations — damped-outrigger high-rise (NBC 105:2025)',
            ha='center', fontsize=12, weight='bold')
    ax.text(2.5, .08, 'Each stage must pass its gate before the next; a failed case stays failed '
            '(no hidden rescaling, trimming or relabelling).', ha='center', fontsize=8, style='italic')
    fig.tight_layout()
    png = Path(out_dir) / 'Workflow_Flowchart.png'
    fig.savefig(png, dpi=170)
    plt.close(fig)
    return [png]


# ------------------------------------------------------------------ helpers
def _slug(c):
    return '_'.join(str(x).replace(' ', '_') for x in (c['variant'], c['limit_state'], c['event'], c['orientation']))


def _write_rows(path, rows):
    path = Path(path)
    if not rows:
        return path
    with open(path, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return path


def make_all(run_root, out_dir, **spectra):
    """Run every figure; return {figure_group: [paths]} (missing inputs are skipped).

    [REF R10 NBC105-2025 §5.5.3, §9.3.3; Uang & Bertero 1990]
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    result = dict(workflow=plot_workflow(out))
    if run_root is None:
        return result
    cases = discover_cases(run_root)
    result['cases_found'] = len(cases)
    for state in ('ULS', 'SLS'):
        result['envelopes_' + state] = plot_story_envelopes(cases, out, state)
    result['roof_drift'] = plot_roof_drift(cases, out)
    result['device_loops'] = plot_device_loops(cases, out)
    result['energy'] = plot_energy(cases, out)
    result['modal'] = plot_modal_table(cases, out)
    result['spectra'] = plot_spectra(cases, out, **spectra)
    (out / 'Figure_Index.json').write_text(json.dumps(
        {k: ([str(p) for p in v] if isinstance(v, list) else v) for k, v in result.items()},
        indent=2), encoding='utf-8')
    return result


def main(argv=None):
    """Command-line entry. [REF docs/source/tools/plot_results.py.md]"""
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--run-root', help='folder containing results/<M?>/<state>/<event>/<XY|YX>')
    p.add_argument('--out', required=True)
    p.add_argument('--flowchart-only', action='store_true')
    p.add_argument('--soil', default='C', choices=('C', 'D'))
    p.add_argument('--zone-Z', type=float)
    p.add_argument('--importance-I', type=float)
    p.add_argument('--target-csv')
    a = p.parse_args(argv)
    if not a.flowchart_only and not a.run_root:
        p.error('--run-root is required unless --flowchart-only')
    res = make_all(None if a.flowchart_only else a.run_root, a.out, soil=a.soil,
                   zone_Z=a.zone_Z, importance_I=a.importance_I, target_csv=a.target_csv)
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in res.items()}, indent=2))


if __name__ == '__main__':
    main()

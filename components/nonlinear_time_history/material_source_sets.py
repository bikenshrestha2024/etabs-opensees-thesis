"""Single-source material sets: every value from ONE paper, gaps labelled.

[REF R01 Kolozvari, Orakcal & Wallace (2015) PEER 2015/12, Appendix B.3 (RW-A15-P10-S78 web materials)]
[REF docs/00_RESEARCH_REFERENCES.md (transfer restrictions)]

The PUBLISHED_REFERENCE basis mixes sources: PEER 2015/12 wall concrete and
steel, the OpenSees primer Concrete01 for frame concrete, nominal Fe500 for
frame rebar, the OpenSees-documented SteelMPF transition, and a user brace
Fy. ``PEER_2015_12_SINGLE_SOURCE`` takes concrete, reinforcing steel
(transition values as printed) and frame concrete/rebar strengths from the
same PEER card. Anything that paper does not give is NOT filled from another
paper. It is labelled MODEL_ASSUMPTION_NOT_IN_SOURCE, NOT_IN_SOURCE or
PROVENANCE_NOT_RECORDED. FVD and BRB have no data in PEER 2015/12; a device
scenario still needs its own citation (sections/mapping_audit.validate_device).
Values are research transfers of a specimen card, not project calibration.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SINGLE_SOURCE_BASIS = 'PEER_2015_12_SINGLE_SOURCE'
BASES = ('PUBLISHED_REFERENCE', 'M30_FE500_SENSITIVITY', SINGLE_SOURCE_BASIS)


def _card(name):
    return json.loads((ROOT / 'Material_Catalog' / name).read_text(encoding='utf-8'))


def peer_single_source():
    """Concrete, steel, frame and FSAM inputs all from PEER 2015/12 Appendix B.3.

    [REF R01 PEER 2015/12 Appendix B.3, printed pp. 90-91]
    Output: dict(wall_concrete, wall_steel, frame_section, fsam, rows) where
    rows is the provenance table (family, parameter, value, unit, status, locator).
    """
    concrete = _card('PEER_Web_ConcreteCM.json')
    steel = _card('PEER_Web_SteelMPF.json')
    patch = _card('PEER_Web_ESFI_Patch.json')
    c = dict(concrete['parameters'])
    s = dict(steel['parameters'])
    # [REF Menegotto & Pinto 1973; Filippou et al. 1983; OpenSees SteelMPF/Steel02]
    # PEER B.3 prints the absolute Menegotto-Pinto term a1=18.5 in
    # R = R0 - a1*xi/(a2+xi). OpenSees uses R = R0*(1 - cR1*xi/(cR2+xi)), so the
    # same-source value is cR1 = a1/R0 = 18.5/20 = 0.925. Passing 18.5 directly
    # makes R negative (NaN on the first reversal; verified natively).
    printed_a1 = s['cR1']
    if s['cR1'] > 1.:
        s['cR1'] = s['cR1'] / s['R0']
    src, loc_c, loc_s = concrete['source'], concrete['citation'], steel['citation']
    frame = dict(cover_fc_mpa=abs(c['fpcc']), core_fcc_mpa=abs(c['fpcc']),
                 cover_epsc0=c['epcc'], core_epsc0=c['epcc'],
                 cover_fcu_mpa=0., core_fpcu_mpa=0., cover_epsU=-.006, core_epsU=-.006,
                 fy_rebar_mpa=s['fyp'], E0_mpa=s['E0'], steel_b=s['bp'],
                 steel_R0=s['R0'], steel_cR1=s['cR1'], steel_cR2=s['cR2'])
    fsam = dict(patch['fsam'])
    rows = []

    def add(family, parameter, value, unit, status, locator):
        rows.append(dict(family=family, parameter=parameter, value=value, unit=unit,
                         status=status, source=src if status == 'FROM_SOURCE' else '',
                         locator=locator))
    for k, v in c.items():
        add('Wall concrete (ConcreteCM)', k, v, 'MPa' if k in ('fpcc', 'Ec', 'ft') else '-', 'FROM_SOURCE', loc_c)
    for k, v in s.items():
        if k == 'cR1' and printed_a1 != v:
            add('Reinforcing steel (SteelMPF)', k, v, '-', 'FROM_SOURCE',
                f'{loc_s}; converted: printed a1={printed_a1:g} / R0={s["R0"]:g} (OpenSees R=R0(1-cR1*xi/(cR2+xi)))')
            continue
        add('Reinforcing steel (SteelMPF)', k, v, 'MPa' if k in ('fyp', 'fyn', 'E0') else '-', 'FROM_SOURCE', loc_s)
    for k in ('cover_fc_mpa', 'cover_epsc0'):
        add('Frame concrete (Concrete01)', k, frame[k], 'MPa' if 'fc' in k else '-', 'FROM_SOURCE',
            'Same PEER web concrete card (fpcc, epcc); unconfined')
    for k in ('cover_fcu_mpa', 'cover_epsU'):
        add('Frame concrete (Concrete01)', k, frame[k], 'MPa' if 'fcu' in k else '-',
            'MODEL_ASSUMPTION_NOT_IN_SOURCE', 'Concrete01 post-peak terms are not in PEER 2015/12')
    for k in ('fy_rebar_mpa', 'E0_mpa', 'steel_b', 'steel_R0', 'steel_cR1', 'steel_cR2'):
        add('Frame rebar (Steel02)', k, frame[k], 'MPa' if k in ('fy_rebar_mpa', 'E0_mpa') else '-',
            'FROM_SOURCE', 'Same PEER web steel card (Steel02 uses the identical Menegotto-Pinto terms)')
    for k, v in fsam.items():
        add('FSAM panel', k, v, '-', 'PROVENANCE_NOT_RECORDED',
            'Value in PEER_Web_ESFI_Patch.json has no recorded locator; verify in PEER 2015/12')
    for family in ('Ordinary SHS brace (Steel01)', 'Fluid viscous damper', 'Buckling-restrained brace'):
        add(family, 'all', None, '-', 'NOT_IN_SOURCE',
            'PEER 2015/12 is an RC wall study; supply a separate cited device/brace card')
    return dict(wall_concrete=c, wall_steel=s, frame_section=frame, fsam=fsam, rows=rows,
                source=src, specimen=concrete.get('specimen_id'))


def source_table(basis):
    """Provenance rows for the GUI/Excel; mixed bases are marked MIXED_SOURCES.

    [REF R01; OpenSees primer Example 3.1; Material_Catalog index]
    """
    if basis == SINGLE_SOURCE_BASIS:
        return peer_single_source()['rows']
    if basis == 'PUBLISHED_REFERENCE':
        return [dict(family='Wall concrete/steel', parameter='card', value='PEER_Web_ESFI_Patch',
                     unit='', status='MIXED_SOURCES', source='PEER 2015/12',
                     locator='SteelMPF transition follows the OpenSees doc unless PEER_APPENDIX_EXACT'),
                dict(family='Frame concrete', parameter='fpc', value=34.47, unit='MPa',
                     status='MIXED_SOURCES', source='OpenSees primer Example 3.1', locator='not PEER 2015/12'),
                dict(family='Frame rebar', parameter='fy', value=500., unit='MPa',
                     status='MIXED_SOURCES', source='Nominal Fe500', locator='not a paper value'),
                dict(family='Brace / FVD / BRB', parameter='all', value=None, unit='',
                     status='NOT_IN_SOURCE', source='', locator='user / device cards')]
    if basis == 'M30_FE500_SENSITIVITY':
        return [dict(family='All', parameter='nominal M30 / Fe500', value=None, unit='',
                     status='NOMINAL_ASSUMPTION', source='Material_Catalog/M30_Fe500_*',
                     locator='02_MODELLING_BASIS.md; not a paper')]
    raise ValueError('Unknown material basis: ' + str(basis))


WALL_KEYS = {'fpcc_mpa': ('c', 'fpcc'), 'epcc': ('c', 'epcc'), 'Ec_mpa': ('c', 'Ec'), 'rc': ('c', 'rc'),
             'xcrn': ('c', 'xcrn'), 'ft_mpa': ('c', 'ft'), 'et': ('c', 'et'), 'rt': ('c', 'rt'),
             'xcrp': ('c', 'xcrp'), 'fyp_mpa': ('s', 'fyp'), 'fyn_mpa': ('s', 'fyn'), 'E0_mpa': ('s', 'E0'),
             'bp': ('s', 'bp'), 'bn': ('s', 'bn'), 'R0': ('s', 'R0'), 'cR1': ('s', 'cR1'), 'cR2': ('s', 'cR2'),
             'a1': ('s', 'a1'), 'a2': ('s', 'a2'), 'a3': ('s', 'a3'), 'a4': ('s', 'a4'),
             'fsam_nu': ('f', 'nu'), 'fsam_alpha': ('f', 'alpha')}


def baseline_values(basis, transition='OPENSEES_DOCUMENTED'):
    """Baseline of every one-at-a-time parameter for the selected basis.

    [REF research_building_materials.define_building_materials (same values)]
    None means the baseline depends on the model (brace E from the section,
    wall rho from wall thickness) and cannot be bracketed generically.
    """
    from components.nonlinear_time_history.research_building_materials import (
        FRAME_OVERRIDE_TARGETS, _steelmpf_transition)
    if basis not in BASES:
        raise ValueError('Unknown material basis: ' + str(basis))
    single = peer_single_source() if basis == SINGLE_SOURCE_BASIS else None
    if basis == 'M30_FE500_SENSITIVITY':
        wall, fc = _card('M30_Fe500_SFI_MVLEM_3D.json'), 24.0
    else:
        wall, fc = _card('PEER_Web_ESFI_Patch.json'), abs(_card('Official_Concrete01.json')['parameters']['fpc_MPa'])
    frame = dict(cover_fc_mpa=fc, core_fcc_mpa=fc, cover_epsc0=-.002, core_epsc0=-.002, cover_fcu_mpa=0.,
                 core_fpcu_mpa=0., cover_epsU=-.006, core_epsU=-.006, fy_rebar_mpa=500., E0_mpa=200000.,
                 steel_b=.01, steel_R0=20., steel_cR1=.925, steel_cR2=.15)
    groups = {'c': dict(wall['wall_concrete']), 's': dict(wall['wall_steel']), 'f': dict(wall['fsam'])}
    if single:
        frame.update(single['frame_section'])
        groups.update(c=dict(single['wall_concrete']), s=dict(single['wall_steel']))
    else:
        groups['s'].update({k: v for k, v in _steelmpf_transition(transition).items() if k != 'basis'})
    out = {'brace.fy_mpa': 345., 'brace.E_mpa': None, 'brace.b': .01,
           'wall.rho_x': None, 'wall.rho_y': None}
    out.update({key: frame[field] for key, field in FRAME_OVERRIDE_TARGETS.items()})
    out.update({'wall.' + k: groups[g].get(field) for k, (g, field) in WALL_KEYS.items()})
    return out


def default_candidates(key, basis, transition='OPENSEES_DOCUMENTED'):
    """'0.9x, 1.0x, 1.1x' of the basis baseline (analyst bracket), or '' with a reason.

    [REF MATERIAL_PARAMETER_REFERENCES['brace.fy_mpa'] candidate rule: analyst +/-10% bracket, not paper bounds]
    Returns (text, note). Values outside MATERIAL_OVERRIDE_BOUNDS are dropped.
    """
    from components.nonlinear_time_history.research_building_materials import MATERIAL_OVERRIDE_BOUNDS
    base = baseline_values(basis, transition).get(key)
    if base is None:
        return '', 'Baseline depends on the model (section modulus or wall thickness); enter reviewed candidates.'
    if base == 0:
        return '', 'Baseline is 0 for this basis; a ratio bracket is undefined. Enter reviewed candidates.'
    lo, hi = MATERIAL_OVERRIDE_BOUNDS.get(key, (float('-inf'), float('inf')))
    vals = []
    for f in (.9, 1., 1.1):
        v = round(base * f, 10)
        a, b = sorted((lo, hi))
        if a <= v <= b and v not in vals:
            vals.append(v)
    if len(vals) < 2:
        return '', f'Baseline {base:g} is at a validation bound; enter reviewed candidates.'
    return ', '.join(f'{v:.6g}' for v in vals), (
        f'Baseline {base:.6g} ({basis}); 0.9/1.0/1.1 is an analyst sensitivity bracket, not paper-reported bounds.')

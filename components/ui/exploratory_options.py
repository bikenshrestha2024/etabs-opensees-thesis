"""Validated diagnostic, damping and case-identity options for the exploratory window.

[REF V168_FIRST_STEP_DIAGNOSTICS.md (ZERO / X / Y / XY probes, zero-damping discriminator)]
[REF components/nonlinear_time_history/damping_regions.py (inherent ratio 0.025, explicit 5% flag)]
[REF components/nonlinear_time_history/soil_c_run_matrix.py (M0-M6 variants, Soil-C event names)]

Before this module these settings existed only as RunConfig.json keys, so the
documented failing probe (Kobe X-only, zero damping) could not be repeated
from the GUI and every GUI run was labelled pair_id UNSPECIFIED /
variant_id UNASSIGNED. The GUI passes plain strings; everything is validated
here so the same rules are testable without a window.
"""
from __future__ import annotations

import math

EXCITATIONS = ('XY', 'X', 'Y', 'ZERO')
DAMPING_MODES = {
    'Rayleigh (configured ratio)': {},
    'ZERO damping (diagnostic)': {'diagnostic_zero_damping': True},
    'Mass-only damping (diagnostic)': {'diagnostic_mass_damping': True},
}
VARIANTS = ('UNASSIGNED', 'M0', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6')
# Record-name fragment -> Soil-C event name used by the run matrix / dashboard.
EVENT_KEYS = (('GORKHA', 'Gorkha'), ('LANDERS', 'Landers'), ('NORTHR', 'Northridge'),
              ('KOBE', 'Kobe'), ('KOCAELI', 'Kocaeli'), ('CHICHI', 'Chi-Chi'),
              ('HECTOR', 'Hector Mine'), ('LOMAP', 'Loma Prieta'))


def event_name(pair_label):
    """Soil-C event name for a catalogue label, else the label itself.

    [REF components/nonlinear_time_history/soil_c_nltha_suite.py FIELD_TYPE]
    Works with plain IDs ('RSN1120_KOBE_TAK000') and Windows folder paths.
    """
    text = str(pair_label or '').replace('\\', '/').rsplit('/', 1)[-1].upper()
    for key, name in EVENT_KEYS:
        if key in text.replace('-', '').replace('_', ''):
            return name
    return text or 'UNSPECIFIED'


def build_options(*, excitation='XY', damping_mode='Rayleigh (configured ratio)',
                  ratio='0.025', allow_above_2_5=False, reference_modes='',
                  energy_balance=False, energy_tolerance='0.05', variant='UNASSIGNED',
                  pair_label=''):
    """Return the RunConfig keys for building_exploratory.run (raises ValueError).

    [REF V168_FIRST_STEP_DIAGNOSTICS.md; PEER TBI 2017 / LATBSDC 2020 (2.5%);
    NBC105-2025 §8.1.1 (repo citation, 5% cap); Uang & Bertero 1990 (energy)]
    reference_modes: '' (exploratory first/last-mode Rayleigh) or two distinct
    1-based mode numbers such as '1, 6'.
    """
    exc = str(excitation).strip().upper()
    if exc not in EXCITATIONS:
        raise ValueError('Excitation must be XY, X, Y or ZERO')
    if damping_mode not in DAMPING_MODES:
        raise ValueError('Unknown damping mode: ' + str(damping_mode))
    out = dict(diagnostic_excitation=exc, **DAMPING_MODES[damping_mode])
    zeta = float(str(ratio).strip())
    if not math.isfinite(zeta) or not 0 < zeta <= 0.05:
        raise ValueError('Inherent damping ratio is a fraction in (0, 0.05], e.g. 0.025')
    if zeta > 0.025 + 1e-12 and not allow_above_2_5:
        raise ValueError('Damping above 0.025 needs the explicit "allow above 2.5%" box')
    out['inherent_damping_ratio'] = zeta
    out['inherent_damping_five_percent'] = bool(allow_above_2_5)
    text = str(reference_modes or '').strip()
    if text:
        try:
            modes = [int(v) for v in text.replace(';', ',').split(',') if v.strip()]
        except ValueError as exc_:
            raise ValueError('Damping reference modes must be two integers, e.g. "1, 6"') from exc_
        if len(modes) != 2 or modes[0] == modes[1] or min(modes) < 1 or max(modes) > 20:
            raise ValueError('Give two distinct 1-based modes within the 20 computed modes')
        out['damping_reference_modes'] = modes
    if energy_balance:
        tol = float(str(energy_tolerance).strip())
        if not math.isfinite(tol) or not 0 < tol < 1:
            raise ValueError('Energy tolerance is a fraction in (0, 1), e.g. 0.05')
        out.update(energy_balance=True, energy_balance_tolerance=tol)
    if variant not in VARIANTS:
        raise ValueError('Variant must be UNASSIGNED or M0..M6')
    out['variant_id'] = variant
    out['pair_id'] = event_name(pair_label)
    return out


def describe(options):
    """One-line run label shown in the status bar and stored with the run.

    [REF V168_FIRST_STEP_DIAGNOSTICS.md] Diagnostic probes are labelled as such.
    """
    damping = ('ZERO damping' if options.get('diagnostic_zero_damping') else
               'mass-only damping' if options.get('diagnostic_mass_damping') else
               f"Rayleigh {100 * options['inherent_damping_ratio']:g}%")
    tag = 'DIAGNOSTIC PROBE' if (options['diagnostic_excitation'] != 'XY' or 'diagnostic_zero_damping' in options
                                 or 'diagnostic_mass_damping' in options) else 'case'
    return (f"{tag}: {options['pair_id']} {options['variant_id']} | excitation {options['diagnostic_excitation']}"
            f" | {damping} | modes {options.get('damping_reference_modes', 'first/last (exploratory)')}"
            f" | energy balance {'on' if options.get('energy_balance') else 'off'}")

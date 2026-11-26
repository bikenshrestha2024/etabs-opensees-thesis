"""NBC 105:2025 clause 7.3 missing-mass correction for modes at or above 33 Hz.

[REF NBC105-2025 §7.3, printed p. 41]
Printed 7.3: "The modal combination shall be carried out only for modes with
natural frequency less than 33 Hz; the effect of modes with natural frequencies
more than 33 Hz shall be included by the missing mass correction procedure
following established principles of structural dynamics." The standard gives no
formula, so this module uses the established residual-rigid-mass (zero period
acceleration) procedure: the part of each storey mass not captured by the
included modes (< 33 Hz) is treated as rigid and loaded statically with the
ZPA coefficient; the residual response is combined with the combined modal
response by SRSS (the combination rule is a choice of the established
procedure, not printed). Exactly 33 Hz is not assigned by the print; here a mode
at 33 Hz goes to the missing-mass side (conservative).

Scope: the calculation works on GIVEN modal data (storey weights, mode shapes of
the included modes in one direction, per-mode effective mass percentages and
frequencies). Integration point for the full building: the eigen solver must
supply the storey mode-shape coefficients and effective masses of the included
modes per direction (components/modal/analysis.py exports per-mode percentages
and story mode shapes) and the MRSM engine must call
``missing_mass_correction_inputs`` per direction and add the residual story
forces to the combined modal story forces. Until that data is wired the MRSM
production gate (``missing_mass_gate``) stays blocked with the exact missing
inputs. Source-to-code review of the arithmetic only; no native OpenSees run.
"""
from __future__ import annotations

import math
from typing import Sequence

__all__ = ["MISSING_MASS_CUTOFF_HZ", "zpa_period_s", "split_modes_by_cutoff",
           "residual_mass_percent", "residual_story_weights", "residual_static_forces",
           "missing_mass_correction_inputs", "combine_modal_and_residual", "missing_mass_gate"]

MISSING_MASS_CUTOFF_HZ = 33.0


def _fin(v, name):
    if isinstance(v, bool):
        raise ValueError(name + " invalid")
    try:
        x = float(v)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(name + " invalid") from exc
    if not math.isfinite(x):
        raise ValueError(name + " must be finite")
    return x


def zpa_period_s():
    """Period of the 33 Hz cut-off, 1/33 s: evaluate the design coefficient Cd here for the ZPA.

    [REF NBC105-2025 §7.3, printed p. 41]
    """
    return 1.0 / MISSING_MASS_CUTOFF_HZ


def split_modes_by_cutoff(frequencies_hz: Sequence[float]):
    """Return (included_indices, missing_mass_indices): f < 33 Hz is combined, f >= 33 Hz is not.

    [REF NBC105-2025 §7.3, printed p. 41]
    Printed "less than 33 Hz" for combination; 33 Hz itself is unassigned and goes to the missing-mass side.
    """
    f = [_fin(v, "frequency") for v in frequencies_hz]
    if any(v <= 0 for v in f):
        raise ValueError("frequencies must be positive")
    inc = [i for i, v in enumerate(f) if v < MISSING_MASS_CUTOFF_HZ]
    miss = [i for i, v in enumerate(f) if v >= MISSING_MASS_CUTOFF_HZ]
    return inc, miss


def residual_mass_percent(modal_mass_percent: Sequence[float], frequencies_hz: Sequence[float]):
    """Missing mass in percent of the total seismic mass in one direction: 100 minus included modes (< 33 Hz).

    [REF NBC105-2025 §7.3, printed pp. 40-41]
    Modes at or above 33 Hz that were extracted are NOT counted as included. A tiny negative
    value from rounding is clipped to zero; more than 1e-6 percent over 100 raises.
    """
    m = [_fin(v, "mass percent") for v in modal_mass_percent]
    if len(m) != len(frequencies_hz) or not m or any(v < 0 for v in m):
        raise ValueError("modal masses and frequencies must match and be nonnegative")
    inc, _ = split_modes_by_cutoff(frequencies_hz)
    covered = math.fsum(m[i] for i in inc)
    if covered > 100.0 + 1e-6:
        raise ValueError("included modal mass exceeds 100 percent")
    return max(0.0, 100.0 - covered)


def residual_story_weights(story_weights: Sequence[float], included_mode_shapes: Sequence[Sequence[float]]):
    """Residual (missing) weight at each storey: w_j (1 - sum_i G_i phi_ji), G_i = sum(w phi_i)/sum(w phi_i^2).

    [REF NBC105-2025 §7.3, printed p. 41; participation per Eq. 7.1(2) printed p. 40]
    ``included_mode_shapes[i][j]`` is phi_ji of included mode i at storey j. The sum of the residual
    weights equals W minus the sum of the effective modal weights of the included modes.
    """
    w = [_fin(v, "storey weight") for v in story_weights]
    if not w or any(v <= 0 for v in w):
        raise ValueError("storey weights must be positive")
    res = list(w)
    for shape in included_mode_shapes:
        phi = [_fin(v, "mode shape") for v in shape]
        if len(phi) != len(w):
            raise ValueError("mode shape length must equal the number of storeys")
        den = math.fsum(wj * p * p for wj, p in zip(w, phi))
        if den <= 0:
            raise ValueError("zero modal mass")
        gamma = math.fsum(wj * p for wj, p in zip(w, phi)) / den
        res = [r - gamma * wj * p for r, wj, p in zip(res, w, phi)]
    return res


def residual_static_forces(residual_weights: Sequence[float], zpa_coefficient: float):
    """Static story forces of the residual rigid mass: F_j = ZPA coefficient x residual weight_j.

    [REF NBC105-2025 §7.3, printed p. 41]
    ``zpa_coefficient`` is the design base-shear coefficient at the cut-off (T = 1/33 s, ``zpa_period_s``)
    from Eq. 7.1(1) (Clause 7 ``modal_design_coefficient``); it is an input, not derived here.
    Returns the story forces and their sum (the residual base shear).
    """
    c = _fin(zpa_coefficient, "ZPA coefficient")
    if c < 0:
        raise ValueError("ZPA coefficient must be nonnegative")
    r = [_fin(v, "residual weight") for v in residual_weights]
    forces = [c * v for v in r]
    return {"story_forces": forces, "base_shear": math.fsum(forces)}


def missing_mass_correction_inputs(story_weights, included_mode_shapes, zpa_coefficient, *,
                                   modal_mass_percent=None, frequencies_hz=None):
    """Residual-mass static/ZPA correction inputs for ONE direction from given modal data.

    [REF NBC105-2025 §7.3, printed pp. 40-41]
    Returns residual weights, residual story forces and base shear, plus (when per-mode percentages and
    frequencies are given) the residual mass percent from ``residual_mass_percent`` for cross-checking:
    the residual weight fraction must equal it when the included shapes are exactly the modes below 33 Hz.
    """
    res = residual_story_weights(story_weights, included_mode_shapes)
    loads = residual_static_forces(res, zpa_coefficient)
    total = math.fsum(float(v) for v in story_weights)
    out = {"residual_weights": res, "residual_weight_percent": 100.0 * math.fsum(res) / total,
           "residual_story_forces": loads["story_forces"], "residual_base_shear": loads["base_shear"],
           "zpa_coefficient": float(zpa_coefficient), "zpa_period_s": zpa_period_s(),
           "combination": "SRSS_WITH_COMBINED_MODAL_RESPONSE_ESTABLISHED_PROCEDURE_NOT_PRINTED"}
    if modal_mass_percent is not None and frequencies_hz is not None:
        out["residual_mass_percent_from_modes"] = residual_mass_percent(modal_mass_percent, frequencies_hz)
    return out


def combine_modal_and_residual(modal_combined_response: float, residual_response: float):
    """SRSS of the combined modal response and the residual (missing-mass) response.

    [REF NBC105-2025 §7.3, printed p. 41]
    The print only says the effect shall be included by an established procedure; SRSS of the
    residual rigid response with the modal response is the established choice (USNRC RG 1.92 form).
    """
    return math.hypot(_fin(modal_combined_response, "modal response"), _fin(residual_response, "residual response"))


def missing_mass_gate(frequencies_hz, modal_mass_percent, *, correction_inputs_supplied=False):
    """Production gate for one direction: is the 33 Hz missing-mass correction needed and available?

    [REF NBC105-2025 §7.3, printed pp. 40-41]
    The correction is needed when an extracted mode is at or above 33 Hz (printed trigger). Status values:
    ``NOT_REQUIRED_ALL_MASS_COVERED`` (no such mode and the included modes carry 100 percent within 1e-4),
    ``NOT_REQUIRED_NO_MODE_AT_OR_ABOVE_33_HZ`` (no such mode; ``residual_mass_percent`` is unextracted mass that
    only the 90 percent rule of 7.3 governs, reported for information),
    ``CORRECTION_INPUTS_SUPPLIED`` (needed and the caller supplied the residual-mass inputs),
    ``BLOCKED_CORRECTION_INPUTS_MISSING`` (needed, not supplied; ``missing`` lists the exact inputs).
    Modes in ``exclude_from_combination`` must not enter the CQC/SRSS combination.
    The 90 percent compliance of 7.3 is separate (``modal_mass_participation_profile``).
    """
    if type(correction_inputs_supplied) is not bool:
        raise ValueError("correction_inputs_supplied must be bool")
    _, high = split_modes_by_cutoff(frequencies_hz)
    resid = residual_mass_percent(modal_mass_percent, frequencies_hz)
    needed = bool(high)
    missing = []
    if needed and not correction_inputs_supplied:
        missing = ["STOREY_MODE_SHAPES_OF_INCLUDED_MODES_IN_DIRECTION", "STOREY_WEIGHTS",
                   "ZPA_DESIGN_COEFFICIENT_AT_T_1_OVER_33_S"]
    status = (("NOT_REQUIRED_ALL_MASS_COVERED" if resid <= 1e-4 else "NOT_REQUIRED_NO_MODE_AT_OR_ABOVE_33_HZ") if not needed else
              "CORRECTION_INPUTS_SUPPLIED" if correction_inputs_supplied else "BLOCKED_CORRECTION_INPUTS_MISSING")
    return {"status": status, "residual_mass_percent": resid, "exclude_from_combination": high,
            "modes_at_or_above_33_Hz": len(high), "missing": missing,
            "basis": "NBC105_2025_7.3_P41_RESIDUAL_RIGID_MASS_ZPA_PROCEDURE_ARITHMETIC_ONLY"}

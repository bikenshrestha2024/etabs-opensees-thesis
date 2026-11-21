"""NBC 105:2025 clause 5 period and seismic-weight helpers (pure Python).

[REF NBC105-2025 §5, printed pp. 28-30] Single source of truth for the
§5.1 lesser-of rule, §5.1.1 Rayleigh period, §5.1.2 empirical period,
§5.1.3 amplification and §5.2 seismic weight. A period computed here is a
design-input calculation, never engineering acceptance of the building.

Equation images 5.1(1), the shear-wall kt equation and Figure 5-1 were not
readable from the PDF text (UNVERIFIED_IMAGE_ONLY); the forms used are the
standard ones recorded in the task brief.
"""
from __future__ import annotations

import math
from typing import Iterable

AMPLIFICATION_FACTOR = 1.25
LWI_OVER_H_MAX = 0.9
KT_BY_SYSTEM = {
    "concrete moment-resisting frame": 0.075,
    "steel moment-resisting frame": 0.085,
    "steel eccentrically braced frame": 0.075,
    "other structural system": 0.05,
}
SHEAR_WALL_KT_NUMERATOR = 0.075
LIVE_LOAD_FACTORS = {"storage": 0.60, "other": 0.30, "roof": 0.0}


def _positive(value, name):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return number


def building_height_m(top_z_m, base_z_m, *, basement_height_m=0.0,
                      basement_excluded=False):
    """Return H = top - base.

    [REF NBC105-2025 §5.1.2 and Figure 5-1, printed p. 29]
    The basement is excluded only when the caller declares the Figure 5-1
    condition true (``basement_excluded=True``); the default includes it.
    When excluded, ``basement_height_m`` is subtracted from H.
    """
    h = float(top_z_m) - float(base_z_m)
    if basement_excluded:
        h -= float(basement_height_m)
    if not math.isfinite(h) or h <= 0:
        raise ValueError("building height must be finite and positive")
    return h


def effective_wall_area_m2(walls: Iterable[tuple[float, float]], height_m):
    """Return Aw = sum(Awi*(0.2+min(Lwi/H, 0.9)**2)) for (Awi, Lwi) walls.

    [REF NBC105-2025 §5.1.2, printed p. 29]
    """
    h = _positive(height_m, "height_m")
    total = 0.0
    count = 0
    for awi, lwi in walls:
        awi = _positive(awi, "Awi")
        lwi = _positive(lwi, "Lwi")
        total += awi * (0.2 + min(lwi / h, LWI_OVER_H_MAX) ** 2)
        count += 1
    if count == 0:
        raise ValueError("at least one wall is required")
    return total


def empirical_period_s(height_m, system_type, aw_m2=None):
    """Return the empirical period kt*H**0.75 (shear walls: kt=0.075/sqrt(Aw)).

    [REF NBC105-2025 §5.1.2, printed p. 29]
    """
    h = _positive(height_m, "height_m")
    system = str(system_type).strip().lower()
    if "concrete shear-wall" in system:
        if aw_m2 is None:
            raise ValueError("aw_m2 is required for a concrete shear-wall system")
        kt = SHEAR_WALL_KT_NUMERATOR / math.sqrt(_positive(aw_m2, "aw_m2"))
    elif system in KT_BY_SYSTEM:
        kt = KT_BY_SYSTEM[system]
    else:
        raise ValueError(f"Unsupported NBC empirical period system: {system}")
    return kt * h ** 0.75


def amplified_period_s(empirical_s, factor=AMPLIFICATION_FACTOR):
    """Return 1.25 times the empirical period; any other factor is rejected.

    [REF NBC105-2025 §5.1.3, printed p. 30]
    """
    if factor != AMPLIFICATION_FACTOR:
        raise ValueError(f"NBC 105:2025 §5.1.3 fixes the factor at {AMPLIFICATION_FACTOR}; got {factor}")
    return AMPLIFICATION_FACTOR * _positive(empirical_s, "empirical_s")


def adopted_period_s(empirical_s, rayleigh_s=None, factor=AMPLIFICATION_FACTOR):
    """Apply the lesser-of rule between Rayleigh and amplified empirical period.

    [REF NBC105-2025 §5.1, printed p. 28]
    A missing Rayleigh period gives ``adopted_s=None`` and status INCOMPLETE,
    never the empirical value.
    """
    amplified = amplified_period_s(empirical_s, factor)
    if rayleigh_s in (None, ""):
        return {"amplified_s": amplified, "rayleigh_s": None, "adopted_s": None,
                "status": "INCOMPLETE: supply NBC Rayleigh period to determine lesser adopted value"}
    rayleigh = _positive(rayleigh_s, "rayleigh_s")
    return {"amplified_s": amplified, "rayleigh_s": rayleigh,
            "adopted_s": min(rayleigh, amplified),
            "status": "READY: adopted period is lesser of Rayleigh and amplified empirical"}


def rayleigh_period_s(weights_kN, displacements_m, forces_kN, g=9.81):
    """Return T = 2*pi*sqrt(sum(W d^2)/(g sum(F d))).

    [REF NBC105-2025 §5.1.1, printed p. 28]
    """
    w, d, f = list(weights_kN), list(displacements_m), list(forces_kN)
    if not (len(w) == len(d) == len(f)) or not w:
        raise ValueError("weights, displacements and forces must be non-empty and equal length")
    numerator = sum(wi * di ** 2 for wi, di in zip(w, d))
    denominator = _positive(g, "g") * sum(fi * di for fi, di in zip(f, d))
    if not (numerator > 0 and denominator > 0):
        raise ValueError("Rayleigh sums must be positive")
    return 2.0 * math.pi * math.sqrt(numerator / denominator)


def seismic_weight_kN(dead_kN, storage_live_kN=0.0, other_live_kN=0.0,
                      roof_live_kN=0.0):
    """Return dead + 0.6 storage + 0.3 other + 0 roof live load.

    [REF NBC105-2025 §5.2 Table 5-1, printed p. 30]
    ``roof_live_kN`` is accepted but always contributes zero.
    """
    return (float(dead_kN) + LIVE_LOAD_FACTORS["storage"] * float(storage_live_kN)
            + LIVE_LOAD_FACTORS["other"] * float(other_live_kN)
            + LIVE_LOAD_FACTORS["roof"] * float(roof_live_kN))


def period_factor_deviation(factor):
    """Return None for 1.25, otherwise a DEVIATION message.

    [REF NBC105-2025 §5.1.3, printed p. 30]
    """
    if factor == AMPLIFICATION_FACTOR:
        return None
    return (f"DEVIATION: period amplification factor {factor} differs from the "
            f"NBC 105:2025 §5.1.3 value {AMPLIFICATION_FACTOR}")

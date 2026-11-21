"""NBC 105:2025 clause 5 period and seismic-weight helpers (pure Python).

[REF NBC105-2025 §5, printed pp. 28-30] Shared implementation of the
§5.1 lesser-of rule, §5.1.1 Rayleigh period, §5.1.2 empirical period,
§5.1.3 amplification and §5.2 seismic weight. A period computed here is a
design-input calculation, never engineering acceptance of the building.

Eq. 5.1(1), the shear-wall kt equation, the Aw summation and the Figure 5-1
height rule are verified against the printed pages 28-30 of NBC 105:2025
(user-supplied PDF).

Production-routed helpers: empirical_period_s, amplified_period_s,
period_factor_deviation, effective_wall_area_m2 (grouped_wall_aw only) and
storey_index_for_elevation. adopted_period_s, rayleigh_period_s,
building_height_m and seismic_weight_kN are reference implementations
exercised by tests; their rules are applied inline elsewhere. See
docs/nbc105/clause_05_dynamic_characteristics_matrix.md.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence

from components.nbc105.constants import GRAVITY_M_S2

__all__ = [
    "AMPLIFICATION_FACTOR", "LWI_OVER_H_MAX", "KT_BY_SYSTEM",
    "SHEAR_WALL_KT_NUMERATOR", "LIVE_LOAD_FACTORS", "building_height_m",
    "effective_wall_area_m2", "empirical_period_s", "amplified_period_s",
    "adopted_period_s", "rayleigh_period_s", "storey_index_for_elevation",
    "seismic_weight_kN", "period_factor_deviation",
]

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

    [REF NBC105-2025 §5.1.2, printed p. 29]
    H definition and Figure 5-1.
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

    [REF NBC105-2025 §5.1.2, printed pp. 29-30]
    Aw summation p. 29; Awi (first-storey effective wall area), Lwi
    (first-storey wall length in the considered direction, Lwi/H <= 0.9) and
    Nw (walls in the considered direction) are defined on p. 30.
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
    Eq. 5.1(2) and the kt list.
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


def rayleigh_period_s(weights_kN, displacements_m, forces_kN, g=GRAVITY_M_S2):
    """Return T = 2*pi*sqrt(sum(W d^2)/(g sum(F d))).

    [REF NBC105-2025 §5.1.1, printed p. 28] ``g`` defaults to the shared
    GRAVITY_M_S2 (9.80665, USER_DECISION; the printed value is 9.81).
    """
    w, d, f = list(weights_kN), list(displacements_m), list(forces_kN)
    if not (len(w) == len(d) == len(f)) or not w:
        raise ValueError("weights, displacements and forces must be non-empty and equal length")
    numerator = sum(wi * di ** 2 for wi, di in zip(w, d))
    denominator = _positive(g, "g") * sum(fi * di for fi, di in zip(f, d))
    if not (numerator > 0 and denominator > 0):
        raise ValueError("Rayleigh sums must be positive")
    return 2.0 * math.pi * math.sqrt(numerator / denominator)


def storey_index_for_elevation(z_m: float, floor_elevations_m: Sequence[float]) -> int:
    """Return the floor index whose seismic weight Wi receives a node at ``z_m``.

    [REF NBC105-2025 §5.2, printed p. 30] Wi is the dead load plus factored
    seismic live load between the mid-heights of the adjacent storeys.
    ``floor_elevations_m`` are ascending lateral-level elevations. A node at or
    below the first floor stays with floor 0 (the lower half of the first
    storey is kept so total weight is preserved; the base carries no lateral
    level). A node at or above the last floor goes to the last index. Between
    floors i-1 and i the node goes to i-1 when it lies below the mid-height
    (e[i-1]+e[i])/2 (within 1e-7 m), otherwise to i. A node on a floor
    elevation (within 1e-7 m) belongs to that floor.
    """
    e = [float(v) for v in floor_elevations_m]
    if not e:
        raise ValueError("floor_elevations_m must not be empty")
    if any(b <= a for a, b in zip(e, e[1:])):
        raise ValueError("floor_elevations_m must be strictly ascending")
    z = float(z_m)
    if not math.isfinite(z):
        raise ValueError("z_m must be finite")
    if z <= e[0] + 1e-7:
        return 0
    if z >= e[-1] - 1e-7:
        return len(e) - 1
    for i in range(1, len(e)):
        if z <= e[i] + 1e-7:
            if z >= e[i] - 1e-7:
                return i
            return i - 1 if z < (e[i - 1] + e[i]) / 2 - 1e-7 else i
    return len(e) - 1


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

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


def _finite(value, name):
    if isinstance(value,bool):
        raise ValueError(f"{name} must be finite")
    try: number=float(value)
    except (TypeError,ValueError,OverflowError) as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number

def _nonnegative(value, name):
    number=_finite(value,name)
    if number<0:raise ValueError(f"{name} must be nonnegative")
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
    GRAVITY_M_S2 (9.81, NBC 105:2025 notation list, printed p. 7).
    Wi must be a positive seismic weight; signed Fi and di are permitted,
    but every input must be finite and the sums must be physically positive.
    """
    w, d, f = list(weights_kN), list(displacements_m), list(forces_kN)
    if not (len(w) == len(d) == len(f)) or not w:
        raise ValueError("weights, displacements and forces must be non-empty and equal length")
    w=[_positive(v, "Wi") for v in w]
    d=[_finite(v, "di") for v in d]
    f=[_finite(v, "Fi") for v in f]
    numerator = math.fsum(wi * di ** 2 for wi, di in zip(w, d))
    denominator = _positive(g, "g") * math.fsum(fi * di for fi, di in zip(f, d))
    if not (math.isfinite(numerator) and math.isfinite(denominator)
            and numerator > 0 and denominator > 0):
        raise ValueError("Rayleigh sums must be finite and positive")
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
    ``roof_live_kN`` is accepted but always contributes zero. All supplied
    load magnitudes must be finite nonnegative gravity-load contributions.
    """
    inputs=[_nonnegative(v,n) for v,n in (
        (dead_kN,"dead_kN"),(storage_live_kN,"storage_live_kN"),
        (other_live_kN,"other_live_kN"),(roof_live_kN,"roof_live_kN"))]
    return (inputs[0]+LIVE_LOAD_FACTORS["storage"]*inputs[1]
            +LIVE_LOAD_FACTORS["other"]*inputs[2])


def period_factor_deviation(factor):
    """Return None for 1.25, otherwise a DEVIATION message.

    [REF NBC105-2025 §5.1.3, printed p. 30]
    """
    if factor == AMPLIFICATION_FACTOR:
        return None
    return (f"DEVIATION: period amplification factor {factor} differs from the "
            f"NBC 105:2025 §5.1.3 value {AMPLIFICATION_FACTOR}")

# [REF NBC105-2025 §5.3 Table 5-2, printed p.32].
# (name, Rmu, Omega_u, Omega_s) keyed by unique printed row; wall and dual
# system share labels but NOT the same coefficients.
_TABLE_5_2 = {
 1:("Steel Moment Resisting Frame",4.,1.5,1.25),
 2:("Reinforced Concrete Moment Resisting Frame",4.,1.5,1.25),
 3:("Steel + RC Composite Moment Resisting Frame",4.,1.5,1.25),
 4:("Steel Eccentrically Braced Frame",4.,1.5,1.25),
 5:("Steel + RC Composite Eccentrically Braced Frame",4.,1.5,1.25),
 6:("Steel Concentric Braced Frame",3.,1.3,1.15),
 7:("Steel + RC Composite Concentric Braced Frame",3.,1.3,1.15),
 8:("Steel Buckling Restraint Braces",4.,1.5,1.25),
 9:("RC Shear wall",3.,1.3,1.15),
 10:("Steel + RC Composite Shear Wall",3.,1.3,1.15),
 11:("Reinforced Masonry Shear wall",2.5,1.2,1.1),
 12:("Confined Masonry wall",2.5,1.2,1.1),
 13:("Unreinforced Masonry wall with horizontal bands and vertical reinforcement bars",2.,1.2,1.1),
 14:("Dual Steel Eccentrically Braced Frame",4.,1.5,1.25),
 15:("Dual Steel + RC Composite Eccentrically Braced Frame",4.,1.5,1.25),
 16:("Dual Steel Concentric Braced Frame",3.5,1.4,1.2),
 17:("Dual Steel + RC Composite Concentric Braced Frame",3.5,1.4,1.2),
 18:("Dual Steel Buckling Restraint Braces",4.,1.5,1.25),
 19:("Dual RC Shear wall",3.5,1.4,1.2),
 20:("Dual Steel + RC Composite Shear Wall",3.5,1.4,1.2),
 21:("Dual Reinforced Masonry Shear wall",2.5,1.2,1.1),
}

def table_5_2_system_factors(row):
    """§5.3.1–5.3.4 p.32: exact Table 5-2 row selection (1..21).
[REF NBC105-2025 §5, printed pp. 28–37]"""
    if isinstance(row,bool) or not isinstance(row,int) or row not in _TABLE_5_2:
        raise ValueError("NBC Table 5-2 requires one of 21 exact row numbers")
    name,rm,ou,os=_TABLE_5_2[row]
    return {"row":row,"system":name,"Rmu":rm,"Omega_u":ou,"Omega_s":os,
            "Rs":1.0,"status":"TABLE_VALUE_ONLY_DETAILING_QUALIFICATION_OPEN"}

def _strictly_below(a,b):
    # NBC writes a strict '<'; an engineering tolerance would weaken it.
    return a < b

def _strictly_above(a,b):
    # NBC writes a strict '>'; do not exempt tiny true exceedances.
    return a > b

def weak_story(story_strength,above_strength):
    """[REF NBC105-2025 §5, printed pp. 28–37]
§5.4.1.1 p.33: story lateral strength strictly <80% of above."""
    return _strictly_below(_positive(story_strength,"strength"),
                           .8*_positive(above_strength,"above strength"))

def soft_story(story_stiffness,above_stiffness,three_above=None):
    """§5.4.1.2 p.33: <70% above OR <80% three-above mean.
    The three-storey criterion is evaluated only if all three values supplied.
    
[REF NBC105-2025 §5, printed pp. 28–37]"""
    current=_positive(story_stiffness,"stiffness")
    above=_positive(above_stiffness,"above stiffness")
    flagged=_strictly_below(current,.7*above)
    if three_above is not None:
        vals=list(three_above)
        if len(vals)!=3:raise ValueError("three_above must have exactly three story stiffnesses")
        mean=math.fsum(_positive(x,"above stiffness") for x in vals)/3.
        flagged=flagged or _strictly_below(current,.8*mean)
    return flagged

def torsion_irregularity(max_displacement,min_displacement):
    """§5.4.2.1–2 p.34: >1.5 torsion, >2.5 extreme (prohibited).
[REF NBC105-2025 §5, printed pp. 28–37]"""
    maxv=_positive(max_displacement,"maximum end displacement")
    minv=_positive(min_displacement,"minimum end displacement")
    if _strictly_above(maxv,2.5*minv):
        return "EXTREME_TORSION_PROHIBITED"
    if _strictly_above(maxv,1.5*minv):
        return "TORSION_IRREGULAR"
    return "REGULAR"

def reentrant_corner_irregularity(projection_m,overall_dimension_m):
    """§5.4.2.3 p.34: projection strictly >15% overall dimension.
[REF NBC105-2025 §5, printed pp. 28–37]"""
    return _strictly_above(_positive(projection_m,"projection"),
                           .15*_positive(overall_dimension_m,"dimension"))

# SINGLE SOURCE of the printed 5.5.3 (p.37) drift limits. 8.1.3.1 (p.43) and
# 9.3.3.1 (p.48) cite "clause 5.6" for these limits, but printed 5.6 is
# Accidental Eccentricity; the limits are in 5.5.3 (see CROSS_REFERENCE_REGISTER).
DRIFT_LIMITS = {"ULS": 0.025, "SLS": 0.006}


def drift_limit_ratio(limit_state):
    """Return the printed 5.5.3 inter-story drift ratio limit for ULS or SLS.

    [REF NBC105-2025 §5.5.3, printed p. 37] 0.025 at ultimate, 0.006 at
    serviceability limit state; the only definition of these numbers in code.
    """
    state = str(limit_state).upper()
    if state not in DRIFT_LIMITS:
        raise ValueError("limit_state must be ULS/SLS")
    return DRIFT_LIMITS[state]


def drift_ratio_status(drift_ratio, limit_state):
    """Return PASS or REVIEW for a drift RATIO, via interstory_drift_check.

    [REF NBC105-2025 §5.5.3, printed p. 37; cited by 8.1.3.1 and 9.3.3.1]
    Used by the linear and nonlinear time-history summaries so every drift
    screen shares clause 5's limits and strict comparison (ratio <= limit).
    """
    return "PASS" if interstory_drift_check(drift_ratio, 1.0, limit_state)["pass"] else "REVIEW"


def interstory_drift_check(relative_deflection_m,storey_height_m,limit_state):
    """§5.5.3 p.37: <=0.025 ULS, <=0.006 SLS (design-level drift).
[REF NBC105-2025 §5, printed pp. 28–37]"""
    drift=float(relative_deflection_m)
    if not math.isfinite(drift):raise ValueError("nonfinite inter-storey drift")
    h=_positive(storey_height_m,"storey height")
    state=str(limit_state).upper()
    if state not in ("ULS","SLS"):raise ValueError("limit_state must be ULS/SLS")
    ratio=abs(drift)/h
    limit=DRIFT_LIMITS[state]
    return {"pass":ratio<=limit,
            "ratio":ratio,"limit":limit,
            "basis":"DESIGN_DRIFT_INPUT_ONLY_NBC_3_4_STIFFNESS_MUST_BE_VERIFIED"}

def uls_design_deflection(linear_deflection_m,ductility_factor):
    """§5.5.1.1 p.36: multiply elastic ESM/MRSM horizontal deflection by Rmu.
[REF NBC105-2025 §5, printed pp. 28–37]"""
    d=float(linear_deflection_m)
    if not math.isfinite(d):raise ValueError("nonfinite elastic displacement")
    return d*_positive(ductility_factor,"Rmu")

def separation_gap_m(building1_design_deflection_m,building2_design_deflection_m):
    """§5.5.2 p.36: SRSS of design horizontal deflections.
[REF NBC105-2025 §5, printed pp. 28–37]"""
    a=float(building1_design_deflection_m);z=float(building2_design_deflection_m)
    if not math.isfinite(a) or not math.isfinite(z):raise ValueError("nonfinite displacement")
    return math.hypot(a,z)

def accidental_eccentricities_m(building_width_m):
    """§5.6 p.37: ±0.05b, distinct from inherent CM–CR eccentricity.
[REF NBC105-2025 §5, printed pp. 28–37]"""
    e=.05*_positive(building_width_m,"b")
    return (-e,e)

__all__ += [
    "DRIFT_LIMITS","drift_limit_ratio","drift_ratio_status",
    "table_5_2_system_factors","weak_story","soft_story","torsion_irregularity",
    "reentrant_corner_irregularity","interstory_drift_check",
    "uls_design_deflection","separation_gap_m","accidental_eccentricities_m",
]


MASS_IRREGULARITY_FRACTION = 0.5


def mass_irregularity(masses, *, exempt=None, reference="LIGHTER_STOREY"):
    """Printed 5.4.1.5 mass irregularity over CONSECUTIVE storeys only.

    [REF NBC105-2025 §5.4.1.5, printed p. 34] "A difference of more than 50%
    between the effective masses of two consecutive stories is considered as
    mass irregularity. Light roofs, penthouse, and mezzanine floors need not
    be considered." ``masses`` run bottom to top (effective storey masses, any
    consistent unit). The print compares two consecutive storeys; it states
    no reference storey and no base for the percentage, so two readings are
    returned for every pair: ``irregular_vs_lighter`` (|dm| > 0.5 min(m); same
    as max/min > 1.5, conservative, the default basis) and
    ``irregular_vs_heavier`` (|dm| > 0.5 max(m); same as max/min > 2).
    ``reference`` selects which one sets ``irregular``. ``exempt`` is an
    iterable of 0-based storey indices the user DECLARES to be a light roof,
    penthouse or mezzanine: a pair with an exempt storey is reported
    ``EXEMPT_DECLARED`` and never flagged. The clause says "need not", so no
    storey is exempt automatically (the roof is exempt only if declared).
    Strict inequality as printed. Returns one dict per consecutive pair.
    """
    if reference not in ("LIGHTER_STOREY", "HEAVIER_STOREY"):
        raise ValueError("reference must be LIGHTER_STOREY or HEAVIER_STOREY")
    m = [_positive(v, "storey mass") for v in masses]
    if len(m) < 2:
        raise ValueError("at least two storeys are required")
    ex = set()
    for i in (exempt or ()):
        if isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < len(m):
            raise ValueError("exempt storey index out of range")
        ex.add(i)
    out = []
    for i in range(len(m) - 1):
        lo, hi = min(m[i], m[i + 1]), max(m[i], m[i + 1])
        diff = hi - lo
        vs_l = _strictly_above(diff, MASS_IRREGULARITY_FRACTION * lo)
        vs_h = _strictly_above(diff, MASS_IRREGULARITY_FRACTION * hi)
        skipped = i in ex or (i + 1) in ex
        out.append({
            "lower_storey_index": i, "upper_storey_index": i + 1,
            "difference_over_lighter": diff / lo, "difference_over_heavier": diff / hi,
            "irregular_vs_lighter": False if skipped else vs_l,
            "irregular_vs_heavier": False if skipped else vs_h,
            "irregular": False if skipped else (vs_l if reference == "LIGHTER_STOREY" else vs_h),
            "status": "EXEMPT_DECLARED" if skipped else ("IRREGULAR" if (vs_l if reference == "LIGHTER_STOREY" else vs_h) else "PASS"),
            "reference": reference})
    return out

__all__ += ["mass_irregularity", "MASS_IRREGULARITY_FRACTION"]


# Two explicitly separate drift outputs (owner ruling 3, 2026-11-26). Never mix.
DRIFT_BASES = ("ETABS_COMPARISON", "OPENSEES_ACTUAL")


def drift_basis(label):
    """Validate and return a drift-basis label (ETABS_COMPARISON or OPENSEES_ACTUAL).

    [REF NBC105-2025 §5.5.1 printed p. 36; §5.5.3 printed p. 37]
    """
    if label not in DRIFT_BASES:
        raise ValueError("drift basis must be one of " + ", ".join(DRIFT_BASES))
    return label


def etabs_comparison_drift(elastic_relative_deflection_m, storey_height_m, limit_state, ductility_factor=None):
    """ETABS_COMPARISON drift: design-scaled the way the ETABS drift output is.

    [REF NBC105-2025 §5.5.1.1 and §5.5.1.2 printed p. 36; §5.5.3 printed p. 37]
    ULS: design deflection = elastic ESM/MRSM deflection x Rmu (5.5.1.1; the
    printed text is explicit that the design deflection is the elastic value
    multiplied by the ductility factor). SLS: design deflection = elastic
    deflection (5.5.1.2). The ratio is then compared with the 5.5.3 limit via
    ``interstory_drift_check``. Compare ONLY with ETABS drift output; this is
    not the OpenSees response (see ``opensees_actual_drift``).
    """
    state = str(limit_state).upper()
    if state not in DRIFT_LIMITS:
        raise ValueError("limit_state must be ULS/SLS")
    elastic = float(elastic_relative_deflection_m)
    if not math.isfinite(elastic):
        raise ValueError("nonfinite elastic inter-storey deflection")
    if state == "ULS":
        if ductility_factor is None:
            raise ValueError("ULS design deflection needs the Rmu ductility factor (5.5.1.1)")
        design = uls_design_deflection(elastic, ductility_factor)
        clause = "5.5.1.1 + 5.5.3"
    else:
        design = elastic
        clause = "5.5.1.2 + 5.5.3"
    out = dict(interstory_drift_check(design, storey_height_m, state))
    out.update(drift_basis="ETABS_COMPARISON", clause=clause, limit_state=state,
               elastic_relative_deflection_m=elastic, design_relative_deflection_m=design,
               elastic_ratio=abs(elastic) / _positive(storey_height_m, "storey height"),
               scaled_by_Rmu=(state == "ULS"),
               note="Design-scaled like ETABS drift output; compare with ETABS only, never with OPENSEES_ACTUAL.")
    return out


def opensees_actual_drift(actual_relative_deflection_m, storey_height_m, limit_state):
    """OPENSEES_ACTUAL drift: actual (unscaled) OpenSees inter-storey response.

    [REF NBC105-2025 §5.5.3 printed p. 37; checked by §8.1.3.1 p. 43 and §9.3.3.1 p. 48]
    The actual elastic or inelastic OpenSees relative deflection is divided by
    the storey height and compared with the 5.5.3 limit. No ductility factor,
    force scale or ESM kd is applied (the function has no such argument).
    """
    state = str(limit_state).upper()
    out = dict(interstory_drift_check(actual_relative_deflection_m, storey_height_m, state))
    out.update(drift_basis="OPENSEES_ACTUAL", clause="5.5.3 (via 8.1.3.1 / 9.3.3.1)",
               limit_state=state, actual_relative_deflection_m=float(actual_relative_deflection_m),
               scaled_by_Rmu=False,
               note="Actual unscaled OpenSees response; compare with ETABS_COMPARISON only through an explicit, labelled reconciliation.")
    return out


def separate_drift_outputs(*, limit_state, storey_height_m, elastic_relative_deflection_m=None,
                           ductility_factor=None, opensees_relative_deflection_m=None):
    """Return the two drift outputs side by side under separate keys, never merged.

    [REF NBC105-2025 §5.5.1 p. 36; §5.5.3 p. 37]
    A missing input leaves its key None; there is no combined pass flag.
    """
    return {
        "ETABS_COMPARISON": None if elastic_relative_deflection_m is None else etabs_comparison_drift(
            elastic_relative_deflection_m, storey_height_m, limit_state, ductility_factor),
        "OPENSEES_ACTUAL": None if opensees_relative_deflection_m is None else opensees_actual_drift(
            opensees_relative_deflection_m, storey_height_m, limit_state),
        "combined_pass": None,
        "mixing_allowed": False,
    }


def require_same_drift_basis(*outputs):
    """Raise if drift outputs carry different bases (comparison would mix bases).

    [REF NBC105-2025 §5.5.1 p. 36; §5.5.3 p. 37]
    """
    bases = {drift_basis(o["drift_basis"]) for o in outputs}
    if len(bases) > 1:
        raise ValueError("refusing to mix drift bases: " + ", ".join(sorted(bases)))
    return bases.pop() if bases else None

__all__ += ["DRIFT_BASES", "drift_basis", "etabs_comparison_drift", "opensees_actual_drift",
            "separate_drift_outputs", "require_same_drift_basis"]


"""NBC 105:2025 §7, printed pp.40–41, MRSM numerical reference tools.

No full modal model or missing-mass solution is inferred from these helpers.
"""
from __future__ import annotations
import math
__all__=["modal_effective_weight","modal_story_forces","force_only_scale",
         "modal_mass_coverage","srss","modal_combination_readiness",
         "modal_design_coefficient","force_scale_factor","cqc_correlation_matrix",
         "modal_participation_profile"]

def _pos(value,name):
    if isinstance(value,bool):raise ValueError(name+" must be finite positive")
    try:x=float(value)
    except (TypeError,ValueError) as exc:raise ValueError(name+" invalid") from exc
    if not math.isfinite(x) or x<=0:raise ValueError(name+" must be positive")
    return x

def _weights_modes(weights,shapes):
    w=list(weights);phi=list(shapes)
    if len(w)!=len(phi) or not w:raise ValueError("Wi and mode shapes mismatched")
    w=[_pos(x,"Wi") for x in w]
    p=[float(v) for v in phi]
    if any(not math.isfinite(x) for x in p):raise ValueError("nonfinite mode shape")
    signed=math.fsum(x*y for x,y in zip(w,p))
    if abs(signed)<1e-12:raise ValueError("zero modal participation")
    return w,p,signed

def modal_effective_weight(weights,shapes):
    """[REF NBC105-2025 §7, printed pp. 40–41]
§7.2 Eq.7.1(2) p.40: (sum wj phi_ji)^2 / sum(wj phi_ji^2)."""
    w,phi,num=_weights_modes(weights,shapes)
    return num*num/math.fsum(x*y*y for x,y in zip(w,phi))

def modal_story_forces(weights,shapes,modal_base_shear):
    """§7.2 Eq.7.1(3) p.40, signed participation may yield signed story forces.
[REF NBC105-2025 §7, printed pp. 40–41]"""
    w,p,d=_weights_modes(weights,shapes);v=_pos(modal_base_shear,"Vi")
    return [v*wi*pi/d for wi,pi in zip(w,p)]

def srss(modal_effects):
    """§7.4 p.41: independent-mode SRSS; close-mode treatment still required.
[REF NBC105-2025 §7, printed pp. 40–41]"""
    a=[float(x) for x in modal_effects]
    if not a or any(not math.isfinite(x) for x in a):
        raise ValueError("nonfinite/empty modal effects")
    return math.sqrt(math.fsum(x*x for x in a))

def modal_mass_coverage(modal_mass_ratios_percent):
    """§7.3: returns accumulated participation percentage, not an acceptance token.
[REF NBC105-2025 §7, printed pp. 40–41]"""
    raw=list(modal_mass_ratios_percent)
    if any(isinstance(x,bool) for x in raw):
        raise ValueError("boolean modal participation is invalid")
    a=[float(x) for x in raw]
    if not a or any(not math.isfinite(x) or x<0 or x>100 for x in a):
        raise ValueError("invalid modal participation")
    s=math.fsum(a)
    if s>100+1e-6:raise ValueError("modal mass ratios exceed 100%")
    return s

def modal_participation_profile(modal_mass_ratios_percent, *, direction):
    """Cumulative directional effective mass with 90% and 100% guideposts.

    [REF NBC105-2025 §7.3, printed p.41]
    90% is the printed minimum; 100% is a visualization target, not an
    automatically achievable finite-mode count or substitute for missing-mass
    treatment. Input ratios are percentages in the considered direction.
    """
    axis=str(direction).strip().upper()
    if axis not in ("X","Y"):
        raise ValueError("direction must be X or Y")
    ratios=list(modal_mass_ratios_percent)
    # Reuse the canonical percent range, finiteness, and 100% sum guard.
    total=modal_mass_coverage(ratios)
    running=0.0
    points=[]
    first_90=None
    for index, raw in enumerate(ratios, 1):
        value=float(raw)
        running=math.fsum((running,value))
        if first_90 is None and running>=90.0:
            first_90=index
        points.append({"mode":index,"incremental_percent":value,
                       "cumulative_percent":min(100.0,running),
                       "at_least_90_percent":running>=90.0})
    return {"direction":axis,"modes":points,"total_percent":total,
            "minimum_required_percent":90.0,"visual_target_percent":100.0,
            "first_mode_meeting_90_percent":first_90,
            "minimum_90_percent_met":total>=90.0,
            "exact_100_percent_observed":math.isclose(total,100.0,rel_tol=0,abs_tol=1e-9),
            "status":"MASS_PARTICIPATION_ONLY_NOT_MODAL_OR_NATIVE_ACCEPTANCE"}


def modal_design_coefficient(elastic_spectrum, *, ductility=None, overstrength,
                             limit_state):
    """§7.1 p.40; delegate the shared ULS/SLS denominator to Clause 6.

    [REF NBC105-2025 §7.1, printed p.40]
    elastic_spectrum is C(Ti) for ULS or Cs(Ti) for SLS, not Ch(T).
    """
    from components.nbc105.clause_06_equivalent_static import base_shear_coefficient
    return base_shear_coefficient(elastic_spectrum,ductility=ductility,
                                   overstrength=overstrength,limit_state=limit_state)

def force_scale_factor(esm_shear, mrsm_shear):
    """§7.5 p.41 scalar only; DO NOT scale displacement or drift.

    [REF NBC105-2025 §7.5, printed p.41]
    """
    v=_pos(esm_shear,"ESM V"); vr=_pos(mrsm_shear,"MRSM VR")
    return max(1.,v/vr)

def force_only_scale(*,esm_shear,mrsm_shear,member_forces,story_shears,
                     base_reactions,drifts,displacements):
    """§7.5 p.41: scale ONLY member forces, story shears, base reactions.
[REF NBC105-2025 §7, printed pp. 40–41]"""
    v=_pos(esm_shear,"ESM V");vr=_pos(mrsm_shear,"MRSM VR")
    scale=force_scale_factor(v,vr)
    def finite_list(seq):
        x=[float(z) for z in seq]
        if any(not math.isfinite(z) for z in x):raise ValueError("nonfinite response")
        return x
    return {"force_scale_factor":scale,
      "member_forces":[scale*z for z in finite_list(member_forces)],
      "story_shears":[scale*z for z in finite_list(story_shears)],
      "base_reactions":[scale*z for z in finite_list(base_reactions)],
      "drifts":finite_list(drifts),"displacements":finite_list(displacements),
      "status":"FORCE_SCALING_ONLY_NOT_MISSING_MASS_VALIDATION"}

def cqc_correlation_matrix(omega_rad_s, damping_ratio=.05):
    """Established CQC modal correlation kernel for NBC §7.4.

    [REF NBC105-2025 §7.4, printed p.41]
    NBC allows CQC, but does not prescribe the CQC correlation equation.
    This uses the pre-existing production implementation for equal modal
    damping and maintains the exact ratio-based formula. Modal frequencies
    must be positive rad/s; damping is limited to the active MRSM <=5% policy.
    """
    modes=list(omega_rad_s)
    if not modes:
        raise ValueError("at least one modal circular frequency is required")
    w=[_pos(x,"modal circular frequency") for x in modes]
    damping=_pos(damping_ratio,"damping ratio")
    if damping>.05:
        raise ValueError("active MRSM damping must be <=0.05")
    result=[]
    for wi in w:
        row=[]
        for wj in w:
            beta=wj/wi
            numerator=8*damping*damping*(1+beta)*beta**1.5
            denominator=(1-beta*beta)**2+4*damping*damping*beta*(1+beta)**2
            value=numerator/denominator
            if not math.isfinite(value):
                raise ValueError("invalid CQC frequency/damping correlation")
            row.append(value)
        result.append(row)
    for k in range(len(result)):
        result[k][k]=1.
    return result

def modal_combination_readiness(*,mass_percent,highest_frequency_hz,
                                missing_mass_procedure_verified=False):
    """§7.3–7.4: 90% participation; modes >=33Hz need separate missing-mass work.
[REF NBC105-2025 §7, printed pp. 40–41]"""
    m=float(mass_percent);f=float(highest_frequency_hz)
    if not math.isfinite(m) or not 0<=m<=100 or not math.isfinite(f) or f<0:
        raise ValueError("invalid modal evidence")
    if type(missing_mass_procedure_verified) is not bool:raise ValueError("must be bool")
    missing=[] if m>=90 else ["DIRECTIONAL_MASS_BELOW_90_PERCENT"]
    if f>=33 and not missing_mass_procedure_verified:
        missing.append("MISSING_MASS_CORRECTION_NOT_VERIFIED")
    return {"ready":not missing,"missing":missing,
            "close_mode_combination":"REQUIRES_FREQUENCY_SPACING_REVIEW"}


MODAL_MASS_THRESHOLD_PERCENT = 90.0   # printed 7.3 p.40: compliance threshold (unchanged)


def modal_mass_participation_profile(per_mode_percent, *, periods_s=None):
    """Cumulative effective modal mass in ONE direction, out to 100 percent.

    [REF NBC105-2025 §7.3, printed p. 40]
    Printed 7.3: "A sufficient number of modes shall be included ... to include
    at least 90% of the total seismic mass in the direction under
    consideration." ``per_mode_percent`` is the effective modal mass of mode 1,
    2, ... N in percent of the total seismic mass in that direction (not
    cumulative). Returns the cumulative series, ``reached_90_at_mode`` (first
    mode with cumulative >= 90, None if never), ``reached_100_at_mode`` (first
    mode with cumulative >= 100 within 1e-4 percent, None if the supplied
    modes do not cover the whole mass), the period at the 90 percent mode when
    ``periods_s`` is given (Tn90 candidate, see 9.3.2.4), a per-mode ``regions``
    list and ``compliant_90`` (the compliance test stays at 90 percent; the
    100 percent figure is information). Region values: ``REQUIRED_FOR_90``
    (modes 1 to the first 90 percent mode, ``highlight_90_region`` True),
    ``BEYOND_90_TO_100`` and ``BEYOND_100`` (numerical tail after the whole mass
    is reached). Source-to-code review of the arithmetic only.
    """
    pm = [float(v) for v in per_mode_percent]
    if not pm or any((not math.isfinite(v)) or v < 0 for v in pm):
        raise ValueError("per-mode participation must be non-empty, finite and nonnegative")
    per = None
    if periods_s is not None:
        per = [float(v) for v in periods_s]
        if len(per) != len(pm) or any((not math.isfinite(v)) or v <= 0 for v in per):
            raise ValueError("periods_s must match the modes and be positive")
    cum, run = [], 0.0
    for v in pm:
        run += v
        cum.append(run)
    total = cum[-1]
    if total > 100.0 + 1e-6:
        raise ValueError("modal mass ratios exceed 100%")
    tol100 = 1e-4
    r90 = next((i + 1 for i, c in enumerate(cum) if c >= MODAL_MASS_THRESHOLD_PERCENT - 1e-9), None)
    r100 = next((i + 1 for i, c in enumerate(cum) if c >= 100.0 - tol100), None)
    regions = []
    for i, c in enumerate(cum):
        mode = i + 1
        if r90 is None or mode <= r90:
            region = "REQUIRED_FOR_90"
        elif r100 is None or mode <= r100:
            region = "BEYOND_90_TO_100"
        else:
            region = "BEYOND_100"
        regions.append({"mode": mode, "mode_percent": pm[i], "cumulative_percent": c, "region": region,
                        "highlight_90_region": region == "REQUIRED_FOR_90",
                        "first_mode_at_90": mode == r90, "first_mode_at_100": mode == r100})
    return {
        "threshold_percent": MODAL_MASS_THRESHOLD_PERCENT,
        "mode_count": len(pm), "cumulative_percent": cum, "total_percent": total,
        "reached_90_at_mode": r90, "reached_100_at_mode": r100,
        "period_at_90_s": None if per is None or r90 is None else per[r90 - 1],
        "compliant_90": r90 is not None,
        "all_mass_covered_100": r100 is not None,
        "shortfall_to_90_percent": max(0.0, MODAL_MASS_THRESHOLD_PERCENT - total),
        "shortfall_to_100_percent": max(0.0, 100.0 - total),
        "regions": regions,
        "basis": "NBC105_2025_7.3_P40_CUMULATIVE_EFFECTIVE_MODAL_MASS_ARITHMETIC_ONLY",
    }


def modal_mass_participation_by_direction(per_mode_percent_by_direction, *, periods_s=None):
    """Apply ``modal_mass_participation_profile`` to each direction (e.g. X and Y).

    [REF NBC105-2025 §7.3, printed p. 40]
    ``compliant_90`` of the result is True only if every direction reaches 90
    percent; each direction keeps its own region flags and mode numbers.
    """
    if not per_mode_percent_by_direction:
        raise ValueError("at least one direction is required")
    out = {d: modal_mass_participation_profile(v, periods_s=periods_s)
           for d, v in per_mode_percent_by_direction.items()}
    return {"directions": out, "compliant_90": all(v["compliant_90"] for v in out.values()),
            "threshold_percent": MODAL_MASS_THRESHOLD_PERCENT}

__all__ += ["MODAL_MASS_THRESHOLD_PERCENT","modal_mass_participation_profile",
            "modal_mass_participation_by_direction"]


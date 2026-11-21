"""NBC 105:2025 §7, printed pp.40–41, MRSM numerical reference tools.

No full modal model or missing-mass solution is inferred from these helpers.
"""
from __future__ import annotations
import math
__all__=["modal_effective_weight","modal_story_forces","force_only_scale",
         "modal_mass_coverage","srss","modal_combination_readiness",
         "modal_design_coefficient","force_scale_factor"]

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
    a=[float(x) for x in modal_mass_ratios_percent]
    if not a or any(not math.isfinite(x) or x<0 or x>100 for x in a):
        raise ValueError("invalid modal participation")
    s=math.fsum(a)
    if s>100+1e-6:raise ValueError("modal mass ratios exceed 100%")
    return s

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

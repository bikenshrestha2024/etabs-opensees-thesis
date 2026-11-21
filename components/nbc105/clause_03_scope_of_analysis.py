"""NBC 105:2025 §3, printed pp.17–21: method eligibility & cracked stiffness.

The original code references irregularity §5.5 in §3.2.1 although the
irregularities are described in §5.4; no silent cross-reference correction.
"""
from __future__ import annotations
import math

__all__=["esm_applicability","cracked_flexural_factor","bearing_pressure_limit",
         "CRACKED_FLEXURAL_FACTORS","LIVE_COMBINATION_FACTORS"]

CRACKED_FLEXURAL_FACTORS={
 "beam":(.35,.70),"column":(.70,.90),"cracked wall":(.50,.70),
 "uncracked wall":(.80,.90),"masonry wall":(.45,.60),
 "flat slab":(.25,.50)}
LIVE_COMBINATION_FACTORS={"storage":.6,"other":.3}

def _positive(v,name):
    if isinstance(v,bool):
        raise ValueError(name+" must be finite and positive")
    try: z=float(v)
    except (ValueError,TypeError) as exc: raise ValueError(name+" must be numeric") from exc
    if not math.isfinite(z) or z<=0:raise ValueError(name+" must be finite and positive")
    return z

def esm_applicability(*,height_m,period_s,irregular,limit_state):
    """§3.2.1 p.17: ESM all SLS, ULS if H<=15, T<0.5 or regular H<40."""
    h=_positive(height_m,"height_m"); t=_positive(period_s,"period_s")
    if type(irregular) is not bool:raise ValueError("irregular must be bool")
    state=str(limit_state).upper()
    if state not in ("ULS","SLS"):raise ValueError("limit_state must be ULS/SLS")
    reasons=["SLS_ALL_BUILDINGS"] if state=="SLS" else (
        (["H_LE_15M"] if h<=15 else [])+
        (["T_LT_0_5S"] if t<.5 else [])+
        (["REGULAR_H_LT_40M"] if not irregular and h<40 else []))
    return {"permitted":bool(reasons),"basis":reasons,
            "scope":"ESM_METHOD_ELIGIBILITY_NOT_DESIGN_COMPLIANCE"}

def cracked_flexural_factor(component,limit_state):
    """§3.4 Table 3-1 p.19, absence of rational cracked-section assessment.
[REF NBC105-2025 §3, printed pp. 17–21]"""
    state=str(limit_state).upper()
    if state not in ("ULS","SLS"):raise ValueError("limit state must be ULS or SLS")
    key=str(component).strip().lower()
    if key not in CRACKED_FLEXURAL_FACTORS:raise ValueError("unknown Table 3-1 component")
    return CRACKED_FLEXURAL_FACTORS[key][0 if state=="ULS" else 1]

def bearing_pressure_limit(allowable_pressure,*,earthquake):
    """§3.8 p.21: upper permissible 50% increase, not automatic approval.
[REF NBC105-2025 §3, printed pp. 17–21]"""
    p=_positive(allowable_pressure,"allowable_pressure")
    if type(earthquake) is not bool:raise ValueError("earthquake must be bool")
    return p*(1.5 if earthquake else 1.0)

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
    """[REF NBC105-2025 §3, printed pp. 17–21]
§3.2.1 p.17: ESM all SLS, ULS if H<=15, T<0.5 or regular H<40."""
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

# [REF NBC105-2025 §§3.6–3.7, printed pp.19–21]
def _load_combination_row(name,DL=0.,LL=0.,Ex=0.,Ey=0.,S=0.):
    return dict(name=name,DL=float(DL),LL=float(LL),Ex=float(Ex),Ey=float(Ey),S=float(S))

def _additional_load_factor(kind,method):
    if kind in (None,"","none"):return 0.
    source={"snow":1.2,"static liquid":1.2,"earth pressure":1.5}
    if str(kind).lower() not in source:raise ValueError("unknown additional load source")
    return 1. if method=="WSM" else source[str(kind).lower()]

def load_combination_coefficients(*,system,method,occupancy,additional_kind=None):
    """Return exact source coefficient combinations, not ETABS action results.

    [REF NBC105-2025 §§3.6.1–3.6.2 and §3.7, printed pp.19–21]
    Ex,Ey denote *seismic effects*, not acceleration or spectral ordinates.
    S refers to the selected additional source load with source-specific
    design multiplier (1.2 snow/liquid, 1.5 earth in LSM; 1.0 in WSM).
    """
    orientation=str(system).lower();stage=str(method).upper();occ=str(occupancy).lower()
    if orientation not in ("parallel","nonparallel"):
        raise ValueError("system must be parallel or nonparallel")
    if stage not in ("LSM","WSM"):raise ValueError("method must be LSM/WSM")
    if occ not in ("storage","other"):raise ValueError("occupancy must be storage/other")
    lam=.6 if occ=="storage" else .3
    rows=[]
    factor=_additional_load_factor(additional_kind,stage)
    if stage=="LSM":
        rows.append(_load_combination_row("ULS_GRAVITY",DL=1.2,LL=1.5))
        if factor:rows.append(_load_combination_row("ULS_GRAVITY_ADDITIONAL",DL=1.2,LL=.5,S=factor))
        for lead in ("X","Y"):
            for sign in (+1,-1):
                if orientation=="parallel":
                    values={("Ex" if lead=="X" else "Ey"):sign}
                    rows.append(_load_combination_row(f"ULS_E_{lead}_{'POS' if sign>0 else 'NEG'}",
                                     DL=1.,LL=lam,**values))
                    rows.append(_load_combination_row(f"ULS_STABILITY_{lead}_{'POS' if sign>0 else 'NEG'}",
                                     DL=.9,**values))
                else:
                    for sign_other in (+1,-1):
                        other="Y" if lead=="X" else "X"
                        signed=("POS" if sign>0 else "NEG")
                        secondary=("POS" if sign_other>0 else "NEG")
                        values={("Ex" if lead=="X" else "Ey"):sign,
                                ("Ey" if lead=="X" else "Ex"):.3*sign_other}
                        rows.append(_load_combination_row(f"ULS_E_{lead}{signed}_{other}{secondary}",
                                       DL=1.,LL=lam,**values))
                        rows.append(_load_combination_row(f"ULS_STABILITY_{lead}{signed}_{other}{secondary}",
                                       DL=.9,**values))
    else:
        rows.append(_load_combination_row("WSM_GRAVITY",DL=1.,LL=1.))
        if factor:rows.append(_load_combination_row("WSM_GRAVITY_ADDITIONAL",DL=1.,LL=1.,S=factor))
        for lead in ("X","Y"):
            for sign in (+1,-1):
                k=("Ex" if lead=="X" else "Ey")
                rows.append(_load_combination_row(f"WSM_E_{lead}_{'POS' if sign>0 else 'NEG'}",
                                     DL=1.,LL=lam,**{k:.7*sign}))
                rows.append(_load_combination_row(f"WSM_STABILITY_{lead}_{'POS' if sign>0 else 'NEG'}",
                                     DL=.7,**{k:.7*sign}))
    return rows

def vertical_seismic_combination(*,z,occupancy,earthquake_sign):
    """§3.6.3 Eq.3.6(3), printed p.21: (1.1+2Z/3)DL+λLL±E.

    [REF NBC105-2025 §3.6.3, printed p.21]
    Caller must establish applicability of vertical seismic effect §4.3.
    """
    zone=_positive(z,"z")
    occ=str(occupancy).lower()
    if occ not in ("storage","other"):raise ValueError("unknown occupancy")
    if earthquake_sign not in (-1,1) or isinstance(earthquake_sign,bool):
        raise ValueError("earthquake_sign must be ±1")
    return {"DL":1.1+(2./3.)*zone,"LL":.6 if occ=="storage" else .3,
            "E":float(earthquake_sign),"scope":"VERTICAL_SEISMIC_COMBINATION_ONLY"}

__all__ += ["load_combination_coefficients","vertical_seismic_combination"]

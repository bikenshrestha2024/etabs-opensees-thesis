"""NBC 105:2025 §9, printed pp.44–48, nonlinear prerequisite checks.

No silent assumption of convergence or full-duration nonlinear case completion.
"""
from __future__ import annotations
import math
__all__=["history_time_step_limit_s","required_component_runs",
         "motion_scale_factor","nonlinear_model_prerequisites",
         "target_spectrum_period_range","pushover_signs","pair_scale_factor"]

def _pos(v,name):
    if isinstance(v,bool):raise ValueError(name+" must be positive")
    try:x=float(v)
    except (ValueError,TypeError) as exc:raise ValueError(name+" invalid") from exc
    if not math.isfinite(x) or x<=0:raise ValueError(name+" must be positive")
    return x

def nonlinear_model_prerequisites(*,is_3d,gravity,p_delta,torsion,
                                 bilinear,hysteretic):
    """[REF NBC105-2025 §9, printed pp. 44–48]
§9.2–9.3 pp.44–45, declarations, NOT proof of material calibration."""
    vals=locals()
    if any(type(v) is not bool for v in vals.values()):
        raise ValueError("nonlinear model prerequisites must be bool")
    missing=[k for k,v in vals.items() if not v]
    return {"status":"PASS" if not missing else "BLOCKED","missing":missing,
            "basis":"DECLARATIONS_ONLY_CONVERGENCE_AND_CALIBRATION_UNVERIFIED"}

def history_time_step_limit_s(T1,Tn,record_digitization_dt_s):
    """§9.3.2.4 p.47: dt<=min(digitization,T1/100,Tn,0.01s).
[REF NBC105-2025 §9, printed pp. 44–48]"""
    return min(_pos(record_digitization_dt_s,"digitization dt"),
               _pos(T1,"T1")/100.,_pos(Tn,"Tn"),.01)

def target_spectrum_period_range(T1,Tn,Rmu):
    """§9.3.2.2(b) p.46: [Tn,sqrt(Rmu)*T1].
[REF NBC105-2025 §9, printed pp. 44–48]"""
    import math
    low=_pos(Tn,"Tn"); high=math.sqrt(_pos(Rmu,"Rmu"))*_pos(T1,"T1")
    if low>=high:raise ValueError("invalid target spectrum period range")
    return low,high

def motion_scale_factor(raw_target,raw_reference):
    """§9.3.2.2(c) p.46: 0.33 <= factor <= 3.
[REF NBC105-2025 §9, printed pp. 44–48]"""
    f=_pos(raw_target,"target")/_pos(raw_reference,"source")
    if not .33<=f<=3.:raise ValueError("discard record: scale factor outside 0.33 to 3")
    return f

def required_component_runs(number_of_pairs,*,is_3d):
    """§9.3.2.1/3 p.46–47: >=3 pairs and XY/YX for torsion-sensitive 3D.
[REF NBC105-2025 §9, printed pp. 44–48]"""
    if type(is_3d) is not bool:raise ValueError("is_3d must be bool")
    if isinstance(number_of_pairs,bool) or not isinstance(number_of_pairs,int) or number_of_pairs<3:
        raise ValueError("minimum three input records or pairs required")
    return 2*number_of_pairs if is_3d else number_of_pairs

def pair_scale_factor(factor_x, factor_y):
    """§9.3.2.2(c,d) p.46: independently fit XY, use lower factor for both.

    [REF NBC105-2025 §9.3.2.2(c,d), printed pp.46–47]
    Both independent factors must be within 0.33–3 BEFORE selection.
    """
    x=_pos(factor_x,"X component scale")
    y=_pos(factor_y,"Y component scale")
    if not (.33<=x<=3 and .33<=y<=3):
        raise ValueError("NBC 9.3.2.2: independent pair factors outside 0.33..3; replace record")
    return min(x,y)

def pushover_signs():
    """§9.2.1 p.44: maximum effects of positive and negative directions.
[REF NBC105-2025 §9, printed pp. 44–48]"""
    return (+1,-1)

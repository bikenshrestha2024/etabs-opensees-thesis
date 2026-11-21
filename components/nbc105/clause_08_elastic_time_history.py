"""NBC 105:2025 §8, printed pp.42–43; model and record acceptance helpers.

Ground motion selection/scaling/time-step rules are delegated to clause 9.3.2.
"""
from __future__ import annotations
import math
__all__=["elastic_model_prerequisites","record_response_aggregate",
         "elastic_member_action_for_design"]

def elastic_model_prerequisites(*,is_3d,gravity,p_delta,torsion,damping_ratio):
    """§8.1.1 p.42: 3D; gravity; P-Delta; inherent torsion; damping<=5%."""
    flags=locals()
    for name in ("is_3d","gravity","p_delta","torsion"):
        if type(flags[name]) is not bool:raise ValueError(name+" must be bool")
    d=float(damping_ratio)
    if not math.isfinite(d) or d<0 or d>.05:
        raise ValueError("linear viscous damping exceeds NBC §8.1.1.5 5% bound")
    missing=[name for name in ("is_3d","gravity","p_delta","torsion") if not flags[name]]
    return {"status":"PASS" if not missing else "BLOCKED",
            "missing":missing,"basis":"INPUT_DECLARATIONS_NOT_NATIVE_MODEL_PROOF"}

def record_response_aggregate(responses):
    """§8.1.3 p.42: <7 max; >7 mean; exactly 7 unspecified -> fail closed."""
    x=[float(v) for v in responses]
    if not x or any(not math.isfinite(v) for v in x):
        raise ValueError("nonfinite/empty time-history responses")
    if len(x)==7:
        raise ValueError("NBC §8.1.3 does not specify exactly seven records")
    return max(x) if len(x)<7 else math.fsum(x)/len(x)

def elastic_member_action_for_design(action,uls_ductility):
    """§8.1.3.2 p.43: divide elastic member action by ULS ductility factor.
    Printed R_P is inconsistent with earlier Rmu notation: caller must
    explicitly provide the reviewed and approved design factor.
    """
    a=float(action);r=float(uls_ductility)
    if not math.isfinite(a) or not math.isfinite(r) or r<=0:
        raise ValueError("invalid action / reviewed ductility")
    return a/r

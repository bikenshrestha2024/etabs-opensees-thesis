"""NBC 105:2025 §8, printed pp.42–43; model and record acceptance helpers.

Ground motion selection/scaling/time-step rules are delegated to clause 9.3.2.
"""
from __future__ import annotations
import math
__all__=["elastic_model_prerequisites","record_response_aggregate",
         "elastic_member_action_for_design","record_response_rule",
         "PROJECT_DECLARED_GROUND_MOTION_COUNT","project_record_set_evaluation"]

# USER_DECLARED 2026-11-26 (docs/nbc105/PROJECT_DECLARATIONS.md section 5): the
# project uses 8 ground motions (more than 7), so the printed 8.1.3 / 9.3.3
# "more than 7" average rule applies when all 8 complete. Not verified by code.
PROJECT_DECLARED_GROUND_MOTION_COUNT=8

def elastic_model_prerequisites(*,is_3d,gravity,p_delta,torsion,damping_ratio):
    """§8.1.1 p.42: 3D; gravity; P-Delta; inherent torsion; damping<=5%.
[REF NBC105-2025 §8, printed pp. 42–43]"""
    flags=locals()
    for name in ("is_3d","gravity","p_delta","torsion"):
        if type(flags[name]) is not bool:raise ValueError(name+" must be bool")
    d=float(damping_ratio)
    if not math.isfinite(d) or d<0 or d>.05:
        raise ValueError("linear viscous damping exceeds NBC §8.1.1.5 5% bound")
    missing=[name for name in ("is_3d","gravity","p_delta","torsion") if not flags[name]]
    return {"status":"PASS" if not missing else "BLOCKED",
            "missing":missing,"basis":"INPUT_DECLARATIONS_NOT_NATIVE_MODEL_PROOF"}

def record_response_rule(number_of_records):
    """§8.1.3 and §9.3.3: <7 MAX, >7 AVERAGE; exactly seven review.

    [REF NBC105-2025 §8.1.3 p.42; §9.3.3 p.47]
    """
    if isinstance(number_of_records,bool) or not isinstance(number_of_records,int) or number_of_records<1:
        raise ValueError("record count must be positive integer")
    if number_of_records==7:
        return "REVIEW_REQUIRED_EXACTLY_SEVEN_NOT_DEFINED_IN_2025_TEXT"
    return "MAXIMUM" if number_of_records<7 else "AVERAGE"

def record_response_aggregate(responses):
    """§8.1.3 p.42: <7 max; >7 mean; exactly 7 unspecified -> fail closed.
[REF NBC105-2025 §8, printed pp. 42–43]"""
    x=[float(v) for v in responses]
    if not x or any(not math.isfinite(v) for v in x):
        raise ValueError("nonfinite/empty time-history responses")
    rule=record_response_rule(len(x))
    if rule.startswith("REVIEW_REQUIRED"):
        raise ValueError("NBC §8.1.3 does not specify exactly seven records")
    return max(x) if rule=="MAXIMUM" else math.fsum(x)/len(x)

def elastic_member_action_for_design(action,uls_ductility):
    """§8.1.3.2 p.43: divide elastic member action by ULS ductility factor.
    Printed R_P is inconsistent with earlier Rmu notation: caller must
    explicitly provide the reviewed and approved design factor.
    
[REF NBC105-2025 §8, printed pp. 42–43]"""
    a=float(action);r=float(uls_ductility)
    if not math.isfinite(a) or not math.isfinite(r) or r<=0:
        raise ValueError("invalid action / reviewed ductility")
    return a/r


def project_record_set_evaluation(accepted_responses,*,declared_count=PROJECT_DECLARED_GROUND_MOTION_COUNT):
    """Evaluate one response quantity over the accepted records of the project set.

    [REF NBC105-2025 §8.1.3 p.42; §9.3.3 p.47] Printed rule: fewer than 7
    records -> maximum; more than 7 -> average; exactly 7 is not defined and is
    returned as BLOCKED (value None), never silently mapped to either rule.
    ``declared_count`` is the USER_DECLARED record count (8). Records that
    failed or did not converge must not be in ``accepted_responses``; if fewer
    than ``declared_count`` are accepted the rule is chosen from the accepted
    count (6 -> maximum, 7 -> BLOCKED) and ``declared_count_met`` is False.
    Source-to-code review only; not engineering acceptance.
    """
    x=[float(v) for v in accepted_responses]
    if any(not math.isfinite(v) for v in x):
        raise ValueError("nonfinite time-history responses")
    if isinstance(declared_count,bool) or not isinstance(declared_count,int) or declared_count<1:
        raise ValueError("declared_count must be a positive integer")
    n=len(x)
    if n==0:
        return {"status":"BLOCKED","rule":"NO_ACCEPTED_RECORDS","value":None,"n_accepted":0,
                "declared_count":declared_count,"declared_count_met":False}
    rule=record_response_rule(n)
    base={"n_accepted":n,"declared_count":declared_count,"declared_count_met":n==declared_count,
          "basis":"NBC105_2025_8.1.3_9.3.3_PRINTED_RULE_DECLARED_COUNT_USER_DECLARED"}
    if rule.startswith("REVIEW_REQUIRED"):
        return dict(base,status="BLOCKED",rule="EXACTLY_SEVEN_NOT_DEFINED",value=None)
    value=max(x) if rule=="MAXIMUM" else math.fsum(x)/n
    return dict(base,status="OK" if n==declared_count else "OK_BUT_DECLARED_COUNT_NOT_MET",
                rule=rule,value=value)

"""NBC 105:2025 NLTHA input screening; never a building design approval.

Government of Nepal, NBC 105:2025, clauses 9.3.1--9.3.3.
https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf
"""
from __future__ import annotations
import json
import math
from pathlib import Path

NBC105_URL="https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf"
DRIFT_LIMITS={"ULS":0.025,"SLS":0.006}
SCALING_TARGET="ULS_ELASTIC_SITE_C_OVER_OMEGA_U"

def positive(value,name):
    try: v=float(value)
    except (TypeError,ValueError,OverflowError) as exc:
        raise ValueError("Missing or invalid NBC input: "+name) from exc
    if not math.isfinite(v) or v<=0:
        raise ValueError(name+" must be finite and positive")
    return v

def nbc105_time_step_limit(*,record_dt_s,t1_x_s,t1_y_s,tn90_x_s,tn90_y_s):
    """§9.3.2.4: delegate per-direction time-step limits to Clause 9.

    Tn90 means the period required for 90% participation in each direction.
    """
    from components.nbc105.clause_09_nonlinear_analysis import history_time_step_limit_s
    values={k:positive(v,k) for k,v in {
        "record_dt_s":record_dt_s,"t1_x_s":t1_x_s,"t1_y_s":t1_y_s,
        "tn90_x_s":tn90_x_s,"tn90_y_s":tn90_y_s}.items()}
    for axis in ("x","y"):
        if values["tn90_"+axis+"_s"]>values["t1_"+axis+"_s"]:
            raise ValueError("Tn90 cannot exceed T1 for axis "+axis)
    return min(history_time_step_limit_s(values["t1_"+axis+"_s"],
               values["tn90_"+axis+"_s"],values["record_dt_s"]) for axis in ("x","y"))

def paired_ground_motion_scale(factor_x,factor_y):
    """§9.3.2.2(c,d): delegate lower pair factor to canonical Clause 9."""
    from components.nbc105.clause_09_nonlinear_analysis import pair_scale_factor
    return pair_scale_factor(factor_x,factor_y)

def scaling_period_range(tn90_s,t1_s,r_mu):
    """§9.3.2.2(b): preserve existing list return shape."""
    from components.nbc105.clause_09_nonlinear_analysis import target_spectrum_period_range
    return list(target_spectrum_period_range(t1_s,tn90_s,r_mu))

def response_aggregation_rule(number_of_pairs):
    """§9.3.3: uses Clause 8's shared record aggregation boundary rule."""
    from components.nbc105.clause_08_elastic_time_history import record_response_rule
    if type(number_of_pairs) is not int:raise TypeError("Pair count must be integer")
    if number_of_pairs<3:raise ValueError("NBC 9.3.2.1: at least 3 orthogonal pairs")
    return record_response_rule(number_of_pairs)


def validate_nbc105_design_metadata(evidence,*,record_dt_s,integration_dt_s,
                                    selected_scale,orientations):
    """Strict REVIEWER-SUPPLIED metadata check; never verifies actual spectrum."""
    if not isinstance(evidence,dict):raise ValueError("NBC evidence must be a JSON object")
    names=("t1_x_s","t1_y_s","tn90_x_s","tn90_y_s","r_mu","omega_u",
           "factor_x","factor_y")
    for name in names:positive(evidence.get(name),name)
    if evidence.get("target_spectrum_kind")!=SCALING_TARGET:
        raise ValueError("NBC 9.3.2.2(a): target must be C(T)/Omega_u")
    digest=str(evidence.get("spectrum_match_evidence_sha256",""))
    if len(digest)!=64 or any(c not in "0123456789abcdefABCDEF" for c in digest):
        raise ValueError("Provide 64-character spectrum fit evidence SHA256")
    if evidence.get("ground_motion_selection_reviewed") is not True:
        raise ValueError("Magnitude, distance and mechanism selection requires review")
    if sorted(orientations)!=["XY","YX"] or len(orientations)!=2:
        raise ValueError("NBC 9.3.2.3: each pair must run XY and YX")
    bound=nbc105_time_step_limit(record_dt_s=record_dt_s,
         t1_x_s=evidence["t1_x_s"],t1_y_s=evidence["t1_y_s"],
         tn90_x_s=evidence["tn90_x_s"],tn90_y_s=evidence["tn90_y_s"])
    dt=positive(integration_dt_s,"integration_dt_s")
    if dt>bound+1e-12:raise ValueError("NBC 9.3.2.4: dt exceeds limit "+str(bound))
    scale=paired_ground_motion_scale(evidence["factor_x"],evidence["factor_y"])
    if not math.isclose(positive(selected_scale,"selected_scale"),scale,rel_tol=1e-9,abs_tol=1e-12):
        raise ValueError("NBC: both components must use lower independent fitted factor")
    ranges={a:scaling_period_range(evidence["tn90_"+a+"_s"],
                                  evidence["t1_"+a+"_s"],evidence["r_mu"])
            for a in ("x","y")}
    return dict(status="METADATA_SCREEN_ONLY_NOT_NBC_DESIGN_APPROVAL",
                nbc_source=NBC105_URL,code="NBC 105:2025",
                max_dt_s=bound,matching_period_windows_s=ranges,
                shared_pair_scale=scale,
                independent_spectrum_reproduced=False,
                gravity_pdelta_torsion_materials_approved=False)

def write_preflight(target,evidence,**kwargs):
    report=validate_nbc105_design_metadata(evidence,**kwargs)
    file=Path(target);file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    return report

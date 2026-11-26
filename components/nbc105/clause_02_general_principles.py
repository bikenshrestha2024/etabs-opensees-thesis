"""NBC 105:2025 §2, printed pp.10–16: performance declaration checks.

This module evaluates declarations, never certifies structural adequacy.
Engineering evidence (overturning, sliding, ductility and function) remains external.
"""
from __future__ import annotations
import math

__all__=["verification_check","PERFORMANCE_STATES","RETURN_PERIOD_YEARS",
         "RIGID_DIAPHRAGM_TOLERANCE","rigid_diaphragm_check"]
PERFORMANCE_STATES=("ULS","SLS")
RETURN_PERIOD_YEARS={"ULS":475,"SLS":20}

def verification_check(*,uls:bool,sls:bool,overturning:bool,sliding:bool,
                       foundation:bool,evacuation_components:bool)->dict:
    """§2.1.1–2.1.3, printed pp.10–11: mandatory verification declarations.
[REF NBC105-2025 §2, printed pp. 10–16]"""
    flags=locals()
    if any(type(v) is not bool for v in flags.values()):
        raise ValueError("NBC §2 inputs must be explicit boolean declarations")
    missing=[k for k,v in flags.items() if not v]
    return {"status":"PASS_INPUT_DECLARATIONS_ONLY" if not missing
            else "MISSING_REQUIRED_DECLARATIONS","missing":missing,
            "acceptance":"DOCUMENT_CHECK_ONLY_NOT_PHYSICAL_VERIFICATION"}


RIGID_DIAPHRAGM_TOLERANCE=0.10   # printed 2.2.4 D, p.14

def rigid_diaphragm_check(flexible_displacements_m,rigid_displacements_m):
    """§2.2.4 D, printed p.14: may a diaphragm be taken as rigid?

    [REF NBC105-2025 §2.2.4 D, printed p. 14]
    Printed: "The diaphragm may be taken as being rigid, if, when it is modeled
    with its actual in-plane flexibility, its horizontal displacements nowhere
    exceed those resulting from the rigid diaphragm assumption by more than 10%
    of the corresponding absolute horizontal displacements under seismic
    forces." Inputs are the horizontal displacements (same points, same
    direction and seismic load case) of the model with actual in-plane
    flexibility and of the rigid-diaphragm model. At each point the excess is
    |u_flex| - |u_rigid| (a flexible displacement below the rigid one is not an
    exceedance) and must not be more than 0.10 |u_rigid| (strict "more than":
    exactly 10 percent passes). Where the rigid displacement is zero, any
    nonzero flexible displacement is an exceedance. Returns a per-point list
    and ``rigid_assumption_supported`` (False = FLAG: model the diaphragm as
    flexible). Both models are analysis outputs the caller must supply; this is
    an arithmetic check, not a diaphragm design.
    """
    f=[float(v) for v in flexible_displacements_m]
    r=[float(v) for v in rigid_displacements_m]
    if not f or len(f)!=len(r) or any(not math.isfinite(v) for v in f+r):
        raise ValueError("flexible and rigid displacements must be equal-length, non-empty and finite")
    points=[]
    for i,(uf,ur) in enumerate(zip(f,r)):
        excess=abs(uf)-abs(ur)
        limit=RIGID_DIAPHRAGM_TOLERANCE*abs(ur)
        exceeds=excess>limit
        points.append({"point":i,"flexible":uf,"rigid":ur,"excess":excess,"limit":limit,
                       "excess_over_rigid":(excess/abs(ur) if ur!=0 else (math.inf if excess>0 else 0.0)),
                       "exceeds":exceeds})
    flagged=[p["point"] for p in points if p["exceeds"]]
    return {"rigid_assumption_supported":not flagged,"flagged_points":flagged,"points":points,
            "tolerance":RIGID_DIAPHRAGM_TOLERANCE,
            "status":"RIGID_ASSUMPTION_SUPPORTED" if not flagged else "FLAG_DIAPHRAGM_NOT_RIGID_MODEL_AS_FLEXIBLE",
            "basis":"NBC105_2025_2.2.4_D_P14_ARITHMETIC_ONLY_NEEDS_TWO_MODEL_RUNS"}


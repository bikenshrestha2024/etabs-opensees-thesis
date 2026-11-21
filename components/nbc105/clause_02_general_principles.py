"""NBC 105:2025 §2, printed pp.10–16: performance declaration checks.

This module evaluates declarations, never certifies structural adequacy.
Engineering evidence (overturning, sliding, ductility and function) remains external.
"""
from __future__ import annotations

__all__=["verification_check","PERFORMANCE_STATES","RETURN_PERIOD_YEARS"]
PERFORMANCE_STATES=("ULS","SLS")
RETURN_PERIOD_YEARS={"ULS":475,"SLS":20}

def verification_check(*,uls:bool,sls:bool,overturning:bool,sliding:bool,
                       foundation:bool,evacuation_components:bool)->dict:
    """§2.1.1–2.1.3, printed pp.10–11: mandatory verification declarations."""
    flags=locals()
    if any(type(v) is not bool for v in flags.values()):
        raise ValueError("NBC §2 inputs must be explicit boolean declarations")
    missing=[k for k,v in flags.items() if not v]
    return {"status":"PASS_INPUT_DECLARATIONS_ONLY" if not missing
            else "MISSING_REQUIRED_DECLARATIONS","missing":missing,
            "acceptance":"DOCUMENT_CHECK_ONLY_NOT_PHYSICAL_VERIFICATION"}

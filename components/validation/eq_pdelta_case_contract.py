"""ETABS EQX/EQY + P-Delta case contracts, no fabricated case results.

The native ETABS workflow explicitly separates:
  nonlinear initial PDelta (1.2D + .5IL +/-1.5 EQ)
  linear lateral EQ (=1.0) using stiffness from that initial case,
  initial loads NOT included in the dependent response.
The unamplified response and code design-amplified response are different.
"""
from __future__ import annotations
import math

DEAD=("Self Weight","Floor Finish","Partition","Wall")
INITIAL_POSITIVE={**{p:1.2 for p in DEAD},"Live":0.5}
POSITIVE_EARTHQUAKE=1.5
CASE_LABELS={
 "X":{"initial_positive":"EQX+ P Delta Initial","dependent_positive":"EQX+ P-Delta","plain":"EQX"},
 "Y":{"initial_positive":"EQY+ P Delta Initial","dependent_positive":"EQY+ P-Delta","plain":"EQY"},
}

def initial_pattern_factors(axis, sign=1):
    """[REF docs/source/components/validation/eq_pdelta_case_contract.py.md] Synthetic evidence and source contract; not native acceptance."""
    axis=str(axis).upper()
    if axis not in CASE_LABELS or sign not in (-1,1):
        raise ValueError("Axis X/Y and sign +/-1 required")
    return {**INITIAL_POSITIVE,"EQ"+axis:sign*POSITIVE_EARTHQUAKE}

def check_etabs_case_contract(case, *, axis, role, initial_case=None):
    """Validate recorded native definition, never infer it from a case name.

    case is a caller-extracted dictionary using explicit normalized fields;
    no COM data is presumed to be present when called.
    
    [REF docs/source/components/validation/eq_pdelta_case_contract.py.md]
    """
    axis=str(axis).upper()
    if axis not in CASE_LABELS or role not in ("initial_positive","initial_negative","dependent_positive","plain"):
        raise ValueError("Invalid direction/role")
    issues=[]
    if not isinstance(case,dict): return ["NATIVE_CASE_DEFINITION_NOT_EXTRACTED"]
    case_type=str(case.get("analysis_type","")).upper()
    factors=case.get("load_pattern_factors")
    if not isinstance(factors,dict):
        issues.append("LOAD_PATTERN_FACTORS_MISSING")
        factors={}
    else:
        for k,v in factors.items():
            try:
                if not math.isfinite(float(v)):issues.append("NONFINITE_LOAD_FACTOR:"+k)
            except (ValueError,TypeError):
                issues.append("NONNUMERIC_LOAD_FACTOR:"+k)
    if role.startswith("initial_"):
        if case_type not in ("NONLINEAR STATIC","STATIC NONLINEAR"):
            issues.append("INITIAL_NOT_NONLINEAR_STATIC")
        if case.get("starts_unstressed") is not True:
            issues.append("INITIAL_NOT_VERIFIED_ZERO_STATE")
        if str(case.get("geometric_nonlinearity","")).lower() not in ("p-delta","pdelta"):
            issues.append("INITIAL_PDELTA_NOT_CONFIRMED")
        target=initial_pattern_factors(axis,-1 if role=="initial_negative" else 1)
        if set(factors)!=set(target):
            issues.append("INITIAL_PATTERN_SET_MISMATCH")
        else:
            for name,expected in target.items():
                try:
                    if abs(float(factors[name])-expected)>1e-9:
                        issues.append("WRONG_INITIAL_FACTOR:"+name)
                except (ValueError,TypeError):
                    issues.append("WRONG_INITIAL_FACTOR:"+name)
    elif role=="dependent_positive":
        if case_type!="LINEAR STATIC":
            issues.append("DEPENDENT_NOT_LINEAR_STATIC")
        if case.get("use_nonlinear_case_stiffness") is not True:
            issues.append("DEPENDENT_NONLINEAR_STIFFNESS_NOT_CONFIRMED")
        if case.get("initial_case_loads_included") is not False:
            issues.append("DEPENDENT_MUST_EXCLUDE_INITIAL_LOADS")
        if initial_case is None or case.get("stiffness_source_case")!=initial_case:
            issues.append("DEPENDENCY_CASE_MISMATCH")
        try: unit_factor=abs(float(factors.get("EQ"+axis,0))-1.)<=1e-9
        except (ValueError,TypeError): unit_factor=False
        if set(factors)!={"EQ"+axis} or not unit_factor:
            issues.append("DEPENDENT_EQ_UNIT_FACTOR_MISMATCH")
    else:
        if case_type!="LINEAR STATIC":issues.append("PLAIN_EQ_NOT_LINEAR_STATIC")
        try: unit_factor=abs(float(factors.get("EQ"+axis,0))-1.)<=1e-9
        except (ValueError,TypeError): unit_factor=False
        if set(factors)!={"EQ"+axis} or not unit_factor:
            issues.append("PLAIN_EQ_UNIT_FACTOR_MISMATCH")
        if case.get("use_nonlinear_case_stiffness") is True:
            issues.append("PLAIN_EQ_USES_NONLINEAR_STIFFNESS")
    return issues

def compare_pdelta_stiffness_response(*, plain_roof_m, dependent_roof_m,
                                     plain_base_kN, dependent_base_kN):
    """Signed numerical comparison; stiffness difference is NOT a code PASS.
    [REF docs/source/components/validation/eq_pdelta_case_contract.py.md]
    """
    values=[float(v) for v in (plain_roof_m,dependent_roof_m,
                                plain_base_kN,dependent_base_kN)]
    if not all(math.isfinite(v) for v in values):
        raise ValueError("Nonfinite response")
    return {
        "roof_displacement_delta_m":values[1]-values[0],
        "base_shear_delta_kN":values[3]-values[2],
        "roof_change_percent":None if abs(values[0])<1e-12 else
            100*(values[1]-values[0])/abs(values[0]),
        "base_change_percent":None if abs(values[2])<1e-12 else
            100*(values[3]-values[2])/abs(values[2]),
        "status":"NUMERIC_DIAGNOSTIC_NOT_STRUCTURAL_ACCEPTANCE",
    }

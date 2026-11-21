"""Fail-closed native NBC 105:2025 engineering evidence checkpoint.

[REF NBC105-2025 Clauses 1–10; docs/nbc105/IMPLEMENTATION_STATUS_20261121.md]
A V10.7 ETABS acceptance JSON can establish matched RS target shears. It cannot
establish model equivalence, true Rayleigh displacements, stiffness, nonlinear
wall convergence or full M0–M6 records. No private files are uploaded.
"""
from __future__ import annotations
import json
import math
import re
from pathlib import Path

__all__=["MANDATORY_GATES","evaluate_project_evidence"]
MANDATORY_GATES=(
    "source_identity","code_period","rayleigh_period","rs_base_shear",
    "soil_vs30","modal_mass_and_missing_mass","drift_and_torsion",
    "wall_grouping_and_stiffness","etabs_opensees","nltha_wall",
    "nltha_224","parts_and_components","all_clause_callers"
)
_DIGEST=re.compile(r"^[a-fA-F0-9]{64}$")

def _gate(status,explanation,**metrics):
    return {"status":status,"reason":explanation,**metrics}

def _positive(v,name):
    if isinstance(v,bool):
        raise ValueError(f"{name} must be finite positive number")
    try: number=float(v)
    except (TypeError,ValueError,OverflowError) as exc:
        raise ValueError(f"{name} must be finite positive number") from exc
    if not math.isfinite(number) or number<=0:
        raise ValueError(f"{name} must be finite positive number")
    return number

def _rs_match(result, tolerance_fraction):
    case_rows=result.get("final_rs")
    if not isinstance(case_rows,list):
        return _gate("OPEN","Full two-direction ETABS post-analysis base shears not provided")
    cases={}
    for row in case_rows:
        if not isinstance(row,dict):
            return _gate("INVALID_EVIDENCE","Non-object RS entry")
        name=str(row.get("case","")).upper()
        direction="X" if "RSX" in name and "RSY" not in name else (
            "Y" if "RSY" in name and "RSX" not in name else None)
        if direction is None or direction in cases:
            return _gate("INVALID_EVIDENCE","RS cases must uniquely identify X and Y")
        try:
            reference=_positive(row.get("target_kN"),"target_kN")
            actual=_positive(row.get("observed_kN"),"observed_kN")
        except ValueError as exc:
            return _gate("INVALID_EVIDENCE",str(exc))
        error=abs(actual-reference)/reference
        cases[direction]={"error_fraction":error,
                          "target_kN":reference,"observed_kN":actual}
    if set(cases)!={"X","Y"}:
        return _gate("OPEN","Both independent RSX/RSY post-run cases are required")
    if any(x["error_fraction"]>tolerance_fraction for x in cases.values()):
        return _gate("MISMATCH","Observed RS base shears exceed numerical tolerance",
                     directions=cases,tolerance_fraction=tolerance_fraction)
    return _gate("NUMERIC_MATCH_REPRODUCED",
                 "RS target-to-observed shear arithmetic matches; not code-complete design",
                 directions=cases,tolerance_fraction=tolerance_fraction)

def evaluate_project_evidence(evidence,*,rs_tolerance_fraction=.001):
    """Assess reported evidence without accepting unsupported engineering claims.

    [REF NBC105-2025 §§3.2,5.1,5.4,5.5,7.3,7.5,9.3,10; docs/nbc105/README.md]
    A numeric RS pass never upgrades the full-model status. Native EDB and
    analysis results must be independently reviewed by the engineer.
    """
    if not isinstance(evidence,dict):
        raise ValueError("acceptance source must be a JSON object")
    digest=evidence.get("source_sha256")
    if not isinstance(digest,str) or not _DIGEST.fullmatch(digest):
        raise ValueError("original ETABS source_sha256 missing or malformed")
    tol=_positive(rs_tolerance_fraction,"RS fractional tolerance")
    if tol>=1:raise ValueError("RS tolerance must be less than 1")
    policy=str(evidence.get("period_policy",""))
    periods=evidence.get("adopted_periods") or {}
    if not isinstance(periods,dict):periods={}
    period_valid=False
    try:
        period_valid=all(_positive(periods.get(axis),f"T_{axis}")>0 for axis in ("X","Y"))
    except ValueError:
        pass
    gates={
        "source_identity":_gate("PARTIAL_PROVENANCE",
            "Source EDB SHA declared; saved EDB SHA, exact native model/analysis state and matching OpenSees source must be compared",
            source_sha256=digest.lower()),
        "code_period":_gate("OPEN" if not period_valid or "NO_ANALYTICAL_PERIOD_CHECK" in policy else "REVIEW_REQUIRED",
            "NBC §5.1 requires the lesser of verified Rayleigh and amplified empirical periods; saved periods alone are insufficient",
            policy=policy,reported_periods=periods),
        "rayleigh_period":_gate("OPEN",
            "Physical floor-CM translations, source mass ledger, force-work sums, gravity/P-Delta and matching ETABS model not supplied as independently validated native evidence"),
        "rs_base_shear":_rs_match(evidence,tol),
        "soil_vs30":_gate("OPEN",
            "For the 95 m project, §4.1.3.1 mandates measured Vs30; geotechnical evidence was not independently checked"),
        "modal_mass_and_missing_mass":_gate("OPEN",
            "Native X/Y Ritz/eigen mass participation >=90% and >=33 Hz missing-mass treatment require source-bound modal results"),
        "drift_and_torsion":_gate("OPEN",
            "Native design drift, edge displacements, accidental torsion and unscaled MRSM displacement channels not independently checked"),
        "wall_grouping_and_stiffness":_gate("OPEN",
            "Two 12 m envelope wall grouping, openings, actual coupled-wall stiffness and Table 3-1 cracked modifiers need structural verification"),
        "etabs_opensees":_gate("OPEN",
            "Same-source support sets, masses, all joint reaction components and elastic tangent stiffness have not been reconciled",
            original_report=str(evidence.get("openSees_equivalence","NOT_PROVIDED"))),
        "nltha_wall":_gate("OPEN",
            "First-step X-wall local-force/convergence issue and calibrated hysteretic material response not demonstrated resolved"),
        "nltha_224":_gate("OPEN",
            "224 unique, full-duration and converged M0–M6/ground-motion orientation histories with raw logs not provided"),
        "parts_and_components":_gate("OPEN",
            "Component inventory, Table 10-1 period checks, connection capacities, service cutoffs and anchor detailing unverified"),
        "all_clause_callers":_gate("CODE_REVIEW_REQUIRED",
            "All ten reference modules are available; active caller tests and complete source semantic review must pass on same commit")
    }
    return {"standard":"NBC 105:2025",
            "overall":"BLOCKED_NOT_FULL_ENGINEERING_ACCEPTANCE",
            "source_sha256":digest.lower(),
            "gates":gates,
            "unverified_gates":[k for k,v in gates.items()
                                if v["status"] not in ("NUMERIC_MATCH_REPRODUCED",)],
            "important":"Numeric target equality is not proof of ETABS/OpenSees equivalence or seismic-code compliance"}

def main(argv=None):
    """Read a native acceptance JSON locally without uploading its contents.

    [REF NBC105-2025 Clauses 1–10; docs/nbc105/README.md]
    """
    import argparse
    p=argparse.ArgumentParser(description="NBC 105 local engineering evidence audit")
    p.add_argument("acceptance_json",help="Path to the locally saved ETABS acceptance JSON")
    args=p.parse_args(argv)
    record=json.loads(Path(args.acceptance_json).read_text(encoding="utf-8-sig"))
    result=evaluate_project_evidence(record)
    print(json.dumps(result,indent=2,allow_nan=False))
    return 2 if result["overall"].startswith("BLOCKED") else 0

if __name__=="__main__":
    raise SystemExit(main())

"""Fail-closed evidence register for ETABS EQX/EQY P-Delta verification.

Read-only: NO ETABS COM call, no solver, no changes to load/mass/EDB.
Stores source definitions and verifies OpenSees case evidence with SHA256.
An ETABS *case name* is NOT a verified P-Delta analysis.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

DIRECTIONS=("X","Y")
REQUIRED=("etabs_case_name","etabs_analysis_type","etabs_pdelta_enabled",
          "etabs_combination_or_case_definition","etabs_evidence_path",
          "opensees_result_path","opensees_preload_evidence_path",
          "opensees_source_model_sha256","limit_state","axis",
          "pdelta_method","gravity_factors","lateral_action_factors")

def _digest(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def _json(path):
    val=json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(val,dict):
        raise ValueError("Expected JSON object: "+str(path))
    return val

def _finite_positive(value, description):
    n=float(value)
    if not math.isfinite(n) or n<=0:
        raise ValueError(description+" must be positive and finite")
    return n

def verify_eq_pdelta_evidence(index_path, output_dir):
    """Generate reviewable evidence register; do not claim physical acceptance.

    Index has X and Y entries; values must be actual native ETABS / OpenSees
    evidence, not guessed case labels or inferred analysis settings.
    """
    index_file=Path(index_path).resolve()
    index=_json(index_file)
    if set(index)!={"X","Y"}:
        raise ValueError("Provide exact X and Y case configurations")
    rows=[]
    for axis in DIRECTIONS:
        record=index[axis]
        if not isinstance(record,dict):
            raise ValueError(axis+": case entry must be an object")
        missing=[k for k in REQUIRED if k not in record or record[k] in ("",None)]
        issues=[("MISSING_FIELDS: "+", ".join(missing))] if missing else []
        if record.get("axis")!=axis:
            issues.append("AXIS_MISMATCH")
        if record.get("etabs_pdelta_enabled") is not True:
            issues.append("NATIVE_ETABS_PDELTA_NOT_CONFIRMED")
        if record.get("limit_state") not in ("ULS","SLS"):
            issues.append("LIMIT_STATE_NOT_EXPLICIT")
        if not isinstance(record.get("gravity_factors"),dict) or not record.get("gravity_factors"):
            issues.append("MISSING_GRAVITY_PATTERN_FACTORS")
        if not isinstance(record.get("lateral_action_factors"),dict) or not record.get("lateral_action_factors"):
            issues.append("MISSING_SIGNED_LATERAL_PATTERN_FACTORS")
        hashes={}
        for kind,key in (("native_etabs","etabs_evidence_path"),
                         ("opensees_result","opensees_result_path"),
                         ("opensees_preload","opensees_preload_evidence_path")):
            raw=record.get(key)
            if not isinstance(raw,str) or not raw.strip():
                continue
            path=Path(raw).expanduser()
            if not path.is_file():
                issues.append("MISSING_"+kind.upper()+"_FILE")
            else:
                hashes[kind]=dict(filename=path.name,sha256=_digest(path),
                                  bytes=path.stat().st_size)
        if record.get("opensees_source_model_sha256"):
            sha=str(record["opensees_source_model_sha256"])
            if len(sha)!=64 or any(x not in "0123456789abcdef" for x in sha.lower()):
                issues.append("INVALID_MODEL_SHA256")
        # This index is a documentation/identity gate: no claim that saved
        # load case, response arrays, or geometric stiffness are correct.
        response_names=("etabs_base_shear_kN","opensees_base_shear_kN",
                        "etabs_roof_displacement_m","opensees_roof_displacement_m")
        supplied={k:record[k] for k in response_names if k in record}
        if len(supplied)!=len(response_names):
            issues.append("INCOMPLETE_RESPONSE_PAIRS")
        for name,value in supplied.items():
            try:
                n=float(value)
                if not math.isfinite(n): raise ValueError()
            except (TypeError,ValueError):
                issues.append("INVALID_RESPONSE_"+name.upper())
        # No comparison of signed base shear unless source case, global
        # coordinate axes, signed loading and PDelta procedures match.
        if (record.get("etabs_analysis_type") not in
                ("Nonlinear Static","Static Nonlinear","Linear Static PDelta",
                 "Linear Static")):
            issues.append("UNVERIFIED_ETABS_ANALYSIS_TYPE")
        if not record.get("pdelta_method"):
            issues.append("UNDECLARED_OPENSEES_GEOMETRIC_STIFFNESS_METHOD")
        rows.append(dict(axis=axis,
            case_name=record.get("etabs_case_name"),
            case_scope=record.get("etabs_analysis_type"),
            evidence_hashes=hashes,proposed_responses=supplied,
            missing_or_blocked=sorted(set(issues)),
            status="EVIDENCE_REGISTERED_NOT_ENGINEERING_ACCEPTED"
                   if not issues else "BLOCKED_MISSING_OR_INCOMPATIBLE_EVIDENCE"))
    out=Path(output_dir)
    out.mkdir(parents=True,exist_ok=True)
    report={
        "schema":"eqx-eqy-pdelta-evidence-v1",
        "index_path":str(index_file),
        "index_sha256":_digest(index_file),
        "status":"PRELIMINARY_NOT_ETABS_OPENSEES_EQUIVALENCE",
        "cases":rows,
        "distinct_from_IS16700_initial_signed_EL_checks":True,
        "distinct_from_100_percent_Dead_plus_100_percent_Live_gravity":True,
        "automatic_gravity_or_seismic_factor_changes":False,
        "requirements":[
            "Obtain actual ETABS nonlinear/static case definitions and PDelta geometric stiffness settings",
            "Preserve original ETABS EDB identity and corresponding source-export fingerprint",
            "Confirm same earthquake lateral source and signed direction in ETABS/OpenSees",
            "Verify actual gravity preload factors, geometric stiffness, support policy and mass model",
            "Compare signed base shear, story forces, displacements, drift and selected member axial/shear result after case compatibility review",
            "Independently check residual unbalanced forces and solver convergence; do not promote a registered file to structural PASS",
        ]}
    path=out/"EQX_EQY_PDelta_Evidence_Gates.json"
    path.write_text(json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    return report

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("index",help="JSON with exact X/Y native and OpenSees case definitions")
    parser.add_argument("--out",default="EQ_PDelta_Evidence")
    args=parser.parse_args()
    result=verify_eq_pdelta_evidence(args.index,args.out)
    for case in result["cases"]:
        print(case["axis"],case["status"],case["missing_or_blocked"])

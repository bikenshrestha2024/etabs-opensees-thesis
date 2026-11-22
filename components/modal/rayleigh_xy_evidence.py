"""Independent NBC105 §5.1.1 X/Y Rayleigh saved-run diagnostic.

Consumes separately solved, source-hashed incremental lateral-perturbation
results. Never generates solver displacements or makes ETABS equivalence claims.

Schema:
{"source": {"edb_sha256": <sha256>, "assembled_model_sha256": <sha256>,
 "story_ledger_sha256": <sha256>, "limit_state": "ULS"|"SLS",
 "gravity_equilibrated": true, "torsion_suppressed": true,
 "displacement_basis": "PHYSICAL_FLOOR_COM", "unit": "kN_m_s"},
 "X": {"reference":[{"master":1,"weight_kN":100,"force_kN":2,
                      "baseline_m":0,"loaded_m":0.01}, ...],
       "perturbed":[{...},...], "etabs_period_s": 1.5},
 "Y": { ... }}

The optional perturbed profile must come from a truly separate solve with
a different lateral force amplitude and an identical gravity/model state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from components.nbc105.clause_05_dynamic_characteristics import rayleigh_period_s


def _positive(value, label):
    if isinstance(value,bool):
        raise ValueError(label + " must be finite positive")
    try:
        n=float(value)
    except (TypeError,ValueError,OverflowError) as exc:
        raise ValueError(label + " must be numeric") from exc
    if not math.isfinite(n) or n<=0:
        raise ValueError(label + " must be finite positive")
    return n


def _finite(value,label):
    if isinstance(value,bool):
        raise ValueError(label + " must be finite")
    try:n=float(value)
    except (TypeError,ValueError,OverflowError) as exc:
        raise ValueError(label + " invalid") from exc
    if not math.isfinite(n):
        raise ValueError(label + " must be finite")
    return n


def _profile(rows,axis):
    if not isinstance(rows,list) or not rows:
        raise ValueError(axis + ": physical floor profile required")
    seen=set()
    observed=[]
    for entry in rows:
        if not isinstance(entry,dict):
            raise ValueError(axis + ": malformed floor row")
        tag=entry.get("master")
        if isinstance(tag,bool) or not isinstance(tag,int) or tag<=0 or tag in seen:
            raise ValueError(axis + ": duplicate/invalid master tag")
        seen.add(tag)
        wi=_positive(entry.get("weight_kN"),"Wi")
        fi=_finite(entry.get("force_kN"),"Fi")
        baseline=_finite(entry.get("baseline_m"),"gravity baseline")
        loaded=_finite(entry.get("loaded_m"),"loaded displacement")
        observed.append((tag,wi,fi,loaded-baseline))
    weights=[row[1] for row in observed]
    forces=[row[2] for row in observed]
    displacements=[row[3] for row in observed]
    period=rayleigh_period_s(weights,displacements,forces)
    return {"period_s":period, "total_weight_kN":math.fsum(weights),
            "force_kN":math.fsum(forces), "rows":observed}


def _amplitude_check(base,perturbed,axis):
    a,b=base["rows"],perturbed["rows"]
    if len(a)!=len(b):
        raise ValueError(axis+": changed floor count between solves")
    for p,q in zip(a,b):
        if p[0]!=q[0] or not math.isclose(p[1],q[1],rel_tol=1e-9,abs_tol=1e-7):
            raise ValueError(axis+": changed floor ledger or ordering")
    factors=[]
    for p,q in zip(a,b):
        if abs(p[2])>1e-12:
            factors.append(q[2]/p[2])
        elif abs(q[2])>1e-12:
            raise ValueError(axis+": force added at previously unloaded floor")
    if not factors:
        raise ValueError(axis+": no reference floor forces")
    ratio=math.fsum(factors)/len(factors)
    if not math.isfinite(ratio) or ratio<=0 or abs(ratio-1)<.01:
        raise ValueError(axis+": require independent, clearly different force amplitude")
    if max(abs(t-ratio) for t in factors)>1e-6*max(1,abs(ratio)):
        raise ValueError(axis+": reference lateral load vectors are not scaled copies")
    maximum_shape_error=0.
    for p,q in zip(a,b):
        predicted=p[3]*ratio
        magnitude=max(abs(predicted),abs(q[3]))
        if magnitude>1e-10:
            maximum_shape_error=max(maximum_shape_error,abs(q[3]-predicted)/magnitude)
    period_error=abs(perturbed["period_s"]/base["period_s"]-1)
    # 1% shape and 0.1% period are diagnostic tolerances, not NBC acceptance.
    return {"force_ratio":ratio,"max_displacement_scaling_error":maximum_shape_error,
            "period_change_fraction":period_error,
            "diagnostic_linear_scaling_pass":maximum_shape_error<=.01 and period_error<=.001,
            "threshold_basis":"DIAGNOSTIC_ONLY_NOT_CODE_OR_MODEL_ACCEPTANCE"}


def audit_rayleigh_pair(payload):
    """Reconstruct both axes; reject unsupported native equivalence assertions.

    [REF NBC105-2025 §5.1.1 printed p.28]
    """
    source=payload.get("source")
    if not isinstance(source,dict):
        raise ValueError("Source hashes and solver state required")
    for key in ("edb_sha256","assembled_model_sha256","story_ledger_sha256"):
        sha=source.get(key)
        if not isinstance(sha,str) or len(sha)!=64 or any(
            c not in "0123456789abcdefABCDEF" for c in sha):
            raise ValueError("Missing/invalid source SHA256: "+key)
    if source.get("limit_state") not in ("ULS","SLS"):
        raise ValueError("Explicit limit state required")
    if source.get("gravity_equilibrated") is not True or source.get(
            "torsion_suppressed") is not True:
        raise ValueError("Native gravity/torsion state not declared")
    if source.get("displacement_basis")!="PHYSICAL_FLOOR_COM":
        raise ValueError("Use physical floor centre of mass translation, not raw master")
    if source.get("unit")!="kN_m_s":
        raise ValueError("Rayleigh data must use kN, m and s")
    result={"status":"SAVED_ARITHMETIC_DIAGNOSTIC_NOT_NATIVE_ACCEPTANCE",
            "source":source, "directions":{}, "unresolved":[
              "Verify source EDB, analytical mesh, physical floor COM and MPC topology",
              "Verify material stiffness, end zones, P-Delta gravity tangent and wall connections",
              "Reconcile distributed nodal mass with NBC storey weight representation",
              "Compare identical native ETABS/OpenSees gravity state and load cases",
            ]}
    for axis in ("X","Y"):
        section=payload.get(axis)
        if not isinstance(section,dict):
            raise ValueError("Both X and Y saved Rayleigh directions are mandatory")
        base=_profile(section.get("reference"),axis)
        native_t=section.get("etabs_period_s")
        etabs_period=_positive(native_t,axis+" ETABS period") if native_t is not None else None
        comparison=None if etabs_period is None else {
            "etabs_period_s":etabs_period,
            "opensees_rayleigh_period_s":base["period_s"],
            "difference_s":base["period_s"]-etabs_period,
            "difference_percent":100*(base["period_s"]/etabs_period-1),
            "not_equivalent_without_identical_method_and_state":True,
        }
        perturbed_rows=section.get("perturbed")
        amplitude=None
        if perturbed_rows is not None:
            amplitude=_amplitude_check(base,_profile(perturbed_rows,axis),axis)
        result["directions"][axis]={"rayleigh_period_s":base["period_s"],
            "floor_count":len(base["rows"]),
            "seismic_weight_kN":base["total_weight_kN"],
            "reference_force_kN":base["force_kN"],
            "comparison":comparison,"amplitude_check":amplitude}
    return result


def write_audit(json_path, output_dir):
    """[REF docs/source/components/modal/rayleigh_xy_evidence.py.md]
    Persist saved dual-axis source-hashed diagnostic only.
    """
    path=Path(json_path)
    report=audit_rayleigh_pair(json.loads(path.read_text(encoding="utf-8-sig")))
    report["saved_source_sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
    dest=Path(output_dir);dest.mkdir(parents=True,exist_ok=True)
    (dest/"Rayleigh_XY_Independent_Evidence.json").write_text(
        json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json")
    parser.add_argument("output_dir")
    a=parser.parse_args()
    print(json.dumps(write_audit(a.input_json,a.output_dir),indent=2))

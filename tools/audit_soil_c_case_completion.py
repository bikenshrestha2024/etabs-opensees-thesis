"""Read-only completeness audit for 7 variants x 2 limits x 8 Soil C pairs x XY/YX.

Does not execute the solver and never promote exploratory outputs to a
qualified optimum. Inputs are from 36_SOIL_C_NLTHA_RUN_MATRIX.py.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

VARIANTS = frozenset("M"+str(i) for i in range(7))
EVENTS = frozenset(("Gorkha","Landers","Northridge","Kobe",
                    "Kocaeli","Chi-Chi","Hector Mine","Loma Prieta"))
LIMITS = frozenset(("ULS","SLS"))
ORIENTATIONS = ("XY","YX")
REQUIRED_METRICS = (
    "peak_roof_UX_m", "peak_roof_UY_m", "max_story_drift_X",
    "max_story_drift_Y", "peak_base_shear_X_kN", "peak_base_shear_Y_kN",
    "peak_roof_torsion_rad",
)
STATUS = ("NOT_RUN","FAILED","INCOMPLETE","RESEARCH_ONLY_FULL_RECORD",
          "PROJECT_EVIDENCE_MISSING")


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def inspect_case(output_dir, variant, state, earthquake, orientation):
    """Check real case summary and accepted-history gate, not folder naming."""
    directory=Path(output_dir)/orientation
    result=dict(variant=variant,limit_state=state,event=earthquake,
                orientation=orientation,status="NOT_RUN")
    failure=directory/"FAILED.json"
    if not failure.is_file():
        failure=Path(output_dir)/"INCOMPLETE.json"
    summary=directory/"Case_Summary.json"
    gate=directory/"Accepted_History_Completion_Gate.json"
    if failure.is_file():
        result.update(status="FAILED",evidence=str(failure))
        return result
    if not summary.is_file() or not gate.is_file():
        if summary.exists() or gate.exists():
            result.update(status="INCOMPLETE",reason="Missing summary or duration gate")
        return result
    try:
        a=_read(summary); b=_read(gate)
        if a.get("variant_id")!=variant or a.get("limit_state")!=state or a.get("orientation")!=orientation:
            raise ValueError("Reported model variant/state/orientation differs from matrix")
        if a.get("pair_id") not in (earthquake, earthquake.replace(" ","_")):
            raise ValueError("Reported earthquake pair differs from matrix")
        if not isinstance(a.get("record_sha256"),str) or len(a["record_sha256"])!=64:
            raise ValueError("Missing paired record SHA256")
        if not isinstance(a.get("model_sha256"),str) or len(a["model_sha256"])!=64:
            raise ValueError("Missing model SHA256")
        if b.get("status")!="FULL_DURATION_NUMERIC_SCREEN" or b.get("full_record_completed") is not True:
            raise ValueError("Accepted history did not reach full record")
        if b.get("accepted_channels_finite") is not True:
            raise ValueError("Accepted history contains nonfinite responses")
        if a.get("diagnostic_excitation")!="XY":
            raise ValueError("X-only/Y-only diagnostic cannot count as a full paired record")
        for name in REQUIRED_METRICS:
            try:
                value=float(a[name])
            except (KeyError,TypeError,ValueError,OverflowError) as exc:
                raise ValueError("Missing/non-numeric response: "+name) from exc
            if not math.isfinite(value):
                raise ValueError("Nonfinite response metric: "+name)
        result.update(status="RESEARCH_ONLY_FULL_RECORD",
                      evidence=str(summary),
                      model_sha256=a["model_sha256"],
                      record_sha256=a["record_sha256"])
        return result
    except (ValueError,TypeError,OSError,KeyError,json.JSONDecodeError) as exc:
        result.update(status="INCOMPLETE",reason=str(exc))
        return result


def audit_matrix(csv_path):
    """Require exact intended 112 cases; report all 224 orientation outcomes."""
    matrix=Path(csv_path).resolve(strict=True)
    with matrix.open(encoding="utf-8-sig",newline="") as stream:
        cases=list(csv.DictReader(stream))
    if len(cases)!=112:
        raise ValueError("Expected exactly 112 planned variant/state/earthquake groups")
    seen=set()
    results=[]
    for row in cases:
        key=(row.get("variant"),row.get("limit_state"),row.get("earthquake"))
        if key in seen or key[0] not in VARIANTS or key[1] not in LIMITS or key[2] not in EVENTS:
            raise ValueError("Duplicate/missing/invalid M0–M6, ULS/SLS, Soil C event row")
        seen.add(key)
        output=row.get("output_directory")
        if not output:
            raise ValueError("Missing output directory in run matrix")
        for orientation in ORIENTATIONS:
            results.append(inspect_case(output,*key,orientation))
    expected={(v,s,e) for v in VARIANTS for s in LIMITS for e in EVENTS}
    if seen!=expected:
        raise ValueError("Planned cases do not cover exact 7 x 2 x 8 cases")
    counts=dict(Counter(r["status"] for r in results))
    complete=counts.get("RESEARCH_ONLY_FULL_RECORD",0)
    return dict(
        status="NOT_READY_FOR_OPTIMUM",
        completed_research_only=complete,
        expected_analyses=224,
        state_counts=counts,
        results=results,
        optimum_selected=False,
        actual_materials_validated=False,
        nbc_compliance_verified=False,
        required_next_evidence=[
            "Native E-SFI wall stability with actual core openings, confinement and source load mapping",
            "Actual FVD and BRB calibrated specimen behavior and device connections",
            "SeismoMatch original pair scaling provenance and modal interval",
            "Actual ULS and independently reviewed SLS motion basis",
            "All 224 full Soil C orientation/case histories and declared acceptance criteria",
            "Outrigger location/configuration sensitivity with consistent gravity, mass and excitation",
        ])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=audit_matrix(args.matrix)
    if args.output.exists():
        raise FileExistsError("Refusing to overwrite original audit results")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False),encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="results"},indent=2))


if __name__=="__main__":
    main()

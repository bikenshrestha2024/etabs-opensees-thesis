"""Read-only completeness audit for 7 variants x 2 limits x 8 Soil C pairs x XY/YX.

Does not execute the solver and never promote exploratory outputs to a
qualified optimum. Inputs are from 36_SOIL_C_NLTHA_RUN_MATRIX.py.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from components.nonlinear_time_history.full_record_gate import verify_accepted_history

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
    """Recheck the recorded time history before counting a case as complete."""
    directory=Path(output_dir)/orientation
    result=dict(variant=variant,limit_state=state,event=earthquake,
                orientation=orientation,status="NOT_RUN")
    failure=directory/"FAILED.json"
    if not failure.is_file():
        failure=Path(output_dir)/"INCOMPLETE.json"
    summary=directory/"Case_Summary.json"
    gate=directory/"Accepted_History_Completion_Gate.json"
    history=directory/"Building_Nonlinear_history.csv"
    if failure.is_file():
        result.update(status="FAILED",evidence=str(failure))
        return result
    if not all(path.is_file() for path in (summary, gate, history)):
        if any(path.exists() for path in (summary, gate, history)):
            result.update(status="INCOMPLETE",reason="Missing summary, duration gate or recorded history")
        return result
    try:
        a=_read(summary); b=_read(gate)
        if not isinstance(a, dict) or not isinstance(b, dict):
            raise ValueError("Case summary and duration gate must be JSON objects")
        if a.get("variant_id")!=variant or a.get("limit_state")!=state or a.get("orientation")!=orientation:
            raise ValueError("Reported model variant/state/orientation differs from matrix")
        if a.get("pair_id") not in (earthquake, earthquake.replace(" ","_")):
            raise ValueError("Reported earthquake pair differs from matrix")
        # A 64-character nonhex string is not a SHA256 digest, and cannot
        # be used as provenance of either the model or the paired record.
        for label in ("record_sha256","model_sha256"):
            digest=a.get(label)
            if (not isinstance(digest,str) or len(digest)!=64 or
                    any(c not in "0123456789abcdefABCDEF" for c in digest)):
                raise ValueError("Missing/invalid "+label+" SHA256")
        if b.get("status")!="FULL_DURATION_NUMERIC_SCREEN" or b.get("full_record_completed") is not True:
            raise ValueError("Accepted history did not reach full record")
        if b.get("accepted_channels_finite") is not True:
            raise ValueError("Accepted history contains nonfinite responses")
        # A standalone boolean from a stale or hand-edited gate is not enough.
        # Check the measured last accepted state against the actual source
        # record duration and the requested endpoint in seconds.
        durations={}
        for key in ("full_record_duration_s","requested_duration_s","achieved_time_s"):
            if isinstance(b.get(key), bool):
                raise ValueError("Invalid boolean accepted duration: "+key)
            try:
                number=float(b[key])
            except (KeyError,ValueError,TypeError,OverflowError) as exc:
                raise ValueError("Missing/invalid accepted duration: "+key) from exc
            if not math.isfinite(number) or number<=0:
                raise ValueError("Nonpositive/nonfinite accepted duration: "+key)
            durations[key]=number
        record=durations["full_record_duration_s"]
        requested=durations["requested_duration_s"]
        achieved=durations["achieved_time_s"]
        if abs(record-requested)>1e-7 or abs(achieved-requested)>1e-7:
            raise ValueError("Accepted duration does not reach full source record")
        # bool, 2.5, "2", or 2.9 must never be silently coerced into
        # an actual count of accepted integration states.
        accepted_states=b.get("accepted_states")
        if type(accepted_states) is not int:
            raise ValueError("Accepted state count must be an integer JSON number")
        if accepted_states<2:
            raise ValueError("Accepted history requires at least two accepted states")
        with history.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, strict=True)
            columns = reader.fieldnames or []
            if len(columns) != len(set(columns)):
                raise ValueError("Recorded history contains duplicate column names")
            trace = verify_accepted_history(list(reader), record, requested)
        if not trace["full_record_completed"] or abs(trace["achieved_time_s"]-achieved)>1e-7:
            raise ValueError("Recorded history duration differs from full-duration gate")
        if trace["accepted_states"] != accepted_states:
            raise ValueError("Recorded history state count differs from duration gate")
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
                      history=str(history),
                      model_sha256=a["model_sha256"],
                      record_sha256=a["record_sha256"])
        return result
    except (ValueError,TypeError,OSError,KeyError,csv.Error) as exc:
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

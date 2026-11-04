"""Full-record physical-duration audit for NLTHA accepted states (not design approval).

PEER 2015/12 component benchmarks and NBC105:2025 nonlinear response history
requirements remain separate scientific/acceptance gates.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

def verify_numeric_accepted_row(row, *, row_index=None):
    """Fail closed before writing a solver-accepted row to the CSV output.

    A solver return code of zero does not guarantee finite displacements,
    forces, wall stresses, or accelerations in every configured recorder.
    """
    where=f" at row {row_index}" if row_index is not None else ""
    if not isinstance(row, dict) or "time_s" not in row or len(row)<2:
        raise ValueError("Accepted history requires time_s and response channels" + where)
    for name, value in row.items():
        if isinstance(value, bool) or value is None:
            raise ValueError(f"Invalid accepted response {name}{where}")
        try:
            number=float(value)
        except (ValueError, TypeError, OverflowError) as exc:
            raise ValueError(f"Invalid accepted response {name}{where}") from exc
        if not math.isfinite(number):
            raise ValueError(f"Nonfinite accepted response {name}{where}")
    return row


def verify_accepted_history(rows, record_end_s, requested_end_s, *,
                            time_tolerance_s=1e-7):
    """Validate accepted, finite monotonic history and full/truncated duration.

    Rows are accepted-state recorder outputs, not attempted Newton iterations.
    No declaration of experimental material validation is made here.
    """
    if not rows:raise ValueError("No accepted response samples")
    end=float(record_end_s);requested=float(requested_end_s)
    if any(not math.isfinite(v) or v<=0 for v in (end,requested)):
        raise ValueError("Nonpositive/nonfinite record duration")
    times=[]
    expected_columns = set(rows[0])
    if "time_s" not in expected_columns or len(expected_columns) < 2:
        raise ValueError("Accepted history must have time_s and recorded response channels")
    for i,row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != expected_columns:
            raise ValueError(f"Accepted response channels missing or inconsistent at row {i}")
        try:
            t=float(row["time_s"])
        except (ValueError, TypeError, OverflowError) as exc:
            raise ValueError(f"Nonfinite/invalid history time {i}") from exc
        if not math.isfinite(t):
            raise ValueError(f"Nonfinite history time {i}")
        verify_numeric_accepted_row(row, row_index=i)
        times.append(t)
    if len(times)<2:raise ValueError("History lacks post-start accepted steps")
    if any(b<=a for a,b in zip(times,times[1:])):
        raise ValueError("Accepted history time must increase strictly")
    if abs(times[0])>time_tolerance_s:
        raise ValueError("Accepted state history does not start at time zero")
    if abs(times[-1]-requested)>time_tolerance_s:
        raise ValueError("Last accepted state does not reach the requested analysis duration")
    if requested>end+time_tolerance_s:
        raise ValueError("Requested duration exceeds the provided earthquake record")
    full=abs(times[-1]-end)<=time_tolerance_s
    return dict(
        status="FULL_DURATION_NUMERIC_SCREEN" if full else "TRUNCATED_DIAGNOSTIC",
        full_record_duration_s=end,requested_duration_s=requested,
        achieved_time_s=times[-1],accepted_states=len(times),
        first_time_s=times[0],min_accepted_step_s=min(b-a for a,b in zip(times,times[1:])),
        max_accepted_step_s=max(b-a for a,b in zip(times,times[1:])),
        time_monotonic=True,accepted_channels_finite=True,
        full_record_completed=full,experimental_materials_validated=False,
        device_qualification_verified=False,model_verification_complete=False)


def write_accepted_history_gate(output_dir,rows,record_end_s,requested_end_s):
    result=verify_accepted_history(rows,record_end_s,requested_end_s)
    out=Path(output_dir)/"Accepted_History_Completion_Gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result,indent=2,allow_nan=False),encoding="utf-8")
    return result


def compare_time_step_results(coarse,fine,*,max_relative_difference=None):
    """Compare same case IDs across two FULL records without declaring tolerance."""
    for r in (coarse,fine):
        if r.get("status")!="FULL_DURATION_NUMERIC_SCREEN":
            raise ValueError("Time-step comparison requires two full-duration screens")
        if r.get("model_sha256")!=coarse.get("model_sha256") or r.get("record_sha256")!=coarse.get("record_sha256"):
            raise ValueError("Time-step comparison model or motion inputs differ")
    # Missing source hashes used to compare equal (None == None); such
    # comparisons had no provenance and must not support timestep selection.
    for key in ("model_sha256", "record_sha256"):
        digest=coarse.get(key)
        if not isinstance(digest,str) or len(digest)!=64 or any(c not in "0123456789abcdefABCDEF" for c in digest):
            raise ValueError("Time-step comparison requires verified 64-digit " + key)
    if max_relative_difference is not None:
        try:
            tol=float(max_relative_difference)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("Invalid time-step comparison tolerance") from exc
        if not math.isfinite(tol) or tol < 0:
            raise ValueError("Time-step comparison tolerance must be finite and nonnegative")
        max_relative_difference=tol
    for name,report in (("coarse",coarse),("fine",fine)):
        for key in ("min_accepted_step_s","max_accepted_step_s"):
            try:
                value=float(report[key])
            except (KeyError,TypeError,ValueError,OverflowError) as exc:
                raise ValueError(f"{name} time-step evidence missing/invalid {key}") from exc
            if not math.isfinite(value) or value<=0:
                raise ValueError(f"{name} time-step evidence {key} must be finite and positive")
    if not fine["max_accepted_step_s"] < coarse["max_accepted_step_s"]:
        raise ValueError("Fine analysis must have a smaller maximum accepted step than coarse analysis")
    fields=("peak_roof_UX_m","peak_roof_UY_m","max_story_drift_X","max_story_drift_Y")
    values={}
    for key in fields:
        a,b=float(coarse[key]),float(fine[key])
        if not all(math.isfinite(x) for x in (a,b)):
            raise ValueError(f"Nonfinite time-step metric {key}")
        values[key]=dict(coarse=a,fine=b,relative_difference=abs(b-a)/max(abs(b),1e-12))
    passed=None if max_relative_difference is None else all(
        item["relative_difference"]<=max_relative_difference for item in values.values())
    return dict(status="COMPARISON_COMPLETE_NOT_PHYSICAL_VALIDATION",
                prescribed_tolerance=max_relative_difference,
                within_user_supplied_tolerance=passed,
                metrics=values)

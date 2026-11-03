"""Research NLTHA audit utilities; do not interpret exploratory output as design acceptance.

All helpers are pure/stdlib only, so they can be tested without native OpenSeesPy.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

SUPPORTED_UNITS = {"g", "m/s2"}


def audit_ground_motion_pair(records, source_paths):
    """Strict record preflight, without changing waveforms or their units."""
    if len(records) != 2 or len(source_paths) != 2:
        raise ValueError("NLTHA requires exactly two paired acceleration records")
    summary = []
    for axis, (record, path) in enumerate(zip(records, source_paths)):
        values, dt, units = record
        unit = str(units)
        if unit not in SUPPORTED_UNITS:
            raise ValueError(f"Record {axis+1}: unsupported source acceleration unit {unit!r}")
        dt = float(dt)
        if not math.isfinite(dt) or dt <= 0:
            raise ValueError(f"Record {axis+1}: time increment must be finite and > 0")
        samples = len(values)
        if samples < 2:
            raise ValueError(f"Record {axis+1}: fewer than two acceleration samples")
        maximum = 0.0
        for i, x in enumerate(values):
            try:
                value = float(x)
            except (ValueError, TypeError, OverflowError) as exc:
                raise ValueError(f"Record {axis+1} has invalid value at index {i}") from exc
            if not math.isfinite(value):
                raise ValueError(f"Record {axis+1} has non-finite value at index {i}")
            maximum = max(maximum, abs(value))
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"Record {axis+1} does not exist: {p}")
        summary.append({
            "axis": "XY"[axis], "path": str(p.resolve()),
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "samples": samples, "dt_s": dt,
            "duration_s": (samples-1)*dt, "source_units": unit,
            "pga_source_units": maximum,
        })
    if summary[0]["samples"] != summary[1]["samples"] or not math.isclose(
        summary[0]["dt_s"], summary[1]["dt_s"], rel_tol=0, abs_tol=1e-10
    ):
        raise ValueError("Paired records have different sample counts or time increments")
    return {"status": "PRECHECK_PASSED", "records": summary,
            "warning": "Source waveform validity, orientation, spectral matching and calibration remain separately unverified."}


def classify_case_result(result, *, tolerance_s=1e-6):
    """A duration gate: completing a short trial never means full-record validation."""
    status = str(result.get("status", ""))
    actual = result.get("physical_time_s")
    full = result.get("full_record_duration_s")
    try:
        actual, full = float(actual), float(full)
        valid = math.isfinite(actual) and math.isfinite(full) and full > 0
    except (ValueError, TypeError, OverflowError):
        valid = False
    full_completed = bool(valid and actual >= full-tolerance_s and actual <= full+tolerance_s)
    permitted = status == "COMPLETED_EXPLORATORY_RECORD" and full_completed
    return {
        "orientation": result.get("orientation"),
        "reported_status": status,
        "record_duration_s": full if valid else None,
        "analyzed_duration_s": actual if valid else None,
        "full_record_completed": full_completed,
        "eligible_for_further_engineering_review": permitted,
        "experimentally_validated": False,
        "validated_thesis_result": False,
        "reason": ("Full duration reported; requires independent convergence, numerical and experimental verification."
                   if permitted else "Not a complete successful exploratory full-record run; exclude from thesis ranking."),
    }


def write_quality_report(output_folder, summaries):
    folder = Path(output_folder)
    folder.mkdir(parents=True, exist_ok=True)
    audited = [classify_case_result(case) for case in summaries]
    report = {
        "status": "RESEARCH_EVIDENCE_ONLY",
        "cases": audited,
        "any_ineligible": any(not c["eligible_for_further_engineering_review"] for c in audited),
        "experimental_calibration_verified": False,
        "design_acceptance": False,
    }
    target = folder / "NLTHA_Quality_Gates.json"
    target.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    return report


def generate_isolation_configs(config, output_dir):
    """Prepare ZERO/X/Y/XY independent runs, never execute or change base config."""
    destination = Path(output_dir).resolve()
    base = dict(config)
    if not base.get("model_folder"):
        raise ValueError("model_folder missing from original nonlinear run config")
    source = Path(base["model_folder"]).resolve()
    if destination == source:
        raise ValueError("Diagnostic outputs must not overwrite the model source")
    if destination.is_relative_to(source) and destination.parent == source:
        # A subfolder is allowed, but never write into a source input file.
        pass
    destination.mkdir(parents=True, exist_ok=True)
    probes = []
    for label in ("ZERO", "X", "Y", "XY"):
        trial = dict(base)
        trial["diagnostic_excitation"] = label
        trial["limit_state"] = "ULS"
        trial["orientations"] = ["XY"]
        trial["duration_s"] = 0.005
        trial["diagnostic_zero_damping"] = True
        trial["diagnostic_mass_damping"] = False
        trial["output_dir"] = str(destination / label)
        name = destination / f"Probe_{label}.json"
        if name.exists():
            raise FileExistsError(f"Will not overwrite existing diagnostic input: {name}")
        probes.append((name, trial))
    for name, trial in probes:
        name.write_text(json.dumps(trial, indent=2), encoding="utf-8")
    return [str(name) for name, _ in probes]


def review_isolation_runs(folder):
    """Read saved evidence only. Missing output is UNKNOWN, not PASS."""
    root = Path(folder)
    rows = []
    for label in ("ZERO", "X", "Y", "XY"):
        directory = root / label
        failure = directory / "INCOMPLETE.json"
        orientation_failure = directory / "XY" / "FAILED.json"
        summary = directory / "XY" / "Case_Summary.json"
        if failure.exists() or orientation_failure.exists():
            p = orientation_failure if orientation_failure.exists() else failure
            data = json.loads(p.read_text(encoding="utf-8-sig"))
            rows.append({"probe": label, "status": "FAILED",
                         "stage": data.get("stage"), "error": data.get("error"),
                         "evidence": str(p)})
        elif summary.exists():
            data = json.loads(summary.read_text(encoding="utf-8-sig"))
            q = classify_case_result(data)
            # Short trials are successful probes when they reached their requested time.
            valid = data.get("status") in (
                "COMPLETED_TRUNCATED_TRIAL", "COMPLETED_EXPLORATORY_RECORD"
            )
            try:
                valid = valid and float(data["physical_time_s"]) >= 0.005-1e-8
            except (ValueError, TypeError, KeyError):
                valid = False
            rows.append({"probe": label, "status": "PROBE_PASSED" if valid else "INCOMPLETE",
                         "evidence": str(summary),
                         "full_record_completed": q["full_record_completed"]})
        else:
            rows.append({"probe": label, "status": "NOT_RUN", "evidence": None})
    states = {row["probe"]: row["status"] for row in rows}
    if states["ZERO"] == "FAILED":
        diagnosis = "ZERO fails: investigate effective tangent/mass/constraint initialization; do not tune damping."
    elif states["ZERO"] == "PROBE_PASSED" and states["X"] == "FAILED":
        diagnosis = "X-specific trigger: inspect AREA:354/482 wall constitutive response, mapping and local stiffness."
    elif states["ZERO"] == "PROBE_PASSED" and states["Y"] == "FAILED":
        diagnosis = "Y-specific trigger: inspect the Y-load path and nonlinear wall/connection response."
    elif all(x == "PROBE_PASSED" for x in states.values()):
        diagnosis = "Short probes pass. This is NOT full-record convergence or calibration."
    else:
        diagnosis = "Inconclusive probes: gather missing runs and compare identical solver/material settings."
    return {"probe_results": rows, "interpretation": diagnosis,
            "thesis_validation": "NOT_ESTABLISHED"}

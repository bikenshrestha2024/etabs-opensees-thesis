"""Experimental-vs-native material/component comparison without fake data.

Supports measured FVD, BRB, and 3D wall histories with time-aligned loading
protocol. No inferred experiment, approved material law, or default limits.
Python standard library only; output stays local.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

TYPES = {
    "FVD": ("time_s", "disp_m", "velocity_m_s", "force_kN"),
    "BRB": ("time_s", "disp_m", "force_kN"),
    "CORE_3D": ("time_s", "disp_x_m", "disp_y_m", "force_x_kN", "force_y_kN"),
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_history(path, required):
    with Path(path).open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or not set(required).issubset(reader.fieldnames):
            raise ValueError("Missing required experimental/simulation fields: " + ", ".join(required))
        rows = []
        for index, raw in enumerate(reader, 2):
            values = {}
            for key in required:
                try:
                    number = float(raw[key])
                except (ValueError, TypeError, OverflowError) as exc:
                    raise ValueError(f"Invalid {key} at row {index}") from exc
                if not math.isfinite(number):
                    raise ValueError(f"Nonfinite {key} at row {index}")
                values[key] = number
            rows.append(values)
    if len(rows) < 10:
        raise ValueError("Need at least 10 measured/simulated samples")
    if any(b["time_s"] <= a["time_s"] for a,b in zip(rows,rows[1:])):
        raise ValueError("Sample times must increase strictly")
    return rows


def signed_work(rows, displacement, force):
    return sum(.5*(a[force]+b[force])*(b[displacement]-a[displacement])
               for a,b in zip(rows, rows[1:]))


def compare(manifest):
    """Compare only when original measured and simulated time points coincide."""
    kind = manifest.get("component_type")
    if kind not in TYPES:
        raise ValueError("component_type must be FVD, BRB, or CORE_3D")
    if manifest.get("units") != "kN-m-s":
        raise ValueError("All histories must be in kN-m-s; convert units explicitly")
    for name in ("source_doi_or_primary_report", "specimen_id", "loading_protocol",
                 "experiment_csv", "simulation_csv", "model_command",
                 "parameter_card_sha256", "experiment_input_sha256"):
        if not isinstance(manifest.get(name), str) or not manifest[name].strip():
            raise ValueError("Missing explicit experiment provenance: " + name)
    if kind == "CORE_3D":
        for key in ("axial_load_kN", "core_geometry_source", "reinforcement_source"):
            if manifest.get(key) in (None, ""):
                raise ValueError("Missing wall specimen qualification: " + key)
    required = TYPES[kind]
    measured = Path(manifest["experiment_csv"]).resolve(strict=True)
    simulated = Path(manifest["simulation_csv"]).resolve(strict=True)
    if sha(measured).lower() != manifest["experiment_input_sha256"].lower():
        raise ValueError("Measured specimen CSV SHA256 differs from manifest")
    original = read_history(measured,required)
    model = read_history(simulated,required)
    if len(original) != len(model):
        raise ValueError("Measured and model histories differ in sample count; no implicit resampling")
    if any(not math.isclose(a["time_s"],b["time_s"],abs_tol=1e-9,rel_tol=0)
           for a,b in zip(original,model)):
        raise ValueError("Measured and simulated sample times differ; align protocol explicitly")
    axes = (("disp_m","force_kN","X"),) if kind != "CORE_3D" else (
        ("disp_x_m","force_x_kN","X"),("disp_y_m","force_y_kN","Y"))
    metrics = {}
    for disp,force,axis in axes:
        differences=[b[force]-a[force] for a,b in zip(original,model)]
        rmse=math.sqrt(sum(v*v for v in differences)/len(differences))
        peak=max(abs(row[force]) for row in original)
        if peak <= 0:
            raise ValueError("Zero measured peak force: normalization undefined")
        work_exp=signed_work(original,disp,force)
        work_sim=signed_work(model,disp,force)
        metrics[axis]=dict(
            measured_peak_abs_force_kN=peak,
            force_rmse_kN=rmse,
            normalized_force_rmse_percent=100*rmse/peak,
            measured_signed_work_kNm=work_exp,
            modeled_signed_work_kNm=work_sim,
            signed_work_difference_kNm=work_sim-work_exp,
        )
    return {
        "status":"COMPARISON_COMPUTED_NO_ACCEPTANCE_THRESHOLD",
        "component_type":kind,"specimen_id":manifest["specimen_id"],
        "sample_count":len(original),"model_command":manifest["model_command"],
        "source_doi_or_primary_report":manifest["source_doi_or_primary_report"],
        "loading_protocol":manifest["loading_protocol"],
        "measured_sha256":sha(measured),
        "simulated_sha256":sha(simulated),
        "metrics":metrics,
        "experimentally_validated":False,
        "project_transfer_approved":False,
        "missing_approval_evidence":[
            "A source-specific published or reviewer-defined acceptance protocol",
            "Independent geometry/reinforcement/material fidelity for the measured specimen",
            "Uncertainty and sensitivity across protocols, amplitudes, and cyclic reversals",
            "Actual building material/element transfer and native convergence evidence",
        ],
    }


def inspect_input(manifest):
    """Nonthrowing evidence-readiness result for incomplete project data."""
    required=("component_type","source_doi_or_primary_report","specimen_id",
              "loading_protocol","experiment_csv","simulation_csv",
              "model_command","parameter_card_sha256","experiment_input_sha256","units")
    missing=[key for key in required if not manifest.get(key)]
    for key in ("experiment_csv","simulation_csv"):
        value=manifest.get(key)
        if value and not Path(value).is_file():
            missing.append("missing file "+key)
    if missing:
        return {"status":"REQUIRES_PROJECT_EVIDENCE","missing":missing,
                "experimentally_validated":False}
    try:
        return compare(manifest)
    except (OSError, ValueError, KeyError) as exc:
        return {"status":"FAIL","reason":str(exc),"experimentally_validated":False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    manifest=json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    result=inspect_input(manifest)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():
        raise FileExistsError("Refusing to overwrite existing experimental evidence")
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False),encoding="utf-8")
    print(json.dumps(result,indent=2))
    return 0 if result["status"]=="COMPARISON_COMPUTED_NO_ACCEPTANCE_THRESHOLD" else 2


if __name__=="__main__":
    raise SystemExit(main())

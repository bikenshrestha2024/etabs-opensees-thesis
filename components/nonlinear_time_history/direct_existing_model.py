"""Directly execute the EXISTING ETABS-derived OpenSees nonlinear model.

Research baseline is paper-informed, NOT a licensed substitute for original
project reinforcement or a verified thesis nonlinear material calibration.
The actual native solver is imported only after source/motion preflight.
[REF docs/programs/38_DIRECT_EXISTING_MODEL_NLTHA.md]
"""
from __future__ import annotations
import argparse
import datetime
import json
import math
import sys
import traceback
from pathlib import Path
from components.nonlinear_time_history.source_model_handoff import (
    required_source_files, source_sha256, literature_section_inventory
)

def make_research_nltha_config(*, model_folder, x_path, y_path, output_dir,
                               event, variant_id, limit_state="ULS",
                               dt_s=0.005, trial_duration_s=0.0):
    """[REF docs/source/components/nonlinear_time_history/direct_existing_model.py.md]
    Prepare actual existing-source XY/YX NLTHA using PEER research material law.

    Never silently label transferred specimen cards as THESIS_NLTHA approval.
    All earthquake components act simultaneously, both orientations rebuilt.
    """
    if limit_state not in ("ULS","SLS"):
        raise ValueError("limit_state must be ULS or SLS")
    if isinstance(dt_s,bool) or not isinstance(dt_s,(int,float)) or not math.isfinite(dt_s) or dt_s<=0 or dt_s>0.01:
        raise ValueError("dt_s must be positive finite seconds <= 0.01; actual digitization may require less")
    if isinstance(trial_duration_s,bool) or not isinstance(trial_duration_s,(int,float)) or not math.isfinite(trial_duration_s) or trial_duration_s<0:
        raise ValueError("trial_duration_s must be finite and nonnegative")
    for label,value in (("event",event),("variant_id",variant_id)):
        if not isinstance(value,str) or not value.strip():
            raise ValueError(label+" must be a nonempty ID")
    return dict(
        model_folder=str(Path(model_folder).expanduser().resolve()),
        output_dir=str(Path(output_dir).expanduser().resolve()),
        x_path=str(Path(x_path).expanduser().resolve()),
        y_path=str(Path(y_path).expanduser().resolve()),
        earthquake_event=event.strip(),pair_id=event.strip(),
        variant_id=variant_id.strip(),limit_state=limit_state,
        analysis_intent="RESEARCH_DIAGNOSTIC",
        nonlinear_walls=True,
        material_basis="PEER_2015_12_SINGLE_SOURCE",
        steelmpf_transition="PEER_APPENDIX_EXACT",
        support_case="PHYSICAL_32",
        orientations=["XY","YX"],diagnostic_excitation="XY",
        diagnostic_zero_damping=False,diagnostic_mass_damping=False,
        source_records_already_scaled=True,scale=1.,
        soil_type="C",soil_c_primary_nltha=False,
        duration_s=float(trial_duration_s),
        dt_s=float(dt_s),max_subdivision_depth=5,
        research_basis_not_project_approval=True,
        material_parameter_status="PEER_SPECIMEN_TRANSFER_UNCALIBRATED",
    )


def preflight_existing_model(config):
    """[REF docs/source/components/nonlinear_time_history/direct_existing_model.py.md]
    Audit exact local model and motion bytes; do not create solver domain.

    Source files are sensitive and remain on the user's workstation; returned
    identity manifest belongs only in its selected local run output folder.
    """
    source=required_source_files(config["model_folder"])
    output=Path(config["output_dir"]).expanduser().resolve()
    if source==output or output==source.parent:
        raise ValueError("Output must be a distinct analysis folder, not source or its parent")
    if config.get("support_case")!="PHYSICAL_32":
        raise ValueError("Direct existing thesis model requires 32 real foundation supports")
    if config.get("analysis_intent")!="RESEARCH_DIAGNOSTIC":
        raise ValueError("Published PEER material transfer cannot be silently labeled calibrated THESIS_NLTHA")
    motions=[]
    for key in ("x_path","y_path"):
        path=Path(config[key]).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(str(path)+" — required real ground-motion component is unavailable")
        if path.stat().st_size<=0:
            raise ValueError("Empty recorded ground-motion component: "+str(path))
        motions.append(path)
    if motions[0]==motions[1] or source_sha256(motions[0])==source_sha256(motions[1]):
        raise ValueError("XY/YX requires distinct verified horizontal motion components")
    # A motion file's name alone is NOT authentication of record, unit,
    # SeismoMatch processing or original scale. The existing runner does its
    # complete parser and NBC provenance check before native solving.
    config_path=source/"OpenSees_Complete_Model_Config_V118.json"
    data_path=source/"OpenSees_Complete_Model_Data_V118.json"
    data=json.loads(data_path.read_text(encoding="utf-8-sig"))
    cfg=json.loads(config_path.read_text(encoding="utf-8-sig"))
    actual_sha=source_sha256(config_path)
    if data.get("config_sha256")!=actual_sha:
        raise ValueError("Model data/config SHA mismatch; refresh export rather than using stale section properties")
    original={str(key) for key in data.get("supports",{})}
    from components.model.support_case_contract import PROJECT_PRIMARY_32
    if not {str(tag) for tag in PROJECT_PRIMARY_32}.issubset(original):
        raise ValueError("Physical 32 foundation tags missing in chosen source export")
    report=json.loads((source/"OpenSees_Complete_Export_Report_V118.json").read_text(encoding="utf-8-sig"))
    if report.get("assembly_errors"):
        raise ValueError("Selected existing model export contains assembly_errors")
    schedule=literature_section_inventory(data,cfg)
    fingerprints={key:source_sha256(source/key)
                  for key in ("OpenSees_Complete_Model_Data_V118.json",
                              "OpenSees_Complete_Model_Config_V118.json",
                              "OpenSees_Element_Connectivity.json",
                              "OpenSees_Complete_Export_Report_V118.json")}
    return dict(
        status="LOCAL_SOURCE_CHECK_ONLY_NOT_SOLVER_RUN",
        checked_at=datetime.datetime.now().astimezone().isoformat(),
        model_files_sha256=fingerprints,
        motion_sha256_A=source_sha256(motions[0]),
        motion_sha256_B=source_sha256(motions[1]),
        actual_foundation_case="PHYSICAL_32",
        original_export_restrained_point_count=len(original),
        physical_support_count=32,
        wall_mesh_transfer_native_equivalence="NOT_VERIFIED",
        literature_section_inventory=schedule,
        applied_material_basis=config["material_basis"],
        calibration_status="RESEARCH_SPECIMEN_TRANSFER_NOT_APPROVED",
        nbc105_2025_code_acceptance="NOT_VERIFIED",
        input_motion_spectral_matching="NOT_VERIFIED_BY_THIS_PRECHECK",
        source_gravity_profile="AS_CONFIGURED_SEPARATE_FROM_FULL_1D_1L_COMPARISON",
    )



def verify_full_duration_pair_outputs(output_dir, config, cases):
    """Verify both saved XY/YX full histories against actual solver summaries.

    [REF NBC105-2025 §9.3.2–9.3.3; components/nonlinear_time_history/full_record_gate.py]
    This is a numerical completion / source-identity screen, NEVER a claim
    of code compliance, project reinforcement or component calibration.
    """
    import csv
    import re

    if (config.get("orientations") != ["XY", "YX"]
            or config.get("diagnostic_excitation") != "XY"):
        raise ValueError("A full XY/YX paired run requires bidirectional XY excitation")
    if config.get("duration_s") not in (None, 0, 0.0):
        raise ValueError("A truncated trial is not a full record")
    if not isinstance(cases, list) or len(cases) != 2:
        raise ValueError("Full NLTHA evidence requires two independent XY/YX cases")
    by_orientation = {c.get("orientation"): c for c in cases if isinstance(c, dict)}
    if len(by_orientation) != 2 or set(by_orientation) != {"XY", "YX"}:
        raise ValueError("Missing or duplicated XY/YX orientation summary")
    required_identity = (
        "model_sha256", "record_sha256", "pair_id", "variant_id",
        "limit_state", "diagnostic_excitation")
    for key in required_identity:
        values = [by_orientation[direction].get(key) for direction in ("XY", "YX")]
        if any(not isinstance(v, str) or not v.strip() for v in values):
            raise ValueError("Missing full-run case identity: " + key)
        if values[0] != values[1]:
            raise ValueError("XY/YX model/record case identity mismatch: " + key)
    for key in ("model_sha256", "record_sha256"):
        if not re.fullmatch(r"[0-9a-fA-F]{64}", by_orientation["XY"][key]):
            raise ValueError("Invalid SHA256 source identity: " + key)
    for key in ("pair_id", "variant_id", "limit_state"):
        if by_orientation["XY"][key] != config.get(key):
            raise ValueError("Requested model/record case identity mismatch: " + key)
    if by_orientation["XY"]["diagnostic_excitation"] != "XY":
        raise ValueError("Only simultaneous XY excitation qualifies as full record")
    results = {}
    for direction in ("XY", "YX"):
        saved = by_orientation[direction]
        gate = saved.get("completion_gate")
        if (saved.get("status") != "COMPLETED_EXPLORATORY_RECORD"
                or not isinstance(gate, dict)
                or gate.get("status") != "FULL_DURATION_NUMERIC_SCREEN"
                or gate.get("full_record_completed") is not True):
            raise ValueError(direction + " is not a full-duration completed numerical case")
        folder = Path(output_dir) / direction
        summary_path = folder / "Case_Summary.json"
        gate_path = folder / "Accepted_History_Completion_Gate.json"
        history_path = folder / "Building_Nonlinear_history.csv"
        for item in (summary_path, gate_path, history_path):
            if not item.is_file():
                raise FileNotFoundError(direction + " required full history evidence missing: " + str(item))
        try:
            on_disk = json.loads(summary_path.read_text(encoding="utf-8-sig"))
            disk_gate = json.loads(gate_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            raise ValueError(direction + " invalid saved case summary or completion gate") from exc
        for key in ("orientation", "status", *required_identity,
                    "physical_time_s", "full_record_duration_s"):
            if on_disk.get(key) != saved.get(key):
                raise ValueError(direction + " saved summary does not match solver case: " + key)
        if on_disk.get("completion_gate") != gate or disk_gate != gate:
            raise ValueError(direction + " saved completion gate differs from solver evidence")
        try:
            end = float(gate["full_record_duration_s"])
            last = float(gate["achieved_time_s"])
            physical_end = float(saved["physical_time_s"])
            count_expected = int(gate["accepted_states"])
        except (KeyError, ValueError, TypeError, OverflowError) as exc:
            raise ValueError(direction + " invalid full-duration gate numbers") from exc
        if (not all(math.isfinite(v) and v > 0 for v in (end, last, physical_end))
                or count_expected < 2
                or abs(last - end) > 1e-7
                or abs(physical_end - end) > 1e-7
                or abs(float(saved["full_record_duration_s"]) - end) > 1e-7):
            raise ValueError(direction + " full-duration end/achieved time mismatch")
        first = None
        previous = None
        count = 0
        with history_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or "time_s" not in reader.fieldnames or len(reader.fieldnames) < 2:
                raise ValueError(direction + " history has no numeric response channels")
            if len(set(reader.fieldnames)) != len(reader.fieldnames):
                raise ValueError(direction + " history contains duplicated channel headers")
            for row in reader:
                if set(row) != set(reader.fieldnames):
                    raise ValueError(direction + " history row has inconsistent channels")
                for key, raw in row.items():
                    try:
                        number = float(raw)
                    except (TypeError, ValueError, OverflowError) as exc:
                        raise ValueError(direction + " history contains invalid numeric response: " + key) from exc
                    if not math.isfinite(number):
                        raise ValueError(direction + " Nonfinite accepted history response: " + key)
                    if key == "time_s":
                        t = number
                if previous is not None and t <= previous:
                    raise ValueError(direction + " history must have strictly increasing accepted time")
                if first is None:
                    first = t
                previous = t
                count += 1
        if (first is None or abs(first) > 1e-7 or count != count_expected
                or previous is None or abs(previous - end) > 1e-7):
            raise ValueError(direction + " accepted states / recorded duration does not match completion gate")
        results[direction] = {
            "status": "FULL_DURATION_NUMERIC_SCREEN_NOT_DESIGN_APPROVAL",
            "accepted_states": count,
            "first_time_s": first, "last_time_s": previous,
            "source_model_sha256": saved["model_sha256"],
            "record_pair_sha256": saved["record_sha256"],
            "history_sha256": source_sha256(history_path),
            "completion_gate_sha256": source_sha256(gate_path),
            "case_summary_sha256": source_sha256(summary_path),
        }
    return results


def run_existing_model_nltha(config, *, check_only=False, executor=None):
    """[REF docs/source/components/nonlinear_time_history/direct_existing_model.py.md]
    Run both orientations immediately in native current interpreter.

    If OpenSees is missing the run is blocked with a saved error; never
    generate fake peak drifts, report completion, or push private model files.
    """
    preflight=preflight_existing_model(config)
    output=Path(config["output_dir"]).expanduser().resolve()
    # An existing case may contain a successful XY/YX run or first-failure
    # snapshots. Never mix a rerun into those immutable scientific records.
    if output.exists():
        if not output.is_dir():
            raise FileExistsError("NLTHA output path already exists as a file: "+str(output))
        if any(output.iterdir()):
            raise FileExistsError(
                "Refusing to overwrite existing NLTHA output evidence: "+str(output))
    output.mkdir(parents=True,exist_ok=True)
    target=output/"DIRECT_EXISTING_NLTHA_STATUS.json"
    plan=output/"DIRECT_EXISTING_NLTHA_SOURCE_AND_SECTION_BASIS.json"
    plan.write_text(json.dumps(preflight,indent=2,allow_nan=False),encoding="utf-8")
    def status(phase,**values):
        record=dict(status=phase,analysis_intent=config["analysis_intent"],
                    original_source_untouched=True,
                    recorded_at=datetime.datetime.now().astimezone().isoformat(),
                    model_sha256=preflight["model_files_sha256"]["OpenSees_Complete_Model_Data_V118.json"],
                    **values)
        target.write_text(json.dumps(record,indent=2,allow_nan=False),encoding="utf-8")
        return record
    if check_only:
        return status("PREFLIGHT_ONLY_NO_SOLVER_RUN",note="Run without --check-only to start OpenSees nonlinear transient")
    status("NATIVE_NLTHA_STARTED",note="Not evidence that analysis completed")
    try:
        if executor is None:
            try:
                import openseespy.opensees  # noqa: F401
            except (ImportError,OSError) as exc:
                raise RuntimeError(
                    "Native OpenSeesPy/XARA is not available in the selected Python interpreter; "
                    "install it in your thesis conda env and use that interpreter, "
                    "then rerun the same verified source/motions.") from exc
            from components.nonlinear_time_history.building_exploratory import run as executor
        result=executor(config)
        cases=result.get("cases") if isinstance(result,dict) else None
        if (not isinstance(cases,list) or len(cases)!=2
                or {c.get("orientation") for c in cases}!={"XY","YX"}
                or any(c.get("status") not in (
                    "COMPLETED_EXPLORATORY_RECORD","COMPLETED_TRUNCATED_TRIAL")
                    for c in cases)):
            raise RuntimeError(
                "Existing NLTHA engine returned no complete, independently identified XY/YX results")
        is_full=all(c["status"]=="COMPLETED_EXPLORATORY_RECORD" for c in cases)
        verified_pair = (verify_full_duration_pair_outputs(output, config, cases)
                         if is_full else {})
        if is_full and any(
                c["source_model_sha256"] != preflight["model_files_sha256"]["OpenSees_Complete_Model_Data_V118.json"]
                for c in verified_pair.values()):
            raise ValueError("Saved full-duration case model differs from preflight source SHA256")
        return status("EXPLORATORY_FULL_DURATION_NUMERICAL_SCREEN"
                      if is_full else "EXPLORATORY_TRUNCATED_TRIAL_ONLY",
                      case_ids=[c.get("orientation") for c in cases],
                      independently_checked_case_histories=verified_pair,
                      native_solver_executed=True,
                      thesis_materials_approved=False,
                      etabs_opensees_equivalence_verified=False,
                      full_thesis_nltha_accepted=False,
                      note="Solver numerical screen only; independent native model/material and code gates remain open")
    except BaseException as exc:
        status("NATIVE_NLTHA_INCOMPLETE",
               failed_reason=str(exc),error_type=type(exc).__name__,
               native_solver_passed=False,
               traceback=traceback.format_exc(limit=15))
        raise


def main(argv=None):
    """[REF docs/source/components/nonlinear_time_history/direct_existing_model.py.md] Execute the one-file local NLTHA CLI."""
    p=argparse.ArgumentParser(
        description="Run the already exported 3D OpenSees model with literature-baseline nonlinear RC walls and XY/YX motions; research-only until calibrated.")
    p.add_argument("--model-folder",required=True)
    p.add_argument("--x-path",required=True,help="Existing matched horizontal component A, NOT a fabricated motion")
    p.add_argument("--y-path",required=True,help="Existing matched horizontal component B")
    p.add_argument("--output-dir",required=True)
    p.add_argument("--event",required=True)
    p.add_argument("--variant-id",required=True,help="Original source model variant ID; use UNVERIFIED if not established")
    p.add_argument("--limit-state",choices=("ULS","SLS"),default="ULS")
    p.add_argument("--dt-s",type=float,default=0.005)
    p.add_argument("--trial-duration-s",type=float,default=0.,
                   help="0 means full record; >0 is an explicit diagnostic trial")
    p.add_argument("--check-only",action="store_true",
                   help="Write input/section preflight only; no OpenSees solver call")
    opts=p.parse_args(argv)
    config=make_research_nltha_config(
        model_folder=opts.model_folder,x_path=opts.x_path,
        y_path=opts.y_path,output_dir=opts.output_dir,
        event=opts.event,variant_id=opts.variant_id,
        limit_state=opts.limit_state,dt_s=opts.dt_s,
        trial_duration_s=opts.trial_duration_s)
    result=run_existing_model_nltha(config,check_only=opts.check_only)
    print(json.dumps(result,indent=2,allow_nan=False))
    return result


if __name__=="__main__":
    main()

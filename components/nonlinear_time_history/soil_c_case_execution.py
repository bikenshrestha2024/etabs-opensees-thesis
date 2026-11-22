"""Execute ONE pre-existing Soil C NLTHA config in an isolated native process.

This module orchestrates the existing building_exploratory solver. It never
creates a new structural model, relaxes project readiness gates, or declares
engineering acceptance. Literature/standard basis: docs/00_RESEARCH_REFERENCES.md
R01/R02/R10 and docs/00_NBC105_2025_NONLINEAR_RESEARCH_IMPLEMENTATION.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from components.nonlinear_time_history.soil_c_nltha_suite import verify_runner_pair
from components.nonlinear_time_history.soil_c_physics_preflight import (
    audit_soil_c_analysis_config,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_EXPORTS = (
    "OpenSees_Complete_Model_Data_V118.json",
    "OpenSees_Complete_Model_Config_V118.json",
    "OpenSees_Complete_Export_Report_V118.json",
    "OpenSees_Load_Conversion_Audit.json",
    "OpenSees_Source_Model_Metadata_V118.json",
)


def _file_sha256(path):
    """Byte identity of a source; not independent physical model validation."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _resolve(path, base):
    if not isinstance(path, str) or not path.strip():
        raise ValueError("Required source/output path must be a nonempty string")
    item = Path(path).expanduser()
    return (item if item.is_absolute() else base / item).resolve()


def preflight_case(config_file, *, allow_research_diagnostic=False):
    """Fail closed on mismatched sources, duplicate output or implicit approval.

    Config values are normalized to absolute local file paths for the child
    process. No source CSV/EDB/ground-motion data leaves this machine.
    """
    path = Path(config_file).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    config = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(config, dict):
        raise ValueError("NLTHA configuration must be a JSON object")
    intent = config.get("analysis_intent")
    if intent == "RESEARCH_DIAGNOSTIC" and not allow_research_diagnostic:
        raise ValueError(
            "The Stage 36 matrix is unqualified RESEARCH_DIAGNOSTIC. "
            "Pass --allow-research-diagnostic for an explicitly exploratory solve; "
            "it cannot be used as accepted thesis performance evidence.")
    audit_soil_c_analysis_config(config)
    if intent == "THESIS_NLTHA" and config.get("source_evidence_not_yet_complete") is not False:
        raise ValueError("THESIS_NLTHA source-evidence gate is not cleared")
    if config.get("variant_id") not in tuple("M"+str(n) for n in range(7)):
        raise ValueError("Select one actual M0–M6 variant; do not relabel a reused model")
    if config.get("pair_id") != config.get("earthquake_event"):
        raise ValueError("Pair identifier and registered earthquake_event disagree")
    model = _resolve(config.get("model_folder"), path.parent)
    output = _resolve(config.get("output_dir"), path.parent)
    x_path = _resolve(config.get("x_path"), path.parent)
    y_path = _resolve(config.get("y_path"), path.parent)
    if model == output or model in output.parents or output in model.parents:
        raise ValueError("Output must be separate from the source model directory")
    if output.exists():
        raise FileExistsError(
            "Refusing to overwrite or reuse existing NLTHA evidence folder: "+str(output))
    if not model.is_dir():
        raise NotADirectoryError(model)
    for name in REQUIRED_EXPORTS:
        if not (model / name).is_file():
            raise FileNotFoundError(model / name)
    pair = verify_runner_pair(
        x_path, y_path,
        registered_event=config["earthquake_event"],
        gorkha_processing_approved=config.get("gorkha_processing_reviewed") is True,
        reviewer=config.get("engineering_reviewer"),
        loma_end_policy=config.get("loma_end_policy", "reject"),
    )
    normalized = dict(config, model_folder=str(model), output_dir=str(output),
                      x_path=str(x_path), y_path=str(y_path))
    return {
        "status": "INPUT_PREFLIGHT_ONLY_NOT_EXECUTED",
        "config_path": str(path),
        "config_sha256": _file_sha256(path),
        "source_model_sha256": _file_sha256(model / REQUIRED_EXPORTS[0]),
        "variant_id": config["variant_id"],
        "pair_id": config["pair_id"],
        "limit_state": config["limit_state"],
        "analysis_intent": intent,
        "output_dir": str(output),
        "registered_pair": pair,
        "normalized_config": normalized,
        "engineering_accepted": False,
    }


def _launch(command, cwd, log_path):
    """Execute the EXISTING OpenSees model runner, never a shell command."""
    with Path(log_path).open("w", encoding="utf-8", errors="replace") as logfile:
        proc = subprocess.run(command, cwd=str(cwd), stdin=subprocess.DEVNULL,
                              stdout=logfile, stderr=subprocess.STDOUT,
                              check=False)
    return proc.returncode


def _orientation_screens(output):
    passed = []
    evidence = {}
    for name in ("XY", "YX"):
        summary = output / name / "Case_Summary.json"
        if not summary.is_file():
            evidence[name] = "MISSING_CASE_SUMMARY"
            continue
        try:
            data = json.loads(summary.read_text(encoding="utf-8-sig"))
            gate = data.get("completion_gate") or {}
            good = (data.get("orientation") == name
                    and data.get("status") == "COMPLETED_EXPLORATORY_RECORD"
                    and gate.get("status") == "FULL_DURATION_NUMERIC_SCREEN"
                    and gate.get("full_record_completed") is True)
        except (ValueError, TypeError, AttributeError):
            good = False
        evidence[name] = "FULL_DURATION_NUMERIC_SCREEN" if good else "NOT_FULL_OR_INVALID"
        if good:
            passed.append(name)
    return passed, evidence


def execute_case(config_file, *, allow_research_diagnostic=False, launcher=None):
    """Run one config (both XY/YX domains) and persist truthful local evidence.

    Exact solver input/state/calibration, wall failure, component tests and
    ETABS parity remain independent gates. A zero child exit code is not enough.
    """
    preflight = preflight_case(
        config_file, allow_research_diagnostic=allow_research_diagnostic)
    config = preflight.pop("normalized_config")
    output = Path(preflight["output_dir"])
    output.mkdir(parents=True, exist_ok=False)
    frozen = output / "Executed_RunConfig.json"
    frozen.write_text(json.dumps(config, indent=2, allow_nan=False),
                      encoding="utf-8")
    command = [sys.executable, "-m",
               "components.nonlinear_time_history.building_exploratory",
               "--config", str(frozen)]
    status_path = output / "Execution_Status.json"
    report = {**preflight, "status": "STARTED_NOT_VERIFIED",
              "runner_exit_code": None, "command": command,
              "orientations_verified": [], "engineering_accepted": False,
              "note": "Source/code/numerical/full-duration/calibration acceptance are separate."}
    status_path.write_text(json.dumps(report, indent=2, allow_nan=False),
                           encoding="utf-8")
    try:
        code = (launcher or _launch)(command, REPO_ROOT, output/"Native_NLTHA_Console.log")
        if isinstance(code, bool) or not isinstance(code, int):
            raise TypeError("Native runner exit code must be an integer")
        passed, evidence = _orientation_screens(output)
        report["runner_exit_code"] = code
        report["orientations_verified"] = passed
        report["orientation_screens"] = evidence
        if code != 0:
            report["status"] = "RUNNER_FAILED"
        elif set(passed) == {"XY", "YX"} and config.get("duration_s") in (None, 0):
            report["status"] = "FULL_DURATION_SOFTWARE_SCREEN_ONLY"
        else:
            report["status"] = "INCOMPLETE_OR_UNVERIFIED"
    except Exception as exc:
        report["status"] = "RUNNER_LAUNCH_ERROR"
        report["launch_error"] = repr(exc)
        status_path.write_text(json.dumps(report, indent=2, allow_nan=False),
                               encoding="utf-8")
        raise
    status_path.write_text(json.dumps(report, indent=2, allow_nan=False),
                           encoding="utf-8")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="Existing Stage 36 case JSON")
    parser.add_argument("--run", action="store_true",
                        help="Actually launch OpenSees in this Python environment")
    parser.add_argument("--allow-research-diagnostic", action="store_true",
                        help="Explicitly allow an uncalibrated exploratory case")
    args = parser.parse_args(argv)
    if args.run:
        result = execute_case(
            args.config, allow_research_diagnostic=args.allow_research_diagnostic)
    else:
        result = preflight_case(
            args.config, allow_research_diagnostic=args.allow_research_diagnostic)
        result.pop("normalized_config")
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result["status"] in (
        "INPUT_PREFLIGHT_ONLY_NOT_EXECUTED",
        "FULL_DURATION_SOFTWARE_SCREEN_ONLY") else 2


if __name__ == "__main__":
    raise SystemExit(main())

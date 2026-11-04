"""Prepare or execute isolated OpenSeesPy core-wall failure probes on Windows.

Default is preparation only. This is NOT a production thesis solver and
will not override the existing THESIS_NLTHA material qualification gate.
Runs each probe in a separate Python process and hence a fresh OpenSees
domain, not a reused potentially contaminated domain.

Source: components/nonlinear_time_history/thesis_quality.py.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from components.nonlinear_time_history.thesis_quality import (
    generate_isolation_configs, review_isolation_runs,
)

REPO = Path(__file__).resolve().parents[1]
PROBES = ("ZERO", "X", "Y", "XY")
SOURCE_FILES = (
    "OpenSees_Complete_Model_Data_V118.json",
    "OpenSees_Complete_Element_Map_V118.json",
    "OpenSees_Complete_Model_Config_V118.json",
)


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def prepare(config_path, output):
    """Create four read-only probe configs and an evidence provenance manifest."""
    config_path = Path(config_path).resolve(strict=True)
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError("Refusing to replace existing probe directory: " + str(output))
    source = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if source.get("analysis_intent") == "THESIS_NLTHA":
        raise ValueError("Only RESEARCH_DIAGNOSTIC mode may use zero-damping probes")
    if source.get("analysis_intent") not in (None, "RESEARCH_DIAGNOSTIC"):
        raise ValueError("Unknown diagnostic analysis intent")
    model = Path(source["model_folder"]).resolve(strict=True)
    if not model.is_dir():
        raise NotADirectoryError(str(model))
    if output == model or model in output.parents or output in model.parents:
        raise ValueError("Probes must be outside the original model/source directory")
    present = {
        name: {"path": str(model / name),
               "sha256": sha256(model / name) if (model / name).is_file() else None}
        for name in SOURCE_FILES
    }
    if present[SOURCE_FILES[0]]["sha256"] is None:
        raise FileNotFoundError("Missing project model export: " + SOURCE_FILES[0])
    generated = generate_isolation_configs(source, output)
    manifest = {
        "schema": "ISOLATED_3D_WALL_PROBES_V1",
        "research_only": True,
        "native_model_verified": False,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "source_config_sha256": sha256(config_path),
        "source_config_path": str(config_path),
        "model_folder": str(model),
        "source_files": present,
        "input_probes": generated,
        "cases": {key: {"status": "NOT_RUN"} for key in PROBES},
        "warnings": [
            "Diagnostic scripts turn damping off intentionally; they cannot establish approved production damping.",
            "The uncalibrated project wall/frame constitutive path is blocked for THESIS_NLTHA.",
            "Short ZERO/X/Y/XY probes cannot establish full nonlinear history or optimized outrigger elevation.",
            "Private source file contents and accelerograms must remain local.",
        ],
    }
    dest = output / "00_WALL_PROBE_EXECUTION_MANIFEST.json"
    dest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return dest


def execute(manifest_path, *, allow_native=False, timeout_s=None):
    """Run existing four probes in independent processes, preserving all errors."""
    if not allow_native:
        raise ValueError("Explicit --execute and --research-only acknowledgement required")
    manifest_path = Path(manifest_path).resolve(strict=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "ISOLATED_3D_WALL_PROBES_V1":
        raise ValueError("Unexpected probe manifest version")
    if any(value.get("status") != "NOT_RUN" for value in manifest["cases"].values()):
        raise ValueError("Probe has existing results; use a new directory to avoid overwrite")
    if sha256(manifest["source_config_path"]) != manifest["source_config_sha256"]:
        raise ValueError("Original configuration changed after probe preparation")
    for entry in manifest["source_files"].values():
        if entry["sha256"] and sha256(entry["path"]) != entry["sha256"]:
            raise ValueError("Model source file changed after probe preparation")
    root = manifest_path.parent
    for probe in PROBES:
        config = root / ("Probe_" + probe + ".json")
        if not config.is_file():
            raise FileNotFoundError(str(config))
        command = [sys.executable, "-m",
                   "components.nonlinear_time_history.building_exploratory",
                   "--config", str(config)]
        log_path = root / ("Probe_" + probe + "_native_console.log")
        case = manifest["cases"][probe]
        case.update(status="STARTED", command=command, log_path=str(log_path),
                    input_config_sha256=sha256(config),
                    started_utc=datetime.now(timezone.utc).isoformat())
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        with log_path.open("x", encoding="utf-8") as log:
            try:
                run = subprocess.run(command, cwd=REPO, stdout=log, stderr=subprocess.STDOUT,
                                     check=False, timeout=timeout_s)
                case.update(return_code=run.returncode,
                            status="PROCESS_EXIT_ZERO_UNREVIEWED" if run.returncode == 0
                            else "NATIVE_PROCESS_FAILED")
            except subprocess.TimeoutExpired:
                case.update(status="NATIVE_PROCESS_TIMEOUT", return_code=None)
        case["completed_utc"] = datetime.now(timezone.utc).isoformat()
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    summary = review_isolation_runs(root)
    summary["source_manifest"] = str(manifest_path)
    summary["native_full_record_completed"] = False
    summary["project_materials_validated"] = False
    output = root / "01_WALL_PROBE_REVIEW.json"
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="Existing research diagnostic configuration")
    parser.add_argument("--output", type=Path, help="New independent probe directory")
    parser.add_argument("--manifest", type=Path, help="Prepared manifest to execute")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--research-only", action="store_true")
    parser.add_argument("--timeout", type=int, default=None, help="Optional per-probe timeout seconds")
    args = parser.parse_args()
    if args.execute:
        if not args.manifest or not args.research_only:
            parser.error("Native execution requires --manifest --execute --research-only")
        result = execute(args.manifest, allow_native=True, timeout_s=args.timeout)
    else:
        if args.manifest or not args.config or not args.output:
            parser.error("Preparation requires --config and --output, without --manifest")
        result = {"manifest": str(prepare(args.config, args.output)),
                  "status": "PREPARED_ONLY_NO_NATIVE_ANALYSIS"}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

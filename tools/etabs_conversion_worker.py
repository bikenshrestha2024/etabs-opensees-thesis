"""Isolated ETABS-to-OpenSees source export worker.

Run from the main GUI in a fresh Python process. ETABS COM is created and used
only inside this process; do not invoke Tk operations from this worker.
Source EDB must not be edited by this diagnostic runner.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))



def _report_signature(path):
    """A complete report must be rewritten by THIS converter invocation."""
    path = Path(path)
    if not path.is_file():
        return None
    st = path.stat()
    return (st.st_mtime_ns, st.st_size)


def validate_converter_report(report_file, *, old_signature=None):
    """Fail closed on stale or numerically incomplete assembly reports.

    This is a worker completion contract, not an ETABS equivalence decision.
    """
    path = Path(report_file)
    signature = _report_signature(path)
    if signature is None or signature == old_signature:
        raise RuntimeError(
            "Conversion did not create a fresh OpenSees complete-export report. "
            "An old report must not be accepted as proof of this run."
        )
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(document, dict):
        raise ValueError("Complete-export report must be a JSON object")
    errors = document.get("assembly_errors")
    if not isinstance(errors, list):
        raise ValueError("Complete-export report lacks the assembly_errors list")
    if errors:
        raise RuntimeError(
            "OpenSees model assembly reported failures; not marking export "
            "successful. Inspect the private report for complete diagnostics. "
            f"Recorded assembly error count: {len(errors)}"
        )
    return document


def run(edb: Path, output: Path, include_live: bool, categorize: bool) -> dict:
    from components.inputs.project_output_layout import create_project_layout
    from components.inputs.lfs_workbook_recovery import audit_optional_gui_workbooks
    from components.ui.application import convert_model

    def log(line):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {line}", flush=True)

    output.mkdir(parents=True, exist_ok=True)
    stage_clock = time.perf_counter()
    log("[WORKER STAGE START] Source EDB digest and project layout")
    context = create_project_layout(str(edb), output)
    log(f"[WORKER STAGE OK] Source EDB digest and project layout: {time.perf_counter()-stage_clock:.2f}s")
    log("[PROJECT_SOURCE] EDB SHA256: " + context["source_edb_sha256"])
    log("[PROJECT_OUTPUT] Root: " + str(context["output_root"]))
    stage_clock = time.perf_counter()
    log("[WORKER STAGE START] Optional workbook verification")
    optional = audit_optional_gui_workbooks(
        REPO_ROOT, output, str(edb), log=log
    )
    log(f"[WORKER STAGE OK] Optional workbook verification: {time.perf_counter()-stage_clock:.2f}s")
    log("[SOURCE_GATE] Optional gravity workbook status: " +
        str(optional.get("evidence_status")))
    report_file = output / "OpenSees_Complete_Export_Report_V118.json"
    previous_signature = _report_signature(report_file)
    stage_clock = time.perf_counter()
    log("[WORKER STAGE START] ETABS import, source viewer export, model assembly")
    convert_model(str(edb), str(output), log, include_live)
    log(f"[WORKER STAGE OK] ETABS import and assembly: {time.perf_counter()-stage_clock:.2f}s")
    report = validate_converter_report(
        report_file, old_signature=previous_signature
    )
    mirror = {"status": "not_requested"}
    if categorize:
        log("[WORKER STAGE START] Optional SHA-verified categorized export mirror")
        mirror_clock=time.perf_counter()
        try:
            from components.inputs.export_mirror import export_mirror
            from components.inputs.output_layout import write_stage_index
            manifest = export_mirror(output, exclude_live_conversion_log=True)
            write_stage_index(output)
            mirror = {"status": "completed", "manifest": str(manifest)}
            log(f"[WORKER STAGE OK] Optional categorized mirror: {time.perf_counter()-mirror_clock:.2f}s")
            log("[EXPORT_ORGANIZED] Categorized mirror generated; legacy outputs retained")
        except Exception as exc:
            # Do not label a successfully completed export as failed for a mirror issue.
            mirror = {"status": "needs_review", "error": str(exc)}
            log("[EXPORT_ORGANIZATION_NEEDS_REVIEW] " + repr(exc))
    errors = report.get("assembly_errors") or []
    log("[WORKER COMPLETED] Assembly errors recorded: " + str(len(errors)))
    return {
        "status": "EXPORT_COMPLETED_REVIEW_REQUIRED",
        "report": str(report_file),
        "assembly_errors": errors[:25],
        "analysis_ready_reported": bool(report.get("analysis_ready", False)),
        "nonlinear_ready_reported": bool(report.get("nonlinear_ready", False)),
        "frame_segments": report.get("frame_segments"),
        "shell_mesh_cells": report.get("shell_mesh_cells"),
        "categorized_mirror": mirror,
        "model_equivalence": "NOT_VERIFIED"
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--edb", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--include-live", action="store_true")
    parser.add_argument("--categorize", action="store_true")
    args = parser.parse_args()
    try:
        if not args.edb.is_file():
            raise FileNotFoundError("ETABS EDB not found: " + str(args.edb))
        response = run(args.edb.resolve(), args.output.resolve(),
                       args.include_live, args.categorize)
        print("[WORKER_RESULT] " + json.dumps(response), flush=True)
        return 0
    except Exception:
        print("[WORKER_ERROR]\n" + traceback.format_exc(), flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

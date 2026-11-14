"""Unified, non-destructive run artifacts and display conventions.

[REF docs/source/components/inputs/output_contract.py.md]

This module creates *new* run directories only. It never relabels old results,
modifies an ETABS EDB/workbook, or interprets a successful solver log as physical
equivalence. Source units and result identity are caller-supplied and audited.
"""
from __future__ import annotations

import csv
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from components.inputs.output_layout import canonical_stage_folder, export_root_for

# Same layout for every newly adopted producing stage; existing consumers may
# continue reading their original paths until complete migration.
RUN_SUBFOLDERS = (
    "00_INPUT_SOURCE", "01_LOGS", "02_RESULTS", "03_EXCEL",
    "04_FIGURES", "05_COMPARISONS", "06_REVIEW", "07_EXPORT_ZIP",
)
SCHEMA = "ETABS_OPENSEES_OUTPUT_CASE_V1"
STATUSES = {
    "CREATED", "RUNNING", "COMPLETED_SOLVER_ONLY", "FAILED",
    "INTERRUPTED", "INCOMPLETE", "VERIFIED_ETABS_EQUIVALENCE",
}
CASE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


def safe_component(value):
    """[REF docs/source/components/inputs/output_contract.py.md]
    Validate one Windows-portable path segment; never clean away separators.
    """
    part = str(value).strip()
    if (not CASE_COMPONENT.fullmatch(part) or part.endswith((".", " "))
            or part.upper().split(".")[0] in {
                "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3",
                "LPT1", "LPT2", "LPT3"}):
        raise ValueError("Unsafe run/case identifier: " + repr(value))
    return part


def atomic_json(path, data):
    """[REF docs/source/components/inputs/output_contract.py.md]
    Stable two-space UTF-8 JSON, replacing only the specified derived output.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".writing_", suffix=".partial", dir=target.parent)
    tmp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False,
                      sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, target)
    finally:
        tmp.unlink(missing_ok=True)
    return target


def write_table(path, rows, *, columns):
    """[REF docs/source/components/inputs/output_contract.py.md]
    Use consistent CSV headers/order, finite values supplied by the caller.
    """
    columns = tuple(columns)
    if not columns or len(set(columns)) != len(columns):
        raise ValueError("Unique nonempty columns required")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".writing_", suffix=".partial", dir=target.parent)
    tmp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="raise",
                                    lineterminator="\n")
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, target)
    finally:
        tmp.unlink(missing_ok=True)
    return target


def create_case_run(export_dir, stage, case_id, *,
                    state="AS_CONFIGURED", model_sha256=None,
                    source_edb_sha256=None, units="kN-m-s"):
    """[REF docs/source/components/inputs/output_contract.py.md]
    Create an explicitly identified RUNS/<state>/<case>/<unique-id> directory.

    No source is touched and a fresh unique directory is used on every call.
    All scalar tags and sha digests are supplied, never guessed from filenames.
    """
    root = export_root_for(export_dir)
    if not root.is_dir():
        raise NotADirectoryError(str(root))
    stage_folder = canonical_stage_folder(stage)
    state, case_id = safe_component(state), safe_component(case_id)
    for digest in (model_sha256, source_edb_sha256):
        if digest is not None and not re.fullmatch("[a-fA-F0-9]{64}", digest):
            raise ValueError("Source/model SHA256 must contain exactly 64 hexadecimal characters")
    if not isinstance(units, str) or units != "kN-m-s":
        raise ValueError("Production run units must be the reviewed kN-m-s basis")
    parent = root / stage_folder / "RUNS" / state / case_id
    parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%S_%fZ") + "_" + uuid4().hex[:8]
    run = parent / run_id
    run.mkdir(exist_ok=False)
    for name in RUN_SUBFOLDERS:
        (run / name).mkdir()
    manifest = {
        "schema": SCHEMA, "stage": stage_folder, "state": state,
        "case_id": case_id, "run_id": run_id, "created_utc": now.isoformat(),
        "units": units, "source_edb_sha256": source_edb_sha256,
        "model_sha256": model_sha256, "solver_status": "CREATED",
        "structural_acceptance": "NOT_VERIFIED",
        "files": [],
        "subfolders": list(RUN_SUBFOLDERS),
    }
    atomic_json(run / "00_INPUT_SOURCE" / "CASE_MANIFEST.json", manifest)
    return run


def record_case_status(run_dir, status, *, message=None):
    """[REF docs/source/components/inputs/output_contract.py.md]
    Update the existing case manifest without inventing validation or load data.
    """
    status = str(status)
    if status not in STATUSES:
        raise ValueError("Unsupported solver status")
    file = Path(run_dir) / "00_INPUT_SOURCE" / "CASE_MANIFEST.json"
    data = json.loads(file.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise ValueError("Unknown case manifest schema")
    data["solver_status"] = status
    data["updated_utc"] = datetime.now(timezone.utc).isoformat()
    if message is not None:
        data["message"] = str(message)
    # Solver completion is explicitly not equivalence. This can only be
    # certified with externally reviewed source/physical comparison evidence.
    if status != "VERIFIED_ETABS_EQUIVALENCE":
        data["structural_acceptance"] = "NOT_VERIFIED"
    elif data.get("structural_acceptance") != "VERIFIED_BY_ENGINEERING_REVIEW":
        raise ValueError("A solver cannot self-certify ETABS equivalence")
    return atomic_json(file, data)

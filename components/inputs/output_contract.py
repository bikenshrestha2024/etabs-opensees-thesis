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



def style_workbook(workbook):
    """[REF docs/source/components/inputs/output_contract.py.md]
    Common, legible Excel style; metadata/content are never fabricated.

    Works on already constructed openpyxl workbooks. Does not save or alter
    any authoritative original source Excel calculation workbook.
    """
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    header = PatternFill("solid", fgColor="182941")
    alternate = PatternFill("solid", fgColor="F2F5F9")
    for sheet in workbook.worksheets:
        sheet.sheet_view.showGridLines = False
        sheet.freeze_panes = sheet.freeze_panes or "A2"
        if sheet.max_row < 1:
            continue
        for cell in sheet[1]:
            cell.fill = header
            cell.font = Font(name="Aptos", size=10, bold=True, color="FFFFFF")
            cell.alignment = Alignment(wrap_text=True, vertical="center")
        sheet.row_dimensions[1].height = 30
        for col in sheet.columns:
            cells = list(col)
            if not cells:
                continue
            width = max((len(str(c.value)) for c in cells[:300]
                         if c.value is not None), default=8)
            sheet.column_dimensions[get_column_letter(cells[0].column)].width = (
                min(58, max(12, width + 2))
            )
        for i in range(2, sheet.max_row + 1):
            if i % 2 == 0:
                for cell in sheet[i]:
                    cell.fill = alternate
            for cell in sheet[i]:
                cell.alignment = Alignment(vertical="top")
        if sheet.max_row > 1 and sheet.max_column > 1 and not sheet.auto_filter.ref:
            sheet.auto_filter.ref = sheet.dimensions
    return workbook


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
    if not isinstance(units, str) or units not in ("kN-m-s", "kN-mm-s"):
        raise ValueError("Declare explicitly reviewed source units: kN-m-s or kN-mm-s")
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



def prepare_history_run(model_script, stage, state, scope, *, model_length_unit):
    """[REF docs/source/components/inputs/output_contract.py.md]
    Create one immutable analysis-run directory, preserving source units.

    This does NOT certify source motions, model readiness or a full-duration
    transient. Users' explicit external output paths are handled by callers.
    """
    import hashlib
    model=Path(model_script).expanduser().resolve(strict=True)
    if not model.is_file() or model.suffix.casefold()!=".py":
        raise ValueError("A real OpenSees model-builder Python file is required")
    method=str(stage).strip().upper()
    if method not in ("LTHA","NLTHA"):
        raise ValueError("History run must be LTHA or NLTHA")
    if model_length_unit not in ("m","mm"):
        raise ValueError("Model length unit must be explicitly m or mm")
    state=safe_component(state)
    scope=safe_component(scope)
    # An explicit model file stem differentiates independent case scenarios;
    # original file SHA is separately recorded as an unaltered source digest.
    case_id=safe_component((method+"_"+scope+"_"+model.stem)[:120].rstrip("._"))
    export=export_root_for(model.parent)
    run=create_case_run(export,method,case_id,state=state,
                        units="kN-m-s" if model_length_unit=="m" else "kN-mm-s")
    atomic_json(run/"00_INPUT_SOURCE"/"HISTORY_INPUT_PROVENANCE.json",{
        "model_script":str(model),
        "model_script_sha256":hashlib.sha256(model.read_bytes()).hexdigest(),
        "assembled_model_sha256":None,
        "source_edb_sha256":None,
        "state":state,
        "method":method,
        "scope":scope,
        "model_length_unit":model_length_unit,
        "status":"SOURCE_SCRIPT_FINGERPRINT_ONLY_NOT_NATIVE_VERIFIED",
    })
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

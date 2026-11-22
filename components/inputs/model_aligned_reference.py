"""[REF docs/source/components/inputs/model_aligned_reference.py.md]
Opt-in 12m source-model-specific workbook provenance. Never infer equivalence
from workbook names, stale cached cell values, or matching base shear alone.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

MANIFEST="MODEL_ALIGNED_12M_WORKBOOK.json"


def _sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(1048576),b""):
            h.update(block)
    return h.hexdigest()


def verified_reference(export_dir, *, state=None):
    """[REF docs/source/components/inputs/model_aligned_reference.py.md]
    Revalidate exact local bytes, EDB identity and source shell verification.
    """
    from components.inputs.project_workbooks import _source_edb_path,_same_edb_file_content,_scaling_summary
    from openpyxl import load_workbook
    root=Path(export_dir).expanduser().resolve()
    manifest=root/"00_SOURCE_MANIFEST"/MANIFEST
    if not manifest.is_file():
        return None
    record=json.loads(manifest.read_text(encoding="utf-8-sig"))
    if record.get("status")!="CURRENT_12M_WORKBOOK_SOURCE_IDENTIFIED_NOT_CODE_ACCEPTED":
        raise ValueError("Unverified or obsolete current 12m workbook manifest")
    workbook=Path(record["workbook_path"]).expanduser().resolve()
    edb_name=_source_edb_path(root)
    if not edb_name or not Path(edb_name).is_file():
        raise ValueError("Current ETABS source EDB not present for reference identity")
    edb=Path(edb_name).resolve()
    if _sha(edb)!=record.get("source_edb_sha256"):
        raise ValueError("EDB changed since model-aligned workbook registration")
    if not workbook.is_file() or _sha(workbook)!=record.get("workbook_sha256"):
        raise ValueError("Model-aligned workbook bytes changed; re-register")
    if state is not None and str(state).upper()!=record.get("limit_state"):
        raise ValueError("Model-aligned workbook ULS/SLS state mismatch")
    wb=load_workbook(workbook,read_only=True,data_only=True)
    try:
        sheets=set(wb.sheetnames)
        if not ({"SCALING SUMMARY","NBC Calculator"} & sheets):
            raise ValueError("Selected workbook has no known NBC calculator or scaling sheet")
        if "SCALING SUMMARY" in sheets:
            source,_=_scaling_summary(wb["SCALING SUMMARY"])
            if not source or not _same_edb_file_content(edb,source):
                # Matching paths are also acceptable when the original EDB
                # is readable; content SHA is still the decisive identity.
                raise ValueError("SCALING SUMMARY B4 EDB is not byte-identical "
                                 "to the selected source model")
        if sorted(sheets)!=record.get("sheets"):
            raise ValueError("Workbook worksheet inventory changed since registration")
    finally:
        wb.close()
    from components.inputs.project_workbooks import import_project_inputs
    from components.inputs.grouped_wall_aw import verify_thesis_two_12m_wall_geometry
    from components.inputs.project_workbooks import source_limit_state
    measured_state,_=source_limit_state(root)
    if measured_state!=record["limit_state"]:
        raise ValueError("Native source state changed since workbook registration")
    # import_project_inputs calls source_workbooks; avoid circular registration
    # validation by separately checking saved geometry evidence in registration.
    geom=record.get("wall_geometry_verification") or {}
    if geom.get("classification")!="EXPORTED_GEOMETRY_VERIFIED_NOT_NATIVE_ETABS_CERTIFIED":
        raise ValueError("No source-verified 12m wall geometry in workbook manifest")
    return dict(record,workbook_path=str(workbook))


def register_reference(export_dir, workbook, *, limit_state):
    """[REF docs/source/components/inputs/model_aligned_reference.py.md]
    Save an exact read-only local workbook identity, never copy/modify XLSX.
    """
    from components.inputs.project_workbooks import (
        _source_edb_path,_same_edb_file_content,_scaling_summary,
        import_project_inputs,source_limit_state)
    from components.inputs.grouped_wall_aw import verify_thesis_two_12m_wall_geometry
    from components.inputs.output_contract import atomic_json
    from openpyxl import load_workbook
    root=Path(export_dir).expanduser().resolve()
    file=Path(workbook).expanduser().resolve()
    state=str(limit_state).strip().upper()
    if not file.is_file() or file.suffix.lower() not in (".xlsx",".xlsm"):
        raise FileNotFoundError("Select an existing current model-aligned XLSX/XLSM")
    actual,_=source_limit_state(root)
    if actual!=state:
        raise ValueError("Selected workbook limit state must match source EDB")
    source=_source_edb_path(root)
    if not source or not Path(source).is_file():
        raise FileNotFoundError("Original source EDB is required before registering any Excel")
    edb=Path(source).resolve()
    imported=import_project_inputs(Path(__file__).resolve().parents[2],root,state)
    v=imported.get("values") or {}
    if not v.get("wall_aw_profile") or v.get("wall_aw_height_m") is None:
        raise ValueError("Source exported wall shell/node geometry is not available")
    verified=verify_thesis_two_12m_wall_geometry(
        v["wall_aw_profile"],v["wall_aw_height_m"])
    wb=load_workbook(file,read_only=True,data_only=True)
    try:
        sheets=set(wb.sheetnames)
        if not ({"SCALING SUMMARY","NBC Calculator"} & sheets):
            raise ValueError("Workbook must contain NBC Calculator or SCALING SUMMARY")
        workbook_source=None
        if "SCALING SUMMARY" in sheets:
            workbook_source,_=_scaling_summary(wb["SCALING SUMMARY"])
            if not workbook_source or not _same_edb_file_content(edb,workbook_source):
                raise ValueError("Workbook SCALING SUMMARY B4 source EDB not verified "
                                 "as byte-identical to current ETABS EDB")
    finally:
        wb.close()
    record={
        "status":"CURRENT_12M_WORKBOOK_SOURCE_IDENTIFIED_NOT_CODE_ACCEPTED",
        "workbook_path":str(file),"workbook_sha256":_sha(file),
        "source_edb":str(edb),"source_edb_sha256":_sha(edb),
        "limit_state":state,"sheets":sorted(sheets),
        "scaling_summary_b4_edb":workbook_source,
        "wall_geometry_verification":verified["wall_geometry_verification"],
        "scope":"FILE_IDENTITY_AND_EXPORTED_WALL_GEOMETRY_NOT_ETABS_EQUIVALENCE",
    }
    dest=root/"00_SOURCE_MANIFEST"/MANIFEST
    atomic_json(dest,record)
    return record

"""Source-backed NLTHA input values for an UNAPPROVED thesis review draft.

No solver, ETABS API, network, automatic review flags or source-model edits.
A sourced value is a candidate input, not an engineering acceptance decision.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from uuid import uuid4

from components.model.readiness import READINESS_CHECK_KEYS


def _sha256(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024),b""):
            digest.update(block)
    return digest.hexdigest()


def _local_source(root: Path, path: Path) -> bool:
    """Accept only real files inside the selected export, never linked paths."""
    try:
        root=root.resolve()
        path=Path(path)
        relative=path.relative_to(root)
        if '..' in relative.parts or not relative.parts:
            return False
        if any((root / Path(*relative.parts[:i])).is_symlink()
               for i in range(1,len(relative.parts)+1)):
            return False
        return path.is_file() and path.resolve().is_relative_to(root)
    except (OSError, ValueError):
        return False


def _source_record(path: Path) -> dict:
    return dict(path=str(path),sha256=_sha256(path),bytes=path.stat().st_size)


def _read_obj(path: Path) -> dict:
    result=json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(result,dict):
        raise ValueError("Expected object in selected project input: "+str(path))
    return result


def _finite_number(value):
    try:
        if isinstance(value,bool):
            return None
        v=float(value)
    except (TypeError,ValueError,OverflowError):
        return None
    return v if math.isfinite(v) else None


def _summarize_geometry(data):
    nodes=data.get("nodes",{})
    shells=data.get("shells",[])
    diaphragms=data.get("diaphragms",[])
    walls={}
    if isinstance(shells,list):
        for shell in shells:
            if not isinstance(shell,dict) or str(shell.get("category","")).upper()!="SHEAR WALL":
                continue
            properties=shell.get("properties") or {}
            name=properties.get("property")
            thick=_finite_number(properties.get("thickness"))
            if isinstance(name,str) and thick is not None and thick>0:
                if name in walls and walls[name]!=thick:
                    raise ValueError("Conflicting source wall thickness for "+name)
                walls[name]=thick
    return dict(node_count=len(nodes) if isinstance(nodes,(list,dict)) else None,
                shell_count=len(shells) if isinstance(shells,list) else None,
                diaphragm_count=len(diaphragms) if isinstance(diaphragms,(list,dict)) else None,
                wall_properties_m=dict(sorted(walls.items())),
                geometry_status="EXPORTED_TOPOLOGY_NOT_INDEPENDENTLY_CHECKED")


def _modal_candidate(root, data_sha):
    stage=root/"04_MODAL"/"RUNS"
    if not stage.is_dir():
        return {"status":"NO_MATCHING_SAVED_MODAL","candidates":[]},{}
    valid_by_state={}
    source_by_state={}
    ambiguous=[]
    seen=0
    for state in ("ULS","SLS"):
        scanned=[]
        # Avoid selecting only one arbitrary run if the folder holds multiple
        # sources with identical model hash/state; force explicit reconciliation.
        for path in sorted(stage.glob(state+"/*/*/02_RESULTS/NBC105_Modal_V111.json"))[:40]:
            if not _local_source(root,path):
                continue
            try:
                value=_read_obj(path)
                scanned.append((path,value))
            except (OSError,ValueError,UnicodeError):
                continue
        seen+=len(scanned)
        matching=[(p,v) for p,v in scanned if (data_sha is not None
                  and v.get("model_sha256")==data_sha
                  and str(v.get("limit_state",state)).upper()==state)]
        if len(matching)>1:
            ambiguous.append(state)
            continue
        if len(matching)!=1:
            continue
        path,result=matching[0]
        rows=result.get("rows",[])
        if not isinstance(rows,list):
            rows=[]
        clean=[]
        for item in rows:
            if isinstance(item,dict):
                clean.append({key:item.get(key) for key in
                    ("mode","period_s","UX_cumulative_percent","UY_cumulative_percent")})
        valid_by_state[state]={
            "source":str(path),"limit_state":state,"mode_count":len(clean),
            "cumulative_UX_percent":next((r["UX_cumulative_percent"] for r in reversed(clean)
                if _finite_number(r["UX_cumulative_percent"]) is not None),None),
            "cumulative_UY_percent":next((r["UY_cumulative_percent"] for r in reversed(clean)
                if _finite_number(r["UY_cumulative_percent"]) is not None),None),
            "periods_first_three_s":[r["period_s"] for r in clean[:3]],
            "meaning":"ELASTIC_MODAL_SOURCE_MATCH_ONLY_NOT_NONLINEAR_INITIAL_STIFFNESS",
        }
        source_by_state[state]=_source_record(path)
    if ambiguous and not valid_by_state:
        status="AMBIGUOUS_MATCHED_MODAL_SOURCES_NOT_REUSED"
    elif valid_by_state:
        status=("PARTIAL_MODAL_MATCH_OTHER_STATE_AMBIGUOUS_REVIEW_REQUIRED" if ambiguous
                else "MATCHED_SERIALIZED_MODEL_REVIEW_REQUIRED")
    else:
        status="MODEL_SHA_MISMATCH_NOT_REUSED" if seen else "NO_MATCHING_SAVED_MODAL"
    return {
        "status":status,
        "source_by_state":source_by_state,
        "ambiguous_states":ambiguous,
        "candidate_count":seen,
        "matched_state_count":len(valid_by_state),
    },valid_by_state


def collect_available_project_values(model_script) -> dict:
    """[REF docs/source/components/model/readiness_available_values.py.md]

    Reuse only available *actual selected export* facts and the installed
    cited PEER research baseline; never turn a candidate into an approval.
    """
    model=Path(model_script).expanduser().resolve()
    if not model.is_file() or model.is_symlink():
        raise FileNotFoundError("Select an existing non-linked nonlinear builder")
    root=model.parent
    sources={}
    def load(name):
        path=root/name
        if not _local_source(root,path):
            return {}
        sources[name]=_source_record(path)
        return _read_obj(path)
    cfg=load("OpenSees_Complete_Model_Config_V118.json")
    data=load("OpenSees_Complete_Model_Data_V118.json")
    gravity=load("OpenSees_Complete_Gravity_Check_V118.json")
    load_audit=load("OpenSees_Load_Conversion_Audit.json")
    metadata=load("OpenSees_Source_Model_Metadata_V118.json")
    if not cfg:
        cfg={}
    project_config={}
    for key in ("gravity_factors","mass_factors","slab_bending_factor",
                "slab_bending_factor_sls","slab_stiffness_source",
                "frame_section_mapping","floor_subdivisions"):
        if key in cfg:
            project_config[key]=cfg[key]
    values={"source_config":project_config}
    if data:
        values["geometry"]=_summarize_geometry(data)
        for key in ("gravity_by_pattern_kN","total_downward_load_kN"):
            if key in data:
                values[key]=data[key]
    if gravity:
        values["saved_gravity_result"]={
            key:gravity[key] for key in (
                "status","case_id","gravity_factors","applied_gravity_kN",
                "support_reactions_kN","max_vertical_displacement_m",
                "equilibrium_error_percent","model_sha256")
            if key in gravity}
        values["saved_gravity_result"]["meaning"]="SAVED_RESULT_REVIEW_REQUIRED_NOT_NLTHA_PDELTA_APPROVAL"
    if load_audit:
        values["load_inventory"]={key:load_audit[key] for key in (
            "status","total_downward_load_kN","gravity_by_pattern_kN",
            "source_model_sha256") if key in load_audit}
    if metadata:
        values["source_support_metadata"]={key:metadata[key] for key in (
            "support_count","source_support_count","physical_support_count",
            "source_edb_sha256","source_edb_path") if key in metadata}
    serialized= root/"OpenSees_Complete_Model_Data_V118.json"
    sha=sources.get(serialized.name,{}).get("sha256")
    modal_ref,modal_by_state=_modal_candidate(root,sha)
    if modal_by_state:
        values["modal_mass_screen_by_state"]=modal_by_state
        # Preserve the single-state convenience field for earlier consumers.
        if len(modal_by_state)==1:
            values["modal_mass_screen"]=next(iter(modal_by_state.values()))
        for state,record in modal_ref["source_by_state"].items():
            sources["MATCHED_MODAL_"+state]=record
    from components.nonlinear_time_history.material_source_sets import peer_single_source, peer_fsam_panel_values
    peer=peer_single_source()
    fsam=peer_fsam_panel_values()
    values["literature_research_only"]={
        "basis":"PEER_2015_12_SINGLE_SOURCE",
        "source_scope":"SPECIMEN_ONLY_NOT_PROJECT_VERIFIED",
        "specimen":peer.get("specimen"),
        "citation":fsam["citation"],
        "source_url":fsam["source"],
        "concrete_cm":peer["wall_concrete"],
        "steel_mpf":peer["wall_steel"],
        "frame_section_research_assumptions":peer["frame_section"],
        "web_fsam":fsam["web"],
        "boundary_fsam":fsam["boundary"],
        "boundary_mapping":"NOT_AVAILABLE_FROM_CURRENT_MODEL_AND_NOT_ASSIGNED",
    }
    missing=[]
    if not cfg.get("nonlinear_materials_file"):
        missing.append("nonlinear_materials_file")
    if not cfg.get("nonlinear_wall_fsam_tags"):
        missing.append("nonlinear_wall_fsam_tags")
    if cfg.get("nonlinear_parameters_reviewed") is not True:
        missing.append("nonlinear_parameters_reviewed")
    if cfg.get("nonlinear_materials_file"):
        raw=Path(cfg["nonlinear_materials_file"]).expanduser()
        mat=raw if raw.is_absolute() else root/raw
        if _local_source(root,mat):
            sources["PROJECT_NONLINEAR_MATERIAL_FILE"]=_source_record(mat)
            values["selected_material_file"]={
                "path":str(mat),"source_sha256":_sha256(mat),
                "meaning":"CONFIGURED_NOT_CALIBRATION_APPROVED"}
        else:
            missing.append("nonlinear_materials_file_not_verified_locally")
    if cfg.get("nonlinear_wall_fsam_tags"):
        values["configured_fsam_mapping"]={
            "tags":cfg["nonlinear_wall_fsam_tags"],
            "meaning":"CONFIGURED_MAPPING_NOT_GEOMETRY_OR_CYCLICALLY_VALIDATED"}
    from components.model.readiness_gui import available_evidence
    _hints,discovered=available_evidence(model,with_metadata=True)
    checks={}
    for key in READINESS_CHECK_KEYS:
        paths=[p for p in discovered.get(key,()) if _local_source(root,Path(p))]
        checks[key]={
            "status":"SOURCE_FOUND_REVIEW_REQUIRED" if paths else "NO_VERIFIED_SOURCE_AVAILABLE",
            "evidence_files":paths,
            "approved":False,
            "required_action":"Source/model-specific numerical review and human decision",
        }
    return {
        "schema":"NLTHA_DIRECT_AVAILABLE_VALUES_V1",
        "model":{"path":str(model),"sha256":_sha256(model)},
        "model_data_sha256":sha,
        "source_files":sources,
        "available_values":values,
        "modal_reference":modal_ref,
        "checklist_candidates":checks,
        "missing_production_inputs":missing,
        "approval_status":"UNAPPROVED",
        "approved_for_nltha":False,
        "physical_equivalence":"NOT_VERIFIED",
        "research_transfer":"DIRECT_LITERATURE_RESEARCH_ONLY",
        "purpose":"POPULATE_EXISTING_FACTS_NOT_ENGINEERING_SIGNOFF",
    }


def attach_available_values_to_draft(model_script, draft_path):
    """[REF docs/source/components/model/readiness_available_values.py.md]
    Store source-backed values in a current UNAPPROVED draft; preserve review.
    """
    model=Path(model_script).expanduser().resolve()
    draft=Path(draft_path).expanduser()
    if draft.is_symlink() or not draft.is_file():
        raise FileNotFoundError("Select a real unlinked model-bound V134 readiness draft")
    draft=draft.resolve()
    if draft.parent!=model.parent:
        raise ValueError("Readiness draft must belong to selected model folder")
    data=_read_obj(draft)
    if data.get("approved_for_nltha") is True:
        raise ValueError("Cannot change an approved human readiness manifest")
    if (str(Path(str(data.get("model_script",""))).expanduser().resolve())!=str(model)
            or data.get("model_script_sha256")!=_sha256(model)):
        raise ValueError("Readiness model binding mismatch; rebind the UNAPPROVED draft first")
    snapshot=collect_available_project_values(model)
    # Re-read before the atomic write so a concurrently edited review is never overwritten.
    before=_sha256(draft)
    data["available_project_values"]=snapshot
    if _sha256(draft)!=before:
        raise RuntimeError("Readiness draft changed during value collection; refused overwrite")
    temporary=draft.with_name(draft.name+".value-snapshot-"+uuid4().hex+".tmp")
    try:
        with temporary.open("x",encoding="utf-8") as stream:
            json.dump(data,stream,indent=2)
        if _sha256(draft)!=before:
            raise RuntimeError("Draft changed during serialization; refused overwrite")
        temporary.replace(draft)
    finally:
        temporary.unlink(missing_ok=True)
    return draft

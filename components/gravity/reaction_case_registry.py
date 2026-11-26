"""Case-specific *solved* support-reaction display, never an applied-load override.

[REF docs/source/components/gravity/reaction_case_registry.py.md]
No ETABS API, OpenSees call or model edits. Rejects stale/foreign results.
"""
from __future__ import annotations
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from components.inputs.output_layout import export_root_for

SCENARIO_SUPPORTS = {
    "ETABS_NONZERO_REACTION_DIAGNOSTIC": 32,
    "ETABS_SOURCE_SUPPORTS": 76,
    "CONTINUOUS_WALL_BASE_FIXED": 97,
}
INDEX_NAME = "Gravity_Case_Reaction_Index.json"
MODEL_INPUT_FILENAMES = ("OpenSees_Complete_Model_Data_V118.json",
                         "OpenSees_Complete_Model_Config_V118.json",
                         "OpenSees_Source_Model_Metadata_V118.json",
                         "OpenSees_Element_Connectivity.json")


def _sha256(path):
    """Hash exact selected model code for result provenance.

    [REF docs/source/components/gravity/reaction_case_registry.py.md]
    """
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def _model_input_fingerprints(model_path):
    """Fingerprint model code and its exported load/config metadata.

    [REF docs/source/components/gravity/reaction_case_registry.py.md]
    """
    model=Path(model_path).resolve()
    names=(model.name,*MODEL_INPUT_FILENAMES)
    return {name:(_sha256(model.parent/name) if (model.parent/name).is_file() else None)
            for name in names}


def checked_reaction_result(payload, model_path, *, scenario, profile,
                            expected_support_tags=None):
    """Verify solver result and 32/76/97 node FZ sum before showing it.

    [REF docs/source/components/gravity/reaction_case_registry.py.md]
    """
    if scenario not in SCENARIO_SUPPORTS:
        raise ValueError("Unknown support case: "+str(scenario))
    if not isinstance(payload,dict) or payload.get("ok") is not True:
        raise ValueError("Only successful completed gravity runs may be displayed")
    if payload.get("wall_support_strategy") != scenario:
        raise ValueError("Result belongs to another support case")
    if payload.get("gravity_profile") != profile:
        raise ValueError("Result belongs to another gravity load profile")
    reported_model = Path(payload.get("model_script","")).resolve()
    current_model = Path(model_path).resolve()
    if reported_model != current_model:
        raise ValueError("Result belongs to a different model path")
    fingerprints=_model_input_fingerprints(current_model)
    script_sha=fingerprints[current_model.name]
    if not script_sha:
        raise ValueError("Current model script is missing")
    if "model_sha256" in payload and payload["model_sha256"]!=script_sha:
        raise ValueError("Solver-recorded model SHA256 differs from current model")
    if "model_input_sha256" in payload:
        if payload["model_input_sha256"]!=fingerprints:
            raise ValueError("Solver-recorded model input SHA256 differs from current model inputs")
        provenance="SOLVER_INPUT_BYTES_MATCH"
    elif "model_sha256" in payload:
        provenance="LEGACY_SOLVER_SCRIPT_SHA_MATCH_ONLY"
    else:
        provenance="LEGACY_NO_SOLVER_INPUT_SHA"
    tags = [int(t) for t in payload.get("support_node_tags",[])]
    if len(tags) != SCENARIO_SUPPORTS[scenario] or len(set(tags)) != len(tags):
        raise ValueError("Result does not contain the required unique support tags")
    if expected_support_tags is not None and set(tags) != set(map(int,expected_support_tags)):
        raise ValueError("Result support tags differ from the current scenario")
    reactions=payload.get("reactions")
    if not isinstance(reactions,list) or len(reactions) != len(tags):
        raise ValueError("Missing or incomplete per-node support reactions")
    observed=set()
    sum_vertical=0.0
    for row in reactions:
        tag=int(row["node_tag"])
        if tag in observed or tag not in tags:
            raise ValueError("Duplicate or unexpected solver reaction node")
        observed.add(tag)
        val=float(row["rz_kN"])
        if not math.isfinite(val):
            raise ValueError("Nonfinite vertical support reaction")
        sum_vertical+=val
    if observed!=set(tags):
        raise ValueError("Missing support reactions")
    rep=payload.get("report")
    if not isinstance(rep,dict):
        raise ValueError("Gravity equilibrium report missing")
    solver_reaction=float(rep["support_vertical_reaction_kN"])
    applied=float(rep["applied_vertical_load_kN"])
    if not all(math.isfinite(v) for v in (solver_reaction,applied)) or applied<=0:
        raise ValueError("Invalid applied load or reaction in equilibrium report")
    tol=max(0.01,abs(solver_reaction)*1e-7)
    if abs(sum_vertical-solver_reaction)>tol:
        raise ValueError("Nodal vertical reactions do not agree with gravity report")
    equilibrium=100*abs(sum_vertical-applied)/applied
    return dict(
        scenario=scenario,profile=profile,model_path=str(current_model),
        model_sha256=script_sha,
        input_sha256=fingerprints,
        solver_input_provenance=provenance,
        support_count=len(tags),
        support_tags=sorted(tags),applied_load_kN=applied,
        summed_reaction_kN=sum_vertical,equilibrium_error_percent=equilibrium,
        balance_pass=equilibrium<=0.5, # Numerical screening, not code acceptance
        status="SOLVED_REACTIONS_NOT_ETABS_VALIDATED")


def publish_gravity_case_index(output_root, record):
    """[REF docs/source/components/gravity/reaction_case_registry.py.md]
    Publish ONE metadata pointer, never duplicate physical solver plots or files.

    Historical 02_GRAVITY/<scenario>/<run> previews remain readable. New
    cases create just 00_INDEXES/CASES/<scenario>/<case-hash>.json.
    """
    from components.gravity.output_ownership import section
    root = Path(output_root).resolve()
    stage = export_root_for(root) / "02_GRAVITY"
    scenario=record["scenario"]
    if scenario not in SCENARIO_SUPPORTS:
        raise ValueError("Unrecognized gravity case identity")
    result_path=Path(record["result_path"]).resolve()
    digest=hashlib.sha256(str(result_path).encode("utf-8")).hexdigest()[:16]
    case_dir=stage/"00_INDEXES"/"CASES"/scenario
    if any(p.is_symlink() for p in (case_dir,*case_dir.parents)):
        raise ValueError("Refusing linked gravity case index directory")
    case_dir.mkdir(parents=True,exist_ok=True)
    summary={
        "status":"INDEX_POINTER_ONLY_NOT_ETABS_VALIDATED",
        "support_strategy":scenario,
        "support_count":record["support_count"],
        "gravity_profile":record["profile"],
        "model_sha256":record["model_sha256"],
        "result_path":str(result_path),
        "original_full_run_folder":str(result_path.parent),
        "applied_load_kN":record["applied_load_kN"],
        "summed_reaction_kN":record["summed_reaction_kN"],
        "equilibrium_error_percent":record["equilibrium_error_percent"],
        "case_result_sha256":record.get("result_sha256"),
        "solver_input_provenance":record.get("solver_input_provenance","LEGACY_UNSPECIFIED"),
    }
    from components.inputs.output_contract import atomic_json
    pointer=case_dir/(digest+".json")
    atomic_json(pointer,summary)
    atomic_json(stage/"00_INDEXES"/"LATEST_GRAVITY_CASES.json",{
        "status":"INDEX_POINTER_ONLY_NOT_ETABS_VALIDATED",
        "last_case":str(pointer),
        "case_index":str(record.get('registry_path') or Path(output_root).resolve()/"00_INDEXES"/INDEX_NAME),
    })
    return pointer


def register_case(output_root, run_result_path, model_path, *,
                  scenario, profile, expected_support_tags=None):
    """Index only a successful native solver result with a valid SHA256.

    [REF docs/source/components/gravity/reaction_case_registry.py.md]
    """
    output_root=Path(output_root).resolve()
    result_path=Path(run_result_path).resolve()
    evidence_bytes=result_path.read_bytes()
    payload=json.loads(evidence_bytes.decode("utf-8-sig"))
    record=checked_reaction_result(payload,model_path,scenario=scenario,
        profile=profile,expected_support_tags=expected_support_tags)
    record["result_path"]=str(result_path)
    # Hash the EXACT bytes verified by the validator, and reject any source
    # mutation observed before committing the public navigation index.
    record["result_sha256"]=hashlib.sha256(evidence_bytes).hexdigest()
    if _sha256(result_path)!=record["result_sha256"]:
        raise RuntimeError("Gravity solver result changed during case registration")
    if _model_input_fingerprints(model_path)!=record["input_sha256"]:
        raise RuntimeError("Model inputs changed during gravity case registration")
    record["indexed_at_utc"]=datetime.now(timezone.utc).isoformat()
    # Keep output index under selected output root; no claims about stale results.
    from components.gravity.output_ownership import index_path, existing_index
    dest=index_path(output_root,INDEX_NAME,create=True)
    old_index=existing_index(output_root,INDEX_NAME)
    if old_index.is_file():
        prior=json.loads(old_index.read_text(encoding="utf-8-sig"))
        if not isinstance(prior,dict):
            raise ValueError("Gravity case registry is invalid")
    else:
        prior={}
    prior[scenario+"|"+profile]=record
    output_root.mkdir(parents=True,exist_ok=True)
    tmp=dest.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(prior,indent=2),encoding="utf-8")
    tmp.replace(dest)
    lines=["GRAVITY OUTPUT INDEX", "Selected output root: "+str(output_root),
           "JSON index: "+str(dest),
           "Each entry identifies a separate load profile and support condition.",
           "Historical entries may be stale; GUI rechecks model/input fingerprints.",
           "Solver completion and equilibrium are not ETABS validation.", ""]
    for key, entry in sorted(prior.items()):
        lines.extend([key, "  Model: "+str(entry.get("model_path")),
            "  Supports: "+str(entry.get("support_count")),
            "  Result: "+str(entry.get("result_path")),
            "  Indexed UTC: "+str(entry.get("indexed_at_utc","unknown")), ""])
    text_path=index_path(output_root,"Gravity_Output_Index.txt",create=True)
    text_tmp=text_path.with_suffix(".txt.tmp")
    text_tmp.write_text("\n".join(lines),encoding="utf-8")
    text_tmp.replace(text_path)
    # Index creation is deterministic and preserves the full legacy record.
    # Failure to build an optional preview must not invalidate solver evidence.
    try:
        publish_gravity_case_index(output_root, record)
    except (OSError, ValueError) as exc:
        (index_path(output_root,"Gravity_Organized_Index_Warning.txt",create=True)).write_text(
            "The solver result is preserved; organized preview failed: " +
            str(exc), encoding="utf-8")
    return record


def current_case(output_root, model_path, *, scenario, profile,
                 expected_support_tags=None):
    """[REF docs/source/components/gravity/reaction_case_registry.py.md]
    Compatibility facade: share the single strict case-validation path.
    The detailed API explains why a saved result cannot be trusted.
    """
    return current_case_diagnostic(
        output_root, model_path, scenario=scenario, profile=profile,
        expected_support_tags=expected_support_tags)["result"]


def current_case_diagnostic(output_root, model_path, *, scenario, profile,
                            expected_support_tags=None):
    """[REF docs/source/components/gravity/reaction_case_registry.py.md]
    Explain why a saved run is unavailable without weakening source checks.

    Inspect only existing index/result metadata. Never trust a global reaction
    sum as evidence of file identity or promote a mismatched 32/76/97 case.
    Codes distinguish NEVER_INDEXED from a previous completed-but-stale run.
    """
    from components.gravity.output_ownership import existing_index, model_workspace
    from components.inputs.output_layout import owned_run_destination
    if scenario not in SCENARIO_SUPPORTS:
        return {"status":"INVALID_SUPPORT_SCENARIO",
                "reason":"Unknown 32/76/97 scenario","result":None}
    index=existing_index(output_root,INDEX_NAME)
    try:
        model = Path(model_path).expanduser().resolve()
        indices = [index]
        if model.is_file():
            workspace = model_workspace(model)
            legacy = owned_run_destination(model.parent, 'GRAVITY', model.stem)
            if workspace != legacy and Path(output_root).resolve() == workspace:
                indices.append(existing_index(legacy, INDEX_NAME))
        entry = None
        found = False
        for path in indices:
            if not path.is_file():
                continue
            index = path
            found = True
            entries = json.loads(index.read_text(encoding='utf-8-sig'))
            if not isinstance(entries, dict):
                raise ValueError('Index is not a JSON object')
            key = scenario+'|'+profile
            if key in entries:
                entry = entries[key]
                if not isinstance(entry, dict):
                    raise ValueError('Case index record is not an object')
                break
        if not found:
            return {"status":"NO_CASE_INDEX","reason":
                    "No saved reaction index at "+str(index),"result":None}
        if entry is None:
            return {"status":"CASE_NOT_INDEXED","reason":
                    "No saved run indexed for this exact support case and gravity profile",
                    "index":str(index),"result":None}
        if not model.is_file():
            return {"status":"MODEL_NOT_FOUND","reason":
                    "Selected model file is missing","index":str(index),"result":None}
        if entry.get("model_sha256")!=_sha256(model):
            return {"status":"MODEL_SHA_CHANGED","reason":
                    "Saved case exists, but selected model bytes differ; choose original model or rerun",
                    "index":str(index),"result":None}
        if entry.get("input_sha256")!=_model_input_fingerprints(model):
            return {"status":"MODEL_INPUTS_CHANGED","reason":
                    "Saved case exists, but model config/load/connectivity fingerprint changed",
                    "index":str(index),"result":None}
        if Path(entry.get("model_path","")).resolve()!=model:
            return {"status":"DIFFERENT_MODEL_PATH","reason":
                    "Saved case belongs to a different original model path",
                    "index":str(index),"result":None}
        target=Path(entry.get("result_path",""))
        if not target.is_file():
            return {"status":"RESULT_FILE_MISSING","reason":
                    "Indexed run was solved previously, but saved result is now missing: "+
                    str(target),"index":str(index),"result":None}
        digest=entry.get("result_sha256")
        if not isinstance(digest,str) or len(digest)!=64:
            return {"status":"LEGACY_DIGEST_NOT_INDEXED","reason":
                    "Saved solver result exists but lacks a registered SHA256; "
                    "re-register from verified source without rerunning the solver",
                    "index":str(index),"result":None}
        original=target.read_bytes()
        if hashlib.sha256(original).hexdigest()!=digest:
            return {"status":"SAVED_RESULT_HASH_CHANGED","reason":
                    "Saved solver result bytes differ from indexed result; evidence not trusted",
                    "index":str(index),"result":None}
        payload=json.loads(original.decode("utf-8-sig"))
        verified=checked_reaction_result(payload,model,scenario=scenario,
                   profile=profile,expected_support_tags=expected_support_tags)
        # Recheck exact file identity after validation, guarding concurrent
        # replacement between the first read and the returned display record.
        if _sha256(target)!=digest:
            return {"status":"SAVED_RESULT_CHANGED_DURING_CHECK",
                    "reason":"Solver result changed while verifying; reselect stable evidence",
                    "index":str(index),"result":None}
        if abs(verified["summed_reaction_kN"]-
               float(entry["summed_reaction_kN"]))>0.01:
            raise ValueError("Indexed vertical reaction differs from solved file")
        if abs(verified["applied_load_kN"]-
               float(entry["applied_load_kN"]))>0.01:
            raise ValueError("Indexed gravity load differs from solved file")
        return {"status":"SOLVED_VERIFIED_INDEX","reason":
                "Completed native OpenSees solver case; ETABS pointwise equivalence NOT certified",
                "index":str(index),
                "result":dict(verified,result_path=str(target),result_sha256=digest,registry_path=str(index))}
    except (OSError,ValueError,KeyError,TypeError,OverflowError) as exc:
        return {"status":"SAVED_CASE_VALIDATION_BLOCKED",
                "reason":str(exc),"index":str(index),"result":None}

"""Case-specific *solved* support-reaction display, never an applied-load override.

[REF docs/source/components/gravity/reaction_case_registry.py.md]
No ETABS API, OpenSees call or model edits. Rejects stale/foreign results.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

SCENARIO_SUPPORTS = {
    "ETABS_NONZERO_REACTION_DIAGNOSTIC": 32,
    "ETABS_SOURCE_SUPPORTS": 76,
    "CONTINUOUS_WALL_BASE_FIXED": 97,
}
INDEX_NAME = "Gravity_Case_Reaction_Index.json"


def _sha256(path):
    """Hash exact selected model code for result provenance.

    [REF docs/source/components/gravity/reaction_case_registry.py.md]
    """
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _model_input_fingerprints(model_path):
    """Fingerprint model code and its exported load/config metadata.

    [REF docs/source/components/gravity/reaction_case_registry.py.md]
    """
    model=Path(model_path).resolve()
    names=(model.name,"OpenSees_Complete_Model_Data_V118.json",
           "OpenSees_Complete_Model_Config_V118.json",
           "OpenSees_Source_Model_Metadata_V118.json",
           "OpenSees_Element_Connectivity.json")
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
        model_sha256=_sha256(current_model),
        input_sha256=_model_input_fingerprints(current_model),
        support_count=len(tags),
        support_tags=sorted(tags),applied_load_kN=applied,
        summed_reaction_kN=sum_vertical,equilibrium_error_percent=equilibrium,
        balance_pass=equilibrium<=0.5, # Numerical screening, not code acceptance
        status="SOLVED_REACTIONS_NOT_ETABS_VALIDATED")


def register_case(output_root, run_result_path, model_path, *,
                  scenario, profile, expected_support_tags=None):
    """Index only a successful native solver result with a valid SHA256.

    [REF docs/source/components/gravity/reaction_case_registry.py.md]
    """
    output_root=Path(output_root).resolve()
    result_path=Path(run_result_path).resolve()
    payload=json.loads(result_path.read_text(encoding="utf-8-sig"))
    record=checked_reaction_result(payload,model_path,scenario=scenario,
        profile=profile,expected_support_tags=expected_support_tags)
    record["result_path"]=str(result_path)
    # Keep output index under selected output root; no claims about stale results.
    dest=output_root/INDEX_NAME
    if dest.is_file():
        prior=json.loads(dest.read_text(encoding="utf-8-sig"))
        if not isinstance(prior,dict):
            raise ValueError("Gravity case registry is invalid")
    else:
        prior={}
    prior[scenario+"|"+profile]=record
    output_root.mkdir(parents=True,exist_ok=True)
    tmp=dest.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(prior,indent=2),encoding="utf-8")
    tmp.replace(dest)
    return record


def current_case(output_root, model_path, *, scenario, profile,
                 expected_support_tags=None):
    """Return matching solved reaction only; never return a stale value.

    [REF docs/source/components/gravity/reaction_case_registry.py.md]
    """
    index=Path(output_root).resolve()/INDEX_NAME
    if not index.is_file():
        return None
    try:
        entries=json.loads(index.read_text(encoding="utf-8-sig"))
        entry=entries.get(scenario+"|"+profile)
        if not entry:
            return None
        if entry["model_sha256"] != _sha256(model_path):
            return None
        if entry.get("input_sha256")!=_model_input_fingerprints(model_path):
            return None
        if Path(entry["model_path"]).resolve()!=Path(model_path).resolve():
            return None
        result=Path(entry["result_path"])
        if not result.is_file():
            return None
        payload=json.loads(result.read_text(encoding="utf-8-sig"))
        freshly=checked_reaction_result(payload,model_path,scenario=scenario,
           profile=profile,expected_support_tags=expected_support_tags)
        if abs(freshly["summed_reaction_kN"]-float(entry["summed_reaction_kN"]))>0.01:
            return None
        if abs(freshly["applied_load_kN"]-float(entry["applied_load_kN"]))>0.01:
            return None
        return dict(freshly,result_path=str(result))
    except (OSError,ValueError,KeyError,TypeError,OverflowError):
        return None

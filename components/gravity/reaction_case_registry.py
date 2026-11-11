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


def publish_gravity_case_index(output_root, record):
    """[REF docs/source/components/gravity/reaction_case_registry.py.md]
    Publish navigable case evidence in the project-selected Gravity folder.

    Keep historical solver files exactly where their registered absolute paths
    point; duplicate only small read-only plot previews and the case summary.
    Never copy source EDB, original private spreadsheets or complete results.
    """
    from shutil import copy2
    root = Path(output_root).resolve()
    # The configured analysis root is .../<selection>/OpenSees_Analysis_Results/
    # <ULS-or-SLS_model>. Fall back to the selected output itself for standalone
    # gravity workflows without that recognizable parent.
    selection = None
    for ancestor in (root, *root.parents):
        if ancestor.name == "OpenSees_Analysis_Results":
            selection = ancestor.parent
            break
    if selection is None:
        selection = root
    destination_root = selection / "02_GRAVITY"
    case_path = Path(record["result_path"]).resolve()
    scenario = record["scenario"]
    if scenario not in SCENARIO_SUPPORTS:
        raise ValueError("Unrecognized gravity case identity")
    # Case path hash avoids collisions even if run folders share a timestamp.
    short = hashlib.sha256(str(case_path).encode("utf-8")).hexdigest()[:12]
    case_dir = destination_root / scenario / (case_path.parent.name + "_" + short)
    case_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "status": "SOLVER_RESULT_INDEXED_NOT_ETABS_VALIDATED",
        "support_strategy": scenario,
        "support_count": record["support_count"],
        "gravity_profile": record["profile"],
        "model_sha256": record["model_sha256"],
        "result_path": str(case_path),
        "original_full_run_folder": str(case_path.parent),
        "applied_load_kN": record["applied_load_kN"],
        "summed_reaction_kN": record["summed_reaction_kN"],
        "equilibrium_error_percent": record["equilibrium_error_percent"],
    }
    (case_dir / "CASE_SUMMARY.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    (case_dir / "README_FIRST.txt").write_text(
        "GRAVITY CASE — " + scenario + "\n" +
        "Number of restrained support nodes: " + str(record["support_count"]) + "\n" +
        "Full native solver reports and plots remain at:\n" +
        str(case_path.parent) + "\n" +
        "This directory is an organized INDEX + lightweight previews.\n" +
        "Numerical equilibrium is not ETABS/OpenSees physical equivalence.\n",
        encoding="utf-8")
    (case_dir / "OPEN_FULL_LEGACY_RUN.url").write_text(
        "[InternetShortcut]\nURL=" + case_path.parent.as_uri() + "\n",
        encoding="utf-8")
    for preview in ("Gravity_Reactions_V123.png",
                    "Gravity_Deformation_V123.png"):
        original = case_path.parent / preview
        if original.is_file() and original.stat().st_size <= 20_000_000:
            copy2(original, case_dir / preview)
    (destination_root / "LATEST_GRAVITY_CASES.json").write_text(
        json.dumps({"status": "INDEX_ONLY_NOT_ETABS_VALIDATED",
                    "last_case": str(case_dir),
                    "legacy_case_index": str(root / INDEX_NAME)}, indent=2),
        encoding="utf-8")
    return case_dir


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
    record["indexed_at_utc"]=datetime.now(timezone.utc).isoformat()
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
    text_path=output_root/"Gravity_Output_Index.txt"
    text_tmp=text_path.with_suffix(".txt.tmp")
    text_tmp.write_text("\n".join(lines),encoding="utf-8")
    text_tmp.replace(text_path)
    # Index creation is deterministic and preserves the full legacy record.
    # Failure to build an optional preview must not invalidate solver evidence.
    try:
        publish_gravity_case_index(output_root, record)
    except (OSError, ValueError) as exc:
        (output_root / "Gravity_Organized_Index_Warning.txt").write_text(
            "The solver result is preserved; organized preview failed: " +
            str(exc), encoding="utf-8")
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

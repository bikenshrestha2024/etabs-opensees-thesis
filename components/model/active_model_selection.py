"""Explicit immutable clear-beam variant selection for analysis launchers."""
import hashlib
import json
from pathlib import Path

def validate_clear_beam_model(root, selected):
    """Validate rebuild identity, not engineering acceptance. [REF docs/source/components/model/active_model_selection.py.md]"""
    root=Path(root).resolve()
    model=Path(selected).resolve()
    base=root/"02_MODEL"/"REBUILDS"/"VERIFIED_CLEAR_BEAM"
    if model.parent!=base:
        raise ValueError("Select a canonical rebuild directly beneath "+str(base))
    status=json.loads((model/"CLEAR_BEAM_REBUILD_STATUS.json").read_text(encoding="utf-8-sig"))
    if status.get("status")!="EXPORT_VERIFIED_NOT_GRAVITY_SOLVED":
        raise ValueError("Rebuild is not marked export-verified")
    if Path(status.get("original_source_dir","")).resolve()!=root:
        raise ValueError("Rebuild belongs to a different original export")
    from components.nonlinear_time_history.source_model_handoff import required_source_files
    required_source_files(model)
    cfg=json.loads((model/"OpenSees_Complete_Model_Config_V118.json").read_text(encoding="utf-8-sig"))
    if cfg.get("etabs_beam_weight_policy")!="ETABS_BEAM_CLEAR_LENGTH" or cfg.get("etabs_clear_beam_weight_confirmed") is not True:
        raise ValueError("Clear-beam source policy is missing")
    report=json.loads((model/"OpenSees_Complete_Export_Report_V118.json").read_text(encoding="utf-8-sig"))
    if report.get("assembly_errors"):
        raise ValueError("Rebuild contains assembly errors")
    return {"folder":str(model),"model_sha256":hashlib.sha256((model/"OpenSees_Complete_Model_Data_V118.json").read_bytes()).hexdigest(),"engineering_acceptance":"NOT_VERIFIED"}

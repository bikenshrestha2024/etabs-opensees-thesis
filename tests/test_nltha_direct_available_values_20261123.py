"""Reuse available project/source inputs without granting nonlinear readiness approval."""
import hashlib
import json
from pathlib import Path

import pytest

from components.model.readiness import bind_readiness_draft, READINESS_CHECK_KEYS
from components.model.readiness_available_values import (
    collect_available_project_values, attach_available_values_to_draft)

ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=ROOT/"OpenSees_Model_Readiness_Template_V116.json"


def project(root):
    model=root/"OpenSees_Complete_Nonlinear_Model.py"
    model.write_text("# existing nonlinear builder",encoding="utf-8")
    cfg=root/"OpenSees_Complete_Model_Config_V118.json"
    cfg.write_text(json.dumps({
        "gravity_factors":{"Dead":1.0,"Live":0.3},
        "mass_factors":{"Dead":1.0,"Live":0.3},
        "slab_bending_factor":0.25,
        "slab_bending_factor_sls":0.35,
        "nonlinear_materials_file":"",
        "nonlinear_wall_fsam_tags":{},
        "nonlinear_parameters_reviewed":False}),encoding="utf-8")
    data=root/"OpenSees_Complete_Model_Data_V118.json"
    data.write_text(json.dumps({
        "nodes":{"1":[0,0,0],"2":[0,0,3]},
        "shells":[{"category":"SHEAR WALL","properties":{"property":"W600","thickness":0.6}},
                  {"category":"FLOOR","properties":{"property":"S150","thickness":0.15}}],
        "diaphragms":[{"id":"D1"}],
        "gravity_by_pattern_kN":{"Dead":1200,"Live":100},
    }),encoding="utf-8")
    modal=root/"04_MODAL"/"RUNS"/"ULS"/"model_case"/"run"/"02_RESULTS"/"NBC105_Modal_V111.json"
    modal.parent.mkdir(parents=True)
    modal.write_text(json.dumps({
        "model_sha256":hashlib.sha256(data.read_bytes()).hexdigest(),
        "limit_state":"ULS",
        "rows":[{"mode":1,"period_s":2.4,
                 "UX_cumulative_percent":80,"UY_cumulative_percent":70},
                {"mode":2,"period_s":1.7,
                 "UX_cumulative_percent":91.7,"UY_cumulative_percent":91.3}],
        "engineering_acceptance":"NOT_VERIFIED",
    }),encoding="utf-8")
    return model,modal


def test_direct_values_read_exact_project_files_and_published_literature(tmp_path):
    model,modal=project(tmp_path)
    result=collect_available_project_values(model)
    assert result["approval_status"]=="UNAPPROVED"
    assert result["model"]["sha256"]==hashlib.sha256(model.read_bytes()).hexdigest()
    values=result["available_values"]
    assert values["source_config"]["slab_bending_factor"]==0.25
    assert values["source_config"]["gravity_factors"]["Live"]==0.3
    assert values["geometry"]["wall_properties_m"]["W600"]==0.6
    assert values["geometry"]["shell_count"]==2
    assert values["literature_research_only"]["web_fsam"]["rho_x"]==0.0074
    assert values["literature_research_only"]["web_fsam"]["rho_y"]==0.0074
    assert values["literature_research_only"]["boundary_fsam"]["rho_y"]==0.0587
    assert values["literature_research_only"]["source_scope"]=="SPECIMEN_ONLY_NOT_PROJECT_VERIFIED"
    assert len(result["checklist_candidates"])==len(READINESS_CHECK_KEYS)
    assert result["checklist_candidates"]["modal_periods_modes_and_mass_participation_reviewed"]["status"]=="SOURCE_FOUND_REVIEW_REQUIRED"
    assert result["modal_reference"]["status"]=="MATCHED_SERIALIZED_MODEL_REVIEW_REQUIRED"
    assert all(not x.get("approved",False) for x in result["checklist_candidates"].values())
    assert all(str(tmp_path) in x["path"] for x in result["source_files"].values())
    assert modal.is_file()


def test_mismatched_modal_results_not_used_as_model_proof(tmp_path):
    model,modal=project(tmp_path)
    obj=json.loads(modal.read_text())
    obj["model_sha256"]="0"*64
    modal.write_text(json.dumps(obj))
    result=collect_available_project_values(model)
    assert result["modal_reference"]["status"]=="MODEL_SHA_MISMATCH_NOT_REUSED"
    assert "modal_mass_screen" not in result["available_values"]


def test_attach_snapshot_to_bound_unapproved_draft_without_approving(tmp_path):
    model,_=project(tmp_path)
    draft=bind_readiness_draft(TEMPLATE,model)
    obj=json.loads(draft.read_text())
    obj["evidence"]["etabs_topology_and_story_mapping_reviewed"]="Human note - retained"
    draft.write_text(json.dumps(obj))
    config=(tmp_path/"OpenSees_Complete_Model_Config_V118.json").read_bytes()
    out=attach_available_values_to_draft(model,draft)
    after=json.loads(draft.read_text())
    assert out==draft
    assert after["approved_for_nltha"] is False
    assert all(after["checks"][x] is False for x in READINESS_CHECK_KEYS)
    assert after["evidence"]["etabs_topology_and_story_mapping_reviewed"]=="Human note - retained"
    assert after["available_project_values"]["available_values"]["geometry"]["wall_properties_m"]["W600"]==0.6
    assert (tmp_path/"OpenSees_Complete_Model_Config_V118.json").read_bytes()==config


def test_refuse_promoting_or_rewriting_approved_or_wrong_model_draft(tmp_path):
    model,_=project(tmp_path)
    draft=bind_readiness_draft(TEMPLATE,model)
    original=json.loads(draft.read_text())
    original["approved_for_nltha"]=True
    draft.write_text(json.dumps(original))
    old=draft.read_bytes()
    with pytest.raises(ValueError,match="approved"):
        attach_available_values_to_draft(model,draft)
    assert draft.read_bytes()==old
    original["approved_for_nltha"]=False
    original["model_script_sha256"]="bad"
    draft.write_text(json.dumps(original))
    old=draft.read_bytes()
    with pytest.raises(ValueError,match="binding"):
        attach_available_values_to_draft(model,draft)
    assert draft.read_bytes()==old


def test_missing_material_mapping_kept_unresolved_not_backfilled_from_peer(tmp_path):
    model,_=project(tmp_path)
    result=collect_available_project_values(model)
    missing=result["missing_production_inputs"]
    assert {"nonlinear_materials_file","nonlinear_wall_fsam_tags",
            "nonlinear_parameters_reviewed"} <= set(missing)
    assert result["available_values"]["literature_research_only"]["web_fsam"]["rho_x"]==0.0074


def test_ulssls_modal_results_loaded_separately_for_same_model(tmp_path):
    model,uls=project(tmp_path)
    sls=tmp_path/"04_MODAL"/"RUNS"/"SLS"/"case"/"run"/"02_RESULTS"/"NBC105_Modal_V111.json"
    sls.parent.mkdir(parents=True)
    payload=json.loads(uls.read_text())
    payload["limit_state"]="SLS"
    payload["rows"][0]["period_s"]=2.8
    sls.write_text(json.dumps(payload))
    result=collect_available_project_values(model)
    screens=result["available_values"]["modal_mass_screen_by_state"]
    assert set(screens)=={"ULS","SLS"}
    assert screens["ULS"]["limit_state"]=="ULS"
    assert screens["SLS"]["limit_state"]=="SLS"
    assert screens["ULS"]["periods_first_three_s"][0]==2.4
    assert screens["SLS"]["periods_first_three_s"][0]==2.8
    assert result["modal_reference"]["status"]=="MATCHED_SERIALIZED_MODEL_REVIEW_REQUIRED"


def test_modal_ambiguous_same_state_does_not_use_that_state(tmp_path):
    model,uls=project(tmp_path)
    other=tmp_path/"04_MODAL"/"RUNS"/"ULS"/"new_case"/"run"/"02_RESULTS"/"NBC105_Modal_V111.json"
    other.parent.mkdir(parents=True)
    other.write_bytes(uls.read_bytes())
    result=collect_available_project_values(model)
    assert result["modal_reference"]["status"]=="AMBIGUOUS_MATCHED_MODAL_SOURCES_NOT_REUSED"
    assert "modal_mass_screen" not in result["available_values"]
    assert "modal_mass_screen_by_state" not in result["available_values"]

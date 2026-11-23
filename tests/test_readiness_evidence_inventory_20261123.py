"""Discovered source documents are review suggestions, not NLTHA approval."""
import hashlib
import json
from components.model.readiness_gui import evidence_inventory
from components.model.readiness import READINESS_CHECK_KEYS


def test_model_hash_and_stale_modal_identity_visible_without_approval(tmp_path):
    model=tmp_path/"OpenSees_Complete_Nonlinear_Model.py"
    model.write_text("# synthetic nonlinear model",encoding="utf-8")
    geo=tmp_path/"OpenSees_Complete_Model_Data_V118.json"
    geo.write_text('{"name":"dummy"}',encoding="utf-8")
    result=tmp_path/"04_MODAL"/"RUNS"/"ULS"/"a"/"run"/"02_RESULTS"/"NBC105_Modal_V111.json"
    result.parent.mkdir(parents=True)
    result.write_text(json.dumps({"model_sha256":"0"*64,"limit_state":"ULS","rows":[{"mode":1}]}))
    original=model.read_bytes()
    report=evidence_inventory(model)
    assert report["approval_unchanged"] is True
    assert report["approved_for_nltha"] is False
    assert report["model_script_sha256"]==hashlib.sha256(original).hexdigest()
    m=report["checks"]["modal_periods_modes_and_mass_participation_reviewed"]
    assert m["status"]=="AVAILABLE_NOT_REVIEWED"
    assert any(x["model_identity"]=="MISMATCH" for x in m["files"])
    assert report["checks"]["etabs_topology_and_story_mapping_reviewed"]["files"]
    assert report["checks"]["single_element_and_wall_benchmark_checks_passed"]["files"]==[]
    assert model.read_bytes()==original
    assert len(report["checks"])==len(READINESS_CHECK_KEYS)


def test_source_provenance_respects_actual_modal_model_hash(tmp_path):
    model=tmp_path/"OpenSees_Complete_Nonlinear_Model.py"
    model.write_text("# model")
    source_payload=tmp_path/"OpenSees_Complete_Model_Data_V118.json"
    source_payload.write_text('{"nodes":{}}')
    current=hashlib.sha256(source_payload.read_bytes()).hexdigest()
    result=tmp_path/"04_MODAL"/"RUNS"/"ULS"/"a"/"run"/"02_RESULTS"/"NBC105_Modal_V111.json"
    result.parent.mkdir(parents=True)
    result.write_text(json.dumps({"model_sha256":current,"limit_state":"ULS","rows":[{"mode":1}]}))
    rec=evidence_inventory(model)["checks"]["modal_periods_modes_and_mass_participation_reviewed"]["files"][0]
    assert rec["model_identity"]=="MATCHING_SERIALIZED_MODEL"
    assert rec["sha256"]==hashlib.sha256(result.read_bytes()).hexdigest()

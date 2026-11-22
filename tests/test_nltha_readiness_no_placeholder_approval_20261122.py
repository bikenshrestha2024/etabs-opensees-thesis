"""Prevent auto-populated readiness hints from becoming human NLTHA approval."""
from pathlib import Path
from components.model.readiness_gui import _is_reviewed_evidence_reference
from components.model.readiness import approval_binding_problems


def test_disallow_auto_discovered_placeholder_as_checked_evidence():
    for candidate in ("", " ", "AVAILABLE FOR REVIEW: saved elastic modal result | foo.json",
                      "INPUT / REVIEW REQUIRED: source wall mesh", "REVIEW REQUIRED: specimen fit"):
        assert _is_reviewed_evidence_reference(candidate) is False
    assert _is_reviewed_evidence_reference(
        "Independently inspected model hash abc, wall test plot and reviewer note") is True


def test_model_approval_cannot_be_saved_with_unreviewed_nonlin_parameters(tmp_path):
    model=tmp_path/"OpenSees_Complete_Nonlinear_Model.py"
    model.write_text("# model",encoding="utf8")
    (tmp_path/"mat.json").write_text('{"reviewed":true}',encoding="utf8")
    import json
    (tmp_path/"OpenSees_Complete_Model_Config_V118.json").write_text(
        json.dumps({"nonlinear_materials_file":"mat.json",
                    "nonlinear_wall_fsam_tags":{"W1":17},
                    "nonlinear_parameters_reviewed":False}),encoding="utf8")
    problems=approval_binding_problems(model)
    assert any("nonlinear_parameters_reviewed" in issue for issue in problems)

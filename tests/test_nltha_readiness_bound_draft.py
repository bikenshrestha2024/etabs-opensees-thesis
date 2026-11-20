"""Headless tests for the model-bound UNAPPROVED readiness draft writer (no tkinter)."""
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.model.readiness import (  # noqa: E402
    READINESS_CHECK_KEYS, bind_readiness_draft, diagnose_nonlinear_readiness,
    material_prerequisite_notice)

TEMPLATE = ROOT / "OpenSees_Model_Readiness_Template_V116.json"


def _model(tmp_path, text="# model\n"):
    model = tmp_path / "OpenSees_Complete_Nonlinear_Model.py"
    model.write_text(text, encoding="utf-8")
    return model


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_draft_is_bound_hashed_and_unapproved(tmp_path):
    model = _model(tmp_path)
    out = bind_readiness_draft(TEMPLATE, model)
    data = _load(out)
    assert out.parent == tmp_path
    assert data["model_script"] == str(model.resolve())
    assert Path(data["model_script"]).is_absolute()
    assert data["model_script_sha256"] == hashlib.sha256(model.read_bytes()).hexdigest()
    assert data["approved_for_nltha"] is False
    assert data["status"] == "UNAPPROVED DRAFT"
    assert set(data["checks"]) == set(READINESS_CHECK_KEYS)
    assert all(v is False for v in data["checks"].values())
    assert "review_notes" in data  # template content carried over


def test_explicit_out_path_and_template_untouched(tmp_path):
    model = _model(tmp_path)
    before = TEMPLATE.read_bytes()
    out = bind_readiness_draft(TEMPLATE, model, tmp_path / "sub" / "draft.json")
    assert out == tmp_path / "sub" / "draft.json" and out.is_file()
    assert TEMPLATE.read_bytes() == before


def test_idempotent_on_unapproved_draft(tmp_path):
    model = _model(tmp_path)
    out = bind_readiness_draft(TEMPLATE, model)
    first = out.read_bytes()
    assert bind_readiness_draft(TEMPLATE, model) == out
    assert out.read_bytes() == first


def test_rebinds_stale_unapproved_draft_after_model_edit(tmp_path):
    model = _model(tmp_path)
    out = bind_readiness_draft(TEMPLATE, model)
    model.write_text("# edited\n", encoding="utf-8")
    bind_readiness_draft(TEMPLATE, model)
    assert _load(out)["model_script_sha256"] == hashlib.sha256(model.read_bytes()).hexdigest()
    assert all(v is False for v in _load(out)["checks"].values())


def test_idempotent_run_keeps_human_saved_checks(tmp_path):
    # A human-ticked check on a current, unapproved draft must survive a re-run.
    model = _model(tmp_path)
    out = bind_readiness_draft(TEMPLATE, model)
    data = _load(out)
    data["checks"][READINESS_CHECK_KEYS[0]] = True
    out.write_text(json.dumps(data), encoding="utf-8")
    bind_readiness_draft(TEMPLATE, model)
    assert _load(out)["checks"][READINESS_CHECK_KEYS[0]] is True


def test_refuses_to_clobber_approved_file(tmp_path):
    model = _model(tmp_path)
    target = tmp_path / "approved.json"
    target.write_text(json.dumps({"approved_for_nltha": True, "checks": {}}), encoding="utf-8")
    before = target.read_bytes()
    with pytest.raises(RuntimeError, match="approved"):
        bind_readiness_draft(TEMPLATE, model, target)
    assert target.read_bytes() == before


def test_refuses_approved_even_when_stale(tmp_path):
    model = _model(tmp_path)
    out = bind_readiness_draft(TEMPLATE, model)
    data = _load(out)
    data["approved_for_nltha"] = True
    out.write_text(json.dumps(data), encoding="utf-8")
    model.write_text("# edited\n", encoding="utf-8")
    with pytest.raises(RuntimeError):
        bind_readiness_draft(TEMPLATE, model)
    assert _load(out)["approved_for_nltha"] is True


def test_missing_model_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        bind_readiness_draft(TEMPLATE, tmp_path / "nope.py")


def test_draft_still_fails_gate_with_not_approved(tmp_path):
    model = _model(tmp_path)
    out = bind_readiness_draft(TEMPLATE, model)
    diag = diagnose_nonlinear_readiness({"model_script": str(model), "model_readiness_json": str(out)})
    codes = [b["code"] for b in diag["blockers"]]
    assert diag["ready"] is False
    assert "not_approved" in codes
    assert "template_unbound" not in codes and "bound_to_other_model" not in codes
    assert "model_sha_mismatch" not in codes
    assert sum(c.startswith("check_false:") for c in codes) == len(READINESS_CHECK_KEYS)


def test_material_notice_lists_non_gate_blockers():
    diag = {"ready": False, "blockers": [
        {"code": "not_approved", "message": "m", "fix": "f"},
        {"code": "material_file_missing", "message": "m", "fix": "f"},
        {"code": "parameters_not_reviewed", "message": "m", "fix": "f"}]}
    text = material_prerequisite_notice(diag)
    assert "material_file_missing" in text and "parameters_not_reviewed" in text
    assert "not_approved" not in text
    assert material_prerequisite_notice({"ready": True, "blockers": []}) == ""

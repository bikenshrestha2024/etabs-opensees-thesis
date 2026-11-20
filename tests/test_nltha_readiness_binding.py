"""Headless tests: approval binding to model config, material file and FSAM tags."""
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.model.readiness import (  # noqa: E402
    READINESS_CHECK_KEYS, approval_binding_problems, bind_readiness_draft,
    canonical_fsam_tags_hash, current_binding, diagnose_nonlinear_readiness,
    material_prerequisite_notice, record_binding)

CFG = "OpenSees_Complete_Model_Config_V118.json"
MAN = "OpenSees_Model_Readiness_V116.json"
FIELDS = ("model_config_sha256", "nonlinear_materials_file_sha256", "nonlinear_wall_fsam_tags_sha256")


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _project(tmp_path, *, material=True, fsam=True):
    model = tmp_path / "OpenSees_Complete_Nonlinear_Model.py"
    model.write_text("# model\n", encoding="utf-8")
    if material:
        (tmp_path / "mat.json").write_text('{"fc": 1}', encoding="utf-8")
    cfg = {"nonlinear_materials_file": "mat.json" if material else "",
           "nonlinear_wall_fsam_tags": {"P2": 2, "P1": 1} if fsam else {},
           "nonlinear_parameters_reviewed": True}
    (tmp_path / CFG).write_text(json.dumps(cfg), encoding="utf-8")
    return model


def _manifest(model, *, bind=True, approved=True, checks=True, **over):
    data = {"model_script": str(model), "model_script_sha256": _sha(model),
            "approved_for_nltha": approved,
            "checks": dict.fromkeys(READINESS_CHECK_KEYS, checks)}
    if bind:
        record_binding(data, model)
    data.update(over)
    (model.parent / MAN).write_text(json.dumps(data), encoding="utf-8")
    return data


def _load_gate():
    """Compile only the gate function; the runner module imports tkinter at top level."""
    import ast
    import types
    src = (ROOT / "components/nonlinear_time_history/runner_and_gui.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)
              and n.name == "_require_nonlinear_readiness")
    ns = {"json": json, "Path": Path}
    exec(compile(ast.Module([fn], []), "runner_gate", "exec"), ns)
    return types.SimpleNamespace(gate=ns["_require_nonlinear_readiness"])


def _codes(d):
    return [b["code"] for b in d["blockers"]]


def test_fsam_hash_is_canonical_and_order_insensitive():
    assert canonical_fsam_tags_hash({"a": 1, "b": 2}) == canonical_fsam_tags_hash({"b": 2, "a": 1})
    assert canonical_fsam_tags_hash({"a": 1}) != canonical_fsam_tags_hash({"a": 2})
    assert canonical_fsam_tags_hash({}) is None and canonical_fsam_tags_hash(None) is None


def test_current_binding_values(tmp_path):
    model = _project(tmp_path)
    b = current_binding(model)
    assert b["model_config_sha256"] == _sha(tmp_path / CFG)
    assert b["nonlinear_materials_file_sha256"] == _sha(tmp_path / "mat.json")
    assert b["nonlinear_wall_fsam_tags_sha256"] == canonical_fsam_tags_hash({"P1": 1, "P2": 2})


def test_bind_draft_records_hashes_and_stays_unapproved(tmp_path):
    model = _project(tmp_path)
    tpl = tmp_path / "tpl.json"
    tpl.write_text(json.dumps({"model_script": "absolute path to x", "checks": {}}), encoding="utf-8")
    out = bind_readiness_draft(tpl, model)
    data = json.loads(out.read_text(encoding="utf-8"))
    for f in FIELDS:
        assert data[f] == current_binding(model)[f]
    assert data["approved_for_nltha"] is False and not any(data["checks"].values())


def test_bind_draft_without_material_records_null(tmp_path):
    model = _project(tmp_path, material=False, fsam=False)
    tpl = tmp_path / "tpl.json"
    tpl.write_text("{}", encoding="utf-8")
    data = json.loads(bind_readiness_draft(tpl, model).read_text(encoding="utf-8"))
    assert data["nonlinear_materials_file_sha256"] is None
    assert data["nonlinear_wall_fsam_tags_sha256"] is None


def test_unchanged_passes_gate_and_diagnosis(tmp_path):
    model = _project(tmp_path)
    _manifest(model)
    assert _load_gate().gate({"model_script": str(model)})["check_count"] == 16
    assert diagnose_nonlinear_readiness({"model_script": str(model)}) == {"ready": True, "blockers": []}


def test_config_change_raises(tmp_path):
    model = _project(tmp_path)
    _manifest(model)
    cfg = json.loads((tmp_path / CFG).read_text(encoding="utf-8"))
    cfg["nonlinear_parameters_reviewed"] = False
    (tmp_path / CFG).write_text(json.dumps(cfg), encoding="utf-8")
    with pytest.raises(RuntimeError, match="model_config_changed"):
        _load_gate().gate({"model_script": str(model)})
    assert "model_config_changed" in _codes(diagnose_nonlinear_readiness({"model_script": str(model)}))


def test_material_file_change_raises(tmp_path):
    model = _project(tmp_path)
    _manifest(model)
    (tmp_path / "mat.json").write_text('{"fc": 2}', encoding="utf-8")
    with pytest.raises(RuntimeError, match="material_file_changed"):
        _load_gate().gate({"model_script": str(model)})


def test_fsam_tags_change_raises_in_isolation(tmp_path):
    model = _project(tmp_path)
    _manifest(model)
    cfg = {"model_script": str(model), "nonlinear_wall_fsam_tags": {"P1": 1, "P2": 3}}
    with pytest.raises(RuntimeError, match="wall_fsam_tags_changed") as e:
        _load_gate().gate(cfg)
    assert "model_config_changed" not in str(e.value)


def test_fsam_tags_change_in_config_file_raises(tmp_path):
    model = _project(tmp_path)
    _manifest(model)
    cfg = json.loads((tmp_path / CFG).read_text(encoding="utf-8"))
    cfg["nonlinear_wall_fsam_tags"]["P2"] = 9
    (tmp_path / CFG).write_text(json.dumps(cfg), encoding="utf-8")
    with pytest.raises(RuntimeError, match="wall_fsam_tags_changed"):
        _load_gate().gate({"model_script": str(model)})


def test_material_removed_after_binding_raises(tmp_path):
    model = _project(tmp_path)
    _manifest(model)
    (tmp_path / "mat.json").unlink()
    with pytest.raises(RuntimeError, match="material_file_changed|material_file_not_found"):
        _load_gate().gate({"model_script": str(model)})


def test_legacy_manifest_passes_gate_with_diagnose_warning(tmp_path):
    model = _project(tmp_path)
    _manifest(model, bind=False)
    assert _load_gate().gate({"model_script": str(model)})["check_count"] == 16
    d = diagnose_nonlinear_readiness({"model_script": str(model)})
    assert _codes(d) == ["binding_not_recorded"] and d["ready"] is False
    assert "binding_not_recorded" in material_prerequisite_notice(d)


def test_approved_without_material_or_tags_raises(tmp_path):
    model = _project(tmp_path, material=False)
    _manifest(model)
    with pytest.raises(RuntimeError, match="material_file_missing"):
        _load_gate().gate({"model_script": str(model)})
    sub = tmp_path / "b"
    sub.mkdir()
    model2 = _project(sub, fsam=False)
    _manifest(model2)
    with pytest.raises(RuntimeError, match="wall_fsam_tags_empty"):
        _load_gate().gate({"model_script": str(model2)})


def test_unapproved_message_unchanged_prefix(tmp_path):
    model = _project(tmp_path, material=False)
    _manifest(model, approved=False, checks=False)
    with pytest.raises(RuntimeError, match="Nonlinear readiness is not approved. Missing prerequisites:"):
        _load_gate().gate({"model_script": str(model)})


def test_partial_binding_reports_missing_fields(tmp_path):
    model = _project(tmp_path)
    data = _manifest(model)
    del data["nonlinear_materials_file_sha256"]
    (tmp_path / MAN).write_text(json.dumps(data), encoding="utf-8")
    d = diagnose_nonlinear_readiness({"model_script": str(model)})
    assert _codes(d) == ["binding_not_recorded"]
    assert "nonlinear_materials_file_sha256" in d["blockers"][0]["message"]


def test_approval_binding_problems_for_save(tmp_path):
    assert approval_binding_problems(_project(tmp_path)) == []
    sub = tmp_path / "x"
    sub.mkdir()
    problems = approval_binding_problems(_project(sub, material=False, fsam=False))
    assert problems and any("material" in p for p in problems) and any("FSAM" in p for p in problems)


def test_code_never_approves(tmp_path):
    model = _project(tmp_path)
    data = {"approved_for_nltha": False, "checks": dict.fromkeys(READINESS_CHECK_KEYS, False)}
    record_binding(data, model)
    assert data["approved_for_nltha"] is False and not any(data["checks"].values())


# ---------------------------------------------------------------------------
# Fix wave: GUI-side reset helper, unreadable inputs (fail closed)
# ---------------------------------------------------------------------------
from components.model.readiness import (  # noqa: E402
    BindingUnreadableError, binding_change_notice, binding_mismatches, rebind_if_binding_changed)


def test_rebind_helper_unchanged_keeps_approval(tmp_path):
    model = _project(tmp_path)
    data = _manifest(model)
    assert binding_mismatches(data, model) == []
    assert rebind_if_binding_changed(data, model) == []
    assert data["approved_for_nltha"] is True
    assert all(v is True for v in data["checks"].values())


def test_rebind_helper_resets_approval_after_config_change(tmp_path):
    model = _project(tmp_path)
    data = _manifest(model)
    old_hash = data["model_config_sha256"]
    (tmp_path / "mat.json").write_text('{"fc": 2}', encoding="utf-8")
    cfg = json.loads((tmp_path / CFG).read_text())
    cfg["nonlinear_wall_fsam_tags"] = {"P1": 9}
    (tmp_path / CFG).write_text(json.dumps(cfg), encoding="utf-8")
    codes = {b["code"] for b in binding_mismatches(data, model)}
    assert codes == {"model_config_changed", "material_file_changed", "wall_fsam_tags_changed"}
    mism = rebind_if_binding_changed(data, model)
    assert {b["code"] for b in mism} == codes
    assert data["approved_for_nltha"] is False
    assert set(data["checks"]) >= set(READINESS_CHECK_KEYS)
    assert not any(data["checks"].values())
    assert data["model_config_sha256"] != old_hash
    assert data["model_config_sha256"] == _sha(tmp_path / CFG)
    # after the rebind nothing differs, so a second call is a no-op
    assert binding_mismatches(data, model) == []


def test_rebind_helper_never_sets_true(tmp_path):
    model = _project(tmp_path)
    data = _manifest(model, approved=False, checks=False)
    (tmp_path / "mat.json").write_text("{}", encoding="utf-8")
    rebind_if_binding_changed(data, model)
    assert data["approved_for_nltha"] is False and not any(data["checks"].values())


def test_rebind_helper_legacy_manifest_untouched(tmp_path):
    model = _project(tmp_path)
    data = _manifest(model, bind=False)
    (tmp_path / "mat.json").write_text("{}", encoding="utf-8")
    assert rebind_if_binding_changed(data, model) == []
    assert data["approved_for_nltha"] is True
    assert not any(f in data for f in FIELDS)


def test_binding_change_notice_lists_codes(tmp_path):
    model = _project(tmp_path)
    data = _manifest(model)
    (tmp_path / "mat.json").write_text("{}", encoding="utf-8")
    text = binding_change_notice(binding_mismatches(data, model))
    assert "material_file_changed" in text and "approval" in text.lower()
    assert binding_change_notice([]) == ""


def _locked(monkeypatch, name):
    real = Path.read_bytes

    def fake(self):
        if self.name == name:
            raise PermissionError("locked by another process")
        return real(self)
    monkeypatch.setattr(Path, "read_bytes", fake)


def test_locked_material_file_is_blocker_in_diagnose(tmp_path, monkeypatch):
    model = _project(tmp_path)
    _manifest(model)
    _locked(monkeypatch, "mat.json")
    d = diagnose_nonlinear_readiness({"model_script": str(model)})
    assert "binding_unreadable" in {b["code"] for b in d["blockers"]}
    assert d["ready"] is False


def test_locked_config_is_blocker_in_diagnose_and_gate(tmp_path, monkeypatch):
    model = _project(tmp_path)
    _manifest(model)
    _locked(monkeypatch, CFG)
    d = diagnose_nonlinear_readiness({"model_script": str(model)})
    assert "binding_unreadable" in {b["code"] for b in d["blockers"]}
    with pytest.raises(RuntimeError, match="binding_unreadable"):
        _load_gate().gate({"model_script": str(model)})


def test_locked_file_raises_clear_error_not_bare_oserror(tmp_path, monkeypatch):
    model = _project(tmp_path)
    _locked(monkeypatch, CFG)
    with pytest.raises(BindingUnreadableError) as exc:
        current_binding(model)
    assert isinstance(exc.value, RuntimeError) and not isinstance(exc.value, OSError)
    assert CFG in str(exc.value)
    problems = approval_binding_problems(model)
    assert any("unreadable" in p.lower() for p in problems)
    template = tmp_path / "t.json"
    template.write_text("{}", encoding="utf-8")
    with pytest.raises(RuntimeError, match="unreadable"):
        bind_readiness_draft(template, model)

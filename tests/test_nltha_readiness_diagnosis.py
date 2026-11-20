"""Headless tests for the structured NLTHA readiness diagnosis (no tkinter)."""
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.model.readiness import (  # noqa: E402
    READINESS_CHECK_KEYS, diagnose_nonlinear_readiness, record_binding)


def _codes(diag):
    return [b["code"] for b in diag["blockers"]]


def _make(tmp_path, *, manifest=None, material=True, fsam=True, reviewed=True, cfg_in_file=True):
    model = tmp_path / "OpenSees_Complete_Nonlinear_Model.py"
    model.write_text("# model\n", encoding="utf-8")
    if material:
        (tmp_path / "mat.json").write_text("{}", encoding="utf-8")
    cfg = {"nonlinear_materials_file": "mat.json" if material else "",
           "nonlinear_wall_fsam_tags": {"P1": 1} if fsam else {},
           "nonlinear_parameters_reviewed": reviewed}
    (tmp_path / "OpenSees_Complete_Model_Config_V118.json").write_text(json.dumps(cfg), encoding="utf-8")
    rpath = tmp_path / "OpenSees_Model_Readiness_V116.json"
    if manifest is not None:
        rpath.write_text(json.dumps(manifest), encoding="utf-8")
    return model, rpath


def _bound(model, **over):
    data = {"model_script": str(model),
            "model_script_sha256": hashlib.sha256(model.read_bytes()).hexdigest(),
            "approved_for_nltha": False,
            "checks": dict.fromkeys(READINESS_CHECK_KEYS, False)}
    record_binding(data, model)  # current-format manifest; legacy (unbound) cases live in test_nltha_readiness_binding.py
    data.update(over)
    return data


def test_sixteen_keys():
    assert len(READINESS_CHECK_KEYS) == 16


def test_runner_keys_match_constant():
    import ast
    src = (ROOT / "components/nonlinear_time_history/runner_and_gui.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)
              and n.name == "_require_nonlinear_readiness")
    tup = next(n for n in ast.walk(fn) if isinstance(n, ast.Tuple) and n.elts
               and isinstance(n.elts[0], ast.Constant)
               and n.elts[0].value == "etabs_topology_and_story_mapping_reviewed")
    assert tuple(e.value for e in tup.elts) == tuple(READINESS_CHECK_KEYS)


def test_manifest_missing(tmp_path):
    model, _ = _make(tmp_path)
    d = diagnose_nonlinear_readiness({"model_script": str(model)})
    assert d["ready"] is False and "manifest_missing" in _codes(d)


def test_template(tmp_path):
    model, _ = _make(tmp_path, manifest={"model_script": "ABSOLUTE PATH TO model", "checks": {}})
    d = diagnose_nonlinear_readiness({"model_script": str(model)})
    assert d["ready"] is False and "template_unbound" in _codes(d)
    assert all(b["message"] and b["fix"] for b in d["blockers"])


def test_bound_to_other_model(tmp_path):
    model, _ = _make(tmp_path, manifest={"model_script": str(tmp_path / "other.py"), "checks": {}})
    assert "bound_to_other_model" in _codes(diagnose_nonlinear_readiness({"model_script": str(model)}))


def test_sha_mismatch(tmp_path):
    model, _ = _make(tmp_path)
    (tmp_path / "OpenSees_Model_Readiness_V116.json").write_text(
        json.dumps(_bound(model, model_script_sha256="0" * 64)), encoding="utf-8")
    assert "model_sha_mismatch" in _codes(diagnose_nonlinear_readiness({"model_script": str(model)}))


def test_bound_unapproved(tmp_path):
    model, _ = _make(tmp_path)
    (tmp_path / "OpenSees_Model_Readiness_V116.json").write_text(json.dumps(_bound(model)), encoding="utf-8")
    d = diagnose_nonlinear_readiness({"model_script": str(model)})
    codes = _codes(d)
    assert d["ready"] is False
    assert "not_approved" in codes
    assert sum(c.startswith("check_false:") for c in codes) == 16


def test_missing_material_file_and_others(tmp_path):
    model, _ = _make(tmp_path, material=False, fsam=False, reviewed=False)
    (tmp_path / "OpenSees_Model_Readiness_V116.json").write_text(json.dumps(_bound(model)), encoding="utf-8")
    codes = _codes(diagnose_nonlinear_readiness({"model_script": str(model)}))
    assert {"material_file_missing", "wall_fsam_tags_empty", "parameters_not_reviewed"} <= set(codes)


def test_material_file_not_found(tmp_path):
    model, _ = _make(tmp_path)
    (tmp_path / "mat.json").unlink()
    (tmp_path / "OpenSees_Model_Readiness_V116.json").write_text(json.dumps(_bound(model)), encoding="utf-8")
    assert "material_file_not_found" in _codes(diagnose_nonlinear_readiness({"model_script": str(model)}))


def test_all_clear_fixture(tmp_path):
    model, _ = _make(tmp_path)
    data = _bound(model, approved_for_nltha=True, checks=dict.fromkeys(READINESS_CHECK_KEYS, True))
    (tmp_path / "OpenSees_Model_Readiness_V116.json").write_text(json.dumps(data), encoding="utf-8")
    d = diagnose_nonlinear_readiness({"model_script": str(model)})
    assert d == {"ready": True, "blockers": []}


def test_one_false_check_blocks(tmp_path):
    model, _ = _make(tmp_path)
    checks = dict.fromkeys(READINESS_CHECK_KEYS, True)
    checks[READINESS_CHECK_KEYS[3]] = False
    (tmp_path / "OpenSees_Model_Readiness_V116.json").write_text(
        json.dumps(_bound(model, approved_for_nltha=True, checks=checks)), encoding="utf-8")
    d = diagnose_nonlinear_readiness({"model_script": str(model)})
    assert d["ready"] is False and _codes(d) == ["check_false:" + READINESS_CHECK_KEYS[3]]


def _load_gate():
    """Compile only the gate function; the runner module imports tkinter at top level."""
    import ast
    import types
    src = (ROOT / "components/nonlinear_time_history/runner_and_gui.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_require_nonlinear_readiness")
    ns = {"json": json, "Path": Path}
    exec(compile(ast.Module([fn], []), "runner_gate", "exec"), ns)
    return types.SimpleNamespace(_require_nonlinear_readiness=ns["_require_nonlinear_readiness"])


def test_gate_superset_messages_and_raises(tmp_path):
    r = _load_gate()
    model, _ = _make(tmp_path)
    cfg = {"model_script": str(model)}
    with pytest.raises(FileNotFoundError):
        r._require_nonlinear_readiness(cfg)
    rp = tmp_path / "OpenSees_Model_Readiness_V116.json"
    rp.write_text(json.dumps({"model_script": "absolute path to x", "checks": {}}), encoding="utf-8")
    with pytest.raises(RuntimeError, match="uncompleted readiness TEMPLATE") as e:
        r._require_nonlinear_readiness(cfg)
    assert "template_unbound" in str(e.value)
    rp.write_text(json.dumps(_bound(model)), encoding="utf-8")
    with pytest.raises(RuntimeError, match="Nonlinear readiness is not approved") as e:
        r._require_nonlinear_readiness(cfg)
    assert "check_false:" in str(e.value)
    rp.write_text(json.dumps(_bound(model, approved_for_nltha=True, checks=dict.fromkeys(READINESS_CHECK_KEYS, True))), encoding="utf-8")
    assert r._require_nonlinear_readiness(cfg)["check_count"] == 16

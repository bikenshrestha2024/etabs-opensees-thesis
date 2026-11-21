"""Headless tests: the run gate raises on unreviewed nonlinear parameters for approved manifests."""
import ast
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.model.readiness import (  # noqa: E402
    APPROVED_CONTRADICTION_CODES, READINESS_CHECK_KEYS, diagnose_nonlinear_readiness,
    gate_binding_blockers, record_binding)

CFG = "OpenSees_Complete_Model_Config_V118.json"
MAN = "OpenSees_Model_Readiness_V116.json"


def _load_gate():
    """Compile only the gate function; the runner module imports tkinter at top level."""
    src = (ROOT / "components/nonlinear_time_history/runner_and_gui.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)
              and n.name == "_require_nonlinear_readiness")
    ns = {"json": json, "Path": Path}
    exec(compile(ast.Module([fn], []), "runner_gate", "exec"), ns)
    return ns["_require_nonlinear_readiness"]


def _project(tmp_path, *, reviewed, approved=True, bind=True):
    model = tmp_path / "OpenSees_Complete_Nonlinear_Model.py"
    model.write_text("# model\n", encoding="utf-8")
    (tmp_path / "mat.json").write_text('{"fc": 1}', encoding="utf-8")
    cfg = {"nonlinear_materials_file": "mat.json", "nonlinear_wall_fsam_tags": {"P1": 1},
           "nonlinear_parameters_reviewed": reviewed}
    (tmp_path / CFG).write_text(json.dumps(cfg), encoding="utf-8")
    data = {"model_script": str(model),
            "model_script_sha256": hashlib.sha256(model.read_bytes()).hexdigest(),
            "approved_for_nltha": approved,
            "checks": dict.fromkeys(READINESS_CHECK_KEYS, True)}
    if bind:
        record_binding(data, model)
    (tmp_path / MAN).write_text(json.dumps(data), encoding="utf-8")
    return {"model_script": str(model)}, data


DIAG = {"blockers": [{"code": "parameters_not_reviewed", "message": "m", "fix": "f"}]}


def test_constant_includes_parameters_not_reviewed():
    assert "parameters_not_reviewed" in APPROVED_CONTRADICTION_CODES


def test_gate_blockers_include_parameters_not_reviewed_when_approved():
    out = gate_binding_blockers(DIAG, {"approved_for_nltha": True})
    assert [b["code"] for b in out] == ["parameters_not_reviewed"]


def test_gate_blockers_exclude_it_when_unapproved():
    assert gate_binding_blockers(DIAG, {"approved_for_nltha": False}) == []


def test_gate_raises_for_approved_manifest_without_reviewed_parameters(tmp_path):
    config, _ = _project(tmp_path, reviewed=False)
    with pytest.raises(RuntimeError, match="parameters_not_reviewed"):
        _load_gate()(config)


def test_gate_passes_when_parameters_reviewed(tmp_path):
    config, _ = _project(tmp_path, reviewed=True)
    assert _load_gate()(config)["check_count"] == 16


def test_unapproved_manifest_keeps_older_approval_error_first(tmp_path):
    config, _ = _project(tmp_path, reviewed=False, approved=False)
    with pytest.raises(RuntimeError, match="not approved") as exc:
        _load_gate()(config)
    assert "binding check failed" not in str(exc.value)


def test_binding_not_recorded_still_advisory(tmp_path):
    config, data = _project(tmp_path, reviewed=True, bind=False)
    codes = [b["code"] for b in diagnose_nonlinear_readiness(config)["blockers"]]
    assert "binding_not_recorded" in codes
    assert gate_binding_blockers({"blockers": [{"code": "binding_not_recorded", "message": "m", "fix": "f"}]}, data) == []
    assert _load_gate()(config)["check_count"] == 16

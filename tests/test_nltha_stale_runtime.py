"""Headless tests for the stale runtime-copy guard (read-only on real evidence folders)."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.model.readiness import (  # noqa: E402
    ACTIVE_GATE_MODULE_MARKERS, ACTIVE_GATE_RUNNER_MARKERS, READINESS_CHECK_KEYS,
    detect_stale_runtime, diagnose_nonlinear_readiness, record_binding, runtime_copy_notice)

SAVED = ROOT / "Saved_Project_V156"
REAL_RUNTIME = SAVED / "OpenSees_Runtime_V118"
REAL_MODEL = SAVED / "OpenSees_Complete_Nonlinear_Model.py"
CFG = "OpenSees_Complete_Model_Config_V118.json"


def _runtime(root, name="OpenSees_Runtime_V300", runner=None, readiness=None):
    """Synthetic runtime copy. ``None`` = fresh (carries every active marker)."""
    rt = root / name
    (rt / "components/nonlinear_time_history").mkdir(parents=True)
    (rt / "components/model").mkdir(parents=True)
    fresh_runner = "\n".join("# " + m for m in ACTIVE_GATE_RUNNER_MARKERS) + "\n"
    fresh_mod = "\n".join("# " + m for m in ACTIVE_GATE_MODULE_MARKERS) + "\n"
    if runner is not False:
        (rt / "components/nonlinear_time_history/runner_and_gui.py").write_text(
            fresh_runner if runner is None else runner, encoding="utf-8")
    if readiness is not False:
        (rt / "components/model/readiness.py").write_text(
            fresh_mod if readiness is None else readiness, encoding="utf-8")
    return rt


def _snapshot(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob("*")) if p.is_file()}


def test_active_repo_is_not_stale():
    """Self-consistency: the active tree must carry its own fingerprint."""
    for p in (ROOT, ROOT / "components/model/readiness.py", ROOT / "OpenSees_Complete_Nonlinear_Model.py"):
        r = detect_stale_runtime(p)
        assert r["stale"] is False, r


def test_real_saved_runtime_is_stale_and_untouched():
    before = _snapshot(REAL_RUNTIME)
    r = detect_stale_runtime(REAL_RUNTIME)
    assert r["stale"] is True
    assert Path(r["runtime_root"]) == REAL_RUNTIME.resolve()
    assert "runner_lacks_active_gate" in r["reasons"] and "readiness_module_lacks_fingerprint" in r["reasons"]
    r2 = detect_stale_runtime(REAL_RUNTIME / "OpenSees_Complete_Nonlinear_Model.py")  # a model script placed inside
    assert r2["stale"] is True
    assert _snapshot(REAL_RUNTIME) == before
    assert not list(REAL_RUNTIME.glob("STALE*"))


def test_real_model_beside_runtime_only_flagged_with_children():
    assert detect_stale_runtime(REAL_MODEL)["stale"] is False  # not inside the runtime copy
    r = detect_stale_runtime(REAL_MODEL, include_children=True)
    assert r["stale"] is True and Path(r["runtime_root"]) == REAL_RUNTIME.resolve()
    assert "OpenSees_Runtime_V118" in runtime_copy_notice(REAL_MODEL)
    assert runtime_copy_notice(ROOT / "OpenSees_Complete_Nonlinear_Model.py") == ""


def test_fresh_synthetic_runtime_not_stale(tmp_path):
    rt = _runtime(tmp_path)
    r = detect_stale_runtime(rt / "OpenSees_Complete_Nonlinear_Model.py")
    assert r["stale"] is False and r["runtime_root"] == str(rt.resolve()) and r["reasons"] == []


def test_old_runner_is_stale(tmp_path):
    rt = _runtime(tmp_path, runner="def _require_nonlinear_readiness(c):\n    pass\n")
    r = detect_stale_runtime(rt)
    assert r["stale"] is True and r["reasons"] == ["runner_lacks_active_gate"]


def test_pr124_style_runner_without_binding_is_stale(tmp_path):
    old = "\n".join("# " + m for m in ACTIVE_GATE_RUNNER_MARKERS if m != "gate_binding_blockers")
    assert detect_stale_runtime(_runtime(tmp_path, runner=old))["stale"] is True


def test_old_readiness_module_is_stale(tmp_path):
    rt = _runtime(tmp_path, readiness="# nothing\n")
    r = detect_stale_runtime(rt)
    assert r["stale"] is True and r["reasons"] == ["readiness_module_lacks_fingerprint"]


def test_named_runtime_without_gate_sources_is_stale(tmp_path):
    rt = tmp_path / "OpenSees_Runtime_V9"
    rt.mkdir()
    r = detect_stale_runtime(rt / "model.py")
    assert r["stale"] is True
    assert r["reasons"] == ["runner_source_missing", "readiness_module_missing"]


def test_plain_folder_is_not_a_runtime(tmp_path):
    (tmp_path / "m.py").write_text("#", encoding="utf-8")
    r = detect_stale_runtime(tmp_path / "m.py")
    assert r == {"stale": False, "runtime_root": None, "reasons": [], "copies": []}


def test_nearest_runtime_root_wins(tmp_path):
    outer = _runtime(tmp_path, runner="# old\n")
    inner = _runtime(outer / "sub", name="OpenSees_Runtime_V400")
    r = detect_stale_runtime(inner / "x.py")
    assert r["stale"] is False and r["runtime_root"] == str(inner.resolve())


def _bound_manifest(model):
    data = {"model_script": str(model), "model_script_sha256": hashlib.sha256(model.read_bytes()).hexdigest(),
            "approved_for_nltha": True, "checks": dict.fromkeys(READINESS_CHECK_KEYS, True)}
    record_binding(data, model)
    (model.parent / "OpenSees_Model_Readiness_V116.json").write_text(json.dumps(data), encoding="utf-8")


def _model_in(folder):
    folder.mkdir(parents=True, exist_ok=True)
    model = folder / "OpenSees_Complete_Nonlinear_Model.py"
    model.write_text("# m\n", encoding="utf-8")
    (folder / "mat.json").write_text("{}", encoding="utf-8")
    (folder / CFG).write_text(json.dumps({"nonlinear_materials_file": "mat.json",
                                          "nonlinear_wall_fsam_tags": {"P": 1},
                                          "nonlinear_parameters_reviewed": True}), encoding="utf-8")
    _bound_manifest(model)
    return model


def test_diagnosis_adds_stale_runtime_copy_blocker(tmp_path):
    stale = _model_in(_runtime(tmp_path / "a", runner="# old\n") / "proj")
    d = diagnose_nonlinear_readiness({"model_script": str(stale)})
    assert [b["code"] for b in d["blockers"]] == ["stale_runtime_copy"] and d["ready"] is False
    assert d["blockers"][0]["fix"] and "runner_lacks_active_gate" in d["blockers"][0]["message"]
    fresh = _model_in(_runtime(tmp_path / "b") / "proj")
    assert diagnose_nonlinear_readiness({"model_script": str(fresh)}) == {"ready": True, "blockers": []}


def test_diagnosis_without_model_script_or_manifest_still_works(tmp_path):
    model = tmp_path / "m.py"
    model.write_text("#", encoding="utf-8")
    codes = [b["code"] for b in diagnose_nonlinear_readiness({"model_script": str(model)})["blockers"]]
    assert "manifest_missing" in codes and "stale_runtime_copy" not in codes

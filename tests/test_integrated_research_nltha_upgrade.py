"""Headless contract tests; not native ETABS/OpenSees acceptance."""
import json
from pathlib import Path
import pytest
from components.shared import eigen_solver
from components.model.active_model_selection import validate_clear_beam_model
from components.nonlinear_time_history import batch_execution as batch

def test_modal_coverage_stops_when_both_axes_reach_threshold(monkeypatch):
    counts=[]
    def solve(ops,n):
        counts.append(n)
        return [1.0]*n
    monkeypatch.setattr(eigen_solver,"solve_eigen",solve)
    values,report,history=eigen_solver.solve_eigen_until_coverage(
        None,lambda v:{"ninety_percent_both_axes":len(v)>=60})
    assert counts==[40,60]
    assert len(values)==60 and report["ninety_percent_both_axes"]
    assert history==[{"modes":40,"coverage_met":False},{"modes":60,"coverage_met":True}]

def test_modal_coverage_is_bounded(monkeypatch):
    monkeypatch.setattr(eigen_solver,"solve_eigen",lambda ops,n:[1.0]*n)
    values,report,history=eigen_solver.solve_eigen_until_coverage(
        None,lambda v:{"ninety_percent_both_axes":False},initial=40,maximum=65)
    assert len(values)==65 and not report["ninety_percent_both_axes"]
    assert [item["modes"] for item in history]==[40,60,65]

def write_source(source):
    source.mkdir(parents=True)
    for name in batch.REQUIRED_SOURCE_FILES:
        (source/name).write_text("{}",encoding="utf-8")
    return source

def test_clear_beam_selection_requires_correct_source_and_completed_status(tmp_path):
    root=tmp_path/"source"
    selected=write_source(root/"02_MODEL"/"REBUILDS"/"VERIFIED_CLEAR_BEAM"/"one")
    (selected/"CLEAR_BEAM_REBUILD_STATUS.json").write_text(json.dumps({
        "status":"EXPORT_VERIFIED_NOT_GRAVITY_SOLVED","original_source_dir":str(root)}))
    (selected/"OpenSees_Complete_Model_Config_V118.json").write_text(json.dumps({
        "etabs_beam_weight_policy":"ETABS_BEAM_CLEAR_LENGTH",
        "etabs_clear_beam_weight_confirmed":True}))
    result=validate_clear_beam_model(root,selected)
    assert result["folder"]==str(selected)
    assert result["engineering_acceptance"]=="NOT_VERIFIED"
    with pytest.raises(ValueError):validate_clear_beam_model(tmp_path/"different",selected)

def test_batch_jobs_have_unique_destinations_and_detect_changed_source(tmp_path):
    source=write_source(tmp_path/"source")
    x=tmp_path/"x.txt";y=tmp_path/"y.txt";x.write_text("0");y.write_text("1")
    cfg={"model_folder":str(source),"x_path":str(x),"y_path":str(y),
         "orientations":["XY"],"output_dir":str(tmp_path/"previous")}
    a=tmp_path/"a.json";a.write_text(json.dumps(cfg))
    b=tmp_path/"b.json";b.write_text(json.dumps(dict(cfg,orientations=["YX"])))
    plan=tmp_path/"plan.json";plan.write_text(json.dumps({"jobs":[str(a),str(b)]}))
    jobs=batch.prepare_jobs(plan,tmp_path/"new")
    assert len(jobs)==2 and jobs[0]["identity"]!=jobs[1]["identity"]
    assert jobs[0]["config"]["output_dir"]!=jobs[1]["config"]["output_dir"]
    assert all(job["config"]["convergence_tolerance"] == 1e-6 for job in jobs)
    assert all(job["config"]["transient_max_iterations"] == 40 for job in jobs)
    assert all(job["config"]["final_relaxed_tolerance"] is None for job in jobs)
    batch.verify_inputs(jobs[0])
    x.write_text("changed")
    with pytest.raises(ValueError,match="changed"):batch.verify_inputs(jobs[0])

def test_batch_duplicate_and_source_overwrite_rejected(tmp_path):
    source=write_source(tmp_path/"source")
    x=tmp_path/"x.txt";x.write_text("0")
    cfg=tmp_path/"cfg.json";cfg.write_text(json.dumps({
        "model_folder":str(source),"x_path":str(x),"y_path":str(x)}))
    plan=tmp_path/"plan.json";plan.write_text(json.dumps({"jobs":[str(cfg),str(cfg)]}))
    with pytest.raises(ValueError,match="Duplicate"):batch.prepare_jobs(plan,tmp_path/"new")
    with pytest.raises(ValueError,match="overwrite"):batch.prepare_jobs(plan,source)


@pytest.mark.parametrize("strict", [False, True])
def test_batch_job_identity_uses_effective_tolerance(tmp_path, strict):
    source = write_source(tmp_path / "source")
    x = tmp_path / "a.txt"
    y = tmp_path / "b.txt"
    x.write_text("0", encoding="utf-8")
    y.write_text("1", encoding="utf-8")
    config = dict(model_folder=str(source), x_path=str(x), y_path=str(y))
    default = tmp_path / "default.json"
    explicit = tmp_path / "explicit.json"
    default.write_text(json.dumps(config), encoding="utf-8")
    explicit.write_text(json.dumps(dict(config, convergence_tolerance=1e-7 if strict else 1e-6,
                                        final_relaxed_tolerance=None)), encoding="utf-8")
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"jobs": [default.name, explicit.name]}), encoding="utf-8")
    if strict:
        jobs = batch.prepare_jobs(plan, tmp_path / "runs")
        assert [job["config"]["convergence_tolerance"] for job in jobs] == [1e-6, 1e-7]
        assert jobs[0]["identity"] != jobs[1]["identity"]
    else:
        with pytest.raises(ValueError, match="Duplicate batch job"):
            batch.prepare_jobs(plan, tmp_path / "runs")


def test_batch_rejects_invalid_tolerance_before_accessing_model_inputs(tmp_path):
    config = tmp_path / "invalid.json"
    config.write_text(json.dumps({"convergence_tolerance": 1e-4}), encoding="utf-8")
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"jobs": [config.name]}), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid.json.*convergence_tolerance"):
        batch.prepare_jobs(plan, tmp_path / "runs")

"""Bounded independent NLTHA process scheduler; no shared OpenSees domain.

Run from repository root: python -m components.nonlinear_time_history.batch_execution
--plan PLAN.json --output NEW_DIRECTORY --workers 2
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

from components.nonlinear_time_history.source_model_handoff import (
    REQUIRED_SOURCE_FILES, OPTIONAL_SOURCE_FILES, required_source_files, source_sha256,
)

def prepare_jobs(plan_path, output):
    """Bind unique research jobs to their source inputs. [REF docs/source/components/nonlinear_time_history/batch_execution.py.md]"""
    from components.nonlinear_time_history.thesis_quality import validate_convergence_settings

    plan_path=Path(plan_path).resolve()
    output=Path(output).resolve()
    plan=json.loads(plan_path.read_text(encoding="utf-8-sig"))
    entries=plan.get("jobs")
    if not isinstance(entries,list) or not entries:
        raise ValueError("Plan must have a nonempty jobs list of configuration JSON paths")
    seen=set()
    jobs=[]
    for index,entry in enumerate(entries,1):
        if not isinstance(entry,str) or not entry.strip():
            raise ValueError("Each jobs entry must be a configuration JSON path")
        path=(plan_path.parent/entry).resolve()
        cfg=json.loads(path.read_text(encoding="utf-8-sig"))
        if cfg.get("analysis_intent")=="THESIS_NLTHA":
            raise ValueError("This scheduler is for exploratory research jobs only")
        try:
            tolerance, max_iterations, final_tolerance = validate_convergence_settings(cfg)
        except ValueError as exc:
            raise ValueError(f"Invalid convergence settings in {path.name}: {exc}") from exc
        cfg.update(convergence_tolerance=tolerance, transient_max_iterations=max_iterations,
                   final_relaxed_tolerance=final_tolerance)
        for key in ("model_folder","x_path","y_path"):
            value=Path(cfg[key]).expanduser()
            if not value.is_absolute():
                raise ValueError("Configuration paths must be absolute: "+key)
        source=required_source_files(cfg["model_folder"])
        if output==source or output in source.parents:
            raise ValueError("Batch output cannot contain or overwrite a source model")
        inputs={name:source_sha256(source/name) for name in REQUIRED_SOURCE_FILES}
        inputs.update({name:source_sha256(source/name) for name in OPTIONAL_SOURCE_FILES
                       if (source/name).is_file()})
        for key in ("x_path","y_path"):
            inputs[key]=source_sha256(cfg[key])
        for key in ("approved_frame_reinforcement_csv","wall_openings_manifest"):
            if cfg.get(key):
                if not Path(cfg[key]).is_absolute():
                    raise ValueError("Configuration paths must be absolute: "+key)
                inputs[key]=source_sha256(cfg[key])
        model_hash=inputs["OpenSees_Complete_Model_Data_V118.json"]
        if cfg.get("expected_model_sha256") not in (None,model_hash):
            raise ValueError("Model differs from previously bound configuration: "+str(path))
        cfg["expected_model_sha256"]=model_hash
        cfg.pop("output_dir",None)
        identity=hashlib.sha256(json.dumps({"config":cfg,"inputs":inputs},
                       sort_keys=True,allow_nan=False).encode("utf-8")).hexdigest()
        if identity in seen:
            raise ValueError("Duplicate batch job: "+str(path))
        seen.add(identity)
        dest=output/("%04d_%s"%(index,identity[:12]))
        cfg["output_dir"]=str(dest)
        jobs.append(dict(id=dest.name,config=cfg,inputs=inputs,identity=identity,
                         source_config=str(path),status="QUEUED"))
    return jobs

def verify_inputs(job):
    """Reject changed job input hashes before launch. [REF components/nonlinear_time_history/source_model_handoff.py]"""
    cfg=job["config"]; source=Path(cfg["model_folder"])
    for name,expected in job["inputs"].items():
        path=Path(cfg[name]) if name in ("x_path","y_path","approved_frame_reinforcement_csv","wall_openings_manifest") else source/name
        if source_sha256(path)!=expected:
            raise ValueError("Batch input changed before launch: "+str(path))

def execute_batch(plan_path, output, workers=1):
    """Run independent exploratory processes with bounded workers. [REF docs/source/components/nonlinear_time_history/batch_execution.py.md]"""
    if type(workers) is not int or not 1<=workers<=4:
        raise ValueError("workers must be an integer from 1 to 4")
    output=Path(output).resolve()
    jobs=prepare_jobs(plan_path,output)
    output.mkdir(parents=True,exist_ok=False)
    root=Path(__file__).resolve().parents[2]
    runner=root/"OpenSees_Building_Exploratory_V138.py"
    pending=list(jobs); active={}
    def save():
        target=output/"Batch_Status.json"
        temporary=output/"Batch_Status.tmp"
        temporary.write_text(json.dumps({"scope":"RESEARCH_ONLY","workers":workers,
            "jobs":jobs},indent=2,allow_nan=False),encoding="utf-8")
        temporary.replace(target)
    save()
    try:
        while pending or active:
            if (output/'STOP_REQUESTED').is_file():
                break
            while pending and len(active)<workers:
                if (output/'STOP_REQUESTED').is_file():
                    break
                job=pending.pop(0)
                try:
                    verify_inputs(job)
                    dest=Path(job["config"]["output_dir"]);dest.mkdir(exist_ok=False)
                    cfgpath=dest/"Requested_Config.json"
                    cfgpath.write_text(json.dumps(job["config"],indent=2),encoding="utf-8")
                    log=(dest/"Run.log").open("w",encoding="utf-8")
                    try:
                        proc=subprocess.Popen([sys.executable,"-u",str(runner),"--config",str(cfgpath)],
                            cwd=str(root),stdout=log,stderr=subprocess.STDOUT)
                    except BaseException:
                        log.close();raise
                    active[job["id"]]=(proc,log,job)
                    job.update(status="RUNNING",pid=proc.pid)
                except Exception as exc:
                    job.update(status="START_FAILED",error=str(exc))
                save()
            for key,(proc,log,job) in list(active.items()):
                code=proc.poll()
                if code is None:continue
                log.close();del active[key]
                cfg=job["config"];dest=Path(cfg["output_dir"])
                name=("Material_Sensitivity_Summary.json" if cfg.get("sensitivity_parameter")
                      else "Research_Batch_Summary_V161.json" if cfg.get("limit_state")=="Both"
                      else "Exploratory_Summary.json")
                summary=dest/name
                job.update(exit_code=code,summary=str(summary),
                    status="PROCESS_COMPLETED_REVIEW_REQUIRED" if code==0 and summary.is_file()
                    else "INCOMPLETE")
                save()
            if active:time.sleep(.5)
    finally:
        for proc,log,job in active.values():
            if proc.poll() is None:
                proc.terminate()
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill();proc.wait()
            log.close();job.update(status="INTERRUPTED",exit_code=proc.returncode)
        for job in pending:job["status"]="NOT_STARTED"
        save()
    return jobs

def main():
    """Expose the research batch CLI. [REF docs/source/components/nonlinear_time_history/batch_execution.py.md]"""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--workers",type=int,default=1)
    args=parser.parse_args()
    jobs=execute_batch(args.plan,args.output,args.workers)
    return 0 if all(j["status"]=="PROCESS_COMPLETED_REVIEW_REQUIRED" for j in jobs) else 1

if __name__=="__main__":
    raise SystemExit(main())

"""Isolated native OpenSeesPy recorder/energy diagnostic for FVD and BRB.

Usage: python 29_NATIVE_DEVICE_BENCHMARK.py --output D:/Thesis/Device_Benchmark
Runs only with a working native OpenSeesPy binary; no simulated PASS fallback.
Units: kN, m, s. Parameter profiles are illustrative, NOT a published measured
device nor thesis building selection.

OpenSees refs:
https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/TwoNodeLink.html
https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/CorotationalTruss.html
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import platform
import sys
import traceback
from pathlib import Path

from components.sections.devices import (
    define_fvd_material, add_fvd_link, define_brb_core_material,
    add_brb_corot_truss,
)

def _vector(raw):
    if raw is None:return []
    if isinstance(raw,(float,int)):return [float(raw)]
    return [float(v) for v in raw]

def _query(ops,element,response):
    try:
        values=_vector(ops.eleResponse(element,response))
        return dict(response=response,values=values,
                    supported=bool(values) and all(math.isfinite(x) for x in values))
    except Exception as exc:
        return dict(response=response,values=[],supported=False,error=str(exc))

def _case(ops,kind,out,*,dt=0.002,duration=2.0):
    """Build the model from scratch, run 2s of dynamic harmonic forcing."""
    ops.wipe()
    ops.model("basic","-ndm",3,"-ndf",6)
    ops.node(1,0,0,0)
    ops.node(2,1,0,0)
    ops.fix(1,1,1,1,1,1,1)
    ops.fix(2,0,1,1,1,1,1)
    ops.mass(2,1.0,1e-12,1e-12,1e-12,1e-12,1e-12)
    if kind=="FVD":
        # Illustrative only. Spring K [kN/m]; Cd [kN (s/m)^alpha].
        params=define_fvd_material(ops,material_tag=10,K=2000.0,Cd=20.0,alpha=0.3)
        add_fvd_link(ops,element_tag=20,i_node=1,j_node=2,material_tag=10,do_rayleigh=False)
        amplitude=10.0
        queries=("basicForce","basicDisplacement","localForce",
                 "material 1 stressStrain")
    else:
        params=define_brb_core_material(ops,material_tag=10,Fy=350000.,E0=200000000.,
                    b=.01,R0=20.,cR1=.925,cR2=.15,
                    a1=0.,a2=1.,a3=0.,a4=1.)
        add_brb_corot_truss(ops,element_tag=20,i_node=1,j_node=2,
                            core_area=0.001,material_tag=10)
        amplitude=400.0
        queries=("axialForce","deformations","material 1 stressStrain")
    n=int(round(duration/dt))
    if n<10:raise ValueError("Too few integration points")
    force=[amplitude*math.sin(2*math.pi*1.0*i*dt) for i in range(n+1)]
    ops.timeSeries("Path",100,"-dt",dt,"-values",*force)
    ops.pattern("Plain",100,100)
    ops.load(2,1.,0.,0.,0.,0.,0.)
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr",1e-8,50)
    ops.algorithm("Newton")
    ops.integrator("Newmark",.5,.25)
    ops.analysis("Transient")
    rows=[]
    response_names=[s.split()[0] for s in queries]
    last_accepted=0.0
    for step in range(n):
        rc=int(ops.analyze(1,dt))
        if rc!=0:
            return {"status":"FAILED_NATIVE_STEP","kind":kind,"step":step+1,
                    "last_accepted_time_s":last_accepted,
                    "return_code":rc,"rows":len(rows),
                    "source_parameters":params}
        last_accepted=float(ops.getTime())
        r={"time_s":last_accepted,
           "displacement_m":float(ops.nodeDisp(2,1)),
           "velocity_m_s":float(ops.nodeVel(2,1)),
           "applied_force_kN":amplitude*math.sin(2*math.pi*last_accepted)}
        checks={}
        for name in queries:
            response=name.split()
            key=name.replace(" ","_")
            q=_query(ops,20,response[0]) if len(response)==1 else (
                 _query(ops,20,response[0]))
            checks[key]=q
            if q["supported"] and len(q["values"])==1:
                r[key+"_value"]=q["values"][0]
            else:
                r[key+"_value"]=None
        rows.append(r)
    out.mkdir(parents=True,exist_ok=True)
    csv_path=out/(kind+"_Accepted_History.csv")
    with csv_path.open("w",newline="",encoding="utf-8") as handle:
        w=csv.DictWriter(handle,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    required="basicForce_value" if kind=="FVD" else "axialForce_value"
    support=all(r[required] is not None for r in rows)
    if not support:
        return {"status":"RECORDER_UNSUPPORTED","kind":kind,
                "history_csv":str(csv_path),"source_parameters":params}
    # F/u mechanical integral: orientation and force sign have NOT been certified.
    signed_power=sum(.5*(rows[i-1][required]*rows[i-1]["velocity_m_s"]+
                          rows[i][required]*rows[i]["velocity_m_s"])*
                      (rows[i]["time_s"]-rows[i-1]["time_s"])
                      for i in range(1,len(rows)))
    return {"status":"NATIVE_COMPLETED_RECORDER_OBSERVED",
            "kind":kind,"history_csv":str(csv_path),
            "source_parameters":params,"samples":len(rows),
            "max_abs_force_kN":max(abs(r[required]) for r in rows),
            "max_abs_stroke_m":max(abs(r["displacement_m"]) for r in rows),
            "signed_internal_force_velocity_work_kNm":signed_power,
            "raw_force_orientation":"UNVERIFIED",
            "energy_sign_verified":False,
            "damper_model_calibrated_to_experiment":False,
            "brb_fatigue_qualified":False,
            "warning":"Recorder availability verified only for this native binary. Check basicDisplacement, resisting action and energy balance separately."}

def main(argv=None):
    arg=argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--output",type=Path,required=True)
    opts=arg.parse_args(argv)
    out=opts.output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    report={"status":"NATIVE_NOT_RUN","python":sys.version,"platform":platform.platform(),
            "units":"kN-m-s","cases":[],"device_parameters":"ILLUSTRATIVE_NOT_CALIBRATED"}
    try:
        import openseespy.opensees as ops
        report["native_version"]=str(ops.version())
        for kind in ("FVD","BRB"):
            try:
                report["cases"].append(_case(ops,kind,out/kind))
            finally:
                ops.wipe()
        report["status"]="NATIVE_EXECUTED_REVIEW_REQUIRED"
    except Exception as exc:
        report["status"]="FAILED_OR_NATIVE_UNAVAILABLE"
        report["error_type"]=type(exc).__name__
        report["error"]=str(exc)
        report["traceback"]=traceback.format_exc()
    finally:
        (out/"Native_Device_Benchmark_Report.json").write_text(
            json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    print(json.dumps({"status":report["status"],
                      "report":str(out/"Native_Device_Benchmark_Report.json")},indent=2))
    return 0 if report["status"]=="NATIVE_EXECUTED_REVIEW_REQUIRED" else 2

if __name__=="__main__":
    raise SystemExit(main())

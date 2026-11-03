"""Audit native recorder time alignment and signed device work; not physical validation."""
import argparse
import json
import math
from pathlib import Path

def numeric(path):
    if not path.is_file():raise FileNotFoundError(path)
    data=[[float(v) for v in line.split()] for line in path.read_text().splitlines() if line.strip()]
    if len(data)<50 or any(len(row)!=2 or any(not math.isfinite(x) for x in row) for row in data):
        raise ValueError("Invalid native scalar response: "+str(path))
    if any(b[0]<=a[0] for a,b in zip(data,data[1:])):
        raise ValueError("Non-monotonic native response times")
    return data

def check_case(folder,kind):
    f=numeric(folder/("basicForce.out" if kind=="FVD" else "axialForce.out"))
    u=numeric(folder/"u.out");v=numeric(folder/"v.out")
    if not len(f)==len(u)==len(v):raise ValueError("Native recorder lengths differ")
    if any(abs(a[0]-b[0])>1e-8 or abs(a[0]-c[0])>1e-8 for a,b,c in zip(f,u,v)):
        raise ValueError("Native recorder time axes differ")
    work=sum(.5*(f[i-1][1]*v[i-1][1]+f[i][1]*v[i][1])*(f[i][0]-f[i-1][0])
             for i in range(1,len(f)))
    out=dict(kind=kind,native_recorder_format_passed=True,samples=len(f),
             end_time_s=f[-1][0],signed_force_velocity_work_kNm=work,
             force_sign_verified=False,experimental_calibration=False)
    if kind=="FVD":
        b=numeric(folder/"basicDisplacement.out")
        if len(b)!=len(u):raise ValueError("FVD basicDisplacement sample mismatch")
        out["basic_vs_node_displacement_error_m"]=max(abs(x[1]-y[1]) for x,y in zip(b,u))
    else:
        de=numeric(folder/"deformations.out")
        if len(de)!=len(u):raise ValueError("BRB deformation sample mismatch")
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("folder",type=Path)
    args=ap.parse_args()
    items=[check_case(args.folder/name,name) for name in ("FVD","BRB")]
    report=dict(status="NATIVE_TCL_RECORDER_SCREEN_PASSED",cases=items,
         scope="Native Tcl conda-forge OpenSees only; Windows OpenSeesPy and experimental qualification not established")
    (args.folder/"Native_Recorder_Evidence.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()

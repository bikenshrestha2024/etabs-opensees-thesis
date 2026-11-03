"""Calibrate Maxwell FVD parameters from *measured* force/displacement histories.

Requires a real experimental CSV with time_s, displacement_m, force_kN
and optional velocity_m_s. Uses SciPy from conda-forge and a serial Maxwell
spring+power-law dashpot ODE in kN-m-s units. No paper example data are
fabricated; output is never labeled experimental validation automatically.

Run:
 python 30_CALIBRATE_FVD_FROM_TEST.py measured.csv --output D:/Thesis/FVD_Fit
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import sys
import traceback
from pathlib import Path

COLUMNS=("time_s","displacement_m","force_kN")

def read_experiment(path):
    p=Path(path)
    if not p.is_file():raise FileNotFoundError(p)
    with p.open(encoding="utf-8-sig",newline="") as file:
        reader=csv.DictReader(file)
        if not reader.fieldnames or any(c not in reader.fieldnames for c in COLUMNS):
            raise ValueError("Measured CSV needs time_s, displacement_m, force_kN")
        rows=list(reader)
    if len(rows)<40:
        raise ValueError("At least 40 measured samples needed for a documented fit")
    keys=COLUMNS+ (("velocity_m_s",) if "velocity_m_s" in reader.fieldnames else ())
    data={k:[] for k in keys}
    for i,row in enumerate(rows):
        for key in keys:
            v=float(row[key])
            if not math.isfinite(v):
                raise ValueError(f"Nonfinite measured {key} at row {i}")
            data[key].append(v)
    t=data["time_s"]
    if abs(t[0])>1e-6 or any(b<=a for a,b in zip(t,t[1:])):
        raise ValueError("Time must begin at 0 and strictly increase")
    if max(data["displacement_m"])-min(data["displacement_m"])<1e-8:
        raise ValueError("Displacement excitation too small to calibrate")
    if max(data["force_kN"])-min(data["force_kN"])<1e-6:
        raise ValueError("Measured cyclic force range too small")
    return data

def maxwell_force(time_s, velocity_m_s, initial_force, K, Cd, alpha):
    """Solve dF/dt = K(v - sign(F)*(abs(F)/Cd)^(1/alpha)).

    F is the internal axial force in the same adopted positive-elongation
    convention as displacement. The sign of the measured load-cell force
    may be opposite and is checked as a separate fit orientation.
    """
    import numpy as np
    from scipy.integrate import solve_ivp
    t=np.asarray(time_s,dtype=float)
    vel=np.asarray(velocity_m_s,dtype=float)
    if not all(math.isfinite(x) and x>0 for x in (K,Cd,alpha)) or alpha>1:
        raise ValueError("Invalid Maxwell parameters")
    def rate(time,force):
        v=np.interp(time,t,vel)
        f=float(force[0])
        v_dash=math.copysign((abs(f)/Cd)**(1.0/alpha),f) if f else 0.0
        return [K*(v-v_dash)]
    result=solve_ivp(rate,(float(t[0]),float(t[-1])),[float(initial_force)],
                     t_eval=t,method="Radau",rtol=1e-5,atol=1e-7)
    if not result.success or result.y.shape[1]!=len(t):
        raise RuntimeError("Maxwell ODE did not solve: "+str(result.message))
    return result.y[0]

def fit_measured_fvd(data,train_fraction=0.75):
    """Fit actual experimental data; preserve held-out comparison evidence."""
    import numpy as np
    from scipy.optimize import least_squares
    t=np.asarray(data["time_s"],dtype=float)
    u=np.asarray(data["displacement_m"],dtype=float)
    fm=np.asarray(data["force_kN"],dtype=float)
    v=np.asarray(data.get("velocity_m_s",np.gradient(u,t)),dtype=float)
    if not 0.5<=train_fraction<=0.85:
        raise ValueError("Training fraction must be 0.50 through 0.85")
    if any(not np.isfinite(x) for x in v):
        raise ValueError("Nonfinite derived velocity")
    n=len(t)
    cutoff=max(20,int(n*train_fraction))
    # Reference scale protects parameters from unrealistic unbounded values;
    # values are numerical fit bounds, NOT experimentally established priors.
    displacement_scale=max(float(np.ptp(u)),1e-6)
    force_scale=max(float(np.max(np.abs(fm))),1e-5)
    velocity_scale=max(float(np.max(np.abs(v))),1e-5)
    stiffness_scale=force_scale/displacement_scale
    coeff_scale=force_scale/max(velocity_scale**0.5,1e-5)
    def params(x):
        return float(np.exp(x[0])),float(np.exp(x[1])),float(x[2])
    best=None
    for sign in (1.,-1.):
        f=sign*fm
        def residual(x):
            try:
                K,Cd,alpha=params(x)
                pred=maxwell_force(t[:cutoff],v[:cutoff],f[0],K,Cd,alpha)
                return (pred-f[:cutoff])/force_scale
            except (ValueError,RuntimeError,OverflowError):
                return np.full(cutoff,1e8)
        start=np.array([math.log(stiffness_scale),math.log(coeff_scale),.5])
        low=np.array([math.log(max(stiffness_scale*1e-5,1e-6)),
                      math.log(max(coeff_scale*1e-5,1e-8)),.05])
        high=np.array([math.log(max(stiffness_scale*1e5,1e-4)),
                       math.log(max(coeff_scale*1e5,1e-6)),1.])
        try:
            solution=least_squares(residual,start,bounds=(low,high),
                                   max_nfev=120,ftol=1e-5,xtol=1e-5)
            K,Cd,alpha=params(solution.x)
            modeled=maxwell_force(t,v,f[0],K,Cd,alpha)
            error=modeled-f
            train_rmse=float(np.sqrt(np.mean(error[:cutoff]**2)))
            holdout_rmse=float(np.sqrt(np.mean(error[cutoff:]**2)))
            candidate=dict(K_kN_m=K,Cd_kN_s_per_m_power_alpha=Cd,
                           alpha=alpha,load_cell_sign_to_internal=int(sign),
                           train_rmse_kN=train_rmse,holdout_rmse_kN=holdout_rmse,
                           fitted_series=modeled.tolist(),nfev=int(solution.nfev),
                           optimizer_success=bool(solution.success))
            if best is None or candidate["holdout_rmse_kN"]<best["holdout_rmse_kN"]:
                best=candidate
        except (ValueError,RuntimeError,OverflowError):
            continue
    if best is None:raise RuntimeError("No converged candidate Maxwell fit")
    return dict(status="MEASURED_DATA_FITTED_NOT_INDEPENDENTLY_VALIDATED",
                n_samples=n,train_points=cutoff,holdout_points=n-cutoff,
                measured_velocity_column="velocity_m_s" in data,
                **best,notes=[
                    "Train/holdout portions are from the same test; independent device validation requires a different cycle/specimen.",
                    "Check instrument force orientation and load-cell zero drift.",
                    "Maxwell spring K must represent both device and brace/connection axial stiffness as modeled.",
                    "Do not assign fitted parameters to the building before source/geometry/stroke qualification."])

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("measured_csv",type=Path)
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args(argv)
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    report=dict(status="NOT_RUN",source=str(args.measured_csv.resolve()),
                model="Maxwell_ViscousDamper",valid_for_building=False)
    try:
        data=read_experiment(args.measured_csv)
        report.update(fit_measured_fvd(data))
        report["source_sha256"]=hashlib.sha256(args.measured_csv.read_bytes()).hexdigest()
        curve=out/"FVD_Measured_vs_Maxwell.csv"
        with curve.open("w",newline="",encoding="utf-8") as f:
            w=csv.writer(f)
            w.writerow(["time_s","measured_force_kN","simulated_internal_force_kN",
                        "measured_displacement_m"])
            for i,time in enumerate(data["time_s"]):
                w.writerow([time,data["force_kN"][i],
                            report["fitted_series"][i],data["displacement_m"][i]])
        report["comparison_csv"]=str(curve)
        del report["fitted_series"]
    except Exception as exc:
        report.update(status="FAILED",error=str(exc),
                      error_type=type(exc).__name__,
                      traceback=traceback.format_exc())
    (out/"FVD_Calibration_Report.json").write_text(
        json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    print(json.dumps(dict(status=report["status"],report=str(out/"FVD_Calibration_Report.json")),indent=2))
    return 0 if report["status"]=="MEASURED_DATA_FITTED_NOT_INDEPENDENTLY_VALIDATED" else 2

if __name__=="__main__":
    raise SystemExit(main())

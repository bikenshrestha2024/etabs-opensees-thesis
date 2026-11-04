"""Pair-specific NBC 105:2025 source-spectrum check (no accelerogram mutation).

Usage: python 32_NBC105_PAIR_SPECTRUM_AUDIT.py --x recordX.AT2 --y recordY.AT2
    --soil C --Z 0.45 --I 1.0 --omega-u 1.5 --r-mu 4
    --t1-x 3.6 --t1-y 3.2 --tn-x .15 --tn-y .12 --output audit.json

All numbers in this example are illustrative. Replace with project inputs.
"""
import argparse
import json
from pathlib import Path
from components.response_spectrum.nbc_pair_spectrum_audit import write_pair_audit

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("x","y","output"):
        p.add_argument("--"+name,required=True)
    p.add_argument("--soil",required=True)
    for dest in ("Z","I","omega_u","r_mu","t1_x","t1_y","tn_x","tn_y"):
        p.add_argument("--"+dest.replace("_","-"),type=float,required=True,dest=dest)
    a=p.parse_args()
    report=write_pair_audit(Path(a.output),a.x,a.y,soil_type=a.soil,Z=a.Z,I=a.I,
      omega_u=a.omega_u,R_mu=a.r_mu,t1_x_s=a.t1_x,t1_y_s=a.t1_y,
      tn90_x_s=a.tn_x,tn90_y_s=a.tn_y)
    print(json.dumps(dict(status=report["status"],shared_pair_scale=
          report["shared_scale_both_components"],output=a.output),indent=2))
    return 0 if report["both_component_factors_in_code_range"] else 2

if __name__=="__main__":raise SystemExit(main())

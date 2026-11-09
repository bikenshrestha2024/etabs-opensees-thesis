# -*- coding: utf-8 -*-
"""Spyder CLI: run isolated, opt-in source-bound EQ PDelta tangent diagnostic.

Usage from repository root:
python tools/OPENSEES_EQ_PDELTA_TANGENT_DIAGNOSTIC.py --source-dir "..." --force-csv "..." --support-table "..." --axis X --out-dir "..."

This launches OpenSeesPy only, never ETABS. Do not use on the production
NLTHA domain or replace the gravity 32-support diagnostic evidence.
"""
from __future__ import annotations
import argparse
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from components.model.eq_pdelta_initial_tangent import (
    run_source_equivalent_initial_and_tangent)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-dir",required=True)
    parser.add_argument("--force-csv",required=True)
    parser.add_argument("--support-table",required=True)
    parser.add_argument("--axis",required=True,choices=("X","Y"))
    parser.add_argument("--out-dir",required=True)
    args=parser.parse_args()
    root=Path(args.out_dir).expanduser().resolve()
    output=root/("OPENSEES_"+args.axis+"_PDELTA_TANGENT_"+
                 datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    try:
        result=run_source_equivalent_initial_and_tangent(
            args.source_dir,args.force_csv,args.support_table,args.axis,
            output)
        print("SOURCE-BOUND TANGENT DIAGNOSTIC",result["axis"])
        print("BASE SHEAR",result["dependent_linear_increment"]["signed_base_shear_kN"],"kN")
        print("ROOF DELTA",result["dependent_linear_increment"]["roof_displacement_increment_m"],"m")
        print("SIGNED FORCE ERROR",result["dependent_linear_increment"]["signed_equilibrium_error_percent"],"%")
        print("EVIDENCE",output)
        print("NOT a native ETABS, wall section-cut or NLTHA acceptance result")
    except Exception:
        output.mkdir(parents=True,exist_ok=True)
        (output/"EQ_PDelta_Diagnostic_Failure.log").write_text(
            traceback.format_exc(),encoding="utf-8")
        raise

if __name__=="__main__":
    main()

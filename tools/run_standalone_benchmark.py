# -*- coding: utf-8 -*-
"""Windows/Spyder-compatible no-ETABS minimal OpenSees example.

From project root: python tools/run_standalone_benchmark.py --out OUTPUT_FOLDER
Only validates a 2-node elastic benchmark, NOT any M0–M6 thesis model.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from src.thesis_core.neutral_model import cantilever_example
from src.opensees_engine.standalone import run_standalone,axial_cantilever_check

def main(out):
    folder=Path(out).expanduser().resolve()
    folder.mkdir(parents=True,exist_ok=True)
    model=cantilever_example()
    (folder/"standalone_input.json").write_text(json.dumps(model,indent=2),encoding="utf-8")
    report=run_standalone(model)
    report["independent_analytic_check"]=axial_cantilever_check(model,report)
    report["overall"]="BENCHMARK_PASS_ONLY" if report["independent_analytic_check"]["pass"] else "BENCHMARK_FAIL"
    (folder/"standalone_results.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(report["overall"],"outputs",folder)
    if not report["independent_analytic_check"]["pass"]:
        raise RuntimeError("Analytical cantilever check failed")
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="standalone_benchmark_output")
    args=parser.parse_args();main(args.out)

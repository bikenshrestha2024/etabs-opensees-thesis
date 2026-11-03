"""Stage 06 M0-M6 outrigger comparison, research evidence only.

python 27_COMPARE_OUTRIGGERS.py "D:/Thesis/M0_M6_Comparison_Manifest.json"
"""
import argparse
import json
from pathlib import Path
from components.nonlinear_time_history.variant_comparison import load_case_manifest

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest",type=Path)
    parser.add_argument("--output",type=Path)
    opts=parser.parse_args(argv)
    result=load_case_manifest(opts.manifest)
    target=opts.output or opts.manifest.parent/"M0_M6_Research_Comparison.json"
    if target.resolve()==opts.manifest.resolve():
        raise ValueError("Output cannot overwrite the input manifest")
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,allow_nan=False),encoding="utf-8")
    print(json.dumps({"status":result["status"],"cases":result["paired_case_keys"],
                      "output":str(target)},indent=2))
    return result
if __name__=="__main__":main()

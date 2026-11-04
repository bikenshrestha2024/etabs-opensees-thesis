"""NBC 105:2025 §4.3 applicability and XY/YX command documentation.

This is a report launcher only; does not run the actual earthquake model.
"""
import argparse
import json
from pathlib import Path
from components.nonlinear_time_history.nbc105_horizontal_input import vertical_acceleration_review

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("features_json",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    data=json.loads(a.features_json.read_text(encoding="utf-8-sig"))
    report=vertical_acceleration_review(data)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    print(json.dumps(report,indent=2))
    return 0 if report["status"]=="NO_CLAUSE_4_3_TRIGGER_DECLARED_REVIEW_REQUIRED" else 2
if __name__=="__main__":raise SystemExit(main())

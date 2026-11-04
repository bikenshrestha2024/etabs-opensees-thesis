"""35: Soil-C 8-pair NLTHA preflight (read-only; DOES NOT run OpenSees).

Examples:
python 35_SOIL_C_NLTHA_PREFLIGHT.py --matched-dir "D:/Thesis/Records/Matched" --output "D:/Thesis/Audits/soil_c_inputs.json"
python 35_SOIL_C_NLTHA_PREFLIGHT.py --matched-dir "D:/Thesis/Records/Matched" --output "D:/Thesis/Audits/soil_c_inputs.json" --t1-x 2.8 --t1-y 3.1 --tn90-x 0.12 --tn90-y 0.13 --analysis-dt 0.005

Example modal periods are NOT the building's accepted periods.
"""
import argparse
import json
from components.nonlinear_time_history.soil_c_nltha_suite import write_suite_report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--matched-dir",required=True)
    p.add_argument("--output",required=True)
    for key in ("t1-x","t1-y","tn90-x","tn90-y","analysis-dt"):
        p.add_argument("--"+key,dest=key.replace("-","_"),type=float)
    a=p.parse_args()
    result=write_suite_report(a.output,a.matched_dir,
          t1_x_s=a.t1_x,t1_y_s=a.t1_y,
          tn90_x_s=a.tn90_x,tn90_y_s=a.tn90_y,
          analysis_dt_s=a.analysis_dt)
    print(json.dumps({
       "status":result["status"],
       "pairs":result["pair_count"],
       "matched_source_errors":len(result["component_source_failures"]),
       "timing_review":result["timing_policy_review_required"],
       "modal_screen":result["current_modal_period_screen"]["status"],
       "report":a.output,
    },indent=2))
    return 2 if result["component_source_failures"] else 3 if result[
      "timing_policy_review_required"] else 0

if __name__=="__main__":
    raise SystemExit(main())

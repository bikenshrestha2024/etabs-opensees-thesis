"""Generate separate reproducible NLTHA diagnostic probe configs or review saved outcomes.

Usage:
  python 21_NLTHA_TRIAGE.py --config existing_RunConfig.json --output D:/NLTHA_Probes
  python 21_NLTHA_TRIAGE.py --review D:/NLTHA_Probes

Run each generated config separately with the V168 exploratory nonlinear runner.
This script does NOT start a solver or silently overwrite earlier runs.
"""
import argparse
import json
from pathlib import Path
from components.nonlinear_time_history.thesis_quality import (
    generate_isolation_configs, review_isolation_runs,
)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--review", type=Path)
    args = parser.parse_args(argv)
    if args.review is not None:
        result = review_isolation_runs(args.review)
        print(json.dumps(result, indent=2))
        return result
    if args.config is None or args.output is None:
        parser.error("Supply --config and --output, or supply --review")
    source = json.loads(args.config.read_text(encoding="utf-8-sig"))
    paths = generate_isolation_configs(source, args.output)
    print(json.dumps({"status": "CONFIGS_CREATED_ONLY", "probe_files": paths,
                      "instruction": "Run each probe through the exploratory runner in a fresh model. No analysis was run."}, indent=2))
    return paths

if __name__ == "__main__":
    main()

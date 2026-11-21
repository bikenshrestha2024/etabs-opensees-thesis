"""Command-line entrypoint for all ten independent NBC 105 modules.

python -m components.nbc105 --list
python -m components.nbc105 --clause 10 --operation component_amplification_factor \
    --json '{"building_period_s":1.0,"component_period_s":1.25}'
No file upload, network connection, ETABS side effect or automatic certification.
"""
from __future__ import annotations
import argparse
import json
import sys
from components.nbc105.dispatch import available_operations, run_operation

def main(argv=None):
    """[REF NBC105-2025 Clauses 1–10; docs/nbc105/README.md]"""
    parser=argparse.ArgumentParser(description="NBC 105:2025 clause-by-clause calculation interface")
    parser.add_argument("--list",action="store_true",help="List exported public operations")
    parser.add_argument("--clause",type=int,help="1–10")
    parser.add_argument("--operation",help="Exported operation name")
    parser.add_argument("--json",default="{}",help="JSON mapping of named parameters")
    args=parser.parse_args(argv)
    try:
        if args.list:
            result=available_operations()
        else:
            if args.clause is None or not args.operation:
                parser.error("--clause and --operation required without --list")
            payload=json.loads(args.json)
            result=run_operation(args.clause,args.operation,payload)
        print(json.dumps(result,indent=2,sort_keys=True,allow_nan=False))
        return 0
    except (ValueError,TypeError,KeyError) as exc:
        print(f"NBC calculation blocked: {exc}",file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())

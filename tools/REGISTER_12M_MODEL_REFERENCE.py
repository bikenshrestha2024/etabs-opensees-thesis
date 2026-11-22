"""[REF docs/source/tools/REGISTER_12M_MODEL_REFERENCE.py.md]
Opt-in local-only validation of the current 12m ETABS workbook reference.
Does not copy, upload or edit the selected workbook or EDB.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))


def main(argv=None):
    """[REF docs/source/tools/REGISTER_12M_MODEL_REFERENCE.py.md]
    Register only after verifying source EDB bytes and 2 x 12m wall layout.
    """
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild-dir",type=Path,required=True)
    parser.add_argument("--current-workbook",type=Path,required=True)
    parser.add_argument("--state",choices=("ULS","SLS"),required=True)
    args=parser.parse_args(argv)
    from components.inputs.model_aligned_reference import register_reference
    evidence=register_reference(args.rebuild_dir,args.current_workbook,
                                limit_state=args.state)
    print("REGISTERED SOURCE-IDENTIFIED REFERENCE, NOT NBC OR ETABS ACCEPTANCE")
    print("Current workbook SHA256:",evidence["workbook_sha256"])
    print("Source EDB SHA256:",evidence["source_edb_sha256"])
    print("Current exported wall verification:",
          evidence["wall_geometry_verification"]["classification"])
    print("Reference only; original XLSX and EDB left unchanged.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())

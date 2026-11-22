"""[REF docs/source/tools/REGISTER_CURRENT_ETABS_TABLES.py.md]
Register current ULS ETABS workbook evidence locally without moving files.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))


def main(argv=None):
    """[REF docs/source/tools/REGISTER_CURRENT_ETABS_TABLES.py.md]
    Record exact SHA256 source identity, not approval of analytical results.
    """
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-root",type=Path,required=True)
    parser.add_argument("--analysis",type=Path,required=True)
    for i in (1,2,3):
        parser.add_argument(f"--beam-{i}",type=Path)
    parser.add_argument("--beam-files",type=Path,nargs="+",
                        help="All ETABS Element Forces - Beams Excel parts (any count)")
    parser.add_argument("--select-beams",action="store_true",
                        help="Open multi-select Excel file picker for all beam-force parts")
    parser.add_argument("--native-assignment",type=Path)
    args=parser.parse_args(argv)
    explicit=[p for p in (args.beam_1,args.beam_2,args.beam_3) if p is not None]
    if args.beam_files and explicit:
        parser.error("Use --beam-files OR --beam-1/2/3, not both")
    if args.select_beams and (args.beam_files or explicit):
        parser.error("Use --select-beams OR explicit beam paths, not both")
    if args.select_beams:
        from tkinter import Tk, filedialog
        window=Tk()
        window.withdraw()
        try:
            chosen=filedialog.askopenfilenames(
                title="Select ALL ETABS Element Forces - Beams Excel files",
                filetypes=[("Excel workbooks","*.xlsx *.xlsm")])
        finally:
            window.destroy()
        beams=[Path(p) for p in chosen]
    else:
        beams=list(args.beam_files or explicit)
    if not beams:
        parser.error("Select one or more beam-force workbooks")
    if explicit and len(explicit)!=3:
        parser.error("Legacy --beam-1/2/3 requires all three; use --beam-files for any count")
    from components.inputs.etabs_table_bundle import register_current_etabs_tables
    dest,meta=register_current_etabs_tables(
        args.export_root,args.analysis,beams,
        assignment=args.native_assignment)
    print("Local source registry:",dest)
    print("ETABS EDB SHA256:",meta["source_edb_sha256"])
    for role,entry in meta["source_workbook_inventory"].items():
        print(role,entry["sha256"],len(entry["sheets"]),"sheets")
    print("REGISTERED EXACT FILES — numerical ETABS validation pending")
    return 0


if __name__=="__main__":
    raise SystemExit(main())

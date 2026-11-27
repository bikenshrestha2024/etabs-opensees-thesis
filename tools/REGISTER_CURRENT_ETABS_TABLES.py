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
    parser.add_argument("--export-root",type=Path)
    parser.add_argument("--analysis",type=Path)
    parser.add_argument("--analysis-files",type=Path,nargs="+",
                        help="Read ALL worksheets of explicitly selected analysis lots (audit only)")
    parser.add_argument("--audit-output",type=Path,
                        help="New private local JSON audit output; required with --analysis-files")
    for i in (1,2,3):
        parser.add_argument(f"--beam-{i}",type=Path)
    parser.add_argument("--beam-files",type=Path,nargs="+",
                        help="All ETABS Element Forces - Beams Excel parts (any count)")
    parser.add_argument("--select-beams",action="store_true",
                        help="Open multi-select Excel file picker for all beam-force parts")
    parser.add_argument("--native-assignment",type=Path)
    args=parser.parse_args(argv)
    if args.analysis_files:
        if (not args.audit_output or args.analysis or args.export_root or args.native_assignment
                or args.select_beams or args.beam_files or any((args.beam_1,args.beam_2,args.beam_3))):
            parser.error("Audit mode: use --analysis-files LOT1 LOT2 ... --audit-output NEW.private.json only")
        target=args.audit_output.expanduser().resolve()
        if target.exists() or not target.name.endswith(".private.json"):
            parser.error("Audit output must be a new .private.json file")
        from components.inputs.etabs_table_bundle import audit_analysis_workbooks
        from components.inputs.output_contract import atomic_json
        result=audit_analysis_workbooks(args.analysis_files,progress=lambda s:print(s,flush=True))
        atomic_json(target,result)
        print(result["status"],result["fully_scanned_worksheets"],"/",result["worksheet_count"],"worksheets")
        print("Private audit:",target)
        return 0 if result["status"]=="ALL_WORKSHEETS_SCANNED_NOT_ENGINEERING_VALIDATION" else 2
    if not args.export_root or not args.analysis or args.audit_output:
        parser.error("Registration requires --export-root and --analysis; audit mode uses --analysis-files")
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

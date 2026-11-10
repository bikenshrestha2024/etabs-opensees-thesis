# -*- coding: utf-8 -*-
"""Rebuild verified clear-length gravity source in a NEW directory.

No ETABS EDB write, no in-place mutation, no solver, no implicit code PASS.
Run in Spyder with no arguments to choose source/workbook/output via GUI.
CLI with all three explicit arguments still works for reproducible batch use.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

REQUIRED_SHEETS=(
    "Material List by Object Type",
    "Material List by Section Prop",
    "Frame Assigns - Summary",
    "Frame Assigns - End Len Offsets",
    "Frame Assigns - Insertion Point",
    "Area Assigns - Insertion Point",
    "Load Pattern Definitions",
    "Shell Uniform Load Sets",
)
SOURCE_REQUIRED_FILES=(
    "OpenSees_Element_Connectivity.json",
    "OpenSees_Section_Assignment_Audit.json",
    "OpenSees_Load_Conversion_Audit.json",
    "OpenSees_Source_Model_Metadata_V118.json",
    "OpenSees_Complete_Model_Config_V118.json",
)


def _verify_before_creating_output(source, workbook, target):
    """Fail closed before creating an output folder or changing source files."""
    source=Path(source).expanduser().resolve()
    workbook=Path(workbook).expanduser().resolve()
    target=Path(target).expanduser().resolve()
    if not source.is_dir():
        raise FileNotFoundError(
            "Source must be the FOLDER containing the existing OpenSees "
            "export JSON and OpenSees_Complete_Gravity_Model.py: "+str(source))
    if not workbook.is_file() or workbook.suffix.lower() not in (".xlsx",".xlsm"):
        raise FileNotFoundError(
            "Select an ORIGINAL ETABS full-assignment Excel workbook (.xlsx/.xlsm); "
            "not the NBC calculation or gravity-results workbook: "+str(workbook))
    if target.exists():
        raise FileExistsError("Refusing to overwrite existing destination: "+str(target))
    if target==source or source in target.parents:
        raise ValueError("Destination must NOT be within the original source export")
    if not target.parent.is_dir():
        raise FileNotFoundError("Selected output parent does not exist: "+str(target.parent))
    missing=[str(source/name) for name in SOURCE_REQUIRED_FILES
             if not (source/name).is_file()]
    if missing:
        raise FileNotFoundError(
            "Selected source is NOT a complete export; missing:\n"+
            "\n".join(missing)+
            "\nSelect the folder containing OpenSees_Element_Connectivity.json.")
    # The original ETA BS Material List and beam offset tables are required,
    # not just an arbitrary workbook with ETABS in its filename.
    from openpyxl import load_workbook
    book=load_workbook(workbook,read_only=True,data_only=True)
    try:
        missing_sheets=[s for s in REQUIRED_SHEETS if s not in book.sheetnames]
    finally:
        book.close()
    if missing_sheets:
        raise ValueError(
            "Workbook does not contain the native ETABS assignment evidence. "
            "Missing sheets: "+", ".join(missing_sheets)+
            ". Export the full model tables from ETABS, including Material List, "
            "Frame Assignments and End Length Offsets.")
    # Reading the source config is a prerequisite; no policy is applied to
    # the source. The new folder is generated from an independent copied file.
    config=json.loads(
        (source/"OpenSees_Complete_Model_Config_V118.json").read_text(
            encoding="utf-8-sig"))
    if not isinstance(config,dict):
        raise ValueError("Source model config must be a JSON object")
    if config.get("joint_volume_weight_policy") not in ("AUDIT_ONLY",None):
        raise ValueError(
            "Source uses a different joint-volume ownership policy; avoid "
            "double beam overlap subtraction. Review it before rebuilding.")
    return source,workbook,target


def _choose_in_spyder():
    """A no-argument interactive path; never runs ETABS or the gravity solver."""
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
    except ImportError as exc:
        raise RuntimeError(
            "Tkinter GUI unavailable; run with --source-dir, "
            "--assignment-workbook and --dest-dir.") from exc
    root=tk.Tk()
    root.withdraw()
    try:
        messagebox.showinfo(
            "Verified clear-beam source rebuild",
            "1. Select the ORIGINAL source-export FOLDER containing the "
            "OpenSees_Element_Connectivity.json file.\n"
            "2. Select the original FULL ETABS native assignment workbook "
            "(Material List, Frame Summary and End Offsets).\n"
            "3. Choose a parent output folder. A NEW timestamped folder "
            "will be created.\n\n"
            "No EDB will be saved, no existing model overwritten, "
            "and gravity will NOT be run.",parent=root)
        source=filedialog.askdirectory(
            parent=root,title="Step 1/3 — Source folder containing ETABS export JSON")
        if not source:return None
        workbook=filedialog.askopenfilename(
            parent=root,title="Step 2/3 — Original full ETABS assignment XLSX",
            filetypes=[("Original ETABS assignment workbook","*.xlsx *.xlsm"),
                       ("All files","*.*")])
        if not workbook:return None
        parent=filedialog.askdirectory(
            parent=root,title="Step 3/3 — Parent directory for NEW corrected export")
        if not parent:return None
        name="Verified_Clear_Beam_"+datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return (source,workbook,str(Path(parent)/name))
    finally:
        root.destroy()


def _resolve_inputs(argv=None):
    parser=argparse.ArgumentParser(
        description="Spyder: run with no arguments to open three selection "
        "dialogs; CLI: provide ALL three flags.")
    parser.add_argument("--source-dir",default=None)
    parser.add_argument("--assignment-workbook",default=None)
    parser.add_argument("--dest-dir",default=None)
    args=parser.parse_args(argv)
    supplied=(args.source_dir,args.assignment_workbook,args.dest_dir)
    if all(supplied):
        return supplied
    if any(supplied):
        parser.error("Provide ALL three flags together; no mixing CLI and dialogs.")
    return _choose_in_spyder()


def main(argv=None):
    selection=_resolve_inputs(argv)
    if selection is None:
        print("[CANCELLED] No files changed; no gravity model generated.",flush=True)
        return None
    source,workbook,target=selection
    print("[START] Source: "+str(Path(source).resolve()),flush=True)
    print("[START] Workbook: "+Path(workbook).name,flush=True)
    print("[START] New export: "+str(Path(target).resolve()),flush=True)
    try:
        result=rebuild_verified_clear_beam(source,workbook,target)
    except Exception as exc:
        print("[BLOCKED] "+type(exc).__name__+": "+str(exc),flush=True)
        print("Original ETABS model and source export remain unchanged.",flush=True)
        raise
    print("[FINISHED] Verified clear-beam SOURCE export generated.",flush=True)
    print("[PENDING] 32-support gravity solver NOT RUN; ETABS reaction "
          "agreement NOT VALIDATED.",flush=True)
    print("[NEXT] In gravity GUI choose the NEW "
          "OpenSees_Complete_Gravity_Model.py under:\n"+str(Path(target).resolve()),
          flush=True)
    print("[EVIDENCE] "+str(Path(target).resolve()/
                          "CLEAR_BEAM_REBUILD_STATUS.json"),flush=True)
    return result


def rebuild_verified_clear_beam(source_dir, native_assignment_workbook, destination_dir):
    source,native,target=_verify_before_creating_output(
        source_dir,native_assignment_workbook,destination_dir)
    print("[RUNNING] Preflight source JSON and native ETABS Excel tables verified.",
          flush=True)
    target.mkdir(parents=True,exist_ok=False)
    print('[RUNNING] New destination created; copying original source evidence.',flush=True)
    copied=[]
    audit={"status":"REBUILD_RUNNING","original_source_dir":str(source),
           "original_assignment_workbook":native.name,
           "original_assignment_sha256":digest(native),
           "created_utc":datetime.now(timezone.utc).isoformat(),
           "files":[],"new_export_directory":str(target)}
    statusfile=target/"CLEAR_BEAM_REBUILD_STATUS.json"
    def write_status():
        statusfile.write_text(json.dumps(audit,indent=2,default=str),encoding="utf-8")
    write_status()
    try:
        # Only top-level source evidence, not stale model/solver outputs.
        ignored=("OpenSees_Complete_Model_Data_V118.json",
                 "OpenSees_Complete_Export_Report_V118.json",
                 "OpenSees_Complete_Model_Config_V118.json")
        for file in source.iterdir():
            if not file.is_file() or file.suffix.lower() not in (".json",".csv",".xlsx"):
                continue
            if file.name in ignored or file.name.startswith("Gravity_"):
                continue
            # Never copy EDB, executable, or original material workbook bytes.
            to=target/file.name
            shutil.copy2(file,to)
            copied.append(file.name)
            audit["files"].append({"name":file.name,"sha256":digest(to)})
        cfg=json.loads((source/"OpenSees_Complete_Model_Config_V118.json").read_text(encoding="utf-8-sig"))
        if cfg.get("joint_volume_weight_policy") not in ("AUDIT_ONLY",None):
            raise ValueError("Single-owner physical volume changes must be independently reviewed")
        cfg["etabs_beam_weight_policy"]="ETABS_BEAM_CLEAR_LENGTH"
        cfg["etabs_clear_beam_weight_confirmed"]=True
        cfg["joint_volume_weight_policy"]="AUDIT_ONLY"
        cfg["etabs_native_assignment_workbook_path"]=str(native)
        (target/"OpenSees_Complete_Model_Config_V118.json").write_text(
            json.dumps(cfg,indent=2,default=str),encoding="utf-8")
        audit["status"]="ASSEMBLING_VERIFIED_CORRECTED_EXPORT"
        write_status()
        print("[RUNNING] Native beam-ID/offset audit and new OpenSees assembly.",flush=True)
        from components.model.assembly import prepare_complete_export
        result=prepare_complete_export(target,runtime_dir=ROOT)
        report_file=target/"OpenSees_Complete_Export_Report_V118.json"
        report=json.loads(report_file.read_text(encoding="utf-8-sig"))
        if report.get("assembly_errors"):
            raise RuntimeError("Re-export errors: "+repr(report["assembly_errors"]))
        proof=target/"ETABS_Native_Assignment_Gravity_Quantity_Audit.json"
        if not proof.is_file():raise RuntimeError("Native ETABS quantity proof missing after assembly")
        record=json.loads(proof.read_text(encoding="utf-8-sig"))
        if (record.get("opensees_beam_crosswalk_status")!="SOURCE_IDS_OFFSETS_AND_TOTAL_MATCH"
                or record.get("clear_candidate_matches_native_quantity") is not True):
            raise RuntimeError("Native ETABS beam IDs/offsets/weight not confirmed")
        beam=json.loads((target/"ETABS_OpenSees_Beam_Weight_Reconciliation.json").read_text(encoding="utf-8-sig"))
        if beam.get("policy")!="ETABS_BEAM_CLEAR_LENGTH":
            raise RuntimeError("Export remains gross beam weight after rebuild")
        native_weight=float(record["beam_weight_kN"])
        actual_weight=float(beam["selected_beam_weight_kN"])
        if abs(actual_weight-native_weight)>0.1:
            raise RuntimeError(f"Corrected beam weight {actual_weight} differs from ETABS {native_weight} kN")
        audit["status"]="EXPORT_VERIFIED_NOT_GRAVITY_SOLVED"
        audit["selected_beam_weight_kN"]=actual_weight
        audit["native_etabs_beam_weight_kN"]=native_weight
        audit["beam_count"]=record["native_beam_objects"]
        audit["result"]=str(result)
        audit["gravity_state"]="NOT_RUN"
        audit["individual_32_reactions"]="NOT_VALIDATED"
        write_status()
        return audit
    except Exception as exc:
        audit["status"]="BLOCKED"
        audit["error"]=type(exc).__name__+": "+str(exc)
        write_status()
        raise

if __name__=="__main__":
    main()

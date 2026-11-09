# -*- coding: utf-8 -*-
"""Rebuild verified clear-length gravity source in a NEW directory.

No ETABS EDB write, no in-place mutation, no solver, no implicit code PASS.
Run in Spyder as script with arguments or from Anaconda Prompt.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def rebuild_verified_clear_beam(source_dir, native_assignment_workbook, destination_dir):
    source=Path(source_dir).resolve()
    native=Path(native_assignment_workbook).resolve()
    target=Path(destination_dir).resolve()
    if not source.is_dir() or not native.is_file():
        raise FileNotFoundError("Source export directory and original ETABS assignment workbook are required")
    if target.exists() or source==target or source in target.parents and source.name==target.name:
        raise FileExistsError("Target must be a brand-new directory; never overwrite gravity/NLTHA source data")
    required=("OpenSees_Element_Connectivity.json",
              "OpenSees_Section_Assignment_Audit.json",
              "OpenSees_Load_Conversion_Audit.json",
              "OpenSees_Source_Model_Metadata_V118.json",
              "OpenSees_Complete_Model_Config_V118.json")
    for name in required:
        if not (source/name).is_file():
            raise FileNotFoundError("Original ETABS source export missing "+name)
    target.mkdir(parents=True,exist_ok=False)
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
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-dir",required=True)
    parser.add_argument("--assignment-workbook",required=True)
    parser.add_argument("--dest-dir",required=True)
    args=parser.parse_args()
    result=rebuild_verified_clear_beam(
        args.source_dir,args.assignment_workbook,args.dest_dir)
    print(json.dumps(result,indent=2))

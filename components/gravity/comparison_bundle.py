"""Package existing gravity evidence for reproducible ETABS vs OpenSees comparison.

READ ONLY on source files. Does not launch ETABS/OpenSees or infer missing values.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import zipfile

SELECTED = (
    "OpenSees_Complete_Export_Report_V118.json",
    "OpenSees_Complete_Model_Config_V118.json",
    "ETABS_OpenSees_Beam_Weight_Reconciliation.json",
    "ETABS_OpenSees_Beam_Weight_Reconciliation.csv",
    "ETABS_Frame_End_Offset_Weight_Audit.csv",
    "Gravity_Single_Count_Self_Weight_Audit.json",
    "OpenSees_Joint_Volume_Ownership_Audit.json",
    "OpenSees_Joint_Volume_Ownership_Audit.csv",
    "OpenSees_Complete_Model_Data_V118.json",
    "OpenSees_Load_Conversion_Audit.json",
    "LOAD_PATH_AND_DIAPHRAGM_AUDIT_V130.json",
    "Gravity_Storey_Load_Breakdown_V131.csv",
    "Gravity_Source_Load_Detail_V131.csv",
    "Gravity_Profile_ULS.json",
    "Gravity_Profile_SLS.json",
    "OpenSees_Complete_Gravity_Check_V118.json",
    "Gravity_Beam_End_Actions_ULS_V141.csv",
    "Gravity_Beam_End_Actions_SLS_V141.csv",
)
EXTRA = ("ETABS_Nonzero_Reaction_Support_Audit.json",
         "Primary_32_ETABS_OpenSees_Reactions.xlsx",
         "Primary_32_ETABS_OpenSees_Reactions.csv",
         "Primary_32_ETABS_OpenSees_Reactions.json",
         "Gravity_Source_Components_Audit.xlsx",
         "Gravity_Source_Components_Audit.json",
         "Gravity_Source_Components_Detail.csv",
         "Gravity_Source_Components_Totals.csv",
         "Gravity_Result_V110.json", "Gravity_Run_V110.log",
         "Gravity_Results_V110.xlsx", "Gravity_GUI_Actions.log",
         "Gravity_Run_V110.py")

# These exports represent actual gravity responses and review diagnostics.
# A file not present is reported in the manifest, never manufactured.
SOURCE_EXTRA = (
    "Linear_Shell_Stiffness_Audit.json",
    "GRAVITY_SAFE_REVIEW.json",
    "CANDIDATE_PROVENANCE.json",
    "ISOLATED_CANDIDATE_PROVENANCE.json",
    "ETABS_Beam_Material_List_Reviewed.csv",
    "Slab_Load_Path_Formulas_V141.xlsx",
    "OpenSees_Element_Connectivity.json",
    "OpenSees_Source_Model_Metadata_V118.json",
    "OpenSees_Complete_Gravity_Model.py",
    "OpenSees_ID_and_Support_Audit.xlsx",
    "OpenSees_ID_Lookup.html",
    "OpenSees_Structural_Elements_By_Storey.html",
    "OpenSees_Element_Connectivity_3D.html",
    "OpenSees_Property_Element_Load_Audit_V125.xlsx",
)
DIRECT_EXTRA = (
    "ETABS_Native_Analysis_Logs",
    "ETABS_OpenSees_Direct_Gravity_Comparison.xlsx",
    "ETABS_Gravity_Extraction.log",
    "ETABS_Gravity_Extraction_Events.jsonl",
    "Direct_Gravity_Comparison.json",
    "ETABS_Base_Reactions.csv",
    "ETABS_Fixed_Support_Reactions.csv",
    "ETABS_Support_Displacements.csv",
    "Gravity_Node_Reaction_Comparison.json",
    "Gravity_All_Support_Nodes.csv",
    "Gravity_Top_Node_Discrepancies.csv",
    "Gravity_Node_Reaction_Comparison.xlsx",
    "etabs_gravity.json",
)
DUAL_FILES = (
    "Gravity_Source_Components_Audit.xlsx",
    "Gravity_Source_Components_Audit.json",
    "Gravity_Source_Components_Detail.csv",
    "Gravity_Source_Components_Totals.csv",
    "Gravity_Result_V110.json",
    "Gravity_Run_V110.log",
    "Gravity_Run_V110.py",
    "Gravity_Results_V110.xlsx",
)
DUAL_COMPARE_FILES = (
    "Gravity_Wall_Base_Strategy_Comparison.json",
    "Gravity_Wall_Base_Strategy_Comparison.xlsx",
    "Gravity_Wall_Base_Nodal_Reaction_Differences.csv",
)
OFFLINE_FILES = (
    "ETABS_OpenSees_Offline_Comparison.xlsx",
    "ETABS_OpenSees_Offline_Comparison.json",
    "ETABS_OpenSees_Offline_Comparison.csv",
)
NODE_COLS = ("tag","x_m","y_m","z_m","ux_m","uy_m","uz_m","rx_rad","ry_rad","rz_rad")
REACT_COLS = ("node_tag","rx_kN","ry_kN","rz_kN")
FORCE_COLS = ("tag","N_i_kN","Vy_i_kN","Vz_i_kN","T_i_kNm","My_i_kNm","Mz_i_kNm",
              "N_j_kN","Vy_j_kN","Vz_j_kN","T_j_kNm","My_j_kNm","Mz_j_kNm")

def digest(path):
    """Compute source SHA256 without changing it.

    [REF docs/review/GRAVITY_ETABS_COMPARISON.md] Source identity requirement.
    """
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""):
            h.update(part)
    return h.hexdigest()

def _csv(path, rows, cols):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore")
        w.writeheader();w.writerows(rows)

def _safe_relative(path, root):
    return path.resolve().is_relative_to(root.resolve())

def export_bundle(export_dir, gravity_dir, output_dir, *, etabs_json=None,
                  max_file_mb=40, dual_run_dir=None, comparison_root=None):
    """Save an uploadable ZIP and an uncompressed evidence folder.

    [REF docs/review/GRAVITY_ETABS_COMPARISON.md] Required same-model case evidence.
    [REF components/validation/etabs_comparison.py collect] No inferred equality.
    Mandatory field presence is audited; absent ETABS results remain MISSING.
    Model and limit-state comparison must be reviewed independently.
    """
    export_dir=Path(export_dir).expanduser().resolve()
    gravity_dir=Path(gravity_dir).expanduser().resolve()
    output_dir=Path(output_dir).expanduser().resolve()
    comparison_root=Path(comparison_root).expanduser().resolve() if comparison_root else gravity_dir
    if not export_dir.is_dir() or not gravity_dir.is_dir():
        raise FileNotFoundError("Select existing ETABS-export and OpenSees gravity-result directories")
    if output_dir in (export_dir,gravity_dir):
        raise ValueError("Use a dedicated comparison output subfolder, not the source root")
    if not output_dir.is_relative_to(export_dir) and not output_dir.is_relative_to(gravity_dir):
        # Other output locations (e.g. D:/Thesis/Gravity_Comparison) are permitted.
        pass
    if not isinstance(max_file_mb,(int,float)) or max_file_mb<=0:
        raise ValueError("max_file_mb must be positive")
    result=gravity_dir/"Gravity_Result_V110.json"
    if not result.is_file():
        raise FileNotFoundError("OpenSees gravity result missing: "+str(result))
    payload=json.loads(result.read_text(encoding="utf-8-sig"))
    if not isinstance(payload,dict):
        raise ValueError("Gravity_Result_V110.json must contain a JSON object")
    if not payload.get("ok"):
        raise ValueError("Gravity result does not report a successful solver run; preserve failure log separately")
    if dual_run_dir is not None:
        dual_run_dir=Path(dual_run_dir).expanduser().resolve()
        if not dual_run_dir.is_dir():
            raise FileNotFoundError("Dual-run folder missing: "+str(dual_run_dir))
    if etabs_json is not None:
        etabs_json=Path(etabs_json).expanduser().resolve()
        if not etabs_json.is_file() or etabs_json.suffix.lower()!=".json":
            raise FileNotFoundError("Selected ETABS result JSON missing")
        # Prevent importing an unrelated arbitrary source file through guesswork.
        doc=json.loads(etabs_json.read_text(encoding="utf-8-sig"))
        if not isinstance(doc,dict):
            raise ValueError("ETABS JSON must be an object")
    # Build in staging area; existing bundle is never overwritten by failed exports.
    output_dir.mkdir(parents=True,exist_ok=True)
    # Keep previous evidence immutable; choose one unused revision for BOTH
    # extracted folder and upload ZIP. Do not overwrite or reuse old data.
    base_name="Gravity_ETABS_OpenSees_Evidence"
    bundle_name=base_name
    rev=1
    while (output_dir/bundle_name).exists() or (output_dir/(bundle_name+".zip")).exists():
        rev+=1
        bundle_name=base_name+f"_V{rev:02d}"
    dest=output_dir/bundle_name
    files=[];missing=[];oversize=[]
    with tempfile.TemporaryDirectory(prefix="gravity_bundle_",dir=output_dir) as tmp:
        stage=Path(tmp)/bundle_name
        stage.mkdir()
        def add(src,arc,required=False):
            src=Path(src)
            if not src.is_file():
                missing.append({"file":arc,"required":required})
                return False
            if src.stat().st_size>max_file_mb*1024*1024:
                # A full model-data or ID-mapping JSON can be highly
                # compressible. Try a *lossless* nested ZIP before dropping
                # source evidence on the per-file size limit.
                essential={
                    "source/OpenSees_Complete_Model_Data_V118.json",
                    "source/OpenSees_Element_Connectivity.json",
                    "source/OpenSees_Source_Model_Metadata_V118.json",
                }
                if arc in essential:
                    nested_arc="source/compressed_originals/"+src.name+".zip"
                    compressed=stage/nested_arc
                    compressed.parent.mkdir(parents=True,exist_ok=True)
                    with zipfile.ZipFile(compressed,"w",
                        compression=zipfile.ZIP_DEFLATED,
                        compresslevel=6) as container:
                        container.write(src,arcname=src.name)
                    if compressed.stat().st_size<=max_file_mb*1024*1024:
                        files.append({"file":nested_arc,"source":str(src),
                                      "bytes":compressed.stat().st_size,
                                      "original_bytes":src.stat().st_size,
                                      "original_sha256":digest(src),
                                      "representation":"LOSSLESS_NESTED_ZIP"})
                        return True
                    compressed.unlink()
                oversize.append({"file":arc,"size_bytes":src.stat().st_size,
                                 "sha256":digest(src),"original_path":str(src),
                                 "reason":"Source exceeds maximum size even after optional lossless compression"})
                return False
            target=stage/arc
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(src,target)
            files.append({"file":arc,"source":str(src),"bytes":src.stat().st_size,
                          "sha256":digest(src)})
            return True
        for name in SELECTED+SOURCE_EXTRA:
            add(export_dir/name,"source/"+name)
        for name in EXTRA:
            # The central root log is included separately; a dual run has
            # no reason to have another copy inside each case subfolder.
            if name=="Gravity_GUI_Actions.log" and comparison_root!=gravity_dir:
                continue
            add(gravity_dir/name,"opensees/"+name,required=name=="Gravity_Result_V110.json")
        if comparison_root != gravity_dir:
            add(comparison_root/"Gravity_GUI_Actions.log",
                "gravity_workflow/Gravity_GUI_Actions.log")
            # Keep a separately executed single gravity run for provenance
            # rather than replacing it with a newer dual-support run.
            for name in EXTRA:
                if name!="Gravity_GUI_Actions.log" and (comparison_root/name).is_file():
                    add(comparison_root/name,"single_run_root/"+name)
            for candidate in sorted(comparison_root.iterdir()):
                if candidate.is_file() and candidate.name.startswith("Gravity_") and (
                    candidate.suffix.lower() in (".png",".pdf",".svg")):
                    add(candidate,"single_run_root/figures/"+candidate.name)
        # Existing gravity figures and failure diagnostics are carried over
        # without allowing unbounded recursive ingestion of model exports.
        for candidate in sorted(gravity_dir.iterdir()):
            if candidate.is_file() and (
                (candidate.suffix.lower() in (".pdf",".png",".svg") and
                 candidate.name.startswith("Gravity_")) or
                candidate.name.startswith("Gravity_Failure_Diagnostics_")):
                add(candidate,"opensees/figures_and_diagnostics/"+candidate.name)
        response=gravity_dir/"Gravity_Response"
        if response.is_dir():
            for candidate in sorted(response.rglob("*")):
                if candidate.is_file():
                    add(candidate,"opensees/Gravity_Response/"+candidate.relative_to(response).as_posix())
        if dual_run_dir is not None:
            for mode in ("ETABS_SOURCE_SUPPORTS","CONTINUOUS_WALL_BASE_FIXED"):
                case=dual_run_dir/mode
                for name in DUAL_FILES:
                    add(case/name,"wall_base_comparison/"+mode+"/"+name,
                        required=name=="Gravity_Result_V110.json")
                if case.is_dir():
                    for candidate in sorted(case.iterdir()):
                        if candidate.is_file() and candidate.name.startswith("Gravity_") and (
                            candidate.suffix.lower() in (".png",".pdf",".svg")):
                            add(candidate,"wall_base_comparison/"+mode+"/figures/"+candidate.name)
            for name in DUAL_COMPARE_FILES:
                add(dual_run_dir/name,"wall_base_comparison/"+name,required=True)
            offline=dual_run_dir/"ETABS_Full_Table_Offline_Comparison"
            if offline.is_dir():
                for candidate in sorted(offline.rglob("*")):
                    if candidate.is_file():
                        add(candidate,"offline_etabs/"+candidate.relative_to(offline).as_posix())
            else:
                missing.append({"file":"offline_etabs/","required":False,
                                "reason":"Offline ETABS comparison not run"})

        # Direct ETABS extraction is saved beside the OpenSees gravity output.
        # Include current comparison evidence in the same archive when present.
        direct=comparison_root/"Gravity_ETABS_OpenSees_Direct"
        for name in ("OpenSees_Applied_Nodal_Gravity_By_Pattern.csv",
                     "OpenSees_Applied_Nodal_Gravity_Summary.json",
                     "Gravity_Node_Reaction_Comparison.json",
                     "Gravity_All_Support_Nodes.csv",
                     "Gravity_All_Model_Nodes.csv",
                     "Gravity_Top_Node_Discrepancies.csv",
                     "Gravity_Node_Reaction_Comparison.xlsx",
                     "ETABS_Gravity_Extraction.log",
                     "ETABS_Gravity_Extraction_Events.jsonl",
                     "Direct_Gravity_Comparison.json",
                     "ETABS_Base_Reactions.csv",
                     "ETABS_Fixed_Support_Reactions.csv",
                     "ETABS_Support_Displacements.csv",
                     "ETABS_OpenSees_Direct_Gravity_Comparison.xlsx"):
            if direct.is_dir():
                add(direct/name,"direct_comparison/"+name)
        if direct.is_dir():
            native=direct/"ETABS_Native_Analysis_Logs"
            if native.is_dir():
                for candidate in sorted(native.rglob("*")):
                    if candidate.is_file():
                        add(candidate,"direct_comparison/native_analysis_logs/"+
                            candidate.relative_to(native).as_posix())
        if etabs_json is None and (direct/"etabs_gravity.json").is_file():
            etabs_json=direct/"etabs_gravity.json"

        # Always export the OpenSees applied nodal load ledger even when
        # the live ETABS API comparison is unavailable. This uses the exact
        # source patterns, not inferred loads from support reactions.
        try:
            from components.validation.gravity_node_comparison import export_opensees_applied_nodal_loads
            summary=export_opensees_applied_nodal_loads(
                export_dir/"OpenSees_Complete_Model_Data_V118.json",
                stage/"opensees")
        except (FileNotFoundError,ValueError,KeyError,TypeError) as exc:
            missing.append({"file":"opensees/OpenSees_Applied_Nodal_Gravity_By_Pattern.csv",
                            "required":False,"reason":str(exc)})
        if etabs_json:
            add(etabs_json,"etabs/etabs_gravity.json",required=True)
        else:
            missing.append({"file":"etabs/etabs_gravity.json","required":True,
                            "reason":"No ETABS gravity JSON selected"})
        # V161: always produce the original 76-support node inventory, even
        # when the native ETABS API cannot read old analysis results.
        # Unavailable ETABS reactions remain blank; no false validation PASS.
        try:
            from components.validation.gravity_node_comparison import (
                export_fixed_source_support_reactions)
            topology_path=export_dir/"OpenSees_Element_Connectivity.json"
            source_topology=json.loads(topology_path.read_text(encoding="utf-8-sig"))
            etabs_source=(json.loads(etabs_json.read_text(encoding="utf-8-sig"))
                          if etabs_json is not None and etabs_json.is_file() else None)
            audit76=export_fixed_source_support_reactions(
                stage/"node_audit_76",payload,source_topology,etabs_source)
            if audit76["missing_or_unverified"]:
                missing.append({"file":"node_audit_76/ETABS_REACTION_MATCHES",
                    "required":True,
                    "reason":str(audit76["missing_or_unverified"])+
                         " of 76 source support points unverified; see status per row."})
        except (OSError,ValueError,TypeError,KeyError,ImportError) as exc:
            missing.append({"file":"node_audit_76/Gravity_76_Source_Support_Reactions.csv",
                "required":True,"reason":type(exc).__name__+": "+str(exc)})
        for key,cols in (("nodes",NODE_COLS),("reactions",REACT_COLS),("local_forces",FORCE_COLS)):
            entries=payload.get(key)
            if not isinstance(entries,list) or not entries:
                missing.append({"file":f"opensees/{key}.csv","required":True,
                                "reason":"Gravity JSON lacks nonempty "+key})
            else:
                if any(not isinstance(x,dict) for x in entries):
                    raise ValueError(key+" requires list of objects")
                _csv(stage/"opensees"/(key+".csv"),entries,cols)
        if isinstance(payload.get("reactions"),list) and payload["reactions"]:
            try:
                rz=sum(float(x["rz_kN"]) for x in payload["reactions"])
                applied=float(payload["report"].get("applied_vertical_load_kN",
                          payload["report"].get("total_downward_load_kN")))
                error=abs(rz-applied)/abs(applied)*100 if applied else None
            except (KeyError,TypeError,ValueError,ZeroDivisionError):
                rz=applied=error=None
        else:
            rz=applied=error=None
        model=export_dir/"OpenSees_Complete_Model_Data_V118.json"
        model_hash=digest(model) if model.is_file() else None
        # Write an explicit NOT VALIDATED/SCREENING verdict for every upload,
        # including both gravity discrepancies and all optional omissions.
        # Read only original local evidence; never infer missing ETABS values.
        from components.gravity.validation_scorecard import (
            create_gravity_scorecard,save_gravity_scorecard)
        scorecard=create_gravity_scorecard(
            export_dir,gravity_dir,comparison_root,missing,oversize)
        save_gravity_scorecard(stage,scorecard)
        # Record all generated CSVs and original files, including derivatives
        # that were not copied via add(). Every member is inside the upload ZIP.
        package_members=sorted(
            [dict(relative_path=file.relative_to(stage).as_posix(),
                  extracted_path=str(dest/file.relative_to(stage)),
                  bytes=file.stat().st_size)
             for file in stage.rglob("*") if file.is_file()],
            key=lambda item:item["relative_path"])
        audit={"schema":"gravity-comparison-evidence-v2",
               "status":"EVIDENCE_EXPORT_ONLY_NOT_ENGINEERING_EQUIVALENCE",
               "source_export_dir":str(export_dir),"source_gravity_dir":str(gravity_dir),
               "dual_run_dir":str(dual_run_dir) if dual_run_dir else None,
               "comparison_root":str(comparison_root),
               "source_model_sha256":model_hash,"source_etabs_json":str(etabs_json) if etabs_json else None,
               "source_files":files,"missing":missing,"oversize_skipped":oversize,
               "packaged_files":package_members,
               "output_zip":str(output_dir/(bundle_name+".zip")),
               "output_folder":str(dest),
               "node_count":len(payload.get("nodes",[])) if isinstance(payload.get("nodes"),list) else None,
               "reaction_count":len(payload.get("reactions",[])) if isinstance(payload.get("reactions"),list) else None,
               "beam_local_force_records":len(payload.get("local_forces",[])) if isinstance(payload.get("local_forces"),list) else None,
               "openSees_support_rz_kN":rz,"openSees_expected_applied_kN":applied,
               "openSees_equilibrium_error_pct":error,
               "compare_verified":False,
               "limitations":["File presence and source hashes do not prove a matching EDB, load combination, stiffness or coordinate convention.",
                              "Local beam force responses require compatible tags/local-axis definitions.",
                              "Shell forces, wall section forces, detailed applied patterns and ETABS per-story reactions are missing unless separately supplied."]}
        audit["validation_scorecard"]=dict(
            file="GRAVITY_VALIDATION_SCORECARD.json",
            conclusion=scorecard["conclusion"],
            unresolved_gates=scorecard["unresolved_gates"])
        (stage/"EVIDENCE_MANIFEST.json").write_text(json.dumps(audit,indent=2,allow_nan=False),encoding="utf-8")
        with (stage/"EVIDENCE_FILE_PATHS.txt").open("w",encoding="utf8") as stream:
            stream.write("GRAVITY EVIDENCE INPUTS AND PACKAGE FILES\\n")
            stream.write("UPLOAD ZIP: "+str(output_dir/(bundle_name+".zip"))+"\\n")
            stream.write("EXTRACTED REVIEW FOLDER: "+str(dest)+"\\n")
            stream.write("SOURCE EXPORT: "+str(export_dir)+"\\n")
            stream.write("GRAVITY ROOT: "+str(gravity_dir)+"\\n")
            stream.write("DUAL RUN: "+str(dual_run_dir or "NOT SUPPLIED")+"\\n")
            stream.write("COMPARISON ROOT: "+str(comparison_root)+"\\n")
            stream.write("PACKAGED FILES:\\n")
            for item in files:stream.write("  "+item["file"]+" <- "+item["source"]+"\\n")
            stream.write("GENERATED AND COPIED PACKAGE MEMBERS:\\n")
            for item in package_members:
                stream.write("  "+item["extracted_path"]+"\\n")
            stream.write("MISSING FILES:\\n")
            for item in missing:stream.write("  "+str(item)+"\\n")
            stream.write("OVERSIZE OMITTED:\\n")
            for item in oversize:stream.write("  "+str(item)+"\\n")
        (stage/"REVIEW_76_NODES_FIRST.txt").write_text(
            "ETABS / OpenSees FOUNDATION REACTION REVIEW — READ FIRST\n"
            "1. This archive uses the original ETABS_SOURCE_SUPPORTS analysis for tags 1–76.\n"
            "2. Open node_audit_76/Gravity_76_Source_Support_Reactions.xlsx, Nodes 1-76.\n"
            "3. Review Critical nodes ranked for the largest ABSOLUTE Rz discrepancies.\n"
            "4. Follow the ETABS point ID map and coordinates, not identical integer IDs.\n"
            "5. Unavailable ETABS results remain blank with an explicit status.\n"
            "6. Compare wall-pier/core region totals independently; never discard node-level errors.\n"
            "7. Original source OpenSees_ID_and_Support_Audit.xlsx and generated Plotly HTML viewers are copied when present.\n"
            "8. Zoom to Node appears ONLY after rebuilding the HTML viewer with current main; old HTML will not update.\n"
            "9. 97-support CONTINUOUS_WALL_BASE_FIXED results are a sensitivity run, NOT nodewise ETABS baseline.\n"
            "10. This package alone never certifies structural equivalence.\n",
            encoding="utf-8")
        (stage/"README_UPLOAD_FIRST.txt").write_text(
            "Upload this ZIP for comparison.\n"
            "OPEN GRAVITY_VALIDATION_SCORECARD.txt FIRST for global and support reaction gates.\n"
            "Include native ETABS gravity JSON with the same load case.\n"
            "Inspect EVIDENCE_MANIFEST.json for MISSING and SKIPPED files.\n"
            "No missing physical responses are inferred.\n",encoding="utf8")
        zip_path=output_dir/(bundle_name+".zip")
        with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED) as z:
            for file in stage.rglob("*"):
                if file.is_file(): z.write(file,file.relative_to(stage.parent).as_posix())
        stage.rename(dest)
    audit["output_folder"]=str(dest)
    audit["output_zip"]=str(zip_path)
    return audit,zip_path

def main(argv=None):
    """Run the read-only evidence bundler via CLI.

    [REF docs/source/components/gravity/comparison_bundle.py.md] CLI contract.
    """
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--export-dir",required=True)
    p.add_argument("--gravity-dir",required=True)
    p.add_argument("--output-dir",required=True)
    p.add_argument("--etabs-json")
    p.add_argument("--max-file-mb",type=float,default=40)
    a=p.parse_args(argv)
    report,archive=export_bundle(a.export_dir,a.gravity_dir,a.output_dir,
                                 etabs_json=a.etabs_json,max_file_mb=a.max_file_mb)
    print(json.dumps({"zip":str(archive),"missing":len(report["missing"]),
                      "oversize":len(report["oversize_skipped"]),
                      "comparison_verified":False},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())

"""Consolidate native ETABS-linked and OpenSees ESM validation evidence.

Read-only; no numerical model updates. Creates ONE timestamped directory,
manifest, human-readable gate report and ZIP; missing items are explicit.
"""
from __future__ import annotations
from datetime import datetime,timezone
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

REQUIRED_SOURCE=(
    "OpenSees_Complete_Model_Config_V118.json",
    "OpenSees_Complete_Model_Data_V118.json",
    "OpenSees_Complete_Export_Report_V118.json",
    "OpenSees_Source_Model_Metadata_V118.json",
    "ETABS_OpenSees_Beam_Weight_Reconciliation.json",
    "OpenSees_Complete_Story_Masters_V118.csv",
    "NBC105_ESM_Story_Weights_Assembled_V118.csv",
)
OPTIONAL_SOURCE=(
    "ETABS_Native_Assignment_Gravity_Quantity_Audit.json",
    "OpenSees_Load_Conversion_Audit.json",
    "OpenSees_Section_Assignment_Audit.json",
    "OpenSees_Element_Connectivity.json",
    "OpenSees_Joint_Volume_Ownership_Audit.json",
    "NBC105_Input_Provenance_V123.json",
    "NBC105_Input_Provenance_V123.xlsx",
    "NBC105_ESM_Calculation_ULS_X+_E0_V111.json",
)
ESM_TERMS=("NBC105_ESM_","NBC105_OpenSees_","NBC105_Input_",
           "ETABS_LINKED_ESM","PDelta","PDELTA","Rayleigh","Irregularity",
           "Response_Recorder_Index")
EXT={".json",".csv",".xlsx",".txt",".log",".png",".pdf",".md"}

def sha(path):
    """[REF docs/source/components/equivalent_static/evidence_bundle.py.md] Synthetic evidence and source contract; not native acceptance."""
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()

def bundle_esm_validation(source_export,esm_output,save_under,progress=None,
                          max_file_bytes=150*1024*1024,
                          native_etabs_evidence=None):
    """[REF docs/source/components/equivalent_static/evidence_bundle.py.md] Synthetic evidence and source contract; not native acceptance."""
    src=Path(source_export).resolve()
    outputs=Path(esm_output).resolve()
    if not src.is_dir():raise FileNotFoundError("Model source export: "+str(src))
    if not outputs.is_dir():raise FileNotFoundError("ESM output folder: "+str(outputs))
    root=Path(save_under).resolve()/(
        "ESM_Validation_Evidence_"+datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    root.mkdir(parents=True,exist_ok=False)
    manifest={"schema":"esm-evidence-bundle-v1",
              "created_utc":datetime.now(timezone.utc).isoformat(),
              "original_source_dir":str(src),"original_esm_dir":str(outputs),
              "status":"COLLECTING","files":[],"missing_required":[],
              "missing_optional":[],"oversize_excluded":[],
              "source_evidence_status":"NOT_INDEPENDENT_ETABS_ACCEPTANCE",
              "case_response_status":"UNVERIFIED_PENDING_NATIVE_ETABS_ALIGNMENT"}
    def announce(message):
        if progress:progress(message)
    def include(file,rel,required=False):
        if not file.is_file():
            (manifest["missing_required"] if required else
             manifest["missing_optional"]).append(rel)
            return
        if file.stat().st_size>max_file_bytes:
            manifest["oversize_excluded"].append(
                {"file":rel,"bytes":file.stat().st_size,
                 "required":required,"reason":"Per-file bounded ZIP size"})
            if required:manifest["missing_required"].append(rel+" (oversize)")
            return
        target=root/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(file,target)
        manifest["files"].append({"path":rel,"sha256":sha(target),
                                  "size":target.stat().st_size,
                                  "original_path":str(file)})
    announce("COLLECTING | authoritative model/source inputs")
    for name in REQUIRED_SOURCE:
        include(src/name,"source/"+name,True)
    for name in OPTIONAL_SOURCE:
        include(src/name,"source/"+name)
    # Preserve all present ETABS-linked XLSX and native provenance JSON
    # without making their Aw/T calculations the same as OpenSees Rayleigh T.
    for loc,label in ((src,"model"),(outputs,"esm")):
        for file in sorted(loc.iterdir()):
            if file.is_file() and file.suffix.lower() in EXT and (
                    any(term.lower() in file.name.lower() for term in ESM_TERMS)
                    or file.name.startswith("GRAVITY_VALIDATION_SCORECARD")):
                include(file,label+"/"+file.name)
    announce("COLLECTING | saved ESM X/Y stories, plots, and diagnostics")
    for file in sorted(outputs.rglob("*")):
        if root in file.parents or any(p.name.startswith("ESM_Validation_Evidence_")
                                       for p in file.parents):
            continue
        if not file.is_file() or file.suffix.lower() not in EXT:continue
        if any(term.lower() in file.name.lower() for term in ESM_TERMS):
            relative=file.relative_to(outputs).as_posix()
            if len(Path(relative).parts)>7:continue
            target="esm_results/"+relative
            if (root/target).exists():continue
            include(file,target)
    # Generated OpenSees ESM runner scripts (*.py) must accompany the force
    # profiles. The generic evidence extension filter intentionally excludes
    # arbitrary Python source: only the six exact generated runner prefixes
    # are eligible. This is an archive of scripts, NOT proof they were run.
    for location,label in ((src,"source"),(outputs,"esm")):
        for runner in sorted(location.glob(
                "OpenSees_NBC105_ESM_Load_And_Static_Analysis_*.py")):
            include(runner,"generated_runners/"+label+"/"+runner.name)
    manifest["generated_runner_count"]=sum(
        1 for x in manifest["files"]
        if x["path"].startswith("generated_runners/"))
    manifest["generated_runner_execution_status"]="NOT_INFERRED_FROM_SCRIPT_EXISTENCE"
    if not manifest["generated_runner_count"]:
        manifest["missing_optional"].append(
            "No generated ESM Python runner source found; cannot reproduce "
            "unexecuted case generation from this ZIP alone")
    for file in sorted(src.glob("*ETABS_LINKED_ESM*")):
        if file.is_file() and file.suffix.lower() in EXT:
            include(file,"etabs_linked_excel/"+file.name)
    # User-selected saved native ETABS case data. No COM query or analysis
    # is triggered by bundling; keep source files and exact hashes unchanged.
    if native_etabs_evidence:
        extra=Path(native_etabs_evidence).resolve()
        if extra.is_file():
            include(extra,"native_etabs/"+extra.name)
        elif extra.is_dir():
            for file in sorted(extra.rglob("*")):
                if not file.is_file():continue
                if len(file.relative_to(extra).parts)>8:continue
                if file.suffix.lower() not in EXT|{".zip"}:continue
                include(file,"native_etabs/"+file.relative_to(extra).as_posix())
        else:
            manifest["missing_required"].append(
                "Native ETABS earthquake evidence path unavailable: "+str(extra))
    else:
        manifest["missing_optional"].append(
            "Native ETABS saved EQX/EQY/P-Delta evidence not supplied")
    # Native ETABS-linked reference: keep the original workbook method
    # distinct from provisional OpenSees continuous-pier geometry.
    linked=[]
    for file in sorted(src.glob("*ETABS_LINKED_ESM.provenance.json")):
        try:
            obj=json.loads(file.read_text(encoding="utf-8-sig"))
            linked.append({
                "filename":file.name,"sha256":sha(file),
                "original_source_excel":obj.get("source_excel"),
                "original_source_excel_sha256":obj.get("source_excel_sha256"),
                "original_source_edb":obj.get("source_edb"),
                "original_source_edb_sha256":obj.get("source_edb_sha256"),
                "reference_status":obj.get("status"),
                "coefficient_provenance":obj.get("coefficients")})
        except Exception as exc:
            manifest["missing_optional"].append(
                "Cannot read ETABS linked provenance "+file.name+": "+str(exc))
    sources={str(x.get("original_source_excel_sha256")) for x in linked}
    coefficient_disagreement=False
    if len(linked)>1:
        ref=linked[0].get("coefficient_provenance")
        coefficient_disagreement=any(
            x.get("coefficient_provenance")!=ref for x in linked[1:])
    audit={
        "status":"ORIGINAL_EXCEL_LINKED_RESEARCH_REFERENCE_ONLY",
        "linked_source_count":len(linked),
        "distinct_original_workbook_hashes":sorted(sources),
        "coefficient_disagreement":coefficient_disagreement,
        "linked_sources":linked,
        "accepted_Aw_T1_source":"Native original Excel method ONLY when same EDB verified; no OpenSees geometry replacement",
        "opensess_continuous_pier_status":"GEOMETRY_DIAGNOSTIC_NOT_CODE_ACCEPTED",
        "calculation_reference_is_not_measured_etabs_response":True}
    audit_path=root/"ETABS_Linked_Original_Excel_Aw_T1_Audit.json"
    audit_path.write_text(json.dumps(audit,indent=2,ensure_ascii=False),
                          encoding="utf-8")
    if coefficient_disagreement:
        manifest["missing_required"].append(
            "Two ETABS-linked workbook calculation sources disagree in Aw/T1/C/k")
    manifest["original_excel_source_audit"]=audit_path.name
    config=src/"OpenSees_Complete_Model_Config_V118.json"
    if config.is_file():
        cfg=json.loads(config.read_text(encoding="utf-8-sig"))
        manifest["beam_policy"]=cfg.get("etabs_beam_weight_policy")
        if cfg.get("etabs_beam_weight_policy")!="ETABS_BEAM_CLEAR_LENGTH":
            manifest["missing_required"].append(
                "CORRECTED_BEAM_POLICY: source still GROSS_SECTION_LENGTH")
    if not any("ETABS_LINKED_ESM.provenance.json" in r["path"]
               for r in manifest["files"]):
        manifest["missing_optional"].append(
            "Original ETABS-linked Aw/T source provenance not found in selected model/output folders")
    manifest["generated_force_profiles_only"]=bool(
        any("NBC105_ESM_Force_Profile_" in r["path"]
            for r in manifest["files"]))
    # A plotted cumulative sum of applied lateral storey forces is not
    # OpenSees-recovered section-cut shear, roof displacement or drift.
    manifest["story_shear_plot_type"]="SUM_OF_APPLIED_FORCES_NOT_SOLVED_SECTION_CUT"
    if not any("NBC105_ESM_OpenSees_Response_" in r["path"]
               for r in manifest["files"]):
        manifest["missing_required"].append(
            "OpenSees saved X/Y ESM response profiles absent")
    if not any("ETABS_EQ_PDELTA_NATIVE_INDEX" in r["path"]
               for r in manifest["files"]):
        manifest["missing_optional"].append(
            "Native ETABS EQX/EQY/PDelta response tables not collected here")
    manifest["status"]="EVIDENCE_COMPLETE_FOR_REVIEW" if not manifest[
        "missing_required"] else "INCOMPLETE_MISSING_EVIDENCE"
    manifest["total_collected"]=len(manifest["files"])
    mpath=root/"ESM_Evidence_Manifest.json"
    mpath.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),
                     encoding="utf-8")
    gate=root/"READ_FIRST_ESM_VALIDATION.txt"
    gate.write_text(
        "ESM EVIDENCE AUDIT: "+manifest["status"]+"\n"+
        "Source beam policy: "+str(manifest.get("beam_policy"))+"\n"+
        "Files copied: "+str(len(manifest["files"]))+"\n"+
        "Missing required:\n"+"\n".join(manifest["missing_required"])+
        "\nMissing optional:\n"+"\n".join(manifest["missing_optional"])+
        "\n\nOBSERVATION != CODE ACCEPTANCE. Compare raw signed EQ loads, "+
        "recovered story shears, seismic mass, initial tangent PDelta "+
        "and true ETABS responses by case, direction, branch and level.\n",
        encoding="utf-8")
    announce("PACKAGING | ESM validation ZIP")
    bundle=root.parent/(root.name+"_UPLOAD.zip")
    with zipfile.ZipFile(bundle,"w",compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6,allowZip64=True) as z:
        for f in sorted(root.rglob("*")):
            if f.is_file():z.write(f,arcname=f.relative_to(root).as_posix())
    announce("FINISHED | evidence files="+str(len(manifest["files"]))+
             " | ZIP="+str(bundle))
    return dict(output_directory=str(root),upload_zip=str(bundle),manifest=manifest)

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",required=True)
    parser.add_argument("--esm",required=True)
    parser.add_argument("--out",required=True)
    parser.add_argument("--native-etabs-evidence",default=None)
    args=parser.parse_args()
    print(json.dumps(bundle_esm_validation(args.source,args.esm,args.out,
                 progress=lambda x:print(x,flush=True),
                 native_etabs_evidence=args.native_etabs_evidence),indent=2))

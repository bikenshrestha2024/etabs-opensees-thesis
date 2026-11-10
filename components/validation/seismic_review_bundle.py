"""Consolidated, read-only seismic comparison archive for ESM or MRSM.

All *existing* output files in selected analysis subtrees are retained by
content, organized by provenance. Identical byte content is included once
with an explicit extraction/reconstruction map to reduce upload size.
Never claim native ETABS validation from OpenSees calculations alone.
"""
from __future__ import annotations
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ALLOWED={".py",".json",".jsonl",".csv",".tsv",".xlsx",".xlsm",".xls",
         ".txt",".log",".md",".pdf",".png",".svg",".html",".htm",
         ".h5",".hdf5",".npz",".npy",".parquet",".sqlite",".db"}
INTERESTING=("esm","nbc105","rayleigh","mrsm","modal","spectrum",
             "drift","displace","reaction","equivalence","etabs",
             "provenance","mass","pdelta","response","story","storey")


def _sha(file):
    h=hashlib.sha256()
    with Path(file).open("rb") as source:
        for block in iter(lambda:source.read(1048576),b""):
            h.update(block)
    return h.hexdigest()


def _file_rows(root, exclude):
    """Do not follow symlinks; never package prior ZIPs or other review bundles."""
    root=Path(root).resolve()
    if not root.is_dir():return
    for file in sorted(root.rglob("*")):
        if not file.is_file() or file.is_symlink() or file.suffix.lower() not in ALLOWED:
            continue
        relative=file.relative_to(root)
        if len(relative.parts)>10:continue
        if any(part.startswith(("ESM_Validation_Evidence_",
                                "Seismic_Review_","Gravity_Evidence_Upload"))
               for part in relative.parts):continue
        if any(file.is_relative_to(e) for e in exclude):continue
        yield file,relative


def _restore_script():
    return '''"""Restore exact-byte duplicate paths after extracting review ZIP.
Run inside the extracted review folder; refuses paths outside it.
"""
import hashlib,json,pathlib,shutil
root=pathlib.Path(__file__).resolve().parent
audit=json.loads((root/"REVIEW_MANIFEST.json").read_text(encoding="utf-8"))
for item in audit["duplicates"]:
    target=(root/item["path"]).resolve()
    original=(root/item["same_content_as"]).resolve()
    if not target.is_relative_to(root) or not original.is_relative_to(root):
        raise ValueError("Unsafe alias path")
    if not original.is_file():raise FileNotFoundError(original)
    h=hashlib.sha256()
    with original.open("rb") as stream:
        for block in iter(lambda:stream.read(1048576),b""):
            h.update(block)
    digest=h.hexdigest()
    if digest!=item["sha256"]:raise ValueError("Checksum mismatch: "+str(original))
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(original,target)
    h=hashlib.sha256()
    with target.open("rb") as stream:
        for block in iter(lambda:stream.read(1048576),b""):
            h.update(block)
    if h.hexdigest()!=digest:raise ValueError("Copied file hash mismatch")
print("Restored",len(audit["duplicates"]),"duplicate files; unique content unchanged.")
'''


def _write_template(root, source_export, results_root, method, issues):
    """Create editable ETABS comparison Excel with no invented native results."""
    target=root/"Comparisons"/"ETABS_OpenSees_Response_Check_Template.xlsx"
    target.parent.mkdir(parents=True,exist_ok=True)
    try:
        from components.validation.etabs_comparison import collect, FIELDS
        rows=[row for row in collect(
            source_export,issues,results_root=results_root)
            if row.get("method")==method]
    except (ValueError,KeyError,OSError) as exc:
        rows=[];issues.append("Normalized source collection blocked: "+str(exc))
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font,PatternFill
        wb=Workbook()
        guide=wb.active;guide.title="READ FIRST"
        for r in (
            ("Engineering result","ETABS-versus-OpenSees diagnostic, NOT code acceptance"),
            ("Method",method),
            ("ETABS response","Blank unless independently extracted from exact analyzed EDB"),
            ("Row semantics","Same case, axis, story, node, units, scale and response basis"),
            ("Required cases","Match ULS/SLS, X/Y and signed eccentricity explicitly"),
            ("Modal result","CQC is an unsigned statistical peak; never compare as signed instant"),
            ("Model identity","Match source EDB hash, stiffness, mass, damping, P-Delta"),
            ("Site and code","NBC eligibility/site Vs30 and original Excel Aw gates remain independent"),
        ):guide.append(r)
        src=wb.create_sheet("OpenSees Normalized")
        src.append(FIELDS+["value","source_file"])
        for r in rows:src.append([r.get(k) for k in FIELDS+["value","source_file"]])
        et=wb.create_sheet("ETABS Native - Enter Verified")
        et.append(FIELDS+["value","source_case","source_edb_sha256","verification_note"])
        for r in rows:
            et.append([r.get(k) for k in FIELDS]+[None,None,None,
                "Populate only from ETABS analysis and verified case mapping"])
        for sheet in (src,et):
            sheet.freeze_panes="A2";sheet.auto_filter.ref=sheet.dimensions
            for cell in sheet[1]:
                cell.font=Font(color="FFFFFF",bold=True)
                cell.fill=PatternFill("solid",fgColor="203A5B")
            sheet.column_dimensions["E"].width=24
            sheet.column_dimensions["F"].width=19
            sheet.column_dimensions["H"].width=36
        wb.save(target)
    except ImportError:
        issues.append("openpyxl unavailable: ETABS comparison template XLSX not generated")
    return target if target.is_file() else None


def bundle_seismic_review(source_export, analysis_output, *, method="ESM",
                          native_etabs=None, include_comparison_template=True,
                          diagnostic_only=True):
    """Build one output folder and one ZIP for source, OpenSees, ETABS and comparison.

    [REF docs/source/components/validation/seismic_review_bundle.py.md]

    - Never reads or changes an EDB.
    - Maximum ZIP member size is not silently capped (ZIP64).
    - Byte-for-byte duplicate files are represented by explicit aliases and
      can be losslessly restored using RESTORE_DUPLICATES.py.
    - Existing extracted earlier archives are excluded to prevent recursion.
    """
    method=str(method).upper()
    if method not in {"ESM","MRSM"}:raise ValueError("method must be ESM or MRSM")
    source=Path(source_export).resolve()
    output=Path(analysis_output).resolve()
    if not source.is_dir() or not output.is_dir():
        raise FileNotFoundError("Model source and analysis output folders must exist")
    review_root=output/"Seismic_Review_Packages"
    review_root.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    package=review_root/(method+"_Review_"+stamp)
    package.mkdir()
    manifest={"schema":"seismic-review-bundle-v1","method":method,
              "created_utc":datetime.now(timezone.utc).isoformat(),
              "source_export":str(source),"analysis_output":str(output),
              "validation":"NOT_STRUCTURALLY_CERTIFIED",
              "collected":[],"duplicates":[],"missing":[],
              "warnings":[],"independent_ETABS_response_verified":False}
    identity={}
    def collect(file,name):
        if not file.is_file():
            manifest["missing"].append(name)
            return
        if file.suffix.lower() not in ALLOWED:return
        dig=_sha(file);length=file.stat().st_size
        relative=Path(name).as_posix()
        if (dig,length) in identity:
            # Same bytes: full content exists once in the archive. Restorable
            # alias has exact relative target, origin and original SHA256.
            manifest["duplicates"].append({
                "path":relative,"same_content_as":identity[(dig,length)],
                "sha256":dig,"bytes":length})
            return
        dest=package/relative
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(file,dest)
        identity[(dig,length)]=relative
        manifest["collected"].append({
            "path":relative,"sha256":dig,"bytes":length,
            "source":str(file)})
    # Selected method: do not take all other versions' results as if they
    # belong to the current run. Preserve existing actual output files.
    for file,rel in _file_rows(source,[review_root]):
        if (file.name.startswith(("OpenSees_Complete_Model_",
                                 "OpenSees_Source_Model_Metadata_",
                                 "OpenSees_Element_Connectivity",
                                 "NBC105_ESM_Story_Weights_",
                                 "OpenSees_Complete_Story_Masters",
                                 "ETABS_OpenSees_Beam_Weight_",
                                 "ETABS_Native_Assignment_Gravity_",
                                 "NBC105_Input_Provenance"))):
            collect(file,"Source_Provenance/"+rel.as_posix())
    for file,rel in _file_rows(output,[review_root]):
        name=rel.as_posix()
        if (method=="ESM" and
                not any(s in name.casefold() for s in
                        ("esm","nbc105","rayleigh","etabs_linked",
                         "comparison","input_sync","pdelta",
                         "response_recorder_index"))):
            continue
        if (method=="MRSM" and
                not any(s in name.casefold() for s in
                        ("mrsm","modal","spectrum","comparison","rayleigh","case_review"))):
            continue
        label=("ETABS_Linked" if "ETABS_LINKED_ESM" in name.upper() else
               "Comparisons" if "comparison" in name.casefold() else
               "OpenSees_Direct")
        collect(file,label+"/"+name)
    if native_etabs:
        p=Path(native_etabs).resolve()
        if p.is_file():
            collect(p,"ETABS_Native/"+p.name)
        elif p.is_dir():
            for file,rel in _file_rows(p,[review_root]):
                collect(file,"ETABS_Native/"+rel.as_posix())
        else:
            manifest["missing"].append("Native ETABS evidence location: "+str(p))
    else:
        manifest["warnings"].append(
            "Independent native ETABS earthquake results unavailable: "
            "the included Excel sheet is a comparison input template, not ETABS output")
    if include_comparison_template:
        t=_write_template(package,source,output,method,manifest["warnings"])
        if t:
            manifest["collected"].append({
                "path":"Comparisons/"+t.name,"bytes":t.stat().st_size,
                "sha256":_sha(t),"source":"generated mapping template"})
    (package/"RESTORE_DUPLICATES.py").write_text(_restore_script(),encoding="utf-8")
    (package/"README_FIRST.txt").write_text(
        "SEISMIC RESEARCH EVIDENCE | "+method+"\n"
        "See REVIEW_MANIFEST.json for exact source paths and SHA256.\n"
        "OpenSees_Direct/ contains actual available solver outputs; "
        "ETABS_Linked/ contains original Excel calculation/reference.\n"
        "ETABS_Native/ is independent analyzed ETABS response evidence, "
        "if provided. Comparisons/ includes a blank ETABS verification template.\n"
        "Duplicate content is archived once; run RESTORE_DUPLICATES.py "
        "after extraction if duplicate file paths are needed.\n"
        "NEVER infer missing ETABS results or accept an ESM/MRSM result "
        "without matched source identity, modal basis and NBC gates.\n",
        encoding="utf-8")
    manifest["unique_file_count"]=len(manifest["collected"])
    manifest["deduplicated_alias_count"]=len(manifest["duplicates"])
    manifest["original_total_bytes"]=sum(x["bytes"] for x in manifest["collected"])+sum(
        x["bytes"] for x in manifest["duplicates"])
    manifest["stored_unique_bytes"]=sum(x["bytes"] for x in manifest["collected"])
    (package/"REVIEW_MANIFEST.json").write_text(
        json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    zip_path=review_root/(package.name+"_UPLOAD.zip")
    with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9,allowZip64=True) as archive:
        for f in sorted(package.rglob("*")):
            if f.is_file():archive.write(f,arcname=f.relative_to(package).as_posix())
    (review_root/("LATEST_"+method+"_REVIEW.txt")).write_text(
        "UPLOAD ZIP: "+str(zip_path)+"\nREVIEW FOLDER: "+str(package)+
        "\nMANIFEST: "+str(package/"REVIEW_MANIFEST.json")+"\n",
        encoding="utf-8")
    return {"zip":str(zip_path),"folder":str(package),"manifest":manifest}


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",required=True)
    parser.add_argument("--results",required=True)
    parser.add_argument("--method",choices=["ESM","MRSM"],default="ESM")
    parser.add_argument("--native-etabs")
    arguments=parser.parse_args()
    print(json.dumps(bundle_seismic_review(
        arguments.source,arguments.results,method=arguments.method,
        native_etabs=arguments.native_etabs),indent=2))

"""Conservative engineering gravity reviewer for ETABS -> OpenSeesPy.

Spyder/Windows compatible, Python >=3.10. No external dependencies for
CSV/JSON; optional openpyxl creates an Excel workbook. No model changes
unless user explicitly stages a candidate configuration. Never changes
original EDB, mesh, boundary conditions or stiffness.

[REF docs/source/Gravity_Safe_Engineering_Review_V1.py.md]
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import shutil
from collections import defaultdict
from pathlib import Path

SOURCE="OpenSees_Complete_Model_Config_V118.json"
BEAM="ETABS_OpenSees_Beam_Weight_Reconciliation.json"
JOINT="OpenSees_Joint_Volume_Ownership_Audit.json"
DIRECT="Direct_Gravity_Comparison.json"
NODE="Gravity_Node_Reaction_Comparison.json"


def load(path):
    path=Path(path)
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else None


def finite(v, label):
    try:
        x=float(v)
    except (TypeError,ValueError):
        raise ValueError(label+" must be a finite number") from None
    if not math.isfinite(x):
        raise ValueError(label+" must be finite")
    return x


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(2**20),b""):h.update(block)
    return h.hexdigest()


def find_gravity_root(folder):
    p=Path(folder).resolve()
    return p/"OpenSees_Analysis_Results" if (p/"OpenSees_Analysis_Results").is_dir() else p


def find_direct(folder):
    root=find_gravity_root(folder)
    choices=sorted(root.rglob(DIRECT),key=lambda p:p.stat().st_mtime,reverse=True)
    return choices[0] if choices else None


def read_etabs_beam_csv(path):
    """Require independent ETABS Material List export with explicit beam row.

    Expected columns: object_type, weight_kN. One row per type.
    An imported CSV alone is NOT proof that the correct EDB/case was used.
    """
    p=Path(path)
    with p.open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not {"object_type","weight_kN"}.issubset(reader.fieldnames or []):
            raise ValueError("ETABS beam CSV needs columns object_type,weight_kN")
        candidates=[row for row in reader if
                    str(row["object_type"]).strip().casefold() in
                    ("beam","beams","frame beam","frame beams")]
    if len(candidates)!=1:
        raise ValueError("Require exactly one independent ETABS Beam material-list total")
    total=finite(candidates[0]["weight_kN"],"ETABS beam material weight")
    if total<=0:raise ValueError("ETABS beam weight must be positive")
    return total


def beam_checks(export,source_beam_weight=None,source_beam_csv=None):
    """Validate source beam arithmetic without chasing ETABS total FZ.

    [REF components/model/beam_weight_convention.py]
    """
    export=Path(export)
    audit=load(export/BEAM)
    config=load(export/SOURCE)
    if not isinstance(audit,dict) or not isinstance(config,dict):
        raise FileNotFoundError("Rebuild source export: missing "+BEAM+" or "+SOURCE)
    rows=audit.get("rows")
    if not isinstance(rows,list) or not rows:
        raise ValueError("Beam audit has no member-level rows")
    ids=set()
    gross=clear=offset=0.
    issues=[]
    for row in rows:
        key=str(row.get("etabs_object","")).strip()
        if not key or key in ids:issues.append("Missing/duplicate beam source ID "+key)
        ids.add(key)
        L=finite(row.get("full_length_m"),"beam "+key+" length")
        A=finite(row.get("frame_area_m2"),"beam "+key+" area")
        gamma=finite(row.get("unit_weight_kN_m3"),"beam "+key+" unit weight")
        li=row.get("end_i_m");lj=row.get("end_j_m")
        if not all(x>0 for x in (L,A,gamma)):
            issues.append(key+": nonpositive length/area/density")
            continue
        if li is None or lj is None:
            issues.append(key+": missing ETABS end offsets")
            continue
        li=finite(li,key+" offset I");lj=finite(lj,key+" offset J")
        if li<0 or lj<0 or li+lj>L+1e-9:
            issues.append(key+": invalid end offsets")
            continue
        w=L*A*gamma;red=(li+lj)*A*gamma
        if abs(w-finite(row.get("gross_weight_kN"),key+" gross"))>max(.001,w*1e-8):
            issues.append(key+": source gross weight arithmetic inconsistent")
        if abs(red-finite(row.get("potential_offset_weight_kN"),key+" offset reduction"))>max(.001,w*1e-8):
            issues.append(key+": source offset weight arithmetic inconsistent")
        gross+=w;clear+=w-red;offset+=red
    if len(ids)!=len(rows):issues.append("Duplicate source beam object IDs")
    if int(audit.get("beam_count",-1))!=len(rows):
        issues.append("Source beam count does not equal member rows")
    recorded=finite(audit.get("gross_beam_weight_kN"),"recorded gross beam weight")
    if abs(gross-recorded)>max(.01,recorded*1e-7):
        issues.append("Sum of per-member gross weights differs from beam total")
    if source_beam_csv is not None:
        expected=read_etabs_beam_csv(source_beam_csv)
        basis=str(Path(source_beam_csv).resolve())
        source_hash=sha256(source_beam_csv)
    elif source_beam_weight is not None:
        expected=finite(source_beam_weight,"user-entered beam weight")
        basis="USER_ENTERED_NUMBER_NOT_INDEPENDENT_FILE"
        source_hash=None
    else:
        expected=None;basis="MISSING_INDEPENDENT_ETABS_BEAM_MATERIAL_LIST";source_hash=None
    delta=clear-expected if expected is not None else None
    tolerance=max(1.0,abs(expected)*0.0001) if expected is not None else None
    matched=bool(expected is not None and abs(delta)<=tolerance)
    if expected is not None and not matched:
        issues.append("Clear-length reconstruction does not match independent ETABS beam source weight")
    if expected is None:
        issues.append("Independent ETABS Material List beam weight is required")
    if config.get("joint_volume_weight_policy")=="VERIFIED_SINGLE_OWNER":
        issues.append("Physical single-owner joint correction already selected: double subtraction prohibited")
    return dict(schema="safe-beam-weight-review-v1",
        source_config=str(export/SOURCE),source_beam_audit=str(export/BEAM),
        source_beam_csv=basis,source_beam_csv_sha256=source_hash,
        object_count=len(rows),gross_kN=gross,
        potential_offset_kN=offset,
        reconstructed_clear_kN=clear,
        etabs_material_list_beam_kN=expected,
        difference_kN=delta,tolerance_kN=tolerance,
        within_screening_tolerance=matched,
        selected_policy=config.get("etabs_beam_weight_policy"),
        note="Numeric match does not prove physical concrete union or ETABS Auto weight rule",
        issues=issues,
        candidate_eligible=bool(matched and not issues and source_hash is not None),
        physical_volume_ownership_verified=False,
        etabs_equivalence_established=False)


def _validate_map(path):
    mapping={}
    with Path(path).open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        required={"etabs_point","region_id","region_type","verified","source_basis"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Region CSV must have "+",".join(sorted(required)))
        for row in reader:
            tag=str(row["etabs_point"]).strip()
            if not tag or tag in mapping:raise ValueError("Invalid/duplicate ETABS source point "+tag)
            if str(row["verified"]).strip().lower() not in ("yes","true","1"):
                raise ValueError("ETABS point "+tag+" has not been physically reviewed")
            region=str(row["region_id"]).strip()
            basis=str(row["source_basis"]).strip()
            if not region or not basis:
                raise ValueError("Region and source geometry rationale required for ETABS point "+tag)
            if row["region_type"].strip().upper() not in ("COLUMN","WALL_PIER","CORE","OTHER"):
                raise ValueError("Unrecognized foundation region type for "+tag)
            mapping[tag]=dict(region_id=region,region_type=row["region_type"].strip().upper(),
                              source_basis=basis)
    return mapping


def foundation_regions(node_comparison, region_csv, *,etabs_base_reaction_kN=None):
    """Integrate only explicitly verified same-physical-region support nodes.

    Outputs both local differences and the load-share difference;
    NEVER suppresses raw joint mismatch.
    [REF components/validation/gravity_node_comparison.py compare_support_nodes]
    """
    data=load(node_comparison) if isinstance(node_comparison,(str,Path)) else node_comparison
    if not isinstance(data,dict) or not isinstance(data.get("rows"),list):
        raise ValueError("Full point-reaction JSON with rows is required")
    mapping=_validate_map(region_csv)
    rows=data["rows"]
    matched=[r for r in rows if r.get("status")=="MATCHED_GLOBAL_Z"]
    if len(matched)!=len(rows):
        raise ValueError("Unmatched, axis-unverified or ambiguous points: reject aggregated foundation comparison")
    observed={str(r.get("etabs_point")) for r in matched}
    if observed!=set(mapping):
        raise ValueError("Region mapping must cover exactly the observed ETABS source support points")
    groups=defaultdict(lambda:dict(etabs_kN=0.,opensees_kN=0.,point_count=0,
                                    max_individual_difference_kN=0.))
    e_total=o_total=0.
    details=[]
    for row in matched:
        tag=str(row["etabs_point"])
        e=finite(row["etabs_global_rz_kN"],"ETABS point "+tag)
        o=finite(row["opensees_rz_kN"],"OpenSees point "+tag)
        reg=mapping[tag]["region_id"]
        g=groups[reg]
        if g["point_count"] and g["region_type"]!=mapping[tag]["region_type"]:
            raise ValueError("Inconsistent region types for "+reg)
        g["region_type"]=mapping[tag]["region_type"]
        g["etabs_kN"]+=e;g["opensees_kN"]+=o;g["point_count"]+=1
        g["max_individual_difference_kN"]=max(
            g["max_individual_difference_kN"],abs(o-e))
        e_total+=e;o_total+=o
        details.append(dict(etabs_point=tag,opensees_node=row.get("opensees_node"),
            region_id=reg,etabs_kN=e,opensees_kN=o,
            point_difference_kN=o-e,source_basis=mapping[tag]["source_basis"]))
    regional=[]
    for key,g in sorted(groups.items()):
        e=g["etabs_kN"];o=g["opensees_kN"]
        regional.append(dict(region_id=key,region_type=g["region_type"],
            point_count=g["point_count"],etabs_kN=e,opensees_kN=o,
            difference_kN=o-e,
            difference_percent=100*abs(o-e)/abs(e) if e else None,
            etabs_load_share_percent=100*e/e_total if e_total else None,
            opensees_load_share_percent=100*o/o_total if o_total else None,
            load_share_difference_percentage_points=(
                100*o/o_total-100*e/e_total if e_total and o_total else None),
            max_individual_difference_kN=g["max_individual_difference_kN"]))
    base_delta=(e_total-etabs_base_reaction_kN) if etabs_base_reaction_kN is not None else None
    return dict(schema="reviewed-foundation-regions-v1",
        status="DIAGNOSTIC_NOT_STRUCTURAL_ACCEPTANCE",
        mapping_csv=str(Path(region_csv).resolve()),
        mapping_sha256=sha256(region_csv),etabs_base_kN=etabs_base_reaction_kN,
        etabs_joint_sum_kN=e_total,openSees_joint_sum_kN=o_total,
        etabs_joint_to_base_difference_kN=base_delta,
        rows=regional,original_individual_rows=details,
        warnings=[
            "Region mapping reviewed by source IDs, not automatic nearby-node clustering",
            "Every single-point mismatch is preserved even if wall/core totals agree",
            "A region sum does not establish wall membrane force or ETABS mesh equivalence"])


def review(export_dir,*,etabs_beam_csv=None,etabs_beam_kN=None,
           region_csv=None,node_comparison=None,etabs_base_kN=None):
    export=Path(export_dir).expanduser().resolve()
    b=beam_checks(export,etabs_beam_kN,etabs_beam_csv)
    out=export/"Gravity_Safe_Engineering_Review"
    out.mkdir(exist_ok=True)
    report=dict(schema="safe-gravity-review-v1",beam=b,
        current_config_sha256=sha256(export/SOURCE),
        conclusion="DIAGNOSTIC_ONLY_NOT_STRUCTURALLY_VALIDATED",
        original_export_not_modified=True)
    if region_csv:
        if not node_comparison:
            raise ValueError("Provide full Gravity_Node_Reaction_Comparison.json for region aggregation")
        report["foundation"]=foundation_regions(node_comparison,region_csv,
                                                  etabs_base_reaction_kN=etabs_base_kN)
    target=out/"GRAVITY_SAFE_REVIEW.json"
    target.write_text(json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    for name,rows in (("BEAM_SOURCE_RECONCILIATION.csv",[b]),
                      ("FOUNDATION_REGIONS.csv",
                       report.get("foundation",{}).get("rows",[]))):
        if rows:
            with (out/name).open("w",encoding="utf-8-sig",newline="") as f:
                fields=list(rows[0]);w=csv.DictWriter(f,fieldnames=fields)
                w.writeheader()
                for row in rows:
                    w.writerow({k:json.dumps(v) if isinstance(v,(dict,list)) else v
                                for k,v in row.items()})
    summary=["GRAVITY ENGINEERING REVIEW — NOT STRUCTURALLY ACCEPTED",
             "Source: "+str(export),
             "Current policy: "+str(b["selected_policy"]),
             "Gross beam weight: %.6f kN"%b["gross_kN"],
             "Offset-weight potential: %.6f kN"%b["potential_offset_kN"],
             "Calculated clear-length weight: %.6f kN"%b["reconstructed_clear_kN"],
             "ETABS material list beam weight: "+str(b["etabs_material_list_beam_kN"]),
             "Candidate eligible: "+str(b["candidate_eligible"]),
             "Engineering caution: do NOT add joint union deduction to clear-span deduction",
             "Independent ETABS equivalence: NOT ESTABLISHED",
             "Issues:"]+["  - "+x for x in b["issues"]]
    if "foundation" in report:
        summary.append("Foundation region count: "+str(len(report["foundation"]["rows"])))
        summary.append("Individual node reaction data remains in GRAVITY_SAFE_REVIEW.json")
    (out/"GRAVITY_SAFE_REVIEW.txt").write_text("\n".join(summary)+"\n",encoding="utf-8")
    _write_optional_excel(out,report)
    return out,report


def stage_candidate(export_dir,review_json,*,approval_text):
    """Produce an immutable CANDIDATE config; never overwrite source files.

    This does not rebuild model or certify ETABS weight calculation.
    The normal export rebuild must be performed only after an operator
    reviews and explicitly installs the candidate configuration.
    """
    if approval_text!="I REVIEWED ETABS BEAM SELF WEIGHT AND SOURCE GEOMETRY":
        raise ValueError("Exact explicit engineering review acknowledgement required")
    export=Path(export_dir).expanduser().resolve()
    rp=Path(review_json).expanduser().resolve()
    data=load(rp)
    if not data or not data.get("beam",{}).get("candidate_eligible"):
        raise ValueError("Cannot stage: independent source weight or offset audit has not passed")
    original=export/SOURCE
    if data.get("current_config_sha256")!=sha256(original):
        raise ValueError("Source config changed since review; rerun audit")
    cfg=load(original)
    if cfg.get("joint_volume_weight_policy")=="VERIFIED_SINGLE_OWNER":
        raise ValueError("Joint union correction conflicts with beam clear-weight mode")
    cfg["etabs_beam_weight_policy"]="ETABS_BEAM_CLEAR_LENGTH"
    cfg["etabs_clear_beam_weight_confirmed"]=True
    stamp=dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out=export/"Gravity_Safe_Engineering_Review"/("CANDIDATE_"+stamp)
    if out.exists():raise FileExistsError(str(out))
    out.mkdir(parents=True)
    candidate=out/SOURCE
    candidate.write_text(json.dumps(cfg,indent=2,allow_nan=False),encoding="utf-8")
    shutil.copy2(original,out/("ORIGINAL_"+SOURCE))
    provenance=dict(state="REVIEWED_CANDIDATE_NOT_APPLIED",
        original_config_sha256=sha256(original),
        independent_etabs_beam_csv_sha256=data["beam"]["source_beam_csv_sha256"],
        review_json_sha256=sha256(rp),source_export=str(export),
        candidate_config=str(candidate),original_unchanged=True)
    (out/"CANDIDATE_PROVENANCE.json").write_text(json.dumps(
        provenance,indent=2),encoding="utf-8")
    (out/"APPLY_INSTRUCTIONS.txt").write_text(
        "The source model was NOT modified. The candidate JSON is a proposal.\n"
        "Review source ETABS Self Weight Option, geometry and insertion points.\n"
        "After engineering approval, back up your original export and install\n"
        "the candidate config yourself, then rebuild the complete OpenSees export.\n"
        "Rerun BOTH gravity support scenarios and direct ETABS comparison.\n"
        "Do not add VERIFIED_SINGLE_OWNER joint-volume reduction.\n"
        "Proceed to modal/ESM/MRSM/NLTHA only after gravity acceptance.\n",
        encoding="utf-8")
    return out


def make_region_template(node_comparison_path,output_csv):
    """Generate an UNVERIFIED point map: user must label every source point.

    [REF components/validation/gravity_node_comparison.py compare_support_nodes]
    """
    data=load(node_comparison_path)
    if not isinstance(data,dict) or not isinstance(data.get("rows"),list):
        raise ValueError("Full node-comparison JSON with individual rows required")
    point_rows=data["rows"]
    output=Path(output_csv)
    if output.exists():
        raise FileExistsError("Refuse to overwrite existing engineering mapping "+str(output))
    output.parent.mkdir(parents=True,exist_ok=True)
    seen=set()
    with output.open("w",newline="",encoding="utf-8-sig") as fp:
        w=csv.writer(fp)
        w.writerow(["etabs_point","region_id","region_type","verified",
                    "source_basis","x_m","y_m","z_m","opensees_node",
                    "etabs_Rz_kN","opensees_Rz_kN","mapping_status"])
        for row in point_rows:
            key=str(row.get("etabs_point") or "")
            if not key or key in seen:continue
            seen.add(key)
            w.writerow([key,"UNASSIGNED","OTHER","NO","",row.get("x_m"),
                row.get("y_m"),row.get("z_m"),row.get("opensees_node"),
                row.get("etabs_global_rz_kN"),row.get("opensees_rz_kN"),
                row.get("status")])
    return output


def _write_optional_excel(folder,report):
    """Readable artifact; preserve machine-readable JSON/CSV if unavailable.

    [REF docs/source/Gravity_Safe_Engineering_Review_V1.py.md]
    """
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font,PatternFill
    except ImportError:
        return None
    book=Workbook()
    ws=book.active;ws.title="Review summary"
    ws.append(["CHECK","VALUE"])
    beam=report["beam"]
    for k,v in beam.items():
        if k=="issues":v=" | ".join(v)
        ws.append([k,json.dumps(v) if isinstance(v,(dict,list)) else v])
    ws.append(["STRUCTURAL ACCEPTANCE","NOT VALIDATED"])
    if "foundation" in report:
        for name,rows in [
            ("Foundation regions",report["foundation"]["rows"]),
            ("Original support points",report["foundation"]["original_individual_rows"])]:
            sheet=book.create_sheet(name)
            if not rows:continue
            fields=list(rows[0])
            sheet.append(fields)
            for row in rows:
                sheet.append([row.get(k) for k in fields])
    for sheet in book.worksheets:
        sheet.freeze_panes="A2"
        sheet.auto_filter.ref=sheet.dimensions
        for cell in sheet[1]:
            cell.font=Font(bold=True,color="FFFFFF")
            cell.fill=PatternFill("solid",fgColor="234264")
        sheet.column_dimensions["A"].width=32
        sheet.column_dimensions["B"].width=36
    result=Path(folder)/"GRAVITY_SAFE_REVIEW.xlsx"
    book.save(result)
    return result


def launch_gui():
    """Spyder-compatible file-selection UI; audit is read-only by default.

    [REF docs/source/Gravity_Safe_Engineering_Review_V1.py.md]
    """
    try:
        import tkinter as tk
        from tkinter import filedialog,messagebox,ttk
    except ImportError as exc:
        raise RuntimeError("Tkinter unavailable: run the documented command-line interface") from exc
    win=tk.Tk()
    win.title("ETABS / OpenSees — Safe Gravity Engineering Review V1")
    win.geometry("1010x690")
    frame=ttk.Frame(win,padding=14);frame.pack(fill="both",expand=True)
    export=tk.StringVar()
    beam_csv=tk.StringVar()
    node_json=tk.StringVar()
    region_csv=tk.StringVar()
    base=tk.StringVar()
    lines=[
        ("OpenSees source export folder",export,True),
        ("ETABS Material List Beam CSV",beam_csv,False),
        ("Full 76-point comparison JSON (optional)",node_json,False),
        ("Verified region map CSV (optional)",region_csv,False),
        ("ETABS base FZ in kN (optional)",base,None)]
    for ix,(label,var,kind) in enumerate(lines):
        ttk.Label(frame,text=label).grid(row=ix,column=0,sticky="w",pady=6)
        ttk.Entry(frame,textvariable=var,width=92).grid(
            row=ix,column=1,sticky="ew",padx=6)
        if kind is not None:
            def browse(v=var,directory=kind):
                found=(filedialog.askdirectory() if directory else
                       filedialog.askopenfilename(
                           filetypes=[("CSV / JSON evidence","*.csv *.json"),
                                      ("All files","*.*")]))
                if found:v.set(found)
            ttk.Button(frame,text="Browse...",command=browse).grid(
                row=ix,column=2,padx=4)
    frame.columnconfigure(1,weight=1)
    text=tk.Text(frame,wrap="word",height=21,font=("Consolas",10))
    text.grid(row=7,column=0,columnspan=3,sticky="nsew",pady=12)
    frame.rowconfigure(7,weight=1)
    def show(msg):
        text.delete("1.0","end")
        text.insert("end",msg)
        text.see("1.0")
    current=[None]
    def audit():
        try:
            if not export.get().strip():raise ValueError("Select source export folder")
            if not beam_csv.get().strip():raise ValueError("Independent ETABS Material List beam CSV required")
            path=Path(export.get()).expanduser().resolve()
            n=node_json.get().strip() or None
            m=region_csv.get().strip() or None
            e=finite(base.get(),"ETABS base reaction") if base.get().strip() else None
            folder,report=review(path,etabs_beam_csv=beam_csv.get(),
                                 node_comparison=n,region_csv=m,etabs_base_kN=e)
            xlsx=_write_optional_excel(folder,report)
            current[0]=folder/"GRAVITY_SAFE_REVIEW.json"
            show((folder/"GRAVITY_SAFE_REVIEW.txt").read_text(encoding="utf8")+
                "\nREVIEW DATA: "+str(current[0])+
                "\nEXCEL: "+str(xlsx or "openpyxl not installed")+
                "\n\nSource config NOT modified.")
        except Exception as exc:
            show("AUDIT BLOCKED: "+repr(exc))
            messagebox.showerror("Audit blocked",str(exc),parent=win)
    def template():
        try:
            if not node_json.get().strip():raise ValueError("Choose 76-point comparison JSON")
            out=(Path(export.get()).expanduser().resolve()/
                 "Gravity_Safe_Engineering_Review"/"FOUNDATION_REGION_TEMPLATE_UNVERIFIED.csv")
            target=make_region_template(node_json.get(),out)
            show("Created UNVERIFIED template:\n"+str(target)+
                 "\nFill all 76 region IDs and source geometry basis; set verified=YES only after reviewing the original ETABS wall/column layout.")
        except Exception as exc:messagebox.showerror("Template error",str(exc),parent=win)
    def stage():
        try:
            if current[0] is None:
                raise ValueError("Audit the source model first")
            if not messagebox.askyesno("Engineering approval required",
                  "You have checked the ORIGINAL ETABS source material list, "
                  "all beam end offsets, beam Self Weight Option, section insertion "
                  "locations and the double-subtraction guard.\n\n"
                  "Stage a NEW proposed config only (do NOT alter production)?",
                  parent=win):
                return
            target=stage_candidate(export.get(),current[0],
                approval_text="I REVIEWED ETABS BEAM SELF WEIGHT AND SOURCE GEOMETRY")
            show("PROPOSED CONFIG CREATED:\n"+str(target)+
                 "\n\nOriginal model, loads, supports and config unchanged.\n"
                 "Review APPLY_INSTRUCTIONS.txt before rebuilding.")
        except Exception as exc:
            messagebox.showerror("Cannot stage candidate",str(exc),parent=win)
    bar=ttk.Frame(frame);bar.grid(row=6,column=0,columnspan=3,sticky="w",pady=10)
    ttk.Button(bar,text="1. AUDIT (read only)",command=audit).pack(side="left",padx=5)
    ttk.Button(bar,text="Create unverified region template",command=template).pack(side="left",padx=5)
    ttk.Button(bar,text="2. Stage reviewed candidate",command=stage).pack(side="left",padx=5)
    ttk.Label(frame,text="A numerical match is not structural acceptance. "
              "This program never changes source EDB, stiffness, supports or production loads.",
              foreground="#a43a27",wraplength=940).grid(
              row=5,column=0,columnspan=3,sticky="w")
    win.mainloop()


def main(argv=None):
    parser=argparse.ArgumentParser(description="Conservative ETABS/OpenSees gravity source reviewer")
    parser.add_argument("--export",required=True,help="ETABS->OpenSees source export folder")
    parser.add_argument("--etabs-beam-csv",help="Material List by Object Type as CSV with object_type,weight_kN")
    parser.add_argument("--etabs-beam-kn",type=float,help="User-entered exploratory value; NOT independent evidence")
    parser.add_argument("--foundation-map",help="Explicit reviewed source ETABS point->region CSV")
    parser.add_argument("--node-comparison",help="Gravity_Node_Reaction_Comparison.json")
    parser.add_argument("--etabs-base-kn",type=float)
    parser.add_argument("--stage-reviewed-candidate",action="store_true")
    parser.add_argument("--approval-text",default="")
    args=parser.parse_args(argv)
    out,report=review(args.export,etabs_beam_csv=args.etabs_beam_csv,
        etabs_beam_kN=args.etabs_beam_kn,region_csv=args.foundation_map,
        node_comparison=args.node_comparison,etabs_base_kN=args.etabs_base_kn)
    print((out/"GRAVITY_SAFE_REVIEW.txt").read_text(encoding="utf-8"))
    if args.stage_reviewed_candidate:
        target=stage_candidate(args.export,out/"GRAVITY_SAFE_REVIEW.json",
                               approval_text=args.approval_text)
        print("Candidate staged (source unchanged):",target)
    return 0


if __name__=="__main__":
    import sys
    if len(sys.argv)==1 or any(a.startswith("--ip=") for a in sys.argv[1:]):
        launch_gui()
    else:
        raise SystemExit(main())

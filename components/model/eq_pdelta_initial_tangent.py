"""Opt-in, isolated diagnostic of ETABS nonlinear initial -> tangent EQ case.

NOT a replacement for existing ESM, modal, MRSM or NLTHA.
Use on a newly verified corrected BEAM_CLEAR source model only.
Runs both phases in one live OpenSees domain; no re-build between phases.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import os
from pathlib import Path

IS_INITIAL={"Self Weight":1.2,"Floor Finish":1.2,"Partition":1.2,
            "Wall":1.2,"Live":0.5,"Roof Live":0.0}
SOURCE_PATTERNS=set(IS_INITIAL)

def _digest(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for data in iter(lambda:f.read(1024*1024),b""):h.update(data)
    return h.hexdigest()

def _read_force_rows(file, axis):
    file=Path(file)
    with file.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        fields={"story_name","height_m","master_node_tag",
                "lateral_force_kN","torsional_moment_kNm"}
        if not fields<=set(reader.fieldnames or []):
            raise ValueError("ESM source force CSV missing "+str(fields-set(reader.fieldnames or [])))
        rows=[]
        for r in reader:
            if r.get("limit_state") and r["limit_state"]!="ULS":
                raise ValueError("For this native ULS case, select ULS force CSV")
            node=int(r["master_node_tag"])
            height=float(r["height_m"])
            lateral=float(r["lateral_force_kN"])
            torsion=float(r["torsional_moment_kNm"])
            if node<=0 or not all(math.isfinite(x) for x in (height,lateral,torsion)):
                raise ValueError("Invalid story/master source input")
            rows.append(dict(story_name=str(r["story_name"]),node=node,
                             z=height,fx=lateral if axis=="X" else 0.,
                             fy=lateral if axis=="Y" else 0.,mz=torsion))
    if not rows or any(rows[i]["z"]>=rows[i+1]["z"] for i in range(len(rows)-1)):
        raise ValueError("ESM stories must be ordered bottom-to-top")
    if len({r["node"] for r in rows})!=len(rows):
        raise ValueError("Duplicate diaphragm master node")
    if abs(sum(r["fx"] if axis=="X" else r["fy"] for r in rows))<=1e-8:
        raise ValueError("No earthquake force in selected direction")
    return rows

def audit_inputs(folder,esm_csv,etabs_joint_table,axis):
    """Fail closed before importing/running OpenSees if evidence incomplete.
    [REF docs/source/components/model/eq_pdelta_initial_tangent.py.md]
    """
    axis=str(axis).upper()
    if axis not in ("X","Y"):raise ValueError("X/Y required")
    source=Path(folder).resolve()
    native=source/"ETABS_Native_Assignment_Gravity_Quantity_Audit.json"
    cfg=source/"OpenSees_Complete_Model_Config_V118.json"
    data=source/"OpenSees_Complete_Model_Data_V118.json"
    topology=source/"OpenSees_Element_Connectivity.json"
    proof=[cfg,data,topology,native,Path(esm_csv),Path(etabs_joint_table)]
    for file in proof:
        if not file.is_file():raise FileNotFoundError(file)
    config=json.loads(cfg.read_text(encoding="utf-8-sig"))
    native_proof=json.loads(native.read_text(encoding="utf-8-sig"))
    if (config.get("etabs_beam_weight_policy")!="ETABS_BEAM_CLEAR_LENGTH"
        or config.get("etabs_clear_beam_weight_confirmed") is not True
        or config.get("joint_volume_weight_policy")!="AUDIT_ONLY"):
        raise ValueError("Re-export verified native clear-beam weight source; no RCC union deduction")
    if (native_proof.get("opensees_beam_crosswalk_status")!=
            "SOURCE_IDS_OFFSETS_AND_TOTAL_MATCH"
        or native_proof.get("clear_candidate_matches_native_quantity") is not True):
        raise ValueError("Missing confirmed native ETABS beam quantity proof")
    parsed=json.loads(data.read_text(encoding="utf-8-sig"))
    patterns=parsed.get("unfactored_patterns")
    if not isinstance(patterns,dict) or not patterns:
        raise ValueError("Unfactored load pattern evidence missing")
    unknown=set(patterns)-SOURCE_PATTERNS
    if unknown:raise ValueError("Unclassified native initial load patterns: "+repr(sorted(unknown)))
    if not {"Self Weight","Floor Finish","Partition","Wall","Live"}<=set(patterns):
        raise ValueError("Native 1.2D+0.5IL pattern components incomplete")
    if any(not all(math.isfinite(float(x)) for x in vector)
           for loads in patterns.values()
           for vector in loads.values()):
        raise ValueError("Nonfinite source gravity force")
    rows=_read_force_rows(esm_csv,axis)
    model_nodes={int(n) for n in parsed["nodes"]}
    if any(r["node"] not in model_nodes for r in rows):
        raise ValueError("ESM master nodes not found in assembled source")
    return dict(axis=axis,source_dir=str(source),
                rows=rows,source_patterns=patterns,
                original_model_hashes={p.name:_digest(p) for p in proof},
                native_proof_name=native.name,
                analysis_scope="ELASTIC_PDELTA_DIAGNOSTIC_NOT_NATIVE_ETABS_EQUIVALENCE")

def run_source_equivalent_initial_and_tangent(
        folder, esm_csv, etabs_joint_table, axis,output_dir):
    """Same-domain nonlinear initial then one-step tangent unit-EQ increment.

    Source initial load: 1.2(SelfWeight+FloorFinish+Partition+Wall)
    + 0.5 Live + 1.5 signed EQ. Subsequent EQ increment has factor 1.0
    about tangent at the previously converged initial state.
    
    [REF docs/source/components/model/eq_pdelta_initial_tangent.py.md]
    """
    pre=audit_inputs(folder,esm_csv,etabs_joint_table,axis)
    out=Path(output_dir).resolve()
    out.mkdir(parents=True,exist_ok=False)
    (out/"EQ_PDelta_Input_Audit.json").write_text(
        json.dumps({k:v for k,v in pre.items() if k!="source_patterns"},
                   indent=2),encoding="utf-8")
    from OpenSees_Complete_Export_V118 import build_complete_model
    import openseespy.opensees as ops
    old={key:os.environ.get(key) for key in (
        "OPENSEES_GRAVITY_PROFILE","OPENSEES_GRAVITY_GUI_MODE",
        "OPENSEES_GRAVITY_WALL_SUPPORT_STRATEGY",
        "OPENSEES_GRAVITY_ETABS_TABLE","OPENSEES_GRAVITY_AUDIT_DIR")}
    try:
        os.environ.update({
            "OPENSEES_GRAVITY_PROFILE":"AS_CONFIGURED",
            "OPENSEES_GRAVITY_GUI_MODE":"1",
            "OPENSEES_GRAVITY_WALL_SUPPORT_STRATEGY":"ETABS_NONZERO_REACTION_DIAGNOSTIC",
            "OPENSEES_GRAVITY_ETABS_TABLE":str(Path(etabs_joint_table).resolve()),
            "OPENSEES_GRAVITY_AUDIT_DIR":str(out)})
        built=build_complete_model(Path(folder).resolve(),
                                   mode="elastic",preload=False,limit_state="ULS")
    finally:
        for key,value in old.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value
    tags=built["gravity_base_support_tags"]
    if len(tags)!=32 or built["gravity_support_strategy"]!="ETABS_NONZERO_REACTION_DIAGNOSTIC":
        raise RuntimeError("Expected exactly 32 source-mapped primary support nodes")
    patterns=pre["source_patterns"]
    # Replace the model's as-configured initial patterns, not its geometry,
    # mass, stiffness, restraints or source-assigned elements.
    for tag in range(700001,700001+len(patterns)):
        ops.remove("loadPattern",tag)
    ops.timeSeries("Linear",971001)
    ops.pattern("Plain",971001,971001)
    gravity_vertical=0.
    for pattern,nodes in patterns.items():
        factor=IS_INITIAL[pattern]
        if factor==0:continue
        for tag,vector in nodes.items():
            vals=[float(factor)*float(v) for v in vector]
            ops.load(int(tag),*vals)
            gravity_vertical-=vals[2]
    for row in pre["rows"]:
        ops.load(row["node"],1.5*row["fx"],1.5*row["fy"],0.,0.,0.,1.5*row["mz"])
    ops.wipeAnalysis()
    ops.constraints("Transformation");ops.numberer("RCM");ops.system("UmfPack")
    ops.test("NormDispIncr",1e-8,50)
    ops.algorithm("Newton");ops.integrator("LoadControl",0.05)
    ops.analysis("Static")
    for step in range(20):
        if ops.analyze(1)!=0:
            raise RuntimeError("Initial PDelta FAILED at step "+str(step+1))
    if abs(float(ops.getLoadFactor(971001))-1.)>1e-8:
        raise RuntimeError("Initial nonlinear PDelta not fully applied")
    dof=1 if pre["axis"]=="X" else 2
    ops.reactions()
    initial_reactions={tag:float(ops.nodeReaction(tag,dof)) for tag in tags}
    initial_reactions_full={
        tag:[float(ops.nodeReaction(tag,j)) for j in range(1,7)]
        for tag in tags}
    initial_displacements={row["node"]:float(ops.nodeDisp(row["node"],dof))
                           for row in pre["rows"]}
    initial_state={
        "initial_gravity_downward_kN":gravity_vertical,
        "initial_lateral_load_kN":1.5*sum(
            row["fx"] if pre["axis"]=="X" else row["fy"] for row in pre["rows"]),
        "initial_support_reaction_kN":sum(initial_reactions.values()),
        "initial_roof_displacement_m":initial_displacements[pre["rows"][-1]["node"]],
        "initial_steps":20,
    }
    ops.loadConst("-time",0.0) # freeze initial gravity AND signed EQ loads
    ops.timeSeries("Linear",971002)
    ops.pattern("Plain",971002,971002)
    for row in pre["rows"]:
        ops.load(row["node"],row["fx"],row["fy"],0.,0.,0.,row["mz"])
    ops.wipeAnalysis()
    ops.constraints("Transformation");ops.numberer("RCM");ops.system("UmfPack")
    # Linear CURRENT tangent, never -initial or -factorOnce.
    # One step avoids recalculating a new nonlinear tangent as the EQ grows.
    ops.algorithm("Linear");ops.integrator("LoadControl",1.0)
    ops.analysis("Static")
    if ops.analyze(1)!=0:
        raise RuntimeError("Unit EQ tangent-step solve FAILED")
    if abs(float(ops.getLoadFactor(971002))-1.)>1e-8:
        raise RuntimeError("Dependent unit EQ not fully applied")
    ops.reactions()
    support_rows=[]
    for n in tags:
        diff=[float(ops.nodeReaction(n,j))-initial_reactions_full[n][j-1]
              for j in range(1,7)]
        support_rows.append(dict(
            node_tag=n,Fx_kN=diff[0],Fy_kN=diff[1],Fz_kN=diff[2],
            Mx_kNm=diff[3],My_kNm=diff[4],Mz_kNm=diff[5],
            scope="Signed incremental unit-EQ reactions minus initial PDelta state"))
    reaction=sum(float(ops.nodeReaction(n,dof))-initial_reactions[n]
                 for n in tags)
    force=sum(row["fx"] if dof==1 else row["fy"] for row in pre["rows"])
    error=100*abs(reaction+force)/max(abs(force),1e-9)
    if not math.isfinite(error) or error>0.1:
        raise RuntimeError("Dependent tangent EQ signed base equilibrium FAILED "+
                           f"{error:.6f}%")
    profiles=[]
    previous_u=0.;previous_z=0.
    for i,row in enumerate(pre["rows"]):
        now=float(ops.nodeDisp(row["node"],dof))
        du=now-initial_displacements[row["node"]]
        height=row["z"]-previous_z
        drift=(du-previous_u)/height
        applied_story_shear=sum(
            r["fx"] if dof==1 else r["fy"] for r in pre["rows"][i:])
        profiles.append(dict(story_name=row["story_name"],elevation_m=row["z"],
            displacement_m=du,drift_ratio=drift,
            applied_story_shear_kN=applied_story_shear,
            recovered_story_shear_kN=None,
            actual_recovered_section_cut_status="NOT_IMPLEMENTED",
            source_master_node_tag=row["node"]))
        previous_z=row["z"];previous_u=du
    report={
        "schema":"opensees-eq-pdelta-initial-tangent-diagnostic-v1",
        "axis":pre["axis"],
        "initial_stage":initial_state,
        "dependent_linear_increment":{
            "signed_base_shear_kN":-reaction,
            "signed_applied_floor_force_kN":force,
            "signed_equilibrium_error_percent":error,
            "roof_displacement_increment_m":profiles[-1]["displacement_m"],
            "roof_drift_ratio":profiles[-1]["drift_ratio"],
            "unit_eq_load_factor":float(ops.getLoadFactor(971002))},
        "source_hashes":pre["original_model_hashes"],
        "source_support_nodes":tags,
        "initial_stage_preserved_same_domain":True,
        "current_tangent_linear_algorithm":True,
        "analysis_model":"ELASTIC_SHELL_PDELTA_FRAME_DIAGNOSTIC",
        "native_etabs_tangent_equivalence":"NOT_VALIDATED",
        "source_earthquake_forces_need_ETABS_NBC_Aw_T1_crosscheck":True,
        "sensitivity_only_32_supports":True,
        "results":profiles,
    }
    (out/"EQ_PDelta_OpenSees_Support_Reactions.csv").write_text(
        "",encoding="utf-8") if not support_rows else None
    if support_rows:
        with (out/"EQ_PDelta_OpenSees_Support_Reactions.csv").open(
                "w",encoding="utf-8-sig",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(support_rows[0]))
            writer.writeheader();writer.writerows(support_rows)
    report["incremental_support_reactions_file"] = str(
        out/"EQ_PDelta_OpenSees_Support_Reactions.csv")
    (out/"EQ_PDelta_OpenSees_Tangent_Results.json").write_text(
        json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    with (out/"EQ_PDelta_OpenSees_Story_Responses.csv").open(
            "w",encoding="utf-8-sig",newline="") as f:
        keys=list(profiles[0])
        writer=csv.DictWriter(f,fieldnames=keys)
        writer.writeheader();writer.writerows(profiles)
    try:
        from openpyxl import Workbook
        wb=Workbook();ws=wb.active;ws.title="EQ PDelta summary"
        ws.append(["Field","Value"])
        for section in ("initial_stage","dependent_linear_increment"):
            ws.append([section,""])
            for key,value in report[section].items():
                ws.append([key,value])
        for name,entries in (
                ("Raw story response",profiles),
                ("Incremental supports",support_rows)):
            sheet=wb.create_sheet(name)
            if entries:
                keys=list(entries[0]);sheet.append(keys)
                for entry in entries:sheet.append([entry.get(k) for k in keys])
            sheet.freeze_panes="A2"
        readme=wb.create_sheet("Scope and blockers")
        readme.append(["Native ETABS/PDelta equivalence","NOT VALIDATED"])
        readme.append(["Recovered internal story section cuts","NOT IMPLEMENTED"])
        readme.append(["Existing M0–M6 NLTHA state","UNCHANGED"])
        readme.append(["Initial stage tangent reused","Same domain; current tangent Linear algorithm"])
        wb.save(out/"EQ_PDelta_OpenSees_Tangent_Results.xlsx")
    except ImportError:
        pass
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig,axs=plt.subplots(1,3,figsize=(15,6),constrained_layout=True)
        z=[p["elevation_m"] for p in profiles]
        axs[0].plot([p["applied_story_shear_kN"] for p in profiles],z,"o-")
        axs[0].set(xlabel="Cumulative applied EQ force (kN)",
                   ylabel="Height (m)",title="LOAD INPUT, not internal story shear")
        axs[1].plot([1000*p["displacement_m"] for p in profiles],z,"o-")
        axs[1].set(xlabel="Raw incremental displacement (mm)",
                   ylabel="Height (m)",title="Same-domain dependent tangent response")
        axs[2].plot([100*p["drift_ratio"] for p in profiles],z,"o-")
        axs[2].set(xlabel="Signed raw interstory drift (%)",
                   ylabel="Height (m)",title="Diaphragm master drift")
        for ax in axs:ax.grid(alpha=0.3)
        fig.suptitle("OpenSees "+pre["axis"]+" PDelta tangent DIAGNOSTIC - ETABS equality unverified")
        fig.savefig(out/"EQ_PDelta_OpenSees_Tangent_Profiles.png",dpi=150)
        plt.close(fig)
    except ImportError:
        pass
    return report

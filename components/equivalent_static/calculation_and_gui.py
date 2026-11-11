# -*- coding: utf-8 -*-
"""NBC 105:2025 equivalent-static seismic weight and floor force calculator.

Input: ETABS converter story-weight CSV or verified user CSV. Geometry/master-node
metadata are linked to the ETABS export folder. Modal periods can be read from
the active ETABS API session after running a modal case.
The dead/live totals must be independently verified against the project model; this GUI never guesses or extracts them.
Outputs: calculation JSON, storey force CSV, and an OpenSeesPy lateral-load
runner. The runner needs a separately verified structural model already built.
"""
from __future__ import annotations

__release__ = '134'
from OpenSees_Timing_V130 import timed_outputs
import csv, json, math, os, sys, time, traceback, subprocess, threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

HERE=Path(__file__).resolve().parent
from components.inputs.project_workbooks import analysis_output_folder
try:
    from NBC105_Analysis_Settings_V109 import (
        NBC105_ESM_SYSTEM_FACTORS, calculate_esm,
    )
except Exception as exc:
    raise RuntimeError("Keep NBC105_Analysis_Settings_V109.py beside this GUI.") from exc



def resolve_esm_state_periods(*, height_m, aw_by_axis, factor, states,
                              rayleigh_by_state):
    """Calculate NBC 105 §5.1 adopted periods from case-specific Rayleigh evidence.

    A ULS Rayleigh period cannot be silently reused for a separately modeled
    SLS stiffness state. Workbook-adopted references are not Rayleigh results.
    Values in seconds and wall indices in square metres.
    """
    h=float(height_m)
    fac=float(factor)
    if not all(math.isfinite(x) and x>0 for x in (h,fac)):
        raise ValueError("ESM height and empirical factor must be finite positive.")
    results={}
    for state in states:
        state=str(state).upper()
        if state not in ("ULS","SLS"):
            raise ValueError("Unsupported ESM limit state: "+state)
        record=rayleigh_by_state.get(state,{})
        results[state]={}
        for axis in ("X","Y"):
            area=float(aw_by_axis[axis])
            if not math.isfinite(area) or area<=0:
                raise ValueError(f"{state} {axis}: wall Aw must be finite and positive.")
            raw=record.get(axis)
            if raw is None or str(raw).strip()=="":
                raise ValueError(f"{state} {axis}: matching limit-state Rayleigh period is required; do not reuse the other state's period.")
            ray=float(raw)
            if not math.isfinite(ray) or ray<=0:
                raise ValueError(f"{state} {axis}: Rayleigh period must be finite positive.")
            empirical=fac*.075*h**.75/math.sqrt(area)
            results[state][axis]=min(empirical,ray)
    return results


def validated_pdelta_sidecar_path(model_script):
    """Return the legacy P-Delta sidecar only for an existing explicit model.

    A blank/invalid GUI model path previously resolved to Path('').parent == '.'
    and wrote OpenSees_Initial_PDelta_Input_V124.json into the current process
    working directory. This can overwrite an unrelated source file. Returning
    None preserves standalone ESM calculation without creating that sidecar.
    """
    value=str(model_script or "").strip()
    if not value:
        return None
    model=Path(value)
    if not model.is_file() or model.suffix.lower()!=".py":
        return None
    return model.parent/"OpenSees_Initial_PDelta_Input_V124.json"


def state_rayleigh_provenance(state, selected_axis, gui_by_axis, sls_by_axis=None):
    """Give each exported case its matching state-specific X/Y Rayleigh metadata.

    Does not generate a period or substitute ETABS modal data. For SLS in a
    joint export, use only independently imported source-matched SLS values.
    """
    selected=str(state).strip().upper()
    if selected not in ("ULS","SLS"):
        raise ValueError("Unknown ESM limit state")
    source=sls_by_axis if selected=="SLS" and sls_by_axis is not None else gui_by_axis
    if not isinstance(source,dict):
        raise ValueError("No period metadata dictionary")
    return {"Rayleigh_T1_X_s":source.get("X") or None,
            "Rayleigh_T1_Y_s":source.get("Y") or None,
            "Rayleigh_evidence_state":selected,
            "Rayleigh_evidence_axis":selected_axis}



def recommended_story_weight_input(export_dir):
    """Choose a complete story ledger only when tags match the current model.

    This verifies import consistency, NOT seismic mass or NBC compliance.
    Original exports are never modified.
    """
    export_dir=Path(export_dir)
    manual=export_dir/'NBC105_ESM_Story_Weights_Input_V108.csv'
    assembled=export_dir/'NBC105_ESM_Story_Weights_Assembled_V118.csv'
    model_path=export_dir/'OpenSees_Complete_Model_Data_V118.json'
    if not (assembled.is_file() and model_path.is_file()):
        return (manual if manual.is_file() else None,
                'No complete model-linked ledger; select verified story weights')
    try:
        with assembled.open(newline='',encoding='utf-8-sig') as f:
            rows=[r for r in csv.DictReader(f) if str(r.get('story_number','')).strip()]
        data=json.loads(model_path.read_text(encoding='utf-8-sig'))
        diaphragms=data['diaphragms']
        if not rows or len(rows)!=len(diaphragms):
            raise ValueError('assembled ledger story count differs from current model')
        current={(int(r['story_number']),int(r['master_node_tag'])) for r in rows}
        source={(int(d['storey_number']),int(d['master_tag'])) for d in diaphragms}
        if len(current)!=len(rows) or current!=source:
            raise ValueError('assembled ledger diaphragm tags differ from current model')
        for i,r in enumerate(rows,2):
            for k in ('height_m','dead_load_kN','storage_live_load_kN','other_live_load_kN'):
                v=float(r[k])
                if not math.isfinite(v) or v<0:
                    raise ValueError(f'invalid {k} at assembled ledger row {i}')
        return assembled,('Assembled story-weight ledger selected: model diaphragm tags match; '
            'independently review ETABS gravity/live-load components and seismic mass')
    except (OSError,ValueError,TypeError,KeyError,OverflowError) as exc:
        return (manual if manual.is_file() else None,
                'Assembled ledger rejected ('+str(exc)+'); regenerate/review export')


def read_story_csv(path):
    rows=[]
    with open(path, newline="", encoding="utf-8-sig") as f:
        for line, r in enumerate(csv.DictReader(f),2):
            if not str(r.get("story_number","")).strip():
                continue
            for key in ("height_m","dead_load_kN","storage_live_load_kN","other_live_load_kN"):
                value=str(r.get(key,"")).strip()
                if not value:
                    raise ValueError(f"CSV row {line}: {key} is blank; enter verified ETABS data.")
                try: r[key]=float(value)
                except ValueError as e: raise ValueError(f"CSV row {line}: {key} must be numeric.") from e
            tag=str(r.get("master_node_tag","")).strip()
            r["master_node_tag"]=int(tag) if tag else None
            if not r["master_node_tag"]:
                raise ValueError(f"CSV row {line}: no unique rigid-diaphragm master node tag; resolve the mapping before force export.")
            r["story_number"]=int(r["story_number"])
            r["story_name"]=str(r.get("story_name",r["story_number"]))
            # Table 5-1 makes roof live load nil in seismic weight regardless
            # of the entered audit field. Preserve it only as a visible note.
            roof=str(r.get("roof_live_load_kN_ignored","")).strip()
            r["roof_live_load_kN_ignored"]=float(roof) if roof else 0.0
            rows.append(r)
    if not rows: raise ValueError("No storey rows were found in the selected CSV.")
    tags=[r["master_node_tag"] for r in rows]
    if len(set(tags)) != len(tags): raise ValueError("Each storey must have a unique diaphragm master-node tag.")
    return rows


def safe_write(path, text):
    Path(path).write_text(text,encoding="utf-8",newline="")


@timed_outputs('Equivalent-static calculations and case export','outdir')
def write_outputs(template_path, rows, result, direction, polarity, accidental, breadth, outdir, model_script=""):
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True)
    ecc_case=(f"E{'+' if int(breadth[1])>0 else '-'}" if accidental and int(breadth[1])!=0 else "E0")
    suffix=f"{result['limit_state']}_{direction}{'+' if polarity>0 else '-'}_{ecc_case}"
    result["response_case"]=suffix
    report=dict(result)
    report["comparison_remark"] = result["esm_eligibility"] if not result.get("code_eligible",True) else "Eligible ESM case"
    report["direction_case"]=suffix
    report["accidental_torsion_included"]=bool(accidental and int(breadth[1])!=0)
    report["accidental_eccentricity_sign"]=int(breadth[1]) if accidental else 0
    report["accidental_eccentricity_m"]=0.05*float(breadth[0])*abs(int(breadth[1])) if accidental else 0.0
    report["note"]="Story gravity totals are user-verified ETABS inputs. Site subsoil status is reported separately; this calculation is not an independent code-compliance certification."
    out_json=out/f"NBC105_ESM_Calculation_{suffix}_V111.json"
    safe_write(out_json,json.dumps(report,indent=2,ensure_ascii=False))
    out_csv=out/f"NBC105_ESM_Storey_Forces_{suffix}_V111.csv"
    out_png=out/f"NBC105_ESM_Force_Profile_{suffix}_V111.png"
    out_xlsx=out/f"NBC105_ESM_Calculation_{suffix}_V111.xlsx"
    fields=["limit_state","location","z_source","soil_type","Vs30_m_s","soil_type_from_Vs30","N_SPT_blow_30cm","soil_type_from_N_SPT","site_subsoil_status","Z","story_number","story_name","master_node_tag","height_m","dead_load_kN","storage_live_load_kN","storage_factor","other_live_load_kN","other_live_factor","roof_live_load_kN_ignored","seismic_weight_kN","k","floor_force_kN","storey_shear_kN","lateral_force_kN","torsional_moment_kNm"]
    with open(out_csv,"w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for story_index,r in enumerate(result["stories"]):
            fx=r["lateral_force_kN"]*polarity
            e=0.05*float(breadth[0])*int(breadth[1]) if accidental else 0.0
            mz=(-fx*e if direction=="X" else fx*e) if accidental else 0.0
            w.writerow({"limit_state":result["limit_state"],"location":result.get("location_name",""),"z_source":result.get("zoning_factor_source",""),"soil_type":result["soil_type"],"Vs30_m_s":result.get("vs30_m_s"),"soil_type_from_Vs30":result.get("soil_type_from_vs30"),"N_SPT_blow_30cm":result.get("n_spt_blow_30cm"),"soil_type_from_N_SPT":result.get("soil_type_from_n_spt"),"site_subsoil_status":result["site_subsoil_status"],"Z":result["zoning_factor_Z"],"story_number":r["story_number"],"story_name":r["story_name"],"master_node_tag":r["master_node_tag"],"height_m":r["height_m"],"dead_load_kN":r["dead_load_kN"],"storage_live_load_kN":r["storage_live_load_kN"],"storage_factor":0.60,"other_live_load_kN":r["other_live_load_kN"],"other_live_factor":0.30,"roof_live_load_kN_ignored":r["roof_live_load_kN_ignored"],"seismic_weight_kN":r["seismic_weight_kN"],"k":r["distribution_exponent_k"],"floor_force_kN":r["lateral_force_kN"],"storey_shear_kN":sum(x["lateral_force_kN"] for x in result["stories"][story_index:]),"lateral_force_kN":fx,"torsional_moment_kNm":mz})
    # Immediate visualization and workbook for the NBC calculation, before
    # launching the OpenSees structural response runner.
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        floors=result["stories"]
        fig,ax=plt.subplots(1,2,figsize=(10,6),constrained_layout=True)
        ax[0].barh([r["height_m"] for r in floors],[r["lateral_force_kN"] for r in floors],height=max(0.15,0.35*min(r["height_m"] for r in floors)))
        ax[0].set(title="NBC 105:2025 floor forces",xlabel="Fi (kN)",ylabel="Height (m)"); ax[0].grid(axis="x",alpha=.25)
        ax[1].step([sum(x["lateral_force_kN"] for x in floors[i:]) for i in range(len(floors))],[r["height_m"] for r in floors],where="mid")
        ax[1].set(title="Cumulative applied floor force (NOT recovered story shear)",xlabel="Σ Fi above level (kN)",ylabel="Height (m)"); ax[1].grid(alpha=.25)
        fig.suptitle(f"{'COMPARISON ONLY | ' if not result.get('code_eligible',True) else ''}{result['limit_state']} {direction} | Z={result['zoning_factor_Z']:g} | soil {result['soil_type']} | V={result['base_shear_kN']:.3f} kN")
        fig.savefig(out_png,dpi=180); plt.close(fig)
    except ImportError:
        report.setdefault("optional_outputs",[]).append("Matplotlib unavailable: force-profile PNG not generated.")
    try:
        from openpyxl import Workbook
        wb=Workbook(); ws=wb.active; ws.title="NBC ESM Summary"
        for row in (("Item","Value"),("Standard",result["standard"]),("Limit state",result["limit_state"]),("Location",result.get("location_name","")),("Z source",result.get("zoning_factor_source","")),("Z",result["zoning_factor_Z"]),("Soil type",result["soil_type"]),("Vs,30 (m/s)",result.get("vs30_m_s")),("Soil type from Vs,30",result.get("soil_type_from_vs30")),("N-SPT (blows/30 cm)",result.get("n_spt_blow_30cm")),("Soil type from N-SPT",result.get("soil_type_from_n_spt")),("Site subsoil status",result["site_subsoil_status"]),("T1 (s)",result["period_s"]),("Ch(T1)",result["spectral_shape_Ch"]),("Cd(T1)",result["design_coefficient_Cd"]),("Seismic weight W (kN)",result["total_seismic_weight_kN"]),("Base shear V (kN)",result["base_shear_kN"]),("Exponent k",result["period_exponent_k"]),("ESM eligibility",result["esm_eligibility"])): ws.append(row)
        wf=wb.create_sheet("Storey Forces")
        with open(out_csv,newline="",encoding="utf-8-sig") as f:
            for row in csv.reader(f): wf.append(row)
        wb.save(out_xlsx)
    except ImportError:
        report.setdefault("optional_outputs",[]).append("openpyxl unavailable: calculation workbook not generated.")
        safe_write(out_json,json.dumps(report,indent=2,ensure_ascii=False))
    load_rows=[]
    e=0.05*float(breadth[0])*int(breadth[1]) if accidental else 0.0
    for r in result["stories"]:
        horizontal=polarity*r["lateral_force_kN"]
        fx,fy=(horizontal,0.0) if direction=="X" else (0.0,horizontal)
        mz=(-fx*e if direction=="X" else fy*e) if accidental else 0.0
        load_rows.append({"story_number":r["story_number"],"story_name":r["story_name"],"height_m":r["height_m"],"master_node_tag":int(r["master_node_tag"]),"Fx_kN":fx,"Fy_kN":fy,"Mz_kNm":mz})
    # This script assumes the verified structural domain is already in OpenSees,
    # and gravity has already been applied/committed if required by the model.
    script=[
        "# NBC 105:2025 equivalent-static lateral load case (generated by V111 earthquake-analysis GUI).",
        "# NBC 105:2025 source clauses: §§3.2.1, 4.1-4.2, 5.1-5.2, 5.5.1, 5.5.3, 5.6, 6.1-6.5; Tables 4-1, 5-1, 5-2, 6-1; Annex C/Table C-1.",
        "# REQUIRED: build the validated structural model first, with matching diaphragm master tags.",
        "# Freeze the verified gravity stage before running this lateral case. This file does not create slabs/walls/elements/materials.",
        "import json, openseespy.opensees as ops",
        "import os, csv, time, traceback, sys",
        "OUTPUT_DIR = "+repr(str(out.resolve())),
        "sys.path.insert(0,os.path.join(os.path.dirname("+repr(str(model_script))+"),'OpenSees_Runtime_V118'))",
        "sys.path.insert(0,"+repr(str(HERE))+")",
        "from OpenSees_Timing_V130 import StageTimer",
        "import atexit",
        "_processing_timer=StageTimer(OUTPUT_DIR,'Equivalent-static solver and response export')",
        "atexit.register(_processing_timer.finish)",
        "os.makedirs(OUTPUT_DIR, exist_ok=True)",
        "LOG_PATH = os.path.join(OUTPUT_DIR, 'NBC105_ESM_OpenSees_Run_'+"+repr(suffix)+"+'.log')",
        "_log_file = open(LOG_PATH,'w',encoding='utf-8')",
        "class _Tee:",
        "    def __init__(self,*streams): self.streams=streams",
        "    def write(self,text):",
        "        for s in self.streams: s.write(text); s.flush()",
        "    def flush(self): [s.flush() for s in self.streams]",
        "sys.stdout = _Tee(sys.__stdout__,_log_file); sys.stderr = _Tee(sys.__stderr__,_log_file)",
        "MODEL_BUILDER_SCRIPT = "+repr(str(Path(model_script).resolve()) if model_script else ""),
        "if not MODEL_BUILDER_SCRIPT: raise RuntimeError('Select a complete OpenSeesPy model builder in the earthquake-analysis GUI first.')",
        "if not os.path.isfile(MODEL_BUILDER_SCRIPT): raise FileNotFoundError(MODEL_BUILDER_SCRIPT)",
        "import runpy",
        "sys.path.insert(0, "+repr(str(HERE))+ ")",
        "sys.path.insert(0, os.path.join(os.path.dirname(MODEL_BUILDER_SCRIPT), 'OpenSees_Runtime_V118'))",
        "from OpenSees_Step13_Analysis_Basis_V115 import validate_initial_pdelta_results",
        "print('Building OpenSees model from:', MODEL_BUILDER_SCRIPT)",
        "MODEL_WORKDIR=os.path.dirname(MODEL_BUILDER_SCRIPT)",
        "os.chdir(MODEL_WORKDIR)",
        "from OpenSees_Initial_PDelta_V124 import ensure_initial_checks",
        "ensure_initial_checks(MODEL_WORKDIR)",
        "os.environ['OPENSEES_LIMIT_STATE'] = "+repr(result["limit_state"]),
        "_MODEL_NAMESPACE = runpy.run_path(MODEL_BUILDER_SCRIPT, run_name='__main__')",
        "IS16700_PDELTA_AUDIT = validate_initial_pdelta_results(_MODEL_NAMESPACE.get('IS16700_INITIAL_PDELTA_RESULTS'), lateral_actions=('EL',), directions=('X','Y'))",
        "print('Recorded independent signed IS16700 initial PDelta case evidence (fresh solver domains; not the tangent stiffness of ETABS dependent EQX/EQY case):', IS16700_PDELTA_AUDIT)",
        "os.chdir(OUTPUT_DIR)",
        "available_nodes=set(ops.getNodeTags())",
        "missing_masters=[row['master_node_tag'] for row in "+repr(load_rows)+" if row['master_node_tag'] not in available_nodes]",
        "if missing_masters: raise RuntimeError('Diaphragm master node(s) missing from model: '+str(missing_masters))",
        "ops.loadConst('-time', 0.0)  # after the required initial P-Delta stage, freeze the reviewed gravity state before this NBC ESM load case",
        "ESM_CASE = "+repr(suffix),
        "ESM_DIRECTION = "+repr(direction),
        "ESM_LOADS = "+repr(load_rows),
        "if any(ESM_LOADS[i]['height_m'] >= ESM_LOADS[i+1]['height_m'] for i in range(len(ESM_LOADS)-1)): raise RuntimeError('ESM story rows must have strictly increasing story elevation; drift and section-force reconstruction otherwise invalid')",
        "_run_started = time.perf_counter()",
        "ESM_LOAD_PATTERN_TAG = 98001",
        "ESM_TIME_SERIES_TAG = 98001",
        "# Model construction and gravity freeze are completed above, before creating this seismic pattern.",
        "DOF = 1 if ESM_DIRECTION == 'X' else 2",
        "MODEL_DATA_PATH=os.path.join(os.path.dirname(MODEL_BUILDER_SCRIPT),'OpenSees_Complete_Model_Data_V118.json')",
        "if not os.path.isfile(MODEL_DATA_PATH): raise FileNotFoundError('ESM reaction recording requires '+MODEL_DATA_PATH)",
        "with open(MODEL_DATA_PATH,encoding='utf-8-sig') as _stream: MODEL_DATA=json.load(_stream)",
        "ESM_SUPPORT_NODES=[int(n) for n,v in MODEL_DATA['supports'].items() if any(bool(x) for x in v[:3])]",
        "if not ESM_SUPPORT_NODES: raise ValueError('No support nodes found for ESM reaction recording')",
        "ops.reactions()",
        "BASE_REACTION_BEFORE_KN = sum(ops.nodeReaction(n, DOF) for n in ESM_SUPPORT_NODES)",
        "BASE_REACTIONS_BEFORE = {n:[float(ops.nodeReaction(n,j)) for j in range(1,7)] for n in ESM_SUPPORT_NODES}",
        "ALL_GRAVITY_U={n:list(ops.nodeDisp(n)) for n in ops.getNodeTags()}",
        "GRAVITY_BASELINE_U = {row['master_node_tag']: ops.nodeDisp(row['master_node_tag'], DOF) for row in ESM_LOADS}",
        "ops.timeSeries('Linear', ESM_TIME_SERIES_TAG)",
        "ops.pattern('Plain', ESM_LOAD_PATTERN_TAG, ESM_TIME_SERIES_TAG)",
        "for row in ESM_LOADS:",
        "    ops.load(row['master_node_tag'], row['Fx_kN'], row['Fy_kN'], 0.0, 0.0, 0.0, row['Mz_kNm'])",
        "ops.wipeAnalysis()",
        "ops.constraints('Transformation')  # required for rigidDiaphragm MP constraints",
        "ops.numberer('RCM')",
        "ops.system('UmfPack')",
        "ops.test('NormDispIncr', 1.0e-8, 50, 0)",
        "ops.algorithm('Newton')",
        "ops.integrator('LoadControl', 0.1)",
        "ops.analysis('Static')",
        "ESM_BASE_CURVE=[]",
        "def _record_esm_state():",
        "    ops.reactions()",
        "    reaction=sum(float(ops.nodeReaction(n,DOF)) for n in ESM_SUPPORT_NODES)-BASE_REACTION_BEFORE_KN",
        "    roof=max(ESM_LOADS,key=lambda x:float(x['height_m']))",
        "    ESM_BASE_CURVE.append({'load_factor':float(ops.getLoadFactor(ESM_LOAD_PATTERN_TAG)), 'time_s':float(ops.getTime()), 'base_shear_kN':-reaction, 'roof_displacement_m':float(ops.nodeDisp(roof['master_node_tag'],DOF)-GRAVITY_BASELINE_U[roof['master_node_tag']])})",
        "ok=0",
        "for _step in range(10):",
        "    ok=ops.analyze(1)",
        "    if ok != 0: break",
        "    _record_esm_state()",
        "if ok != 0:",
        "    ops.wipeAnalysis(); ops.constraints('Transformation'); ops.numberer('RCM'); ops.system('UmfPack')",
        "    ops.test('NormDispIncr', 1.0e-7, 100, 0); ops.algorithm('NewtonLineSearch')",
        "    ops.analysis('Static')",
        "    # Earlier successful steps remain committed. Advance only to factor 1.",
        "    ok = 0",
        "    for _recovery_step in range(21):",
        "        remaining = 1.0 - float(ops.getLoadFactor(ESM_LOAD_PATTERN_TAG))",
        "        if remaining <= 1.0e-10: break",
        "        ops.integrator('LoadControl', min(0.05, remaining))",
        "        ok = ops.analyze(1)",
        "        if ok != 0: break",
        "        _record_esm_state()",
        "if ok != 0:",
        "    raise RuntimeError(f'NBC ESM static analysis did not converge; OpenSees return code={ok}. Review model, sections, gravity state, constraints, and solver log.')",
        "if abs(float(ops.getLoadFactor(ESM_LOAD_PATTERN_TAG)) - 1.0) > 1.0e-8:",
        "    raise RuntimeError('ESM did not reach the intended load factor 1.0; response output suppressed.')",
        "ops.reactions()",
        "ESM_RESPONSE = []",
        "KD = "+repr(result["deflection_scale_factor_kd"]),
        "R_MU = "+repr(result["ductility_factor_R_mu"]),
        "LIMIT_STATE = "+repr(result["limit_state"]),
        "DRIFT_LIMIT = "+repr(result["drift_limit_ratio"]),
        "print('ESM REMARK:',"+repr(result["esm_eligibility"])+")",
        "PREV_U = 0.0; PREV_RAW = 0.0; PREV_H = 0.0",
        "for row in ESM_LOADS:",
        "    n = row['master_node_tag']; u_raw=ops.nodeDisp(n,DOF)-GRAVITY_BASELINE_U[n]",
        "    displacement_factor = (R_MU if LIMIT_STATE == 'ULS' else 1.0) * KD",
        "    u_design = u_raw * displacement_factor",
        "    story_h = row['height_m'] - PREV_H",
        "    raw_drift_signed = (u_raw-PREV_RAW)/story_h if story_h > 0 else float('nan')",
        "    elastic_drift = abs(u_raw-(PREV_U/((R_MU if LIMIT_STATE == 'ULS' else 1.0)*KD)))/story_h if story_h > 0 else float('nan')",
        "    drift_ratio = abs(u_design-PREV_U)/story_h if story_h > 0 else float('nan')",
        "    story_shear = sum(x['Fx_kN'] if ESM_DIRECTION == 'X' else x['Fy_kN'] for x in ESM_LOADS if x['height_m'] >= row['height_m'])",
        "    drift_m = abs(u_raw-(PREV_U/((R_MU if LIMIT_STATE == 'ULS' else 1.0)*KD)))",
        "    story_stiffness_kN_per_m = abs(story_shear)/drift_m if drift_m > 1.0e-15 else float('inf')",
        "    ESM_RESPONSE.append({**row, 'response_case':"+repr(suffix)+", 'U_elastic_m':u_raw, 'U_design_m':u_design, 'raw_signed_interstory_drift_ratio':raw_drift_signed, 'raw_abs_interstory_drift_ratio':abs(raw_drift_signed), 'raw_response_basis':'UNAMPLIFIED_INCREMENT_FROM_GRAVITY_BASELINE', 'story_height_m':story_h, 'elastic_drift_ratio':elastic_drift, 'design_drift_ratio':drift_ratio, 'story_shear_kN':story_shear, 'story_shear_basis':'SUM_OF_APPLIED_FLOOR_LOADS_NOT_RECOVERED_SECTION_CUT', 'etabs_dependent_nonlinear_stiffness_matched':False, 'story_stiffness_kN_per_m':story_stiffness_kN_per_m, 'drift_limit':DRIFT_LIMIT, 'drift_screen_pass':(drift_ratio <= DRIFT_LIMIT)})",
        "    PREV_U=u_design; PREV_RAW=u_raw; PREV_H=row['height_m']",
        "BASE_REACTION_KN = sum(ops.nodeReaction(n, DOF) for n in ESM_SUPPORT_NODES) - BASE_REACTION_BEFORE_KN",
        "APPLIED_BASE_SHEAR_KN = sum(row['Fx_kN'] if ESM_DIRECTION == 'X' else row['Fy_kN'] for row in ESM_LOADS)",
        "BASE_SHEAR_ERROR_PCT = abs(BASE_REACTION_KN + APPLIED_BASE_SHEAR_KN)/max(abs(APPLIED_BASE_SHEAR_KN),1.0e-12)*100.0",
        "if not (BASE_SHEAR_ERROR_PCT <= 0.1): raise RuntimeError(f'Signed incremental base reaction fails independent lateral equilibrium check: {BASE_SHEAR_ERROR_PCT:.6g}%')",
        "with open(os.path.join(OUTPUT_DIR,'NBC105_ESM_OpenSees_Response_'+ESM_CASE+'.json'),'w',encoding='utf-8') as f: json.dump(ESM_RESPONSE,f,indent=2)",
        "with open(os.path.join(OUTPUT_DIR,'NBC105_ESM_OpenSees_Response_'+ESM_CASE+'.csv'),'w',newline='',encoding='utf-8-sig') as f:",
        "    import csv; w=csv.DictWriter(f,fieldnames=list(ESM_RESPONSE[0]) if ESM_RESPONSE else []); w.writeheader(); w.writerows(ESM_RESPONSE)",
        # Independent per-node displacement ledger and explicit provenance.
        "import hashlib as _hashlib",
        "_hash=_hashlib.sha256()",
        "with open(MODEL_DATA_PATH,'rb') as _sf:",
        "    for _block in iter(lambda:_sf.read(1048576),b''): _hash.update(_block)",
        "_digest=_hash.hexdigest()",
        "ESM_META={'schema':'esm-response-source-v1','model_sha256':_digest,'limit_state':LIMIT_STATE,'axis':ESM_DIRECTION,'response_case':ESM_CASE,'story_shear_basis':'SUM_OF_APPLIED_FLOOR_LOADS_NOT_RECOVERED_SECTION_CUT','gravity_baseline_subtracted':True,'source_model':MODEL_DATA_PATH}",
        "with open(os.path.join(OUTPUT_DIR,'NBC105_ESM_OpenSees_Response_META_'+ESM_CASE+'.json'),'w',encoding='utf-8') as f: json.dump(ESM_META,f,indent=2)",
        "ESM_NODE_MAP={}",
        "TOPO_PATH=os.path.join(os.path.dirname(MODEL_BUILDER_SCRIPT),'OpenSees_Element_Connectivity.json')",
        "if os.path.isfile(TOPO_PATH):",
        "    with open(TOPO_PATH,encoding='utf-8-sig') as tf: topo=json.load(tf)",
        "    ESM_NODE_MAP={str(r['opensees_node_tag']):r.get('etabs_point_name') for r in topo.get('node_map',[]) if r.get('opensees_node_tag') is not None}",
        "ESM_ALL_NODE_ROWS=[]",
        "for node in ops.getNodeTags():",
        "    nid=int(node);cur=list(ops.nodeDisp(nid));init=ALL_GRAVITY_U[nid];xyz=MODEL_DATA['nodes'].get(str(nid),[None,None,None])",
        "    d=[float(cur[j])-float(init[j]) for j in range(3)]",
        "    ESM_ALL_NODE_ROWS.append(dict(opensees_node_tag=nid,etabs_point_name=ESM_NODE_MAP.get(str(nid)),x_m=xyz[0],y_m=xyz[1],z_m=xyz[2],du_x_m=d[0],du_y_m=d[1],du_z_m=d[2],design_du_x_m=d[0]*displacement_factor,design_du_y_m=d[1]*displacement_factor,response_case=ESM_CASE,limit_state=LIMIT_STATE,model_sha256=_digest))",
        "with open(os.path.join(OUTPUT_DIR,'NBC105_ESM_All_Node_Displacements_'+ESM_CASE+'.csv'),'w',newline='',encoding='utf-8-sig') as f:",
        "    import csv;writer=csv.DictWriter(f,fieldnames=list(ESM_ALL_NODE_ROWS[0]) if ESM_ALL_NODE_ROWS else ['opensees_node_tag']);writer.writeheader();writer.writerows(ESM_ALL_NODE_ROWS)",
        "ESM_BASE_CURVE_PATH=os.path.join(OUTPUT_DIR,'NBC105_ESM_BaseShear_RoofDisplacement_'+ESM_CASE+'.csv')",
        "with open(ESM_BASE_CURVE_PATH,'w',newline='',encoding='utf-8-sig') as f:",
        "    import csv; w=csv.DictWriter(f,fieldnames=['load_factor','time_s','base_shear_kN','roof_displacement_m']); w.writeheader(); w.writerows(ESM_BASE_CURVE)",
        "SUPPORT_REACTION_ROWS=[]",
        "for n in ESM_SUPPORT_NODES:",
        "    values=[float(ops.nodeReaction(n,j))-BASE_REACTIONS_BEFORE[n][j-1] for j in range(1,7)]",
        "    SUPPORT_REACTION_ROWS.append(dict(node_tag=n,Fx_kN=values[0],Fy_kN=values[1],Fz_kN=values[2],Mx_kNm=values[3],My_kNm=values[4],Mz_kNm=values[5]))",
        "with open(os.path.join(OUTPUT_DIR,'NBC105_ESM_Support_Reactions_'+ESM_CASE+'.csv'),'w',newline='',encoding='utf-8-sig') as f:",
        "    import csv; w=csv.DictWriter(f,fieldnames=list(SUPPORT_REACTION_ROWS[0]) if SUPPORT_REACTION_ROWS else ['node_tag']); w.writeheader(); w.writerows(SUPPORT_REACTION_ROWS)",
        "with open(os.path.join(OUTPUT_DIR,'Response_Recorder_Index_'+ESM_CASE+'.json'),'w',encoding='utf-8') as f: json.dump({'analysis':'equivalent_static','files':[{'name':os.path.basename(ESM_BASE_CURVE_PATH),'channels':['accepted load factor','base shear','roof displacement']},{'name':'NBC105_ESM_OpenSees_Response_'+ESM_CASE+'.csv','channels':['story displacement','story drift','story shear','secant story stiffness']},{'name':'NBC105_ESM_Support_Reactions_'+ESM_CASE+'.csv','channels':['incremental support forces and moments']},{'name':'NBC105_ESM_All_Node_Displacements_'+ESM_CASE+'.csv','channels':['every node displacement increment and ETABS original source ID']},{'name':'NBC105_ESM_OpenSees_Response_META_'+ESM_CASE+'.json','channels':['model SHA256 and response provenance']}],'notes':['The base-shear/roof-displacement curve is the converged linear static load-control path, not a nonlinear pushover capacity curve.']},f,indent=2)",
        "try:",
        "    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt",
        "    fig, ax=plt.subplots(1,5,figsize=(20,6),constrained_layout=True); h=[r['height_m'] for r in ESM_RESPONSE]",
        "    ax[0].barh(h,[r['Fx_kN'] if ESM_DIRECTION=='X' else r['Fy_kN'] for r in ESM_RESPONSE]); ax[0].set(title='Floor force',xlabel='Fi (kN)',ylabel='Height (m)')",
        "    ax[1].step([r['story_shear_kN'] for r in ESM_RESPONSE],h,where='mid'); ax[1].set(title='Storey shear',xlabel='Vi (kN)')",
        "    ax[2].plot([1000*r['U_design_m'] for r in ESM_RESPONSE],h,'o-'); ax[2].set(title='Design displacement',xlabel='u (mm)')",
        "    ax[3].barh(h,[r['design_drift_ratio'] for r in ESM_RESPONSE]); ax[3].axvline(DRIFT_LIMIT,color='r',ls='--'); ax[3].set(title='Design drift',xlabel='Drift ratio')",
        "    ax[4].plot([r['story_stiffness_kN_per_m']/1000 for r in ESM_RESPONSE],h,'o-'); ax[4].set(title='Secant storey stiffness',xlabel='ki (MN/m)')",
        "    [a.grid(alpha=.25) for a in ax]; fig.suptitle('NBC 105:2025 '+ESM_CASE+' | V='+str(round(abs(APPLIED_BASE_SHEAR_KN),3))+' kN'); fig.savefig(os.path.join(OUTPUT_DIR,'NBC105_ESM_Response_Profiles_'+ESM_CASE+'.png'),dpi=180); plt.close(fig)",
        "except ImportError: print('Matplotlib not available: response plot skipped.')",
        "try:",
        "    from openpyxl import Workbook",
        "    wb=Workbook(); ws=wb.active; ws.title='ESM Summary'; ws.append(['Item','Value'])",
        "    for item,value in [('Case',ESM_CASE),('Limit state',LIMIT_STATE),('Design base shear (kN)',APPLIED_BASE_SHEAR_KN),('Base reaction (kN)',BASE_REACTION_KN),('Equilibrium error (%)',BASE_SHEAR_ERROR_PCT),('Drift limit',DRIFT_LIMIT),('kD',KD)]: ws.append([item,value])",
        "    wr=wb.create_sheet('OpenSees Response'); wr.append(list(ESM_RESPONSE[0]) if ESM_RESPONSE else []); [wr.append([r.get(k) for k in ESM_RESPONSE[0]]) for r in ESM_RESPONSE]",
        "    wb.save(os.path.join(OUTPUT_DIR,'NBC105_ESM_OpenSees_Response_'+ESM_CASE+'.xlsx'))",
        "except ImportError: print('openpyxl not available: response workbook skipped.')",
        "_processing_timer.finish('completed')",
        "print('OpenSees ESM elapsed (s):', round(time.perf_counter()-_run_started,3))",
        "print('Run log:', LOG_PATH)",
        "print('NBC ESM case completed:', ESM_CASE, '| stories:', len(ESM_RESPONSE), '| design V (kN):', "+repr(result["base_shear_kN"])+")",
        "print('Base reaction (kN):', BASE_REACTION_KN, '| applied shear (kN):', APPLIED_BASE_SHEAR_KN, '| equilibrium error (%):', BASE_SHEAR_ERROR_PCT)",
        "from OpenSees_Response_Checks_V132 import export_static_response",
        "export_static_response(ops,MODEL_BUILDER_SCRIPT,OUTPUT_DIR,ESM_RESPONSE,LIMIT_STATE,ALL_GRAVITY_U,(R_MU if LIMIT_STATE=='ULS' else 1.)*KD)",
        "print('Master-node displacement/drift results saved under', OUTPUT_DIR)",
        "# Interpret displacements using NBC 105:2025 §§5.5.1, 5.5.3, 6.5 and effective stiffness per §3.4.",
    ]
    out_py=out/f"OpenSees_NBC105_ESM_Load_And_Static_Analysis_{suffix}_V111.py"
    safe_write(out_py,"\n".join(script)+"\n")
    return tuple([out_json,out_csv,out_py]+[p for p in (out_png,out_xlsx) if p.is_file()])


class ESMGui:
    def __init__(self,root):
        self.root=root; root.title("NBC 105:2025 — Earthquake Analysis — Equivalent Static Method")
        self.export_dir=None  # initialized after locating the selected export
        self.esm_module=tk.StringVar(value="OpenSees Direct Equivalent Static")
        export_dir=Path(sys.argv[1]) if len(sys.argv)>1 and Path(sys.argv[1]).is_dir() else Path(r"D:\Thesis Opensees\Etabs Nodes Export")
        self.export_dir=export_dir
        from components.inputs.project_workbooks import source_limit_state
        detected_state,detected_note=source_limit_state(export_dir)
        # Default to the source model, not a mixed ULS/SLS export. If the
        # source is unidentified ULS is only a visible UI default and the
        # project import gate still requires an explicitly reviewed model.
        initial_state=detected_state or 'ULS'
        story_csv,story_source_note=recommended_story_weight_input(export_dir)
        self.path=tk.StringVar(value=str(story_csv) if story_csv and story_csv.is_file() else "")
        self.story_source_note=story_source_note
        self.outdir=tk.StringVar(value=str(analysis_output_folder(export_dir,initial_state)))
        self._output_is_automatic=True
        self.state=tk.StringVar(value=initial_state); self.soil=tk.StringVar(value="C")
        self.T=tk.StringVar(value=""); self.Z=tk.StringVar(value="")
        self.location=tk.StringVar(value=""); self.z_source=tk.StringVar(value="Annex C municipality table")
        self.I=tk.StringVar(value=""); self.vs30=tk.StringVar(value=""); self.n_spt=tk.StringVar(value=""); self.system=tk.StringVar(value="Select / determine from Table 5-2")
        self.rmu=tk.StringVar(value=""); self.omegau=tk.StringVar(value=""); self.omegas=tk.StringVar(value="")
        self.irregular=tk.StringVar(value="Unknown — confirm")
        self.use_workbook_periods=tk.BooleanVar(value=False); self.period_sources={}; self.awx=tk.StringVar(); self.awy=tk.StringVar(); self.period_factor=tk.StringVar(value="1.25")
        self.rayleigh_tx=tk.StringVar(); self.rayleigh_ty=tk.StringVar()
        self.etabs_tx=tk.StringVar(); self.etabs_ty=tk.StringVar()
        self.adopted_tx=tk.StringVar(); self.adopted_ty=tk.StringVar()
        self.computed_x=tk.StringVar();self.computed_y=tk.StringVar()
        self.excel_tx=tk.StringVar();self.excel_ty=tk.StringVar()
        self.period_note=tk.StringVar(value="Load ETABS story export; enter directional Aw and optional ETABS modal periods.")
        self.etabs_modal_metadata=None
        self.excel_direct_reference=None
        self.direction=tk.StringVar(value="Both X/Y"); self.polarity=tk.StringVar(value="Both ±")
        self.centered_case=tk.BooleanVar(value=True); self.include_torsion=tk.BooleanVar(value=True); self.bdim=tk.StringVar(value="")
        self.eccsign=tk.StringVar(value="Both ±")
        self.model_script=tk.StringVar(value="")
        self.python_exe=tk.StringVar(value=sys.executable)
        self.last_runners=[]
        self.status=tk.StringVar(value="Select a verified story-weight CSV, enter project/code inputs, then run the in-house Python NBC calculation.")
        self.esm_operation_state=tk.StringVar(value="IDLE | No ESM process running")
        self._esm_busy=False
        self._build()
        from OpenSees_Complete_Export_V118 import autoselect_inputs
        autoselect_inputs(self, export_dir, 'modal_model_script')
        self._load_project_inputs()
        if not detected_state:
            self.status.set('SOURCE STATE REQUIRES REVIEW: '+detected_note+' | ULS shown as a UI default only; verify the actual .EDB before calculation.')
        self.state.trace_add('write',lambda *_:self._state_changed())
        self.direction.trace_add('write',lambda *_: self._direction_changed())
        # ETABS is an optional comparison source; on-start ROT attachment can
        # fail with WinError -2147221021 even when workbook/geometry inputs are
        # valid. Do not automatically obscure input diagnostics with a COM error.
        self.awx.trace_add('write',lambda *_:self._show_empirical())
        self.awy.trace_add('write',lambda *_:self._show_empirical())
        self.rayleigh_tx.trace_add('write',lambda *_:self._show_empirical())
        self.rayleigh_ty.trace_add('write',lambda *_:self._show_empirical())

    def _set_esm_operation(self,state,detail=""):
        """Main Tk thread only; independent of verbose console status."""
        self.esm_operation_state.set(str(state)+" | "+str(detail))
        if state=="RUNNING":
            self.esm_busy_bar.start(12)
        else:
            self.esm_busy_bar.stop()

    def _auto_bundle_seismic_review(self):
        """Package current ETABS-linked and OpenSees ESM evidence automatically.

        The worker runs off the Tk thread. Missing independent ETABS response
        evidence is explicit; no ETABS model is modified or results invented.
        """
        import threading
        if getattr(self,"_review_bundle_running",False):
            self.status.set(self.status.get()+
                "\\nESM review archive already being built; existing run remains available.")
            return
        self._review_bundle_running=True
        source=Path(self.export_dir)
        output=Path(self.outdir.get())
        def worker():
            try:
                from components.validation.seismic_review_bundle import bundle_seismic_review
                result=bundle_seismic_review(source,output,method="ESM")
                def finished():
                    self._review_bundle_running=False
                    self.status.set(self.status.get()+
                        "\\n[ESM_AUTO_REVIEW_ZIP] "+result["zip"])
                self.root.after(0,finished)
            except Exception as exc:
                reason=str(exc)
                def failed():
                    self._review_bundle_running=False
                    self.status.set(self.status.get()+
                        "\\n[ESM_AUTO_REVIEW_FAILED] "+reason)
                self.root.after(0,failed)
        threading.Thread(target=worker,daemon=True).start()

    def _bundle_esm_evidence(self):
        """One-click rerun of the automatic, SHA-deduplicated review ZIP.

        No extra folder selection and no ambiguous native case inference.
        Current model and analysis output paths are taken from selected GUI.
        """
        if getattr(self,"_review_bundle_running",False):
            self.status.set("Review ZIP creation is already running; see output folder.")
            return
        self._auto_bundle_seismic_review()
        self.status.set(self.status.get()+
            "\\nReview ZIP creation started automatically; find the latest "
            "path in Seismic_Review_Packages/LATEST_ESM_REVIEW.txt.")

    def _export_organized_evidence(self):
        """[REF docs/source/components/ui/organized_results.py.md] Publish copies only."""
        if getattr(self,'_organized_export_busy',False):
            self.status.set('Categorized ZIP export is already running.')
            return
        self._organized_export_busy=True
        self.status.set('Creating categorized Gravity / ESM / Modal / MRSM evidence copies…')
        def task():
            try:
                from components.ui.organized_results import publish_organized_results
                output=Path(self.outdir.get())
                result=publish_organized_results(output)
                def done():
                    self._organized_export_busy=False
                    self.status.set('ORGANIZED ZIP: '+result['zip_files']['ALL_MODULES']+
                                    ' | manifest '+result['manifest'])
                    messagebox.showinfo(
                        'Organized result ZIPs',
                        'Upload all modules:\\n'+result['zip_files']['ALL_MODULES']+
                        '\\n\\nSeparate modules and manifest:\\n'+result['folder']+
                        '\\n\\nOriginal analysis outputs remain unchanged.',
                        parent=self.root)
                self.root.after(0,done)
            except Exception as exc:
                error=str(exc)
                def failed():
                    self._organized_export_busy=False
                    self.status.set('ORGANIZED EXPORT FAILED: '+error)
                    messagebox.showerror('Organized results export',error,parent=self.root)
                self.root.after(0,failed)
        threading.Thread(target=task,daemon=True).start()

    def _run_etabs_linked(self):
        """Use the uploaded original Excel/ETABS engine, without touching RS scaling."""
        from components.equivalent_static.etabs_linked_excel import run_etabs_excel
        from components.inputs.project_workbooks import _source_edb_path, registered_project_source
        source=_source_edb_path(self.export_dir)
        if not source or not Path(source).is_file():
            source=filedialog.askopenfilename(parent=self.root,title="Select ETABS EDB (read-only)",
                                            filetypes=[("ETABS model","*.edb")])
        if not source: return
        try:
            workbook=registered_project_source(self.export_dir,'nbc_calculator')
            engine=registered_project_source(self.export_dir,'nbc_engine')
        except (OSError,ValueError) as exc:
            messagebox.showerror('Registered source requires review',str(exc),parent=self.root)
            return
        if not workbook:
            workbook=filedialog.askopenfilename(parent=self.root,title="Select original NBC105 Excel calculator",
                                              filetypes=[("Excel calculator","*.xlsx")])
        if not workbook: return
        if not engine:
            engine=filedialog.askopenfilename(parent=self.root,title="Select original ETABS NBC105 integrated Python engine",
                                           filetypes=[("Python engine","*.py")])
        if not engine: return
        out=Path(self.outdir.get())/'ETABS_Linked_ESM'
        out.mkdir(parents=True,exist_ok=True)
        if self._esm_busy:
            messagebox.showwarning("ETABS-linked ESM","Another ESM task is running.",
                parent=self.root)
            return
        self._esm_busy=True
        self._set_esm_operation("RUNNING","ETABS-linked workbook / source identity")
        self.status.set("ETABS linked ESM: reading model and populating a new Excel copy (no RS scaling).")
        def task():
            try:
                target,audit,coeff=run_etabs_excel(source,workbook,engine,out,
                    log=lambda msg:self.root.after(0,lambda m=str(msg):self.status.set(m)))
                def success():
                    self._esm_busy=False
                    self._set_esm_operation("FINISHED",
                        "Original ETABS Excel calculation: "+str(target))
                    self.status.set("ETABS linked Excel ready: "+str(target)+" | provenance "+str(audit))
                    self._auto_bundle_seismic_review()
                    messagebox.showinfo("ETABS Linked ESM",f"Populated original Excel method:\n{target}\n\nAudit:\n{audit}\n\nOpenSees Direct remains available in the dropdown.",parent=self.root)
                    # [REF NBC105-2025 §5.1.2] the computed Aw/T were previously
                    # discarded; offer them to the form with their EDB identity.
                    try:
                        from components.inputs.aw_sources import linked_reference_from_audit
                        from components.inputs.project_workbooks import _source_edb_path
                        reference=linked_reference_from_audit(
                            json.loads(Path(audit).read_text(encoding='utf-8')),audit,
                            state=self.state.get(),current_edb=_source_edb_path(self.export_dir))
                        self._confirm_and_apply_excel_reference(reference,confirm=False)
                    except Exception as exc:
                        self.status.set('ETABS-linked Aw/T not applied to the form: '+str(exc))
                        messagebox.showwarning('ETABS-linked values not applied',str(exc),parent=self.root)
                self.root.after(0,success)
            except Exception as exc:
                error=str(exc)
                self.root.after(0,lambda:self._finish_linked_failure(error))
                self.root.after(0,lambda:messagebox.showerror("ETABS Linked ESM failed",error,parent=self.root))
                self.root.after(0,lambda:self.status.set("ETABS linked ESM FAILED: "+error))
        threading.Thread(target=task,daemon=True).start()

    def _finish_linked_failure(self,error):
        self._esm_busy=False
        self._set_esm_operation("BLOCKED",error)

    def _field(self,parent,label,var,row,col=0,width=18):
        ttk.Label(parent,text=label).grid(row=row,column=col,sticky="w",padx=5,pady=4)
        ttk.Entry(parent,textvariable=var,width=width).grid(row=row,column=col+1,sticky="ew",padx=5,pady=4)

    def _build(self):
        # Persistent actions remain visible; only the long input form scrolls.
        footer=ttk.Frame(self.root,padding=8);footer.pack(side='bottom',fill='x')
        ttk.Button(footer,text='1. Calculate + export',command=self._calculate).pack(side='left',padx=3)
        ttk.Button(footer,text='ETABS Linked: populate original Excel',command=self._run_etabs_linked).pack(side='left',padx=3)
        ttk.Button(footer,text='Compare ETABS vs ESM/MRSM responses',
                   command=lambda:__import__(
                       'components.validation.etabs_comparison',
                       fromlist=['launch']).launch(
                           self.root,self.export_dir,
                           results_root=self.outdir.get())).pack(side='left',padx=3)
        self.run_button=ttk.Button(footer,text='2. Run exported cases',command=self._run_generated,state='disabled');self.run_button.pack(side='left',padx=3)
        ttk.Button(footer,text='Open output folder',command=self._open_export_folder).pack(side='left',padx=3)
        ttk.Button(footer,text='Plots…',command=self._view_plots).pack(side='left',padx=3)
        ttk.Button(footer,text='Excel sources…',command=self._choose_workbooks).pack(side='left',padx=3)
        ttk.Button(footer,text='Use original Excel Aw/T (research)',command=self._use_explicit_excel_calculation).pack(side='left',padx=3)
        ttk.Button(footer,text='Audit Excel vs continuous-pier Aw',command=self._audit_wall_aw).pack(side='left',padx=3)
        ttk.Button(footer,text='Why are Aw/period fields blank?',command=self._show_source_diagnostics).pack(side='left',padx=3)
        ttk.Button(footer,text='Sync from OpenSees model',command=self._sync_opensees_inputs).pack(side='left',padx=3)
        ttk.Button(footer,text='Check live ETABS geometry (read-only)',command=lambda:self._sync_opensees_inputs(etabs=True)).pack(side='left',padx=3)
        ttk.Button(footer,text='Preliminary Rayleigh run (X/Y)',command=self._run_rayleigh).pack(side='left',padx=3)
        ttk.Button(footer,text='Bundle ALL ESM validation evidence ZIP',
                   command=self._bundle_esm_evidence).pack(side='left',padx=3)
        ttk.Button(footer,text='Export organized module ZIPs',
                   command=self._export_organized_evidence).pack(side='left',padx=3)

        for button in footer.winfo_children():button.pack_forget()
        for index,button in enumerate(footer.winfo_children()):
            button.grid(row=index//3,column=index%3,sticky='ew',padx=3,pady=3)
        for column in range(3):footer.columnconfigure(column,weight=1)
        self.esm_busy_bar=ttk.Progressbar(footer,mode='indeterminate')
        self.esm_busy_bar.grid(row=5,column=0,columnspan=3,sticky='ew',padx=6,pady=2)
        ttk.Label(footer,textvariable=self.esm_operation_state,
                  wraplength=920).grid(row=5,column=0,columnspan=3,
                                       sticky='w',padx=6,pady=2)
        from OpenSees_Research_UI_V123 import scrollable_form
        top=scrollable_form(self.root)
        ttk.Label(top,text="NBC 105:2025 EQUIVALENT STATIC ANALYSIS",font=("Segoe UI",16,"bold")).pack(anchor="w")
        module_row=ttk.Frame(top);module_row.pack(fill="x",pady=5)
        ttk.Label(module_row,text="ESM analysis module:").pack(side="left",padx=(0,8))
        ttk.Combobox(module_row,textvariable=self.esm_module,
                     values=["OpenSees Direct Equivalent Static","ETABS Linked Equivalent Static"],
                     state="readonly",width=39).pack(side="left")
        ttk.Label(module_row,text="ETABS linked uses original workbook + ETABS OAPI; OpenSees direct uses existing ESM force export.",
                  wraplength=520).pack(side="left",padx=8)
        ttk.Label(top,text="This earthquake-analysis module calculates NBC forces and can run a complete OpenSeesPy model builder followed by the lateral analysis. ETABS EDB extraction remains in the main converter.",wraplength=1000).pack(anchor="w",pady=(2,10))
        ttk.Label(top,text="ETABS linkage: story elevations and diaphragm tags are read from the selected export. The selected assembled ledger contains imported gravity components. Compare its story totals with ETABS before design use.",foreground="#174a7e",wraplength=1000).pack(anchor="w",pady=(0,6))
        filebox=ttk.LabelFrame(top,text="1. Verified story seismic-weight CSV (ETABS export or prepared input)",padding=8); filebox.pack(fill="x",pady=5)
        ttk.Entry(filebox,textvariable=self.path).pack(side="left",fill="x",expand=True,padx=4)
        ttk.Button(filebox,text="Browse…",command=self._browse).pack(side="left",padx=4)
        ttk.Label(filebox,text="The EDB is not read here. Load the story-weight CSV generated by the main ETABS converter, or a correctly formatted CSV prepared from verified data. Enter DL, storage LL and other LL in kN per storey; roof LL is excluded from Wi by Table 5-1. Count self-weight once.",wraplength=850).pack(anchor="w",pady=5)
        periodbox=ttk.LabelFrame(top,text="2. NBC §5.1 directional period: empirical estimate + Rayleigh period",padding=8); periodbox.pack(fill="x",pady=5)
        self._field(periodbox,"Wall index Aw-X (m²)",self.awx,0,0,12); self._field(periodbox,"Wall index Aw-Y (m²)",self.awy,0,2,12)
        ttk.Label(periodbox,text="Workbook adopted T1-X (s)").grid(row=1,column=0,sticky="w",padx=5)
        ttk.Entry(periodbox,textvariable=self.excel_tx,state="readonly",width=18).grid(row=1,column=1,sticky="w",padx=5)
        ttk.Label(periodbox,text="Workbook adopted T1-Y (s)").grid(row=1,column=2,sticky="w",padx=5)
        ttk.Entry(periodbox,textvariable=self.excel_ty,state="readonly",width=18).grid(row=1,column=3,sticky="w",padx=5)
        self._field(periodbox,"Rayleigh T1-X (s)",self.rayleigh_tx,2,0,12); self._field(periodbox,"Rayleigh T1-Y (s)",self.rayleigh_ty,2,2,12)
        self._field(periodbox,"Adopted design T1-X (s)",self.adopted_tx,12,0,12)
        self._field(periodbox,"Adopted design T1-Y (s)",self.adopted_ty,12,2,12)
        self._field(periodbox,"Empirical multiplier (NBC 1.25)",self.period_factor,3,0,12)
        ttk.Button(periodbox,text="Adopt lesser period for selected direction",command=self._update_periods).grid(row=3,column=2,columnspan=2,sticky="w",padx=5)
        ttk.Button(periodbox,text="Open ETABS / refresh X-Y periods",command=self._read_etabs_periods).grid(row=3,column=4,columnspan=3,sticky="w",padx=5)
        ttk.Label(periodbox,textvariable=self.period_note,foreground="#174a7e",wraplength=1000).grid(row=4,column=0,columnspan=7,sticky="w",padx=5,pady=4)
        for row,axis,var in [(6,'X',self.computed_x),(7,'Y',self.computed_y)]:
            ttk.Label(periodbox,text=f'{axis}: empirical / amplified / adopted (s)').grid(row=row,column=0,columnspan=2,sticky='w')
            ttk.Entry(periodbox,textvariable=var,state='readonly',width=55).grid(row=row,column=2,columnspan=5,sticky='ew')
        ttk.Label(periodbox,text="Empirical Aw/T1 follows the supplied workbook and NBC §5.1.2 wall-system expression; include first-storey wall lengths and openings. NBC §5.1.3 amplifies empirical T1 by 1.25. Enter the separately calculated directional Rayleigh period (NBC §5.1.1); adopted design-action T1 is the lesser of Rayleigh and amplified empirical. ETABS eigenperiod is a comparison only and does not replace Rayleigh. Use the modal-analysis dialog to document modal results and Rayleigh inputs.",wraplength=1000).grid(row=5,column=0,columnspan=7,sticky="w",padx=5)
        for row,axis,var in [(8,'X',self.etabs_tx),(9,'Y',self.etabs_ty)]:
            ttk.Label(periodbox,text=f'{axis}: measured ETABS modal reference (separate)').grid(row=row,column=0,columnspan=2,sticky='w')
            ttk.Entry(periodbox,textvariable=var,state='readonly',width=55).grid(row=row,column=2,columnspan=5,sticky='ew')
        ttk.Label(periodbox,text='Workbook adopted references are not measured eigenperiods. Open ETABS to replace comparison fields with live modal results.',foreground='#8a3412').grid(row=10,column=0,columnspan=7,sticky='w')
        ttk.Checkbutton(periodbox,text="Use documented workbook adopted-period references when fresh Rayleigh results are unavailable",variable=self.use_workbook_periods).grid(row=11,column=0,columnspan=7,sticky="w")
        refs=ttk.LabelFrame(top,text="NBC 105:2025 references",padding=8); refs.pack(fill="x",pady=5)
        ttk.Label(refs,text="NBC 105:2025: §3.2.1 ESM eligibility | §4.1.2/Table 4-1 soil spectrum | §4.1.4 and Annex C/Table C-1 zoning Z | Table 4-4 importance I | §4.2 SLS spectrum | §5.1 period | Table 5-1 seismic weight | Table 5-2 system factors | §§6.1–6.4 coefficient, base shear, vertical distribution and eccentric application | §5.5.1 ULS/SLS deflections | §5.5.3 drift limits | §5.6 accidental eccentricity | §6.5 ESM deflection scale kd. Official PDF: https://ebps.kathmandu.gov.np/UploadFiles/NBC_105_2025_Sesmic_Design.pdf | DUDBC code index: https://www.dudbc.gov.np/pages/24231978/. Enter the exact municipality and verified Annex C/Table C-1 Z, or document map interpolation; the GUI does not guess Z. ETABS mapping: ETABS_to_OpenSees_Node_Mapping.csv and OpenSees_Element_Connectivity.json.",wraplength=1000).pack(anchor="w")
        calc=ttk.LabelFrame(top,text="3. Code/project parameters — verify against the approved design basis",padding=8); calc.pack(fill="x",pady=5)
        calc.columnconfigure(1,weight=1); calc.columnconfigure(3,weight=1)
        ttk.Label(calc,text="Limit state cases").grid(row=0,column=0,sticky="w",padx=5,pady=4); ttk.Combobox(calc,textvariable=self.state,values=["ULS","SLS"],state="readonly",width=16).grid(row=0,column=1,sticky="w",padx=5)
        ttk.Label(calc,text="Soil type (Table 4-1)").grid(row=0,column=2,sticky="w",padx=5,pady=4); ttk.Combobox(calc,textvariable=self.soil,values=["A","B","C","D"],state="readonly",width=16).grid(row=0,column=3,sticky="w",padx=5)
        self._field(calc,"Adopted T1 (s), lesser value per §5.1",self.T,1,0); self._field(calc,"Zoning factor Z, §4.1.4",self.Z,1,2)
        self._field(calc,"Location / municipality",self.location,2,0)
        ttk.Label(calc,text="Z source").grid(row=2,column=2,sticky="w",padx=5,pady=4)
        ttk.Combobox(calc,textvariable=self.z_source,values=["Annex C municipality table","Figure 4-3 map interpolation","Geotechnical/project value"],state="readonly",width=34).grid(row=2,column=3,sticky="ew",padx=5)
        self._field(calc,"Importance factor I, Table 4-4",self.I,3,0)
        ttk.Label(calc,text="Structural system (Table 5-2)").grid(row=3,column=2,sticky="w",padx=5,pady=4)
        self.system_combo=ttk.Combobox(calc,textvariable=self.system,values=["Select / determine from Table 5-2"]+list(NBC105_ESM_SYSTEM_FACTORS),state="readonly",width=34)
        self.system_combo.grid(row=3,column=3,sticky="ew",padx=5)
        self.system_combo.bind("<<ComboboxSelected>>",self._apply_system_factors)
        self._field(calc,"Rμ (ULS; SLS uses spectrum per §4.2)",self.rmu,4,0); self._field(calc,"Ωu (ULS)",self.omegau,4,2)
        self._field(calc,"Ωs (SLS)",self.omegas,5,0)
        ttk.Label(calc,text="ULS regularity (§5.4)").grid(row=5,column=2,sticky="w",padx=5,pady=4)
        ttk.Combobox(calc,textvariable=self.irregular,values=["Unknown — confirm","Regular","Irregular"],state="readonly",width=30).grid(row=5,column=3,sticky="ew",padx=5)
        self._field(calc,"Measured Vs,30 (m/s; required if H>40 m)",self.vs30,6,0)
        self._field(calc,"N-SPT (blows/30 cm; alternative if H<=40 m)",self.n_spt,7,0)
        ttk.Label(calc,text="Choose a Nepal municipality and use its Annex C PGA (Z); otherwise select Figure 4-3 interpolation. Enter the verified Z explicitly. Site soil A–D comes from geotechnical classification (Table 4-2 / §4.1.3), not the municipality. Vs,30 is required for H>40 m; otherwise N-SPT may be used when Vs,30 is unavailable. A missing value or mismatch is flagged in the outputs; results remain exploratory until resolved.",foreground="#8a341c",wraplength=1000).grid(row=8,column=0,columnspan=4,sticky="w",padx=5,pady=5)
        tors=ttk.LabelFrame(top,text="4. Direction and accidental eccentricity",padding=8); tors.pack(fill="x",pady=5)
        ttk.Label(tors,text="Earthquake direction").grid(row=0,column=0,sticky="w",padx=5,pady=4); ttk.Combobox(tors,textvariable=self.direction,values=["Both X/Y","X","Y"],state="readonly",width=8).grid(row=0,column=1,sticky="w",padx=4)
        ttk.Label(tors,text="Polarity").grid(row=0,column=2,sticky="w",padx=5); ttk.Combobox(tors,textvariable=self.polarity,values=["Both ±","+1 (+ direction)","-1 (- direction)"],state="readonly",width=18).grid(row=0,column=3,sticky="w",padx=4)
        ttk.Checkbutton(tors,text="Include accidental eccentricity e = selected sign × 0.05b",variable=self.include_torsion).grid(row=1,column=0,columnspan=2,sticky="w",padx=5,pady=4)
        self._field(tors,"b = plan dimension perpendicular to loading (m)",self.bdim,1,2,14)
        ttk.Label(tors,text="Eccentricity sign").grid(row=2,column=0,sticky="w",padx=5); ttk.Combobox(tors,textvariable=self.eccsign,values=["Both ±","+1","-1"],state="readonly",width=10).grid(row=2,column=1,sticky="w",padx=4)
        ttk.Checkbutton(tors,text="Also export centered E0 cases for clause 5.4 torsion review",variable=self.centered_case).grid(row=4,column=0,columnspan=4,sticky="w")
        ttk.Label(tors,text="The default creates both force polarities and both accidental-eccentricity signs for the selected direction. Both X/Y calculates each axis with its own period and perpendicular plan dimension. Master nodes are assumed at the mass centre; verify inherent eccentricity separately.",wraplength=850).grid(row=3,column=0,columnspan=4,sticky="w",padx=5,pady=5)
        runbox=ttk.LabelFrame(top,text="5. OpenSeesPy model execution",padding=8); runbox.pack(fill="x",pady=5)
        ttk.Label(runbox,text="Complete model script (nodes, sections/elements, diaphragms, mass and gravity)").grid(row=0,column=0,sticky="w",padx=5,pady=3)
        ttk.Entry(runbox,textvariable=self.model_script).grid(row=0,column=1,sticky="ew",padx=5,pady=3)
        ttk.Button(runbox,text="Browse…",command=self._browse_model).grid(row=0,column=2,padx=4)
        ttk.Label(runbox,text="Python executable with OpenSeesPy").grid(row=1,column=0,sticky="w",padx=5,pady=3)
        ttk.Entry(runbox,textvariable=self.python_exe).grid(row=1,column=1,sticky="ew",padx=5,pady=3)
        ttk.Button(runbox,text="Browse…",command=self._browse_python).grid(row=1,column=2,padx=4)
        runbox.columnconfigure(1,weight=1)
        ttk.Label(runbox,text="The runner starts a fresh Python process and builds the model. Before NBC ESM it requires the model builder to attest that both IS 16700:2023 §7.2(d) initial P-Delta cases converged and were reviewed (1.2DL + 0.5IL ± 1.5EL/WL). It then freezes the reviewed gravity state, checks diaphragm masters, applies NBC floor forces/torsion, and reports reactions, drift and storey stiffness. This prerequisite does not replace NBC §3.6 combinations; a partial topology exporter is not a complete analysis model.",foreground="#8a341c",wraplength=1100).grid(row=2,column=0,columnspan=3,sticky="w",padx=5,pady=4)
        out=ttk.LabelFrame(top,text="6. Output folder (model/state/floor-specific default under OpenSees_Analysis_Results)",padding=8); out.pack(fill="x",pady=5)
        ttk.Entry(out,textvariable=self.outdir).pack(side="left",fill="x",expand=True,padx=4); ttk.Button(out,text="Browse…",command=self._browse_out).pack(side="left",padx=4)
        from OpenSees_Research_UI_V123 import copyable_log
        self.run_log=copyable_log(top,self.status)
        ttk.Label(top,text="Workflow: ETABS exports provide story weights, elevations and diaphragm tags. This dialog calculates NBC actions and can execute a complete user-selected OpenSeesPy model-builder script. It does not directly open an ETABS EDB; ETABS API periods can be read when ETABS is open and its modal case has been run.",foreground="#8a341c",wraplength=1100).pack(anchor="w",pady=5)
        if self.path.get(): self._load_story_metadata(self.path.get())
        if self.story_source_note:self.status.set(self.story_source_note)

    def _audit_wall_aw(self):
        """Compare original Excel and geometric candidates without altering NBC inputs."""
        try:
            from components.equivalent_static.aw_reconciliation import export_reconciliation
            state=self.state.get().strip().upper()
            if state not in ('ULS','SLS'):
                raise ValueError('Select one ULS or SLS state to audit Aw provenance.')
            output=Path(self.outdir.get())/'Aw_Reconciliation'
            report,folder=export_reconciliation(self.export_dir,state,output)
            x=report['axes']['X'];y=report['axes']['Y']
            self.status.set(
                f"Aw comparison (not code acceptance): X Excel={x['original_excel_aw_m2']:.8g}, "
                f"continuous={x['continuous_pier_diagnostic_m2']}; "
                f"Y Excel={y['original_excel_aw_m2']:.8g}, "
                f"continuous={y['continuous_pier_diagnostic_m2']}; "+str(folder))
            messagebox.showinfo('NBC 105 Aw reconciliation',
                'Read-only original Excel / current-source wall diagnostic saved:\n'+
                str(folder)+'\n\nA wall-by-wall match remains blocked unless '
                'both sources have verified common physical wall IDs.\n'
                'No source EDB or Excel calculation was changed.',
                parent=self.root)
        except Exception as exc:
            messagebox.showerror('Aw reconciliation requires source verification',
                                 str(exc),parent=self.root)

    def _view_plots(self):
        # Do not present Python-generated applied-force charts as solved ETABS
        # base reactions, story shears, displacements or drift.
        if self.esm_module.get() == "ETABS Linked Equivalent Static":
            messagebox.showinfo(
                "ETABS-linked ESM: calculation versus structural response",
                "The linked workbook contains the original NBC/ETABS-linked "
                "calculation and source provenance. It does NOT by itself "
                "contain a completed ETABS lateral analysis.\n\n"
                "For verified base shear, recovered storey shear, displacement "
                "and drift, use 'Compare ETABS vs ESM/MRSM responses' and "
                "supply completed, same-model ETABS results. OpenSees direct "
                "force profiles are plotted separately.",
                parent=self.root)
            return
        from OpenSees_Results_UI_V127 import esm_comparison
        esm_comparison(self.root,self.outdir.get())
        try:
            from matplotlib.figure import Figure
            from OpenSees_Research_UI_V123 import embed_figures
            import matplotlib.image as image
            paths=sorted(set(Path(self.outdir.get()).rglob('NBC105_ESM_Force_Profile*.png')) |
                         set(Path(self.outdir.get()).rglob('NBC105_ESM_Response_Profiles*.png')))
            if not paths:raise ValueError('Calculate cases first to create force-profile figures.')
            figures=[]
            for path in paths:
                fig=Figure(figsize=(10,6),layout='constrained');ax=fig.add_subplot();ax.imshow(image.imread(path));ax.axis('off');figures.append((('APPLIED FORCES | ' if 'Force_Profile' in path.name else 'SOLVER RESPONSE | ')+path.stem.replace('NBC105_ESM_Force_Profile_',''),fig))
            window=tk.Toplevel(self.root);window.title('OpenSees Direct ESM | applied force and separately solved response profiles');window.geometry('1250x850');window._esm_output_folder=self.outdir.get();__import__('OpenSees_Case_Selection_V134').profiles(window,figures)
        except Exception as exc:messagebox.showerror('Result plots',str(exc))

    def _state_changed(self):
        from components.inputs.project_workbooks import source_limit_state
        actual,note=source_limit_state(self.export_dir)
        selected=self.state.get()
        if actual and selected!=actual:
            self.status.set('CROSS-STATE COMPARISON BLOCKED: '+note)
            self.state.set(actual)
            return
        if self._output_is_automatic:
            self.outdir.set(str(analysis_output_folder(self.export_dir,self.state.get())))
        self._load_project_inputs()

    def _load_project_inputs(self):
        self.excel_direct_reference=None
        try:
            from components.inputs.project_workbooks import require_source_state
            require_source_state(self.export_dir,self.state.get())
            self.rayleigh_tx.set('');self.rayleigh_ty.set('')
            from OpenSees_Project_Inputs_V123 import populate
            data=populate(self,HERE,self.export_dir)
            self.project_input_audit=data
            from OpenSees_ETABS_Periods_V125 import populate as period_references
            refs=period_references(self,HERE,self.export_dir)
            self.etabs_modal_metadata={'source':'Excel references unless live ETABS replaces them','references':refs}
            for key,r in refs.items():
                if isinstance(r,dict) and 'value' in r:data['audit'].append(dict(field='period_reference_'+key,value=r['value'],source=r['source'],sheet=r['sheet'],cell=r['cell']))
            from openpyxl import Workbook
            # The ESM dialog is initialized with state='Both'; unlike a
            # preliminary Rayleigh run there was no rayleigh_state local here.
            # The earlier NameError aborted source-provenance export silently.
            selected_state=self.state.get().strip().upper()
            if selected_state not in ('BOTH','ULS','SLS'):
                raise ValueError('ESM state must be Both, ULS or SLS')
            out=analysis_output_folder(self.export_dir,selected_state) if self._output_is_automatic else Path(self.outdir.get())
            out.mkdir(exist_ok=True,parents=True)
            (out/'NBC105_Input_Provenance_V123.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
            wb=Workbook();ws=wb.active;ws.title='Imported inputs';ws.append(['Field','Value','Workbook/result file','Sheet','Cell'])
            for row in data['audit']:ws.append([row[k] for k in ['field','value','source','sheet','cell']])
            notes=wb.create_sheet('Review notes')
            for note in data['notes']:notes.append([note])
            segments=data['values'].get('wall_geometry_segments',[])
            if segments:
                walls=wb.create_sheet('Wall Aw geometry');headers=list(segments[0]);walls.append(headers)
                for segment in segments:walls.append([segment[k] for k in headers])
                walls.freeze_panes='A2';walls.auto_filter.ref=walls.dimensions
            wb.save(out/'NBC105_Input_Provenance_V123.xlsx')
            present=data['values']
            missing=[k for k in ('awx','awy','Z','I','rmu','omegau','omegas')
                     if k not in present or not str(present[k]).strip()]
            self._show_empirical()
            self._direction_changed()
            if self.state.get() in ('ULS','SLS'):
                # [REF Excel method decision register] same-EDB ETABS-linked
                # original method result is authoritative over geometry.
                try:
                    from components.inputs.aw_sources import latest_linked_reference
                    linked,why=latest_linked_reference(self.export_dir,self.state.get())
                except Exception as exc:
                    linked,why=None,str(exc)
                if linked:
                    self._confirm_and_apply_excel_reference(linked,confirm=False)
                    missing=[k for k in missing if k not in ('awx','awy')]
                    data['notes'].append('Aw loaded from ETABS-linked original Excel method: '
                                         +linked['provenance_json'])
            if missing:
                source_notes=[str(note) for note in data['notes']
                              if ('SCALING SUMMARY' in str(note) or
                                  'source EDB differs' in str(note) or
                                  'No NBC Calculator' in str(note) or
                                  'Aw reconstruction unavailable' in str(note) or
                                  'wall Aw reconstruction unavailable' in str(note) or
                                  'Invalid aw' in str(note))]
                self.status.set('ESM source import incomplete: missing '+', '.join(missing)
                    +'. '+(' | '.join(source_notes[:3]) if source_notes else
                          'No model-matched source fields were found.')
                    +' | Click Why are Aw/period fields blank? for the source and geometry errors. '
                    'You may manually enter independently verified Aw; no guessed values are used.')
            else:
                self.status.set('ESM workbook inputs loaded. Rayleigh periods require a matching '
                    'preliminary run; ETABS eigenperiods are reference-only. Review provenance.')
        except Exception as exc:
            # Never suppress the reason for an empty input field. Keep the
            # dialog open for manual/reviewed inputs and report the precise
            # failure in the status line as well as the user-visible dialog.
            self.status.set('Project input import failed: '+str(exc))
            self.period_note.set('Automatic Excel/project import failed: '+str(exc)
                +' | Use Excel sources… to select the exact current model workbooks.')
            if getattr(self,'_show_import_failure_dialog',True):
                messagebox.showwarning('ESM input import incomplete',
                    'Verified project inputs could not be imported. '
                    'The dialog remains usable, but blank values must not be '
                    'interpreted as zero or calculated defaults.\n\n'+str(exc),
                    parent=self.root)

    def _show_empirical(self):
        """Show only periods supported by imported story height and real Aw.

        A missing workbook or wall index is *not* a failure of the entire
        Excel loader. The previous float('') raised ValueError, causing the
        GUI to misreport a failed import and leaving both period fields blank.
        """
        try:
            rows=read_story_csv(self.path.get())
            H=max(float(r['height_m']) for r in rows)
        except (OSError,ValueError,TypeError) as exc:
            self.computed_x.set('');self.computed_y.set('')
            for name in ('adopted_tx','adopted_ty'):
                field=getattr(self,name,None)
                if field is not None:field.set('')
            self.period_note.set('Story-weight CSV not yet usable for ESM periods: '+str(exc))
            return
        values=[]
        for axis,var in [('X',self.awx),('Y',self.awy)]:
            target=self.computed_x if axis=='X' else self.computed_y
            raw=var.get().strip()
            try:
                aw=float(raw)
                factor=float(self.period_factor.get())
                if not (math.isfinite(aw) and aw>0 and math.isfinite(factor) and factor>0):
                    raise ValueError('nonpositive/nonfinite input')
                empirical=.075*H**.75/math.sqrt(aw)
                amplified=factor*empirical
                ray=(self.rayleigh_tx if axis=='X' else self.rayleigh_ty).get().strip()
                if ray:
                    ray_value=float(ray)
                    if not math.isfinite(ray_value) or ray_value<=0:
                        raise ValueError('invalid Rayleigh period')
                    adopted=f'{min(amplified,ray_value):.9g}'
                else:
                    adopted='pending Rayleigh run'
                    if getattr(self,'use_workbook_periods',None) and self.use_workbook_periods.get() and self.excel_direct_reference:
                        reference_period=self.excel_direct_reference['values'].get('workbook_adopted_t'+axis.lower())
                        if reference_period is not None:
                            adopted=f'{float(reference_period):.12g}'
                adopted_field=getattr(self,'adopted_t'+axis.lower(),None)
                if adopted_field is not None:
                    adopted_field.set(adopted if adopted!='pending Rayleigh run' else '')
                target.set(f'{empirical:.9g} / {amplified:.9g} / {adopted}')
                values.append(f'{axis}: empirical={empirical:.6g} s; amplified={amplified:.6g} s; adopted={adopted}')
            except (TypeError,ValueError):
                adopted_field=getattr(self,'adopted_t'+axis.lower(),None)
                if adopted_field is not None:adopted_field.set('')
                target.set('')
                values.append(f'{axis}: needs reviewed wall Aw, period factor and Rayleigh input')
        self.period_note.set(' | '.join(values)+' | Rayleigh and ETABS modal are separate analysis results.')

    def _direction_changed(self):
        data=getattr(self,'project_input_audit',{}).get('values',{})
        if self.direction.get()=='Both X/Y':
            self._show_empirical();return
        value=data.get('breadth_'+self.direction.get())
        if value is not None:self.bdim.set(str(value))
        ray=(self.rayleigh_tx if self.direction.get()=='X' else self.rayleigh_ty).get()
        if ray:self._update_periods()
        else:self.T.set('')

    def _use_explicit_excel_calculation(self):
        """User-selected historic Excel method, with source-identity warning."""
        from tkinter import filedialog
        from components.inputs.project_workbooks import read_explicit_excel_calculation
        path=filedialog.askopenfilename(parent=self.root,
            title='Select original ETABS NBC 105 calculated SCALING SUMMARY',
            filetypes=[('Excel workbook','*.xlsx')])
        if not path:return
        try:
            reference=read_explicit_excel_calculation(path,self.export_dir,self.state.get())
            self._confirm_and_apply_excel_reference(reference)
        except Exception as exc:
            self.status.set('Direct Excel calculation import failed: '+str(exc))
            messagebox.showerror('Excel calculation source rejected',str(exc),parent=self.root)

    def _confirm_and_apply_excel_reference(self,reference,*,confirm=True):
        """Show the source identity, then apply Excel-method Aw/T to the form.

        [REF NBC105-2025 §5.1.2; docs/review/20261106_THESIS_EXCEL_METHOD_DECISION_REGISTER.md]
        Shared by 'Use original Excel Aw/T' and the ETABS-linked run.
        """
        if True:
            mismatch=reference['source_identity']=='DIFFERENT_EDB_RESEARCH_REFERENCE_ONLY'
            if mismatch and not confirm:
                raise ValueError('Automatic Excel input reuse requires matching source EDB identity.')
            notice=('Workbook: '+reference['source_workbook']+
                '\nOriginal source EDB: '+reference['workbook_source_edb']+
                '\nCurrent source EDB: '+str(reference['current_export_source_edb'])+
                '\nIdentity: '+reference['source_identity']+
                '\n\nAw-X = '+str(reference['values']['awx'])+' m² ('+
                reference['cells']['awx']+')'+
                '\nAw-Y = '+str(reference['values']['awy'])+' m² ('+
                reference['cells']['awy']+')'+
                '\n\nThe module will use these exact Excel values as '
                'a RESEARCH reference, not derive new ones from the wall mesh. '
                'Workbook adopted periods remain separate from '
                'ETABS eigenperiods and OpenSees Rayleigh periods. '
                'Original EDB, workbook and OpenSees model stay unchanged.')
            if mismatch:
                notice+='\n\nWARNING: The Excel source EDB has NOT been '
                'verified identical to the current Copy EDB. Results using '
                'these inputs are research comparisons only.'
            if reference.get('direct_thickness_status'):
                notice+=('\n\nDirect ETABS wall thickness check (PropArea.GetWall): '
                         +str(reference['direct_thickness_status']))
            if confirm and not messagebox.askyesno('Use original Excel calculation?',
                notice+'\n\nApply these Excel values to the ESM form?',
                parent=self.root):return
            self.excel_direct_reference=reference
            self.awx.set(f"{reference['values']['awx']:.12g}")
            self.awy.set(f"{reference['values']['awy']:.12g}")
            self.excel_tx.set(str(reference['values'].get('workbook_adopted_tx','')))
            self.excel_ty.set(str(reference['values'].get('workbook_adopted_ty','')))
            self.use_workbook_periods.set(
                all('workbook_adopted_t'+axis in reference['values']
                    for axis in ('x','y')))
            self._aw_sync_evidence={
                axis:{'status':'EXCEL_METHOD_DIRECT_'+reference['source_identity'],
                      'code_accepted':False,
                      'source_workbook':reference['source_workbook'],
                      'cell':reference['cells']['aw'+axis.lower()]}
                for axis in ('X','Y')}
            self.period_note.set('Original Excel Aw and workbook-adopted T references: '
                'X='+self.excel_tx.get()+' s, Y='+self.excel_ty.get()+' s. '
                'These do NOT represent OpenSees Rayleigh or ETABS measured eigenperiods.')
            self._show_empirical()
            self.status.set('DIRECT EXCEL CALCULATION: Aw-X='+
                str(reference['values']['awx'])+', Aw-Y='+
                str(reference['values']['awy'])+' m² | '+
                reference['source_identity']+' | '+reference['source_workbook']+
                ' | RESEARCH/REFERENCE ONLY; review EDB identity and openings.')

    def _sync_opensees_inputs(self,etabs=False):
        """Source-labelled wall and period audit; never a silent EDB edit."""
        try:
            from datetime import datetime
            from components.inputs.opensees_nbc_sync import synchronize
            selected=str(self.state.get()).strip().upper()
            if selected not in ('ULS','SLS'):
                messagebox.showwarning('Select source state',
                    'Choose one matching source Ultimate→ULS or Service→SLS model.',
                    parent=self.root)
                return
            audit_dir=Path(self.outdir.get())/'NBC105_Input_Sync'/(
                datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
            report,paths=synchronize(self.export_dir,selected,
                output_dir=audit_dir,etabs_fallback=etabs)
            # A provisional reconstructed wall geometry must NEVER overwrite
            # a model-matched native ETABS-linked ORIGINAL Excel calculation.
            # Keep it as a separate diagnostic, even when a user clicks Sync.
            preserved=getattr(self,'excel_direct_reference',None)
            preserved_status=(preserved or {}).get('source_identity')
            keep_original=bool(preserved and preserved_status in (
                'SAME_EDB_PATH_REFERENCE','SAME_EDB_SHA256',
                'SAME_EDB_SHA256_REFERENCE'))
            statuses=[]
            for axis,var in (('X',self.awx),('Y',self.awy)):
                value=report['aw_candidate_m2'][axis]
                evidence=report['aw_evidence'][axis]['status']
                if keep_original:
                    statuses.append(
                        f"{axis}: OpenSees geometry candidate={value} m² "
                        f"({evidence}); original Excel Aw={preserved['values']['aw'+axis.lower()]} m² "
                        "PRESERVED (candidate NOT applied)")
                elif value is not None and evidence in (
                    'OPEN_SEES_GEOMETRY_CANDIDATE_REVIEW_REQUIRED',
                    'PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC'):
                    # Prefill the source-derived *diagnostic* to enable a
                    # preliminary comparison, never silent NBC acceptance.
                    var.set(f'{value:.10g}')
                    statuses.append(f'{axis}: {value:.8g} m² '
                        + ('(CONTINUOUS-PIER GEOMETRIC DIAGNOSTIC ONLY; not NBC accepted)'
                           if evidence=='PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC'
                           else '(geometry candidate; REVIEW REQUIRED)'))
                else:
                    statuses.append(f'{axis}: not automatically filled ({evidence})')
            for axis,var in (('X',self.rayleigh_tx),('Y',self.rayleigh_ty)):
                period=report['rayleigh_s'][axis]
                if period is not None:
                    var.set(f'{period:.10g}')
            if not keep_original:
                self.excel_direct_reference=None
                self._aw_sync_evidence=report['aw_evidence']
            # Preserve workbook adopted T and Excel SHA256 reference as well.
            self._aw_sync_model_hash=report['assembled_model_sha256']
            self._show_empirical()
            lines=['OpenSees-first audit complete. No ETABS EDB was modified.',
                   *statuses,'Excel audit copy: '+str(paths[1]),
                   'JSON provenance: '+str(paths[0])]
            deductions=(report.get('opening_reduction_audit') or {}).get('axes',{})
            for axis in ('X','Y'):
                reduction=deductions.get(axis)
                if reduction:
                    lines.append(
                        f"{axis} opening-reduced geometry: "
                        f"gross projected Aw={reduction['gross_projected_Aw_m2']:.8g} m²; "
                        f"continuous pier Aw={reduction['continuous_pier_Aw_m2']} m²; "
                        f"excluded projected contribution="
                        f"{reduction['excluded_noncontinuous_Aw_m2']:.8g} m². "
                        "NOT the vertical opening area or approved NBC Aw.")
            if etabs:
                fallback=report.get('etabs_fallback',{})
                lines.append('ETABS read-only fallback: '+str(fallback.get('status')))
                if fallback.get('reason'):lines.append(fallback['reason'])
                matched=report.get('geometry_crosscheck',{})
                lines.append('ETABS↔OpenSees pier/opening geometry: '
                             +str(matched.get('status','NO_COMPARISON')))
                if matched.get('total_mismatches'):
                    lines.append(f"{matched['total_mismatches']} discrepancies "
                                 f"at {matched.get('checked_slices',0)} elevation slices.")
                elif matched.get('status')=='GEOMETRY_MATCHED_REVIEW_REQUIRED':
                    lines.append('Geometry matches numerically; engineer must still '
                                 'confirm first-storey effective piers and NBC §5.1.2.')
            self.status.set(' | '.join(lines))
            messagebox.showinfo('NBC 105 source synchronization',
                '\n'.join(lines)+'\n\nDo not treat a candidate Aw as '
                'NBC acceptance until wall piers/openings are reviewed.',
                parent=self.root)
        except Exception as exc:
            self.status.set('Input synchronization failed: '+str(exc))
            messagebox.showerror('NBC 105 input sync',str(exc),parent=self.root)

    def _show_source_diagnostics(self):
        from components.inputs.project_workbooks import scaling_workbook_diagnostics
        source=getattr(self,'project_input_audit',{}) or {}
        notes=[str(v) for v in source.get('notes',[])]
        notes+=scaling_workbook_diagnostics(HERE,self.export_dir,self.state.get())
        notes=list(dict.fromkeys(notes))
        from components.inputs.project_workbooks import _source_edb_path
        intro=('Current export: '+str(self.export_dir)+'\n'
               +'Source EDB: '+(_source_edb_path(self.export_dir) or 'NOT RECORDED')
               +'\nLimit state: '+self.state.get()
               +'\n\nA workbook with a different B4 EDB is rejected unless '
               +'both EDB files exist and have identical SHA256. Workbook text '
               +'and unevaluated formulas are never wall areas. '
               +'If the exported wall geometry cannot independently reconstruct Aw, '
               +'enter a separately calculated and documented Aw-X/Aw-Y manually. '
               +'ETABS COM connection is optional for importing Excel.\n\n')
        profile=source.get('values',{}).get('wall_aw_profile')
        if profile:
            rows=profile['rows']
            intro+=('First-storey wall footprint: '+
                ('uniform across height' if profile['uniform_footprint'] else
                 'NONUNIFORM (do not adopt one Aw automatically)')+
                 '\n')
            intro+='Wall slices:\n'
            for r in rows:
                intro+=(f"  z={r['z_bottom_m']:.4f}..{r['z_top_m']:.4f} m, "
                        f"Aw-X={r['aw_x_m2']:.8g} m², Aw-Y={r['aw_y_m2']:.8g} m²; "
                        f"segments X={r['x_segment_count']}, Y={r['y_segment_count']}\n")
        report=intro+'\n'.join(notes or ['No additional source diagnostics recorded.'])
        output=Path(self.outdir.get())
        output.mkdir(parents=True,exist_ok=True)
        (output/'ESM_Source_Diagnostics.txt').write_text(report,encoding='utf-8')
        # An information messagebox rendered hundreds of workbook candidates
        # as an unreadable single paragraph. Use a scrollable, selectable
        # report with source files and wall slices on separate lines.
        from tkinter.scrolledtext import ScrolledText
        window=tk.Toplevel(self.root)
        window.title('ESM source audit — read-only diagnostics')
        window.geometry('1080x720')
        ttk.Label(window,text=('Current source and first-storey wall '
            'audit (not NBC engineering acceptance)'),padding=8).pack(anchor='w')
        viewer=ScrolledText(window,wrap='word',font=('Consolas',10))
        viewer.pack(fill='both',expand=True,padx=8,pady=5)
        viewer.insert('1.0',report)
        viewer.configure(state='disabled')
        ttk.Label(window,text='Saved report: '+str(output/'ESM_Source_Diagnostics.txt'),
                  wraplength=1000,padding=8).pack(anchor='w')
        ttk.Button(window,text='Close',command=window.destroy).pack(pady=6)

    def _choose_workbooks(self):
        names=filedialog.askopenfilenames(title='Select calculator and/or scaling workbooks',filetypes=[('Excel workbooks','*.xlsx')])
        if names:
            (self.export_dir/'NBC105_Workbook_Source.json').write_text(json.dumps({'workbooks':list(names)},indent=2),encoding='utf-8')
            self._load_project_inputs()

    @staticmethod
    def _rayleigh_input_preflight(awx_text, awy_text, limit_state, export_dir):
        """Explicit source/field diagnostics before a costly OpenSees model build.

        This checks numeric and file readiness only. It CANNOT certify wall
        openings, NBC §5.1.2 effective pier grouping, or physical ETABS
        equivalence, which remain separately reviewed evidence gates.
        """
        issues=[]
        values={}
        for axis,raw in (('X',awx_text),('Y',awy_text)):
            raw=str(raw).strip()
            if not raw:
                issues.append(f'Aw-{axis} is blank. Inspect first-storey wall slices in '
                              '"Why are Aw/period fields blank?", review pier grouping '
                              'and openings, then enter your source-verified Aw (m²).')
                continue
            try:
                area=float(raw)
            except (TypeError,ValueError,OverflowError):
                issues.append(f'Aw-{axis} must be a finite positive number in m², '
                              f'not {raw!r}. Excel labels are not wall areas.')
                continue
            if not math.isfinite(area) or area<=0:
                issues.append(f'Aw-{axis} must be finite and greater than zero: {raw!r}.')
                continue
            values[axis]=area
        state=str(limit_state).strip().upper()
        if state not in ('ULS','SLS','BOTH'):
            issues.append('Select ULS or SLS from the source-matched stiffness model.')
        folder=Path(export_dir)
        for filename in ('OpenSees_Complete_Model_Data_V118.json',
                         'NBC105_ESM_Story_Weights_Assembled_V118.csv'):
            if not (folder/filename).is_file():
                issues.append(f'Missing current-export input: {folder/filename}. '
                              'Rebuild/export the current model and reconciled story weights.')
        try:
            from components.inputs.project_workbooks import source_limit_state
            actual,reason=source_limit_state(folder)
            if actual and state!='BOTH' and actual!=state:
                issues.append(f'Cross-state source blocked: selected {state}, '
                              f'but export identifies {actual}. {reason}')
            # BOTH is an existing advanced workflow with separate ULS/SLS
            # runs; retain compatibility. The caller must still validate
            # both state-specific source models before accepting results.
            # The source validation for individual states is strict.
        except Exception as exc:
            issues.append('Could not verify source stiffness state: '+str(exc))
        return values,issues

    def _run_rayleigh(self):
        """Run distinct ULS/SLS reference analyses when Both is selected.

        Previous behavior generated ULS only, while the Both ESM export
        (correctly) requires state-specific ULS *and* SLS Rayleigh evidence.
        Each subprocess uses its own stiffness state and result directory;
        no result is synthesized from the other state. Failed runs retain
        their logs and do not become imported periods.
        """
        try:
            areas,issues=self._rayleigh_input_preflight(
                self.awx.get(),self.awy.get(),self.state.get(),self.export_dir)
            if issues:
                explanation=('Preliminary Rayleigh cannot start because source '
                    'inputs are incomplete or mismatched. Gravity PASS does not '
                    'provide the missing effective wall areas.\n\n'
                    + '\n'.join(f'{i+1}. {reason}' for i,reason in enumerate(issues))
                    + '\n\nUse "Why are Aw/period fields blank?" to inspect '
                      'first-storey wall slices. If wall openings change the '
                      'footprint, calculate a reviewed effective Aw from the '
                      'source wall piers. Do not copy values from another EDB.')
                self.status.set('Rayleigh PRECHECK BLOCKED: '+ '; '.join(issues))
                messagebox.showwarning('Rayleigh input evidence required',
                                       explanation,parent=self.root)
                return
            awx=areas['X'];awy=areas['Y']
            # Works through both the root compatibility launcher and direct
            # components.equivalent_static imports (e.g. tests / Spyder).
            script=HERE/'OpenSees_Rayleigh_Preliminary_V123.py'
            if not script.is_file():
                script=HERE.parents[1]/'OpenSees_Rayleigh_Preliminary_V123.py'
            if not script.is_file():raise FileNotFoundError(script)
            states=['ULS','SLS'] if self.state.get()=='Both' else [self.state.get()]
            if any(state not in ('ULS','SLS') for state in states):
                raise ValueError('Select ULS, SLS or Both.')
            out=Path(self.outdir.get());out.mkdir(parents=True,exist_ok=True)
            self.status.set('Running separate '+', '.join(states)+' X/Y Rayleigh reference analyses…')
            def worker():
                import os
                completed=[]
                for state in states:
                    command=[self.python_exe.get(),str(script),str(self.export_dir),
                             str(awx),str(awy),'.01',state]
                    try:
                        proc=subprocess.run(command,capture_output=True,text=True,
                            errors='replace',encoding='utf-8',
                            env={**dict(os.environ),'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'})
                        log=out/('NBC105_Rayleigh_Preliminary_V123_'+state+'.log')
                        log.write_text(proc.stdout+'\n'+proc.stderr,encoding='utf-8')
                        if proc.returncode:
                            raise RuntimeError(state+' Rayleigh failed (exit '+str(proc.returncode)+
                                               '), see '+str(log)+': '+proc.stderr[-1200:])
                        completed.append(state)
                        self.root.after(0,lambda state=state:self.status.set(
                            state+' Rayleigh X/Y complete; '+str(len(completed))+
                            '/'+str(len(states))+' states finished.'))
                    except Exception as exc:
                        reason=str(exc)
                        self.root.after(0,lambda reason=reason:self.status.set(
                            'Rayleigh run stopped: '+reason+
                            ' | No periods fabricated for uncompleted states.'))
                        return
                self.root.after(0,self._load_project_inputs)
                self.root.after(0,lambda:self.status.set(
                    'State-specific '+', '.join(states)+
                    ' X/Y Rayleigh analyses completed; inspect the per-state JSON, Excel and plots.'))
            threading.Thread(target=worker,daemon=True).start()
        except Exception as exc:
            self.status.set('Rayleigh setup error: '+str(exc))
            messagebox.showerror('Rayleigh setup',str(exc),parent=self.root)

    def _apply_system_factors(self,_event=None):
        factors=NBC105_ESM_SYSTEM_FACTORS.get(self.system.get())
        if factors:
            self.rmu.set(str(factors[0])); self.omegau.set(str(factors[1])); self.omegas.set(str(factors[2]))
    def _browse(self):
        p=filedialog.askopenfilename(title="Select a verified NBC 105 story-weight CSV",initialdir=self.outdir.get(),filetypes=[("CSV","*.csv"),("All files","*.*")])
        if p:
            self.path.set(p);self._output_is_automatic=True
            self.outdir.set(str(analysis_output_folder(self.export_dir,self.state.get())))
            self._load_story_metadata(p)
    def _browse_out(self):
        p=filedialog.askdirectory(title="Select output folder",initialdir=self.outdir.get())
        if p:self._output_is_automatic=False;self.outdir.set(p)
    def _browse_model(self):
        p=filedialog.askopenfilename(title="Select complete OpenSeesPy model builder",initialdir=self.outdir.get(),filetypes=[("Python script","*.py"),("All files","*.*")])
        if p: self.model_script.set(p)
    def _browse_python(self):
        p=filedialog.askopenfilename(title="Select Python executable with OpenSeesPy",initialdir=str(Path(sys.executable).parent),filetypes=[("Python executable","python.exe"),("All files","*.*")])
        if p: self.python_exe.set(p)
    def _load_story_metadata(self,path):
        try:
            with open(path,newline="",encoding="utf-8-sig") as f: rows=[r for r in csv.DictReader(f) if str(r.get("story_number","")).strip()]
            blanks=sum(1 for r in rows for k in ("dead_load_kN","storage_live_load_kN","other_live_load_kN") if not str(r.get(k,"")).strip())
            if rows: self.period_note.set(f"Loaded {len(rows)} ETABS stories; roof elevation H={max(float(r['height_m']) for r in rows):.3f} m; diaphragm tags imported. {blanks} DL/LL input cells are blank and require verified ETABS totals.")
        except Exception as exc: self.period_note.set(f"ETABS export metadata could not be read: {exc}")
    def _adopted_axis_period(self,axis,height):
        if axis not in ("X","Y"):
            raise ValueError("Axis must be X or Y.")
        aw=float((self.awx if axis=='X' else self.awy).get())
        factor=float(self.period_factor.get())
        H=float(height)
        if not all(math.isfinite(v) and v>0 for v in (aw,factor,H)):
            raise ValueError(axis+": Aw, height and factor must be finite positive.")
        empirical=factor*.075*H**.75/math.sqrt(aw)
        ray=(self.rayleigh_tx if axis=='X' else self.rayleigh_ty).get().strip()
        if ray:
            ray_value=float(ray)
            if not math.isfinite(ray_value) or ray_value<=0:
                raise ValueError(axis+": Rayleigh period must be finite positive.")
            self.period_sources[axis]='Calculated directional Rayleigh and amplified empirical minimum'
            return min(empirical,ray_value)
        if self.use_workbook_periods.get() and getattr(self,'excel_direct_reference',None):
            r=self.excel_direct_reference
            if r['limit_state']!=self.state.get().strip().upper():
                raise ValueError(axis+': Excel reference belongs to another limit state.')
            original_aw=r['values'].get('aw'+axis.lower())
            original_period=r['values'].get('workbook_adopted_t'+axis.lower())
            if original_aw is None or original_period is None:
                raise ValueError(axis+': Excel calculation lacks an attributed Aw/adopted T pair.')
            if not math.isclose(float(original_aw),aw,rel_tol=1e-7,abs_tol=1e-9):
                raise ValueError(axis+': current Aw differs from selected Excel calculation. '
                                 'Re-select workbook or run Rayleigh.')
            value=float(original_period)
            if not math.isfinite(value) or value<=0 or value>empirical+1e-5:
                raise ValueError(axis+': Excel adopted period exceeds the '
                                 'NBC amplified empirical bound for current H/Aw. '
                                 'Run source-matched Rayleigh.')
            self.period_sources[axis]=(
                'DIRECT EXCEL NBC ADOPTED PERIOD REFERENCE (NOT ETABS EIGEN; '
                'NOT OPENSEES RAYLEIGH); '+r['source_identity'])
            return value
        if self.use_workbook_periods.get():
            v=getattr(self,'project_input_audit',{}).get('values',{})
            raw=v.get('workbook_adopted_t'+axis.lower())
            imported_aw=v.get('aw'+axis.lower())
            if raw is None or imported_aw is None:
                raise ValueError(axis+": an attributed workbook adopted-period and wall Aw reference is required.")
            if not math.isclose(float(imported_aw),aw,rel_tol=1e-7,abs_tol=1e-9):
                raise ValueError(axis+": selected Aw differs from the workbook Aw used for its adopted period; recalculate Rayleigh.")
            geometry_aw=v.get('geometry_aw_'+axis.lower())
            if geometry_aw is not None and not math.isclose(float(geometry_aw),aw,rel_tol=1e-6,abs_tol=1e-9):
                raise ValueError(axis+": workbook Aw conflicts with the exported-wall geometry estimate; reconcile physical wall grouping/openings before relying on its period.")
            value=float(raw)
            if not math.isfinite(value) or value<=0 or value>empirical+1e-5:
                raise ValueError(axis+": workbook adopted period is invalid or exceeds the amplified empirical bound.")
            self.period_sources[axis]='EXPLICIT workbook adopted-period reference only; no matching Rayleigh calculation'
            return value
        raise ValueError(axis+' requires a matching calculated Rayleigh period; workbook reference use is disabled by default.')

    def _update_periods(self):
        if self.direction.get()=='Both X/Y':
            self._show_empirical()
            self.period_note.set(self.period_note.get()+f' | Calculated Rayleigh X={self.rayleigh_tx.get() or "pending"} s, Y={self.rayleigh_ty.get() or "pending"} s. Export adopts each axis separately.')
            return
        try:
            with open(self.path.get(),newline="",encoding="utf-8-sig") as f: rows=[r for r in csv.DictReader(f) if str(r.get("story_number","")).strip()]
            H=max(float(r["height_m"]) for r in rows); d=self.direction.get().upper()
            aw=float((self.awx if d=="X" else self.awy).get()); factor=float(self.period_factor.get())
            if aw<=0 or H<=0 or factor<=0: raise ValueError("Enter positive directional Aw and verify the ETABS story heights.")
            empirical=0.075/math.sqrt(aw)*H**0.75; amplified=factor*empirical
            rayleigh=(self.rayleigh_tx if d=="X" else self.rayleigh_ty).get().strip()
            if not rayleigh:
                adopted=self._adopted_axis_period(d,H);self.T.set(f'{adopted:.9g}');self.period_note.set(d+': adopted T1='+str(adopted)+' s | '+self.period_sources[d]);return
            rayleigh=float(rayleigh)
            if rayleigh<=0: raise ValueError('Rayleigh period must be positive.')
            modal=(self.etabs_tx if d=="X" else self.etabs_ty).get().strip()
            adopted=min(amplified,rayleigh)
            self.T.set(f"{adopted:.12g}")
            self.period_note.set(f"{d}: H={H:.3f} m; Aw={aw:.4f} m²; empirical T1={empirical:.4f} s; amplified={amplified:.4f} s; Rayleigh T1={rayleigh:.4f} s; ETABS/Excel period reference={modal or 'not supplied'}; adopted T1=min(amplified empirical, Rayleigh)={adopted:.4f} s.")
        except Exception as exc: messagebox.showerror("Period calculation needs review",str(exc))
    def _read_etabs_periods(self, show_error=True):
        """Read analyzed ETABS modal periods and mass ratios from the active ETABS session."""
        try:
            import comtypes.client
            from OpenSees_ETABS_Periods_V125 import attach_or_open
            self.status.set('Opening/attaching to the source ETABS model…' if show_error else 'Checking live ETABS period references…')
            self.root.update_idletasks()
            etabs=attach_or_open(self.export_dir,open_if_needed=show_error)
            sap=etabs.SapModel
            # Select a single existing modal case before querying results.
            cases=sap.LoadCases.GetNameList()
            case_names=next((list(x) for x in cases if isinstance(x,(tuple,list))),[])
            modal_cases=[]
            for name in case_names:
                kind=sap.LoadCases.GetTypeOAPI(name)
                if int(kind[0])==3: modal_cases.append(name)
            if len(modal_cases)!=1: raise RuntimeError('Select one modal case in ETABS; found '+str(modal_cases))
            sap.Results.Setup.DeselectAllCasesAndCombosForOutput()
            sap.Results.Setup.SetCaseSelectedForOutput(modal_cases[0])
            raw=sap.Results.ModalParticipatingMassRatios()
            if not isinstance(raw,(tuple,list)) or len(raw)<9:
                raise RuntimeError("ETABS returned an unexpected ModalParticipatingMassRatios result. Verify CSI API version and run a modal case.")
            # CSI API order has LoadCase, StepType, StepNum, Period, UX, UY...
            # COM wrappers differ on whether the scalar return code is first or last;
            # anchor extraction on the LoadCase string SAFEARRAY instead of assuming.
            string_arrays=[]
            for idx,value in enumerate(raw):
                try:
                    seq=list(value)
                    if seq and all(isinstance(v,str) for v in seq): string_arrays.append((idx,seq))
                except Exception: pass
            if not string_arrays: raise RuntimeError("ETABS returned no modal result rows for the selected case. Run ETABS analysis with a modal load case and confirm its results are available; OpenSees modal results do not populate the ETABS Results API.")
            case_idx,cases=string_arrays[0]; period_idx=case_idx+3
            periods=list(raw[period_idx]); ux=list(raw[period_idx+1]); uy=list(raw[period_idx+2])
            scalar_codes=[]
            for value in (raw[0],raw[-1]):
                try:
                    if isinstance(value,(int,float)): scalar_codes.append(int(value))
                except Exception: pass
            ret=scalar_codes[-1] if scalar_codes else 0
            if ret!=0: raise RuntimeError(f"ETABS ModalParticipatingMassRatios returned code {ret}; run/verify modal analysis first.")
            n=min(len(periods),len(ux),len(uy),len(cases)); modes=[]
            for i in range(n):
                p=float(periods[i]); rx=float(ux[i]); ry=float(uy[i])
                if math.isfinite(p) and p>0: modes.append((p,rx,ry,str(cases[i]),i+1))
            if not modes: raise RuntimeError("No positive modal periods were returned. Run a modal analysis in ETABS.")
            mx=max(modes,key=lambda a:a[1]); my=max(modes,key=lambda a:a[2])
            self.etabs_tx.set(f"{mx[0]:.8g}"); self.etabs_ty.set(f"{my[0]:.8g}")
            self.etabs_modal_metadata={"source":"Active ETABS API Results.ModalParticipatingMassRatios","X_dominant":{"mode_number":mx[4],"period_s":mx[0],"UX_ratio":mx[1],"load_case":mx[3]},"Y_dominant":{"mode_number":my[4],"period_s":my[0],"UY_ratio":my[2],"load_case":my[3]}}
            from OpenSees_ETABS_Periods_V125 import save_live
            save_live(self.export_dir,mx[0],my[0],self.etabs_modal_metadata)
            self.period_note.set(f"ETABS autofill complete: T_X={mx[0]:.5g}s from UX-dominant mode {mx[4]} ({mx[1]:.1%} UX); T_Y={my[0]:.5g}s from UY-dominant mode {my[4]} ({my[2]:.1%} UY). These ETABS eigenperiods are comparison values only; the NBC adopted ESM period is still the lesser of 1.25×empirical and the directional Rayleigh period. Verify mode shapes when torsion couples with translation.")
        except Exception as exc:
            if show_error: messagebox.showerror("ETABS modal results unavailable",f"ETABS comparison periods could not be refreshed. This does not invalidate the separate workbook-adopted or Rayleigh periods already shown. To refresh ETABS references, run a modal case in ETABS and retry.\n\n{exc}")
            else: self.status.set('Excel/source inputs loaded. ETABS modal refresh unavailable: '+str(exc))
    def _open_export_folder(self):
        try: os.startfile(self.outdir.get())
        except Exception as e: messagebox.showerror("Could not open export folder",str(e))
    def _open_csv(self):
        if not self.path.get(): self._browse(); return
        try: os.startfile(self.path.get())
        except Exception as e: messagebox.showerror("Could not open CSV",str(e))
    def _calculate(self):
        if self.esm_module.get()=="ETABS Linked Equivalent Static":
            return self._run_etabs_linked()
        if self.direction.get()=='Both X/Y':
            if not all((self.rayleigh_tx if axis=='X' else self.rayleigh_ty).get().strip() or (self.use_workbook_periods.get() and (self.excel_tx if axis=='X' else self.excel_ty).get().strip()) for axis in ('X','Y')):
                self.last_runners=[];self.run_button.configure(state='disabled')
                self.status.set('Both X/Y export needs calculated Rayleigh periods in both axes. Excel reference periods are already shown separately. Run Preliminary Rayleigh (X/Y), then Calculate + export.')
                messagebox.showerror('Directional periods needed',self.status.get());return
            all_runners=[]
            axis_counts=[]
            for axis in ('X','Y'):
                self.last_runners=[]
                self.direction.set(axis);self._calculate()
                all_runners.extend(self.last_runners)
                axis_counts.append(len(self.last_runners))
            self.last_runners=all_runners;self.direction.set('Both X/Y')
            if not all(axis_counts):
                self.last_runners=[];self.run_button.configure(state='disabled')
                self.status.set('Both-axis export incomplete. Resolve the axis-specific errors in the run log; no combined run is enabled.');return
            self.status.set(f'Combined X/Y export: {len(all_runners)} runners. Each direction uses its own adopted period.')
            return
        started=time.perf_counter()
        self._set_esm_operation("RUNNING","Calculating source-linked NBC ESM forces")
        try:
            from components.inputs.project_workbooks import require_source_state
            require_source_state(self.export_dir,self.state.get())
            if not self.path.get(): raise ValueError("Choose the verified story-weight CSV first; this dialog does not read an EDB directly.")
            self._update_periods()
            if not self.T.get().strip() or not self.Z.get().strip(): raise ValueError("Enter the adopted T1 and seismic zoning factor Z from project/geotechnical/code data.")
            # Never relabel a research comparison using a provisional
            # continuous-pier geometry candidate as qualified NBC design.
            candidate_evidence=getattr(self,'_aw_sync_evidence',{})
            preliminary_axes=[axis for axis in ('X','Y')
                if candidate_evidence.get(axis,{}).get('status')==
                    'PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC']
            if preliminary_axes:
                self.status.set(
                    'GEOMETRIC DIAGNOSTIC ONLY: provisional continuous-pier '
                    'Aw used in '+', '.join(preliminary_axes)+
                    '. Review physical NBC §5.1.2 wall piers/openings before '
                    'design acceptance. ESM is comparison only.')
            self._adopted_axis_period(self.direction.get(),max(float(r["height_m"]) for r in read_story_csv(self.path.get())))
            if not self.location.get().strip(): raise ValueError("Enter the project municipality/location used to establish Z.")
            if self.system.get()=="Select / determine from Table 5-2": raise ValueError("Choose the verified structural system in NBC Table 5-2 so the Rμ and Ω factors are populated.")
            rows=read_story_csv(self.path.get())
            # Signed stability checks use a documented ULS coefficient reference.
            # This does not make high-rise ULS ESM a permitted design method.
            references={}
            height=max(float(r['height_m']) for r in rows)
            # Distinct ULS/SLS stiffness states require their own Rayleigh evidence.
            # Do not silently propagate ULS T1 to an SLS ESM force profile.
            selected_states=['ULS','SLS'] if self.state.get()=='Both' else [self.state.get()]
            state_periods={}
            if len(selected_states)==2:
                from components.inputs.project_workbooks import import_project_inputs
                sls_values=import_project_inputs(HERE,self.export_dir,'SLS')['values']
                state_periods=resolve_esm_state_periods(
                    height_m=height,aw_by_axis={'X':float(self.awx.get()),'Y':float(self.awy.get())},
                    factor=float(self.period_factor.get()),states=selected_states,
                    rayleigh_by_state={
                        'ULS':{'X':self.rayleigh_tx.get(),'Y':self.rayleigh_ty.get()},
                        'SLS':{'X':sls_values.get('rayleigh_tx'),'Y':sls_values.get('rayleigh_ty')},
                    })
            for axis,awvar,rayvar in [('X',self.awx,self.rayleigh_tx),('Y',self.awy,self.rayleigh_ty)]:
                adopted=self._adopted_axis_period(axis,height)
                reference=calculate_esm(rows,period_s=adopted,soil_type=self.soil.get(),zoning_factor_z=float(self.Z.get()),importance_factor_i=float(self.I.get()),limit_state='ULS',r_mu=float(self.rmu.get()),omega_u=float(self.omegau.get()),vs30_m_s=self.vs30.get(),n_spt_blow_30cm=self.n_spt.get(),diagnostic_reference=True)
                references[axis]=dict(period_s=adopted,stories=reference['stories'],basis='NBC ULS coefficient and floor distribution used only as a diagnostic EL reference; high-rise design requires the applicable dynamic method.',code_eligible=reference['code_eligible'],site_subsoil_status=reference['site_subsoil_status'])
            # Only create the historical P-Delta sidecar next to an explicitly
            # selected, existing .py model. Standalone ESM calculations are
            # permitted without a model script, but never write into cwd.
            pdelta_path=validated_pdelta_sidecar_path(self.model_script.get())
            if pdelta_path is not None:
                safe_write(pdelta_path,json.dumps(references,indent=2))
            else:
                self.status.set('P-Delta sidecar skipped: select a verified existing Python model script. ESM force tables remain available.')
            H=max(float(r["height_m"]) for r in rows)
            selected=self.state.get(); states=["ULS","SLS"] if selected=="Both" else [selected]
            irr={"Regular":False,"Irregular":True,"Unknown — confirm":None}[self.irregular.get()]
            if self.include_torsion.get():
                if not self.bdim.get().strip(): raise ValueError("Enter the plan dimension b perpendicular to the selected earthquake direction.")
                bdim=float(self.bdim.get())
                if bdim<=0: raise ValueError("The perpendicular plan dimension b must be positive.")
                ecc_signs=[1,-1] if self.eccsign.get()=="Both ±" else [int(self.eccsign.get())]
            else: bdim=0.0; ecc_signs=[0]
            if self.include_torsion.get() and self.centered_case.get() and 0 not in ecc_signs:ecc_signs.append(0)
            polarities=[1,-1] if self.polarity.get()=="Both ±" else [1 if self.polarity.get().startswith("+1") else -1]
            made=[]; summaries=[]; failures=[]; self.last_runners=[]
            for state in states:
                try:
                    result=calculate_esm(rows,period_s=(state_periods[state][self.direction.get()] if state_periods else self._adopted_axis_period(self.direction.get(),H)),soil_type=self.soil.get(),zoning_factor_z=float(self.Z.get()),importance_factor_i=float(self.I.get()),limit_state=state,r_mu=float(self.rmu.get() or 1.0),omega_u=float(self.omegau.get() or 1.0),omega_s=float(self.omegas.get() or 1.0),irregular=irr,location_name=self.location.get(),zoning_source=self.z_source.get(),vs30_m_s=self.vs30.get(),n_spt_blow_30cm=self.n_spt.get(),diagnostic_reference=True)
                    if not result["code_eligible"]:summaries.append("ULS COMPARISON ONLY: "+result["esm_eligibility"])
                    if not result["site_subsoil_verified"]:summaries.append("SITE CLASSIFICATION NOT VERIFIED: "+result["site_subsoil_status"])
                    result["period_source"]=("Separate matched "+state+" Rayleigh/empirical minimum" if state_periods else self.period_sources.get(self.direction.get(),"Directional Rayleigh/empirical calculation"))
                    result["input_provenance"]=getattr(self,"project_input_audit",{})
                    result["wall_aw_source_classification"]={
                        axis: getattr(self,'_aw_sync_evidence',{}).get(axis,{}).get(
                            'status','USER_OR_IMPORTED_UNVERIFIED') for axis in ('X','Y')}
                    result["wall_aw_code_accepted"]=False
                    if self.excel_direct_reference:
                        result['excel_method_direct_reference']=self.excel_direct_reference
                        result['diagnostic_only']=True
                        result['research_only_reason']=(
                            'Explicit original Excel calculation: workbook values '
                            'used directly; physical wall area and current EDB '
                            'equivalence not yet verified.')
                        summaries.append('EXCEL METHOD DIRECT RESEARCH REFERENCE — '
                                         'not native model or code acceptance.')
                    if any(status=='PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC'
                           for status in result["wall_aw_source_classification"].values()):
                        result["diagnostic_only"]=True
                        summaries.append("OPENING PIER DIAGNOSTIC ONLY — "
                            "source continuous-through-height geometric Aw "
                            "is NOT NBC engineering acceptance.")
                    period_evidence=state_rayleigh_provenance(
                        state,self.direction.get(),
                        {"X":self.rayleigh_tx.get(),"Y":self.rayleigh_ty.get()},
                        {"X":sls_values.get("rayleigh_tx"),"Y":sls_values.get("rayleigh_ty")} if state_periods and state=="SLS" else None)
                    result["period_selection"]={"direction":self.direction.get(),"empirical_Aw_X_m2":self.awx.get() or None,"empirical_Aw_Y_m2":self.awy.get() or None,"empirical_multiplier":self.period_factor.get(),**period_evidence,"ETABS_or_Excel_reference_T1_X_s":self.etabs_tx.get() or None,"ETABS_or_Excel_reference_T1_Y_s":self.etabs_ty.get() or None,"ETABS_modal_metadata":self.etabs_modal_metadata,"selected_period_s":result["period_s"],"selection_rule":"NBC §5.1: adopt the lesser of 1.25 times the empirical period and the directional Rayleigh period. ETABS eigenperiod is a comparison only."}
                    for polarity in polarities:
                        for ecc_sign in ecc_signs:
                            breadth=(bdim,ecc_sign)
                            state_outdir=analysis_output_folder(self.export_dir,state) if self._output_is_automatic else Path(self.outdir.get())
                            output_paths=write_outputs(self.path.get(),rows,result,self.direction.get(),polarity,self.include_torsion.get(),breadth,state_outdir,self.model_script.get())
                            made.extend(output_paths); self.last_runners.append(str(output_paths[2]))
                            summaries.append(f"{state} {self.direction.get()}{'+' if polarity>0 else '-'} E{('+' if ecc_sign>0 else '-') if self.include_torsion.get() and ecc_sign else '0'}: V={result['base_shear_kN']:.3f} kN, k={result['period_exponent_k']:.4f}")
                except Exception as state_exc:
                    failures.append(f"{state}: {state_exc}")
            if not made: raise ValueError("No case was calculated. " + " | ".join(failures))
            elapsed=time.perf_counter()-started
            files=", ".join(Path(p).name for p in made)
            note=("\nBlocked cases: " + " | ".join(failures)) if failures else ""
            self._set_esm_operation("FINISHED",
                str(len(self.last_runners))+" ESM case scripts generated | "+
                str(len(failures))+" blocked state cases")
            self.status.set(f"Completed in {elapsed:.2f} s | Location={self.location.get()} | soil={self.soil.get()} | Z={self.Z.get()} ({self.z_source.get()})\n"+"\n".join(summaries)+note+f"\nCreated: {files}")
            self.run_button.configure(state="normal" if Path(self.model_script.get()).is_file() else "disabled")
            self._auto_bundle_seismic_review()
            messagebox.showinfo("NBC 105 ESM calculation",f"Created {len(self.last_runners)} case runner(s) and documented force profiles.\n" + ("Blocked: "+" | ".join(failures) if failures else "Review inputs before running the exported cases.") + "\n\nUse Plots or Open output folder to inspect the results.")
        except Exception as exc:
            self._set_esm_operation("BLOCKED",str(exc))
            self.status.set("Blocked: "+str(exc)); messagebox.showerror("ESM calculation blocked",str(exc))

    def _run_generated(self):
        if not self.last_runners:
            messagebox.showerror("No generated cases","Calculate the selected ESM case(s) first."); return
        if not Path(self.model_script.get()).is_file():
            messagebox.showerror("Model builder required","Select a complete OpenSeesPy model-building script first."); return
        if not Path(self.python_exe.get()).is_file():
            messagebox.showerror("Python executable required","Select the Python executable with OpenSeesPy installed."); return
        self.run_button.configure(state="disabled")
        self._set_esm_operation("RUNNING",
            "OpenSeesPy analysis | 0 of "+str(len(self.last_runners))+" cases")
        self.status.set("Running OpenSeesPy ESM case(s)… per-case logs are being written to the output folder.")
        def worker():
            outcomes=[]
            for script in self.last_runners:
                try:
                    proc=subprocess.Popen([self.python_exe.get(),'-u',script],cwd=self.outdir.get(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True, env={**dict(__import__('os').environ),'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'}, encoding='utf-8')
                    chunks=[]
                    for line in proc.stdout:
                        chunks.append(line);self.root.after(0,lambda text=line:self.status.set(text.rstrip()))
                    proc.wait();proc.stdout=''.join(chunks);proc.stderr='' 
                    self.root.after(0,lambda script=script:self._set_esm_operation(
                        "RUNNING","Finished case "+Path(script).stem+
                        " | collecting solver status"))
                    log_path=Path(self.outdir.get())/("GUI_Run_"+Path(script).stem+".log")
                    safe_write(log_path,"COMMAND: "+repr([self.python_exe.get(),script])+"\nRETURN CODE: "+str(proc.returncode)+"\n--- STDOUT ---\n"+proc.stdout+"\n--- STDERR ---\n"+proc.stderr)
                    outcomes.append((Path(script).name,proc.returncode,str(log_path)))
                except Exception as exc:
                    outcomes.append((Path(script).name,-999,str(exc)))
            def done():
                self.run_button.configure(state="normal")
                completed=bool(outcomes) and all(code==0 for _,code,_ in outcomes)
                self._set_esm_operation("FINISHED" if completed else "BLOCKED",
                    str(sum(code==0 for _,code,_ in outcomes))+
                    " of "+str(len(outcomes))+" OpenSees earthquake cases converged")
                lines=[f"{name}: {'SUCCESS' if code==0 else 'FAILED'} | {log}" for name,code,log in outcomes]
                self.status.set("OpenSeesPy earthquake cases finished.\n"+"\n".join(lines))
                self._auto_bundle_seismic_review()
                if all(code==0 for _,code,_ in outcomes): messagebox.showinfo("ESM analysis complete",self.status.get())
                else: messagebox.showerror("ESM analysis needs review",self.status.get())
            self.root.after(0,done)
        threading.Thread(target=worker,daemon=True).start()


def main():
    root=tk.Tk(); ESMGui(root); root.mainloop()
if __name__=="__main__": main()

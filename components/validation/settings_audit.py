"""Read-only audit of selected ETABS/OpenSees configuration and unresolved inputs.

[REF docs/source/components/validation/settings_audit.py.md]
No reported option establishes actual native section command/stiffness or code approval.
"""
from pathlib import Path
import json
import math
import datetime

NBC=("https://giwmscdnone.gov.np/media/files/"
     "NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf")


def _numeric_setting(cfg,key,expected):
    value=cfg.get(key)
    try:
        n=float(value)
    except (ValueError,TypeError,OverflowError):
        return "CONFIG VALUE MISSING / INVALID"
    if not math.isfinite(n):
        return "CONFIG VALUE MISSING / INVALID"
    return ("CONFIG MATCHES ADOPTED VALUE; SHELL NOT VERIFIED"
            if abs(n-expected)<=1e-10 else "CONFIG FACTOR DISAGREES WITH PROJECT ADOPTION")


def audit(folder):
    """[REF docs/source/components/validation/settings_audit.py.md]
    Do not infer actual shell wall EI, gravity mass or calibration from a GUI.
    """
    from components.inputs.output_layout import export_root_for
    from components.model.analysis_basis import IS16700_SLAB_MODIFIERS
    root=export_root_for(folder)
    config_path=root/"OpenSees_Complete_Model_Config_V118.json"
    config={}
    notes=[]
    if config_path.is_file():
        try:
            parsed=json.loads(config_path.read_text(encoding="utf-8-sig"))
            if not isinstance(parsed,dict):
                raise ValueError("Expected JSON object")
            config=parsed
        except (OSError,ValueError,TypeError) as exc:
            notes.append("Selected model configuration is unreadable: "+str(exc))
    else:
        notes.append("Selected model configuration is missing; no project factors can be verified")
    slab=IS16700_SLAB_MODIFIERS["inertia_Ig"]
    uls=float(slab["strength"])
    sls=float(slab["serviceability"])
    uls_state=_numeric_setting(config,"slab_bending_factor",uls)
    sls_state=_numeric_setting(config,"slab_bending_factor_sls",sls)
    slab_state=( "CONFIG FACTOR DISAGREES WITH PROJECT ADOPTION"
                if "DISAGREES" in (uls_state+" "+sls_state)
                else "CONFIG VALUE MISSING / INVALID"
                if "MISSING" in (uls_state+" "+sls_state)
                else "VERIFY GENERATED ETABS AND OPENSEES SHELL SECTION")
    rows=[
        dict(item="Gravity versus seismic mass",
             value=config.get("gravity_factors","NOT AVAILABLE"),
             status="REVIEW COMBINATION BASIS",
             basis="NBC §5.2/Table 5-1 seismic mass is not a universal gravity combination. Separately verify sustained preload, model mass, occupancy and self-weight overlap."),
        dict(item="Elastic wall effective stiffness",
             value="CURRENT GENERATED WALL EI NOT EXTRACTED BY THIS AUDIT",
             status="ACTION REQUIRED",
             basis="NBC 105:2025 Table 3-1 cracked wall EI ULS 0.50 and SLS 0.70; uncracked 0.80/0.90. Inspect actual OpenSees in-plane wall/section model and equivalent ETABS section before claiming application. A config flag or gross ShellMITC4 label is not native evidence."),
        dict(item="Conventional slab bending factors",
             value=[config.get("slab_bending_factor"),
                    config.get("slab_bending_factor_sls")],
             status=slab_state,
             basis=(f"Adopted IS 16700:2023 Table 5 conventional beam-supported slab EI ULS {uls:g} and SLS {sls:g}. "
                    f"ULS: {uls_state}; SLS: {sls_state}. "
                    "Source: "+str(config.get("slab_stiffness_source") or "NOT RECORDED")
                    +". NBC Table 3-1 flat-slab 0.25/0.50 is a different type; actual native section and physical mass remain unverified.")),
        dict(item="RC frame effective EI",
             value="Beam 0.35/0.70; column 0.70/0.90 (ULS/SLS)",
             status="IMPLEMENTATION REFERENCE",
             basis="NBC 105:2025 Table 3-1; verify source ETABS stiffness, E, local member axes and the actual OpenSees section; reference is not an assignment."),
        dict(item="Section adequacy",
             value="Actual reinforcement / capacities required",
             status="NOT VERIFIED",
             basis="Global equilibrium and modal mass coverage do not establish PMM, shear, stability, anchorage or ductile detailing."),
        dict(item="Drift",
             value="ULS 0.025; SLS 0.006",
             status="CODE LIMIT REFERENCE",
             basis="NBC §5.5.3; confirm source-matched run, ULS Rμ and ESM kd. MRSM force-only scaling must not multiply drift."),
        dict(item="Wall nonlinear calibration",
             value={"reviewed":config.get("nonlinear_parameters_reviewed"),
                    "materials":config.get("nonlinear_materials_file"),
                    "FSAM":config.get("nonlinear_wall_fsam_tags")},
             status="REQUIRES PROJECT EVIDENCE",
             basis="Kolozvari et al. 2023 E-SFI-MVLEM-3D and alternate layered-shell literature do not certify the project materials."),
    ]
    if notes:
        rows.append(dict(item="Current selected export configuration",
                         value=str(config_path),status="NOT VERIFIED",
                         basis="; ".join(notes)))
    return dict(created=datetime.datetime.now().astimezone().isoformat(),
                source=NBC,selected_export=str(root),
                selected_config_path=str(config_path),
                selected_config_exists=config_path.is_file(),
                rows=rows,overall="REVIEW REQUIRED - not a compliance certificate")


def launch(parent,folder):
    import tkinter as tk
    from tkinter import ttk,messagebox
    try:
        report=audit(folder)
    except Exception as exc:
        messagebox.showerror("Settings audit",str(exc),parent=parent)
        return None
    win=tk.Toplevel(parent)
    win.title("NBC settings — source values and unresolved native evidence")
    win.geometry("1150x700")
    text=tk.Text(win,wrap="word")
    sy=ttk.Scrollbar(win,command=text.yview)
    text.configure(yscrollcommand=sy.set)
    sy.pack(side="right",fill="y")
    text.pack(fill="both",expand=True)
    text.insert("end",json.dumps(report,indent=2,ensure_ascii=False))
    text.configure(state="disabled")
    return win

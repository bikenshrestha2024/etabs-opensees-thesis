"""NBC 105:2025 project settings and source-evidence viewer (read-only by default).

[REF docs/source/components/ui/nbc105_settings_panel.py.md]
This viewer never assigns ETABS/OpenSees properties or declares code acceptance.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

NBC_PDF = ("https://giwmscdnone.gov.np/media/files/"
           "NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf")
COLUMNS = ("Topic", "Item / equation", "ULS / strength", "SLS / service", "Authority", "Evidence status", "Interpretation / verification")
STATUS_UNVERIFIED = "NOT VERIFIED"
STATUS_REFERENCE = "CODE REFERENCE ONLY"
STATUS_PROJECT = "PROJECT-ADOPTED; VERIFY APPLIED"


def _row(topic, item, uls="", sls="", authority="", status=STATUS_REFERENCE, note=""):
    return dict(zip(COLUMNS,(topic,str(item),str(uls),str(sls),str(authority),
                             str(status),str(note))))


def _file_sha(path):
    p=Path(path)
    if not p.is_file():
        return None
    with p.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def design_check_output_diagnostic(export_root):
    """[REF docs/source/components/ui/nbc105_settings_panel.py.md]
    Classify existing V135 folders without moving or deleting historical files.
    """
    from components.validation.design_checks import design_check_locations
    canonical,legacy=design_check_locations(export_root)
    filename="Design_Check_Report_V135.json"
    new_file,old_file=canonical/filename,legacy/filename
    modern=new_file.is_file()
    historical=old_file.is_file()
    status=("CANONICAL_REPORT_PRESENT" if modern else
            "LEGACY_REPORT_ONLY" if historical else "NO_SAVED_DESIGN_REPORT")
    if modern and historical and old_file.stat().st_mtime_ns>new_file.stat().st_mtime_ns:
        status="LEGACY_REPORT_NEWER_REVIEW_ACTIVE_LAUNCHER"
    return {
        "status":status,
        "canonical_dir":str(canonical),
        "legacy_dir":str(legacy),
        "canonical_report_exists":modern,
        "legacy_report_exists":historical,
        "canonical_report_mtime_ns":new_file.stat().st_mtime_ns if modern else None,
        "legacy_report_mtime_ns":old_file.stat().st_mtime_ns if historical else None,
        "interpretation":("Current source writes new V135 reports under 09_SOFTWARE_DIAGNOSTICS/"
                          "DESIGN_CHECKS_V135. An old legacy report does not prove the "
                          "running executable uses the new source. If the legacy report "
                          "is newly updated, pull main, restart the launcher, inspect "
                          "the runtime module path, and re-run V135. Never delete or "
                          "silently relocate the user-edited historical criteria."),
    }


def build_analysis_settings_review(export_dir):
    """[REF docs/source/components/ui/nbc105_settings_panel.py.md]
    Collect code references, adoption, runtime and actual selected-export evidence.

    Neither section flags nor JSON config values establish that a generated
    OpenSees section, ETABS setting or run has the displayed physical property.
    """
    from components.inputs.output_layout import export_root_for
    from components.model.analysis_basis import (
        NBC105_FLEXURAL_MODIFIERS, IS16700_INITIAL_PDELTA_FACTORS,
        IS16700_SLAB_MODIFIERS)
    from components.equivalent_static import legacy_code_basis as source
    root=export_root_for(export_dir)
    config_path=root/"OpenSees_Complete_Model_Config_V118.json"
    model_path=root/"OpenSees_Complete_Model_Data_V118.json"
    config={}
    warnings=[]
    if config_path.is_file():
        try:
            item=json.loads(config_path.read_text(encoding="utf-8-sig"))
            if not isinstance(item,dict):
                raise ValueError("Expected a JSON object")
            config=item
        except (OSError,ValueError,TypeError) as exc:
            warnings.append("Cannot read model configuration: "+str(exc))
    else:
        warnings.append("Selected export has no OpenSees_Complete_Model_Config_V118.json")
    if not model_path.is_file():
        warnings.append("Selected export has no OpenSees_Complete_Model_Data_V118.json")
    slab_basis=IS16700_SLAB_MODIFIERS["inertia_Ig"]
    slab_uls=float(slab_basis["strength"])
    slab_sls=float(slab_basis["serviceability"])
    for state,key,expected in (("ULS","slab_bending_factor",slab_uls),
                               ("SLS","slab_bending_factor_sls",slab_sls)):
        if key in config:
            try:
                actual=float(config[key])
                if not math.isfinite(actual):
                    raise ValueError("Nonfinite stiffness coefficient")
                if actual <= 0:
                    raise ValueError("Nonpositive stiffness coefficient")
                if abs(actual-expected)>1e-10:
                    warnings.append(
                        f"{state} conventional slab bending factor {actual:g} differs "
                        f"from adopted IS 16700 value {expected:g}; review generated section.")
            except (TypeError,ValueError,OverflowError):
                warnings.append(f"{state} slab bending factor is not a valid number")
        else:
            warnings.append(f"Missing {state} adopted slab factor {key} in selected config")
    diagnostic=design_check_output_diagnostic(root)
    if diagnostic["status"] in ("LEGACY_REPORT_ONLY","LEGACY_REPORT_NEWER_REVIEW_ACTIVE_LAUNCHER"):
        warnings.append("V135 outputs are still recorded under the legacy results path; inspect running launcher/version")
    if not root.is_dir():
        warnings.append("Selected ETABS export directory does not exist")
    code=[]
    for label,limits in NBC105_FLEXURAL_MODIFIERS.items():
        code.append(_row("Effective elastic flexural EI",label,
                         limits["ULS"],limits["SLS"],
                         "NBC 105:2025 §3.4, Table 3-1",STATUS_REFERENCE,
                         "Applies to equivalent ELASTIC stiffness; no direct multiplication of nonlinear fiber/FSAM constitutive response."))
    code.extend([
        _row("Compatibility torsion","RC beam cracked torsion J",0.10,"",
             "NBC 105:2025 §3.4",STATUS_REFERENCE,
             "10% gross torsional stiffness is recommended for compatibility torsion only; equilibrium torsion needs separate review."),
        _row("Design method","Limit State Method (LSM)","ULS","SLS",
             "NBC 105:2025 §3.5-3.7",STATUS_REFERENCE,
             "Working Stress Method combinations are excluded by the adopted workflow; retain serviceability checks."),
        _row("Parallel combinations","Gravity","1.2 DL + 1.5 LL","",
             "NBC 105:2025 §3.6.1",STATUS_REFERENCE,"Separate design combination; NOT the seismic mass source."),
        _row("Parallel combinations","Conditional action","1.2 DL + 0.5 LL + S","",
             "NBC 105:2025 §3.6.1",STATUS_REFERENCE,
             "S = 1.2 snow/static-liquid action or 1.5 earth-pressure action; verify applicability."),
        _row("Parallel combinations","Seismic and uplift","DL + λ LL ± E","0.9 DL ± E",
             "NBC 105:2025 §3.6.1",STATUS_REFERENCE,
             "ULS/SLS use state-specific seismic actions. The 0.9 DL form is a separate uplift/overturning combination."),
        _row("Nonparallel combinations","100% + 30%","DL + λ LL ± (Ex ± 0.3 Ey)",
             "0.9 DL ± (Ey ± 0.3 Ex)","NBC 105:2025 §3.6.2",STATUS_REFERENCE,
             "Illustrative X-primary and Y-primary forms; include sign permutations, opposite primary direction and applicable geometry."),
        _row("Load-combination λ","Storage / other occupancies","0.60","0.30",
             "NBC 105:2025 §3.6.1",STATUS_REFERENCE,
             "Combination λ is separate from factored mass and from gravity preload."),
        _row("Seismic weight Wi","Dead + occupancy-weighted live","Storage 0.60","Other 0.30; roof 0",
             "NBC 105:2025 §5.2, Table 5-1",STATUS_REFERENCE,
             "Mass source is not a 1.2DL+1.5LL gravity combination. Compute m=Wi/g."),
        _row("Period (§5.1.1)","Rayleigh T_R","2π sqrt[Σ(Wi di²)/(g Σ(Fi di))]","X/Y separate",
             "NBC 105:2025 §5.1.1",STATUS_REFERENCE,
             "Use elastic center-of-mass translation ignoring torsion for each direction; validate weights/forces/displacements."),
        _row("Period (§5.1.2)","RC wall empirical","T_emp=0.075 H^(3/4)/sqrt(Aw)","Aw=Σ Awi[0.2+(Lwi/H)²]",
             "NBC 105:2025 §5.1.2",STATUS_REFERENCE,
             "First-story effective wall sections; Lwi/H <= 0.9. Openings require justified pier segmentation and original Excel provenance."),
        _row("Design period (§5.1.3)","Adopt X and Y","min[T_R,1.25 T_emp]","separate X/Y",
             "NBC 105:2025 §5.1.3",STATUS_REFERENCE,
             "Do not confuse empirical/adopted Rayleigh period with eigenperiod or number of modes."),
        _row("ESM coefficient and shear","V=Cd(T1)W","ULS Cd(T)","SLS Cd(T)",
             "NBC 105:2025 §§6.1-6.2",STATUS_REFERENCE,"Verify soil/site/spectrum parameters and accepted source W."),
        _row("Storey force","Fi=V Wi hi^k/Σ(Wj hj^k)","k=1 for T<=0.5s","k=2 for T>=2.5s",
             "NBC 105:2025 §6.3",STATUS_REFERENCE,
             "Use interpolation for intermediate T, applied story-level forces and required eccentricities."),
        _row("Drift","Design horizontal deflection","Rμ × elastic (ESM applicable kd)","elastic",
             "NBC 105:2025 §§5.5, 6.5, 9.3.3",STATUS_REFERENCE,
             "ULS drift limit 0.025; SLS 0.006. Do not multiply MRSM displacements by a force-only scale."),
        _row("Lateral load / P-Delta","Geometric second-order action","P-Delta required","same reviewed model basis",
             "NBC 105:2025 §§8.1.1.3, 9.3.1.3",STATUS_REFERENCE,
             "Independent P-Delta readiness evidence required before using transient results."),
    ])
    project=[
        _row("REQUIRED project adoption","Conventional beam-supported RC slab EI",
             f"{slab_uls:g} Ig",f"{slab_sls:g} Ig",
             "IS 16700:2023 Table 5 (PROJECT ADOPTION)",
             STATUS_PROJECT,"Not NBC flat-slab 0.25/0.50. Keep membrane area, slab physical thickness, weight and mass separately. Verify generated OpenSees section AND ETABS modifiers."),
        _row("REQUIRED project gate","Signed initial P-Delta EL/WL",
             f'{IS16700_INITIAL_PDELTA_FACTORS["DL"]:g} DL + '
             f'{IS16700_INITIAL_PDELTA_FACTORS["IL"]:g} IL ± '
             f'{IS16700_INITIAL_PDELTA_FACTORS["EL_or_WL"]:g} EL/WL',
             "X+/X−, Y+/Y−",
             "IS 16700:2023 §7.2(d) (PROJECT ADOPTION)",
             STATUS_PROJECT,"Must converge and retain audit evidence; distinct from sustained NLTHA preload and NBC §3.6 combinations."),
        _row("Supplementary stability screen","Initial P-Delta θ",
             "Pi Δi / (Vi h(i-1) R)","review θ<=0.20",
             "IS 16700:2023 §7.3.10 (SUPPLEMENTARY)",
             STATUS_UNVERIFIED,"Use clause interpretation and correct P-Delta load combinations; no θ can be inferred from a diagram."),
        _row("Existing project input","Current slab ULS bending factor",
             config.get("slab_bending_factor","MISSING"),
             config.get("slab_bending_factor_sls","MISSING"),
             "OpenSees_Complete_Model_Config_V118.json",STATUS_UNVERIFIED,
             "Saved configuration is not evidence that the produced shell plate section applied each factor."),
        _row("Existing project input","Current slab source",
             config.get("slab_stiffness_source","MISSING"),"",
             "Selected export config",STATUS_UNVERIFIED,
             "Use project-adopted IS Table 5 for beam-supported conventional slab, and verify native implementation."),
        _row("Existing project input","Gravity load factors",
             json.dumps(config.get("gravity_factors","MISSING"),ensure_ascii=False),"",
             "Selected export config",STATUS_UNVERIFIED,
             "Gravity preload is not automatically equal to seismic mass; check double self-weight and occupancy."),
        _row("Seismic inertia","Actual mass center and torsional Jm","NOT COMPUTED","NOT COMPUTED",
             "Model node/element/mass extraction",STATUS_UNVERIFIED,
             "Asymmetric/open plan needs actual mass-weighted inertia; rectangular-floor Jm cannot be assumed."),
        _row("Elastic wall model","Wall in-plane effective stiffness","NOT VERIFIED","NOT VERIFIED",
             "NBC Table 3-1 / native element audit",STATUS_UNVERIFIED,
             "Source gross ShellMITC4 stiffness must be reconciled against ETABS effective flexural wall model."),
        _row("Material/model gate","FSAM wall, FVD/BRB and reinforcement","NOT VERIFIED","NOT VERIFIED",
             "Project-specific nonlinear calibration",STATUS_UNVERIFIED,
             "Do not treat literature examples or nominal properties as calibrated capacities."),
        _row("Foundation gravity","32/76/97 support reactions","NOT VERIFIED","NOT VERIFIED",
             "ETABS/OpenSees independent comparison",STATUS_UNVERIFIED,
             "Do not infer foundation agreement from matching global gravity summation."),
        _row("Slab mesh","MESH_04/08/16 independent gravity recovery","NOT VERIFIED","NOT VERIFIED",
             "Separate source snapshots / solver force recovery",STATUS_UNVERIFIED,
             "A generated workbook alone does not establish convergence or actual transferred forces."),
    ]
    general=[
        _row("Numerical mechanics","Linear eigenproblem","(K−ω² M)φ=0","T=2π/ω",
             "General structural dynamics, NOT NBC equation",STATUS_REFERENCE,
             "Verify eigenmode shapes and X/Y/Rz modal participation; mode 1 need not be an X translation."),
        _row("Material mechanics","Isotropic shear modulus","G=E/[2(1+ν)]","A=bh",
             "General elasticity, NOT NBC equation",STATUS_REFERENCE,
             "Validate local axes for Iy and Iz; torsion uses Saint-Venant J, not Iy+Iz."),
        _row("Rayleigh damping","C=a0M+a1K","ζ(ω)=a0/(2ω)+a1ω/2","≤5% calibration basis",
             "NBC 105:2025 §8.1.1 / OpenSees formulation",STATUS_REFERENCE,
             "Check actual modal damping at all relevant frequencies and nonlinear stiffness choice."),
        _row("Unit check","Ec=4700 sqrt(fc')","NOT NBC 105","source-dependent",
             "Material standard / ETABS source",STATUS_UNVERIFIED,
             "Do not use an unverified Ec equation as if it came from NBC 105."),
        _row("Gravity equilibrium","ΣR=ΣP","six-component reactions","per-load-pattern",
             "General mechanics, NOT NBC equation",STATUS_REFERENCE,
             "Check local forces, physical supports, signs and beam/slab/wall load transfer."),
        _row("Solver preset","Constraint/numberer/system",
             source.OPENSEES_ANALYSIS_STACK["constraints"],
             source.OPENSEES_ANALYSIS_STACK["system"],
             "OpenSees recommended configuration (not NBC)",STATUS_UNVERIFIED,
             "Display-only; actual generated runner, MPC choice and solver must be inspected."),
        _row("Solver preset","Static and transient nonlinear algorithms",
             source.OPENSEES_ANALYSIS_STACK["nonlinear_static"]["algorithm"],
             source.OPENSEES_ANALYSIS_STACK["nonlinear_transient"]["algorithm"],
             "OpenSees implementation reference",STATUS_UNVERIFIED,
             "Alternative algorithms are diagnostics, not repairs for unstable materials or constraints."),
    ]
    mass=[]
    mass_spec=source.EARTHQUAKE_MASS_SOURCE
    for key,description in (
        ("dead_load_factor","Dead weight"),
        ("storage_live_factor","Storage occupancy live weight"),
        ("other_live_factor","Other occupancy live weight"),
        ("roof_live_factor","Roof live weight"),
    ):
        mass.append(_row("NBC seismic mass",description,
                         mass_spec[key],"",
                         "NBC 105:2025 §5.2, Table 5-1",STATUS_REFERENCE,
                         "Mass factor; NOT a gravity DL/LL combination. Confirm assigned physical story weight and m=W/g."))
    for key in ("dead_pattern_names","storage_pattern_names",
                "other_live_pattern_names","roof_live_pattern_names"):
        mass.append(_row("ETABS pattern configuration",key,
                         ", ".join(mass_spec[key]),"",
                         "Configurable pattern-name defaults",STATUS_UNVERIFIED,
                         "Verify these pattern aliases against the selected EDB export; a missing assignment must not silently become zero mass."))
    mass.append(_row("Gravity vs mass","Configured gravity preload factors",
                     json.dumps(config.get("gravity_factors","MISSING"),ensure_ascii=False),"",
                     "Selected export config",STATUS_UNVERIFIED,
                     "An AS_CONFIGURED 0.3 LL gravity factor is NOT automatically the NBC mass source nor the NBC §3.6 strength combination."))
    configured_patterns=config.get("gravity_factors")
    if isinstance(configured_patterns,dict):
        all_referenced=set(name.casefold() for key in (
            "dead_pattern_names","storage_pattern_names",
            "other_live_pattern_names","roof_live_pattern_names"
        ) for name in mass_spec[key])
        unmatched=[name for name,factor in configured_patterns.items()
                   if str(name).casefold() not in all_referenced and
                   isinstance(factor,(int,float)) and not isinstance(factor,bool)
                   and factor!=0]
        if unmatched:
            warnings.append(
                "NONZERO source gravity patterns missing from illustrative mass aliases: "
                +", ".join(map(str,unmatched))
                +". Self Weight and Wall may be assembled independently of "
                 "pattern aliases; verify source model mass assembler and "
                 "all physical load groups before accepting seismic mass.")
        mass.append(_row(
            "Mass mapping crosswalk","Unmatched source gravity pattern names",
            ", ".join(map(str,unmatched)) if unmatched else "NONE",
            "NOT A MASS VALIDATION",
            "Current export gravity_factors vs illustrative pattern defaults",
            STATUS_UNVERIFIED,
            "A missing alias is not proof that mass is missing: self-weight, "
            "wall and other sources can enter by an independent mesh/section "
            "ledger. Verify final per-storey assembled mass and matching ETABS mass source."))
    else:
        warnings.append("Cannot cross-check source gravity pattern names: gravity_factors missing or not a dictionary")
    mass.append(_row("Torsional mass","Asymmetric floor rotational inertia Jm",
                     "SOURCE MESH REQUIRED","",
                     "Element/node mass coordinates",STATUS_UNVERIFIED,
                     "Compute from actual floor masses and coordinates; do not assume a uniformly filled rectangular diaphragm."))

    pdelta_results=(config.get("IS16700_INITIAL_PDELTA_RESULTS")
                    or config.get("is16700_initial_pdelta_results") or {})
    if not isinstance(pdelta_results,dict):
        pdelta_results={}
        warnings.append("P-Delta initial case evidence mapping is not a valid dictionary")
    for direction in ("X","Y"):
        for sign in ("PLUS","MINUS"):
            name="PD_INIT_EL_"+direction+"_"+sign
            observed=pdelta_results.get(name)
            if isinstance(observed,dict):
                details=json.dumps(observed,ensure_ascii=False)
                status=("EVIDENCE RECORDED; NATIVE CHECK REQUIRED" if
                        observed.get("converged") is True and
                        (observed.get("result_file") or observed.get("result_note"))
                        else STATUS_UNVERIFIED)
            else:
                details="NO SAVED CASE RECORD"
                status=STATUS_UNVERIFIED
            if status==STATUS_UNVERIFIED:
                warnings.append(
                    name+" signed initial P-Delta evidence absent or incomplete "
                    "in selected config; inspect independent case evidence.")
            project.append(_row("Mandatory signed P-Delta",name,details,"",
                                "Project IS 16700:2023 §7.2(d)",status,
                                "A saved convergence flag is not a substitute for native solver logs and state-transfer validation."))

    audit_rows=[]
    if config_path.is_file():
        try:
            from components.validation.settings_audit import audit
            saved_audit=audit(root)
            for entry in saved_audit.get("rows",[]):
                val=entry.get("value")
                audit_rows.append(_row("Selected-export audit",
                    entry.get("item","unnamed"),
                    json.dumps(val,ensure_ascii=False) if isinstance(val,(dict,list)) else str(val),
                    "", "components/validation/settings_audit.py",
                    entry.get("status",STATUS_UNVERIFIED),
                    entry.get("basis","")))
        except (OSError,ValueError,TypeError,KeyError) as exc:
            warnings.append("Current exported settings audit unavailable: "+str(exc))
    if not audit_rows:
        audit_rows.append(_row("Selected-export audit","NO CURRENT SETTINGS AUDIT",
                               "NOT EVALUATED","", "Selected model config",
                               STATUS_UNVERIFIED,
                               "Provide valid OpenSees_Complete_Model_Config_V118.json before reviewing actual project assignments."))

    source_rows=[
        _row("Runtime","Viewer module source path",__file__,"",
             "Loaded Python source","RUNTIME PATH ONLY",
             "Use this path to identify stale installed copies; restart after a git pull."),
        _row("Runtime","Source basis implementation",str(Path(source.__file__).resolve()),"",
             "Imported code basis","RUNTIME PATH ONLY","Not an ETABS source model approval."),
        _row("Selected export","Source root",str(root),"",
             "Selected export path","RUNTIME PATH ONLY","Files are not uploaded; all diagnostics remain local."),
        _row("Selected export","Model config SHA256",_file_sha(config_path) or "MISSING","",
             "Source JSON SHA256",STATUS_UNVERIFIED,"Hash identifies bytes, not ETABS physical equivalence."),
        _row("Selected export","Serialized model SHA256",_file_sha(model_path) or "MISSING","",
             "Source JSON SHA256",STATUS_UNVERIFIED,"Do not infer native structural validity from this checksum."),
        _row("V135 output","Preferred new directory",diagnostic["canonical_dir"],"",
             "Current main implementation","RUNTIME PATH ONLY",
             "V135 should write new reports here; legacy edited criteria are read-only fallback."),
        _row("V135 output","Historical directory",diagnostic["legacy_dir"],"",
             "Historical compatibility","RUNTIME PATH ONLY",
             "Do not delete or overwrite historical user-edited criteria."),
        _row("V135 output","Observed report placement",diagnostic["status"],"",
             "Read-only filesystem check",STATUS_UNVERIFIED,diagnostic["interpretation"]),
    ]
    tabs={
        "Review & project":project,
        "NBC code & combinations":code,
        "Mass source & patterns":mass,
        "Current model audit":audit_rows,
        "Mechanics & solver":general,
        "Runtime & folders":source_rows,
    }
    return {"schema":"NBC105_ANALYSIS_SETTINGS_REVIEW_V12",
            "basis":"CODE_REFERENCE_AND_PROJECT_ADOPTION_NOT_ENGINEERING_CERTIFICATE",
            "code_pdf":NBC_PDF,
            "selected_export":str(root),
            "selected_config_exists":config_path.is_file(),
            "selected_model_exists":model_path.is_file(),
            "v135_output_diagnostic":diagnostic,
            "warnings":warnings,
            "tables":tabs}


def export_analysis_settings_review(report):
    """[REF docs/source/components/ui/nbc105_settings_panel.py.md]
    Explicit, local-only JSON+Excel evidence export in the canonical stage.
    """
    from components.inputs.output_layout import export_root_for
    from components.inputs.output_contract import atomic_json,style_workbook
    from openpyxl import Workbook
    root=export_root_for(report["selected_export"])
    if not root.is_dir():
        raise NotADirectoryError(str(root))
    parent=root/"09_SOFTWARE_DIAGNOSTICS"/"ANALYSIS_SETTINGS"
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    run=parent/"RUNS"/stamp
    jsonfile=run/"JSON"/"NBC105_Settings_Reference.json"
    xlsxfile=run/"EXCEL"/"NBC105_Settings_Reference.xlsx"
    local=dict(report,created_utc=datetime.now(timezone.utc).isoformat())
    atomic_json(jsonfile,local)
    wb=Workbook()
    readme=wb.active
    readme.title="Read first"
    readme.append(("Item","Description"))
    for field,description in [
        ("Scope","Code reference and project-selected settings; NOT a compliance certificate"),
        ("Export",report["selected_export"]),
        ("NBC source",report["code_pdf"]),
        ("V135 placement",report["v135_output_diagnostic"]["status"]),
        ("Warning count",str(len(report["warnings"]))),
    ]:
        readme.append((field,description))
    for tab,rows in report["tables"].items():
        name=tab[:31]
        ws=wb.create_sheet(name)
        ws.append(COLUMNS)
        for item in rows:
            ws.append(tuple(item[col] for col in COLUMNS))
    ws=wb.create_sheet("Warnings")
    ws.append(("Warning","Evidence needed"))
    for warning in report["warnings"]:
        ws.append((warning,"Verify latest launcher and source export"))
    style_workbook(wb)
    xlsxfile.parent.mkdir(parents=True,exist_ok=True)
    wb.save(xlsxfile)
    return jsonfile,xlsxfile


def launch(parent,export_dir):
    """[REF docs/source/components/ui/nbc105_settings_panel.py.md]
    Readable, tabbed, searchable reference UI with selected-row details.
    """
    import tkinter as tk
    from tkinter import ttk,messagebox
    from tkinter.scrolledtext import ScrolledText

    win=tk.Toplevel(parent)
    win.title("NBC 105:2025 | code, project adoption, source + output review")
    win.geometry("1330x840")
    win.minsize(940,620)
    win.transient(parent)
    frame=ttk.Frame(win,padding=12)
    frame.pack(fill="both",expand=True)
    ttk.Label(frame,text="NBC 105:2025 ANALYSIS BASIS & CURRENT MODEL EVIDENCE",
              font=("Segoe UI",15,"bold")).pack(anchor="w")
    ttk.Label(frame,text=("Code requirements, project-adopted IS provisions, numerical "
                         "mechanics and current export evidence are shown separately. "
                         "This window does not assign stiffness or execute solvers."),
              wraplength=1150).pack(anchor="w",pady=(3,8))
    export_var=tk.StringVar(value=str(export_dir))
    row=ttk.Frame(frame)
    row.pack(fill="x")
    ttk.Label(row,text="Export case:").pack(side="left")
    ttk.Entry(row,textvariable=export_var).pack(side="left",fill="x",expand=True,padx=6)
    state=tk.StringVar()
    ttk.Label(frame,textvariable=state,wraplength=1200,foreground="#875014").pack(fill="x",pady=5)
    bar=ttk.Frame(frame);bar.pack(fill="x",pady=4)
    ttk.Label(bar,text="Find within selected tab:").pack(side="left")
    query=tk.StringVar()
    ttk.Entry(bar,textvariable=query,width=36).pack(side="left",padx=(6,12))
    book=ttk.Notebook(frame)
    book.pack(fill="both",expand=True)
    detail=ScrolledText(frame,height=6,wrap="word",font=("Consolas",9))
    detail.pack(fill="x",pady=(7,4))
    detail.configure(state="disabled")
    toolrow=ttk.Frame(frame);toolrow.pack(fill="x")
    report_holder={"report":None,"tables":[]}

    def show_details(item):
        detail.configure(state="normal")
        detail.delete("1.0","end")
        for k in COLUMNS:
            detail.insert("end",k+": "+str(item.get(k,""))+"\n")
        detail.configure(state="disabled")

    def paint():
        report=report_holder["report"]
        for t in book.tabs():
            book.forget(t)
        report_holder["tables"]=[]
        for name,items in report["tables"].items():
            tab=ttk.Frame(book)
            book.add(tab,text=name)
            tab.columnconfigure(0,weight=1)
            tab.rowconfigure(0,weight=1)
            tree=ttk.Treeview(tab,columns=COLUMNS,show="headings",selectmode="browse")
            for col,width in zip(COLUMNS,(160,290,220,220,245,205,430)):
                tree.heading(col,text=col)
                tree.column(col,width=width,minwidth=100,stretch=False)
            ys=ttk.Scrollbar(tab,orient="vertical",command=tree.yview)
            xs=ttk.Scrollbar(tab,orient="horizontal",command=tree.xview)
            tree.configure(xscrollcommand=xs.set,yscrollcommand=ys.set)
            tree.grid(row=0,column=0,sticky="nsew")
            ys.grid(row=0,column=1,sticky="ns")
            xs.grid(row=1,column=0,sticky="ew")
            report_holder["tables"].append((name,tree,items))
            def on_select(event,tree=tree,items=items):
                selected=tree.selection()
                if not selected:return
                idx=int(selected[0])
                show_details(items[idx])
            tree.bind("<<TreeviewSelect>>",on_select)
        filter_rows()

    def filter_rows(*unused):
        selected=book.select()
        for name,tree,items in report_holder["tables"]:
            if selected and str(tree.master)!=str(book.nametowidget(selected)):
                continue
            tree.delete(*tree.get_children())
            needle=query.get().strip().casefold()
            for i,item in enumerate(items):
                if needle and needle not in " ".join(str(x) for x in item.values()).casefold():
                    continue
                tree.insert("","end",iid=str(i),values=tuple(item.get(c,"") for c in COLUMNS))

    def refresh():
        try:
            report=build_analysis_settings_review(export_var.get())
            report_holder["report"]=report
            diagnostic=report["v135_output_diagnostic"]
            state.set("Selected-model evidence: "
                      +("model JSON found" if report["selected_model_exists"] else "model JSON MISSING")
                      +" | V135: "+diagnostic["status"]
                      +" | outstanding input/runtime warnings: "+str(len(report["warnings"])))
            paint()
        except Exception as exc:
            messagebox.showerror("Analysis settings reference",str(exc),parent=win)

    def export():
        if report_holder["report"] is None:
            return
        try:
            paths=export_analysis_settings_review(report_holder["report"])
            messagebox.showinfo("Local reference evidence",
                "Saved in canonical 09_SOFTWARE_DIAGNOSTICS/ANALYSIS_SETTINGS:\n"
                +"\n".join(map(str,paths)),parent=win)
        except Exception as exc:
            messagebox.showerror("Could not export settings evidence",str(exc),parent=win)

    def copy_selected():
        txt=detail.get("1.0","end").strip()
        if txt:
            win.clipboard_clear()
            win.clipboard_append(txt)

    def open_clause_calculator():
        """Open local, isolated NBC clauses 1–10 calculation interface."""
        from components.nbc105.dispatch import (
            available_operations, run_operation,
            available_annex_operations, run_annex_operation)
        all_ops=available_operations()
        all_ops.update(available_annex_operations())
        dialog=tk.Toplevel(win)
        dialog.title("NBC 105:2025 | clauses 1–10 and Annexes A/B")
        dialog.geometry("840x610")
        dialog.transient(win)
        box=ttk.Frame(dialog,padding=12)
        box.pack(fill="both",expand=True)
        ttk.Label(box,text="NBC clauses 1–10 + Annex A/B | reference rules, NOT engineering acceptance",
                  font=("Segoe UI",12,"bold")).pack(anchor="w",pady=(0,8))
        ttk.Label(box,text=("Select a clause and exported operation, enter JSON named parameters, "
                           "and evaluate a code calculation. This tool never changes ETABS/OpenSees "
                           "or marks structural compliance as passed."),
                  wraplength=790).pack(anchor="w")
        picker=ttk.Frame(box)
        picker.pack(fill="x",pady=9)
        ttk.Label(picker,text="Clause").pack(side="left")
        clause_var=tk.StringVar(value="10")
        clause_box=ttk.Combobox(picker,textvariable=clause_var,
                                 values=[str(i) for i in range(1,11)]+["A","B"],
                                 state="readonly",width=6)
        clause_box.pack(side="left",padx=(6,20))
        ttk.Label(picker,text="Operation").pack(side="left")
        operation_var=tk.StringVar()
        op_box=ttk.Combobox(picker,textvariable=operation_var,
                            state="readonly",width=53)
        op_box.pack(side="left",fill="x",expand=True,padx=(6,0))
        ttk.Label(box,text="Input JSON (named parameters)").pack(anchor="w")
        payload=ScrolledText(box,height=7,wrap="none",font=("Consolas",10))
        payload.pack(fill="x",pady=(3,8))
        ttk.Label(box,text="Result (local calculation only)").pack(anchor="w")
        output=ScrolledText(box,height=13,wrap="word",font=("Consolas",10))
        output.pack(fill="both",expand=True,pady=(3,8))
        output.configure(state="disabled")
        status_var=tk.StringVar(value="Code calculation only; native ETABS acceptance remains open.")
        ttk.Label(box,textvariable=status_var,wraplength=790).pack(anchor="w")
        controls=ttk.Frame(box)
        controls.pack(fill="x",pady=8)
        def refresh_operations(*unused):
            selection=clause_var.get()
            key=int(selection) if selection.isdigit() else selection
            names=all_ops.get(key,[])
            op_box.configure(values=names)
            operation_var.set("component_amplification_factor"
                if "component_amplification_factor" in names else
                names[0] if names else "")
            payload.delete("1.0","end")
            if operation_var.get()=="component_amplification_factor":
                payload.insert("1.0",json.dumps(
                    {"building_period_s":1.0,"component_period_s":1.25},indent=2))
            elif operation_var.get()=="seismic_link_rotation_limit_rad":
                payload.insert("1.0",json.dumps({
                    "link_length_m":1.6,"mp_kNm":100,"vp_kN":100,
                    "orientation":"horizontal","section_type":"I"},indent=2))
            elif operation_var.get()=="rc_wall_detailing_minima":
                payload.insert("1.0",json.dumps({
                    "thickness_mm":600,"wall_length_mm":12000,"coupled":True,
                    "fck_mpa":30,"shear_stress_mpa":1.0,
                    "horizontal_ratio":0.0025,"vertical_ratio":0.0025,
                    "bar_diameter_mm":20,"bar_spacing_mm":200,
                    "reinforcement_curtains":2},indent=2))
            else:
                payload.insert("1.0","{}")
        def evaluate():
            try:
                arguments=json.loads(payload.get("1.0","end").strip())
                selection=clause_var.get()
                result=(run_operation(int(selection),operation_var.get(),arguments)
                        if selection.isdigit() else
                        run_annex_operation(selection,operation_var.get(),arguments))
                text=json.dumps(result,indent=2,allow_nan=False)
                status_var.set(result["status"])
            except Exception as exc:
                text="BLOCKED: "+str(exc)
                status_var.set("Invalid/incomplete input; no result approved.")
            output.configure(state="normal")
            output.delete("1.0","end")
            output.insert("1.0",text)
            output.configure(state="disabled")
        ttk.Button(controls,text="Calculate reference rule",command=evaluate).pack(side="left")
        ttk.Button(controls,text="Close",command=dialog.destroy).pack(side="right")
        clause_box.bind("<<ComboboxSelected>>",refresh_operations)
        refresh_operations()

    ttk.Button(toolrow,text="NBC clauses 1–10",command=open_clause_calculator).pack(side="left",padx=8)
    ttk.Button(toolrow,text="Refresh source and paths",command=refresh).pack(side="left")
    ttk.Button(toolrow,text="Export JSON + formatted Excel",command=export).pack(side="left",padx=8)
    ttk.Button(toolrow,text="Copy selected reference",command=copy_selected).pack(side="left")
    ttk.Button(toolrow,text="Close",command=win.destroy).pack(side="right")
    query.trace_add("write",filter_rows)
    book.bind("<<NotebookTabChanged>>",filter_rows)
    refresh()
    return win

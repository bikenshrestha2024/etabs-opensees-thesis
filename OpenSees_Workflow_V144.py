"""Numbered workflow and factual input inventory; no automatic calibration approval."""
from pathlib import Path
import json
from components.nbc105.constants import GRAVITY_M_S2
STEPS=[
('1 Export','01_MAIN_GUI.py','Read source EDB; verify model hash, counts and physical units.'),
('2 Inputs','02_INPUT_READINESS.py','Verify source identity and incomplete section, load and diaphragm evidence.'),
('3 Gravity','10_GRAVITY.py','Compare exactly matched gravity cases and support reactions with ETABS.'),
('4 Modal','11_MODAL_ULS_SLS.py','Run ULS/SLS; check X/Y/Rz mass and eigenperiods.'),
('5 Static','12_EQUIVALENT_STATIC.py','Review NBC force profiles and ULS ESM eligibility.'),
('6 MRSM','13_RESPONSE_SPECTRUM.py','Review source-matched CQC ULS/SLS response.'),
('7 Linear history','14_LINEAR_TIME_HISTORY.py','Check paired records, conversion and full duration.'),
('8 Building trial','15_BUILDING_NONLINEAR_TRIAL.py','Short exploratory trials are not complete nonlinear history.'),
('9 Reviewed nonlinear','16_NONLINEAR_REVIEWED_MODEL.py','Requires actual project reinforcement and material calibration.')
]
GUIDE={
'wall_nonlinear_materials_and_reinforcement_cited_calibrated':'Obtain wall thickness, web/boundary reinforcement ratios, bar grades, concrete strength, confinement and axial load from drawings/tests. Define ConcreteCM + SteelMPF + FSAM per wall region; benchmark cyclic force-drift and axial response against applicable experiments. Enter material file and property-to-FSAM tags in model config. Do not substitute specimen reinforcement for project data.',
'frame_concrete_and_rebar_materials_reviewed':'Read ETABS section dimensions/materials and project reinforcement schedules (bar count, diameter, cover, ties). Replace illustrative M35/Fe550 templates; verify stress units, confinement and cyclic parameters with tests/literature. Run section moment-curvature and a member cyclic benchmark.',
'is16700_initial_pdelta_plus_minus_cases_completed':'Use stability/case progression module to generate signed initial lateral PDelta cases. Solve both signs with stated gravity factors; save convergence and stability results for this exact model hash.',
'device_properties_cited_calibrated_or_devices_disabled':'If FVD/BRB is absent, document disabled scenario. Otherwise obtain manufacturer/test K,Cd,alpha or BRB core area, yield, hardening, overstrength and stroke limits; benchmark device response and check units.',
'rayleigh_damping_and_device_damping_not_double_counted':'Use nonlinear initial eigenperiods to calculate alphaM/betaK. Check modal damping over inspected modes and justify damping allocation with devices. Save coefficients, mode band and source.',
'single_element_and_wall_benchmark_checks_passed':'Run frame/member and wall cyclic tests with your selected constitutive parameters; compare strength, stiffness, pinching, degradation and energy. Attach actual benchmark output and acceptance rationale.',
'wall_opening_and_coupling_beam_mesh_reviewed':'Open 3D connectivity and wall-only view. Check each opening, pier, coupling beam, shared node and local axis against ETABS/drawings; perform mesh sensitivity.',
'area_and_frame_gravity_loads_reconciled_to_etabs':'Export ETABS story/pattern totals and reactions with matching gravity factors. Compare with Source load detail and slab formula workbook, including physical self-weight exactly once.',
'seismic_mass_reconciled_to_etabs_by_storey':'Export ETABS mass summary by story and diaphragm; compare independent total and directional masses with assembled ledger, including live-load fractions and roof treatment.',
'record_pair_units_scales_and_nbc_limits_reviewed':(
    'Use the record audit and site spectrum diagnostic. Confirm each component’s units, '
    'record time step (dt), sample count and duration, and the NBC matching/scaling band. '
    f'Convert Acc(g) to m/s² once using {GRAVITY_M_S2:g} m/s² per g. '
    'For input already in m/s², use a conversion factor of 1. '
    'Record the dimensionless motion scale separately.')}
def inventory(folder):
    folder=Path(folder);cfgpath=folder/'OpenSees_Complete_Model_Config_V118.json';cfg=json.loads(cfgpath.read_text(encoding='utf-8-sig')) if cfgpath.is_file() else {}
    facts={'folder':str(folder),'config_file':str(cfgpath),'configuration':cfg}
    for name,key in [('OpenSees_Complete_Export_Report_V118.json','assembly'),('OpenSees_Complete_Gravity_Check_V118.json','gravity')]:
        path=folder/name
        if path.is_file():facts[key]=json.loads(path.read_text(encoding='utf-8-sig'))
    data=folder/'OpenSees_Complete_Model_Data_V118.json'
    if data.is_file():
        d=json.loads(data.read_text(encoding='utf-8-sig'));facts['model_counts']={k:len(d.get(k,[])) for k in ['nodes','frames','shells','diaphragms']};facts['gravity_by_pattern_kN']=d.get('gravity_by_pattern_kN');facts['total_downward_load_kN']=d.get('total_downward_load_kN')
    from OpenSees_Readiness_GUI_V134 import available_evidence
    facts['available_evidence']=available_evidence(folder/'OpenSees_Complete_Nonlinear_Model.py');facts['how_to_obtain_missing_values']=GUIDE
    # Reuse project inputs and cited PEER values directly, but do not infer a
    # review check, auto-approve NLTHA, or alter the configured material file.
    builder=folder/'OpenSees_Complete_Nonlinear_Model.py'
    if builder.is_file():
        from components.model.readiness_available_values import collect_available_project_values
        try:
            facts['direct_available_values']=collect_available_project_values(builder)
        except (OSError,ValueError,KeyError,TypeError) as exc:
            facts['direct_available_values_error']=str(exc)
    return facts

def workflow_status(folder):
    """[REF docs/source/OpenSees_Workflow_V144.py.md]
    Candidate file presence only. Search legacy and model/state result trees.
    """
    root=Path(folder).expanduser().resolve()
    from components.inputs.output_layout import STAGE_FOLDERS
    legacy=root/"OpenSees_Analysis_Results"
    def find_candidate(stage, *patterns):
        # Do not browse unrelated stage roots, generated processing sidecars,
        # source symlinks or historical runtime snapshots.
        bases=([root] if stage=="SOURCE" else
               [root/STAGE_FOLDERS[stage],legacy])
        for base in bases:
            if not base.is_dir() or base.is_symlink():
                continue
            for pattern in patterns:
                try:
                    matches=sorted(base.glob(pattern))
                except (OSError,ValueError):
                    continue
                for match in matches:
                    if (match.is_file() and not match.is_symlink() and
                            not match.name.casefold().endswith(".processing.json")):
                        return str(match)
        return None
    sources=[
        find_candidate("SOURCE",'OpenSees_Complete_Export_Report_V118.json',
                       '01_ETABS_EXPORT/**/OpenSees_Complete_Export_Report_V118.json'),
        find_candidate("SOURCE",'OpenSees_Complete_Model_Config_V118.json',
                       '01_ETABS_EXPORT/**/OpenSees_Complete_Model_Config_V118.json'),
        find_candidate("GRAVITY",'**/OpenSees_Complete_Gravity_Check_V118.json',
                       '**/*Gravity*Check*.json','**/*Gravity*Result*.json'),
        find_candidate("MODAL",'**/NBC105_Modal_V111.json','**/*Modal*Summary*.json'),
        find_candidate("ESM",'**/NBC105_ESM_Calculation_*.json','**/*ESM*Summary*.json'),
        find_candidate("MRSM",'**/*MRSM*Summary*.json','**/*MRSM*Result*.json',
                       '**/MRSM_ULS/*.json','**/MRSM_SLS/*.json'),
        find_candidate("LTHA",'**/LTH_*/*Summary*.json','**/LTH_*/*Performance*.json'),
        find_candidate("NLTHA",'**/EXPLORATORY_*/*Summary*.json',
                       '**/BUILDING_TRIAL*/*Summary*.json'),
        find_candidate("NLTHA",'**/NLTH_*/*Summary*.json',
                       '**/*Nonlinear*Summary*.json')
    ]
    return [
        ('CANDIDATE FILE FOUND - VALIDATION REQUIRED',
         'Candidate: '+found+' | SHA, case status and completeness NOT checked.')
        if found else
        ('NO FILE DISCOVERED IN SEARCHED LOCATIONS',
         'Another export/model/state folder may contain results; absence does not prove no run.')
        for found in sources
    ]
def workflow_evidence_status(folder):
    """[REF docs/source/OpenSees_Workflow_V144.py.md]
    Surface saved-case provenance, without mislabeling file presence as approval.

    Keep the original workflow_status() candidate lookup for compatibility.
    This GUI-only layer checks canonical run manifests, current model bytes and
    whether a selected file is a review snapshot rather than solver output.
    A completed manifest is NOT proof that output data are complete/converged.
    """
    import hashlib
    from components.inputs.output_contract import inspect_case_manifest
    from components.inputs.output_layout import STAGE_FOLDERS
    root=Path(folder).expanduser().resolve()
    statuses=workflow_status(root)
    model=root/"OpenSees_Complete_Model_Data_V118.json"
    source_sha=(hashlib.sha256(model.read_bytes()).hexdigest()
                if model.is_file() and not model.is_symlink() else None)
    stages={2:"GRAVITY",3:"MODAL",4:"ESM",5:"MRSM",
            6:"LTHA",7:"NLTHA",8:"NLTHA"}
    reviewed=[]
    for index,(state,description) in enumerate(statuses):
        if index not in stages or not state.startswith("CANDIDATE"):
            reviewed.append((state,description))
            continue
        label=stages[index]
        # workflow_status returns a single selected path after "Candidate: ".
        path=Path(description.split("Candidate: ",1)[1].split(" | SHA",1)[0])
        stage_dir=root/STAGE_FOLDERS[label]
        try:
            path.relative_to(stage_dir)
        except ValueError:
            reviewed.append((state,description+" | LEGACY LOCATION: no run manifest verification"))
            continue
        if "REVIEW_SNAPSHOTS" in path.parts or "07_EXPORT_ZIP" in path.parts:
            reviewed.append(("REVIEW SNAPSHOT ONLY - NOT EXECUTED",
                             "Candidate: "+str(path)+" | This is review/export evidence, "
                             "not a solver run. Select completed stage RUNS evidence."))
            continue
        run=next((parent for parent in path.parents
                  if parent.parent.name=="RUNS" or (
                      len(parent.parents)>2 and parent.parents[2].name=="RUNS")),None)
        # Recognize only canonical <stage>/RUNS/<state>/<case>/<run-id>/02_RESULTS/file
        try:
            relative=path.relative_to(stage_dir)
            parts=relative.parts
            if len(parts)<6 or parts[0]!="RUNS" or parts[4]!="02_RESULTS":
                raise ValueError("Not canonical result path")
            run=stage_dir.joinpath(*parts[:4])
        except ValueError:
            reviewed.append((state,description+" | STAGE FILE NOT A CANONICAL SOLVER RESULT"))
            continue
        identity=inspect_case_manifest(run,expected_stage=label)
        if not identity["valid"]:
            reviewed.append(("CANDIDATE - RUN MANIFEST INCOMPLETE",
                             "Candidate: "+str(path)+" | Manifest issues: "+
                             ", ".join(identity["issues"])+" | NOT engineering approved"))
            continue
        manifest=json.loads((run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json").read_text(encoding="utf-8-sig"))
        recorded=manifest.get("model_sha256")
        if not source_sha or not recorded or recorded.lower()!=source_sha:
            reviewed.append(("CANDIDATE - MODEL IDENTITY MISMATCH",
                             "Candidate: "+str(path)+
                             " | Source/model SHA missing or differs from selected model; "
                             "do not reuse this result."))
            continue
        if identity["solver_status"]!="COMPLETED_SOLVER_ONLY":
            reviewed.append(("CANDIDATE - SOLVER COMPLETION NOT VERIFIED",
                             "Candidate: "+str(path)+" | MODEL SHA MATCHED; manifest "
                             "solver status="+str(identity["solver_status"])+
                             ". No numeric completeness verified."))
            continue
        reviewed.append(("MANIFEST COMPLETED - NUMERICAL EVIDENCE UNVERIFIED",
                         "Candidate: "+str(path)+" | MODEL SHA MATCHED; valid run "
                         "manifest and COMPLETED_SOLVER_ONLY recorded. This does not "
                         "validate response content, convergence, structural equivalence "
                         "or engineering approval."))
    return reviewed


def launch(parent=None,folder=None):
    import tkinter as tk
    from tkinter import ttk,filedialog,messagebox
    win=tk.Toplevel(parent) if parent else tk.Tk();win.title('1–9 workflow | available inputs and how to obtain values');win.geometry('1100x800')
    path=tk.StringVar(value=str(folder or ''));bar=ttk.Frame(win);bar.pack(fill='x');ttk.Entry(bar,textvariable=path).pack(side='left',fill='x',expand=True)
    ttk.Button(bar,text='Select export',command=lambda:path.set(filedialog.askdirectory(parent=win))).pack(side='left')
    tabs=ttk.Notebook(win);tabs.pack(fill='both',expand=True)
    def page(title):
        frame=ttk.Frame(tabs);tabs.add(frame,text=title);text=tk.Text(frame,wrap='word');scroll=ttk.Scrollbar(frame,command=text.yview);text.configure(yscrollcommand=scroll.set);scroll.pack(side='right',fill='y');text.pack(fill='both',expand=True);return text
    guide=page('1–9 run order')
    values=page('Available values / provenance');missing=page('Obtain missing values');missing.insert('end','\n\n'.join(k.replace('_',' ')+'\n'+v for k,v in GUIDE.items()))
    def refresh():
        if not path.get():return
        try:
            facts=inventory(path.get());values.delete('1.0','end');values.insert('end',json.dumps(facts,indent=2))
            statuses=workflow_evidence_status(path.get());guide.delete('1.0','end');guide.insert('end','Workflow status checks canonical run identity where available, but numerical completion and engineering acceptance require independent evidence. Linear time history is optional for nonlinear execution.\n\n'+'\n\n'.join(a+' — '+b+'\n'+statuses[i][0]+' | '+statuses[i][1]+'\n'+c for i,(a,b,c) in enumerate(STEPS)));return facts
        except Exception as exc:messagebox.showerror('Inventory',str(exc),parent=win)
    def export():
        facts=refresh()
        if facts:
            from datetime import datetime
            from uuid import uuid4
            root=Path(path.get()).expanduser().resolve()
            stage=root/'01_ETABS_EXPORT'
            manifest=stage/'00_MANIFEST'
            target_dir=manifest/'INPUT_READINESS'
            if any(p.is_symlink() for p in (stage,manifest,target_dir)):
                raise ValueError('Refusing linked workflow output folder')
            target_dir.mkdir(parents=True,exist_ok=True)
            target=target_dir/('Available_Inputs_And_Steps_V144_'
                +datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'_'+uuid4().hex[:8]+'.json')
            with target.open('x',encoding='utf-8') as stream:
                json.dump(facts,stream,indent=2)
            messagebox.showinfo('Saved',str(target),parent=win)
    ttk.Button(bar,text='Refresh available data',command=refresh).pack(side='left');ttk.Button(bar,text='Export inventory + steps',command=export).pack(side='left');refresh()
    if parent is None:win.mainloop()
    return win

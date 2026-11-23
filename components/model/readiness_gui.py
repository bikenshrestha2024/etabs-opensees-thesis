"""Model-bound readiness drafts and transparent missing prerequisites."""
from pathlib import Path
import json,hashlib


def _is_reviewed_evidence_reference(value):
    """Only reviewer-supplied source references qualify, never UI placeholders.

    Presence of a discovered local result is not a reviewed source approval.
    This syntactic guard cannot independently authenticate a human review,
    experiment or nonlinear source material calibration.
    """
    if not isinstance(value,str) or not value.strip():
        return False
    normalized=value.strip().casefold()
    return not normalized.startswith((
        "available for review:",
        "input / review required:",
        "review required:",
        "missing:",
        "not configured",
    ))


def review_metadata_problems(checks, evidence, reviewers, review_dates):
    """[REF docs/source/components/model/readiness_gui.py.md]
    Validate human-entered reviewer / ISO calendar date for checked items.
    This is a UI documentation gate, not independent source certification.
    """
    from datetime import date
    issues=[]
    for key,flag in checks.items():
        if not flag:
            continue
        if not _is_reviewed_evidence_reference(evidence.get(key, '')):
            issues.append(key+': reviewer-cited evidence reference is required')
        who=str(reviewers.get(key,'')).strip()
        when=str(review_dates.get(key,'')).strip()
        if not who:
            issues.append(key+': named reviewer is required')
        try:
            if not when or date.fromisoformat(when).isoformat()!=when:
                raise ValueError('not an ISO date')
        except ValueError:
            issues.append(key+': review date must be ISO YYYY-MM-DD')
    return issues


def prepare(model_script,template=None):
    """Create or reuse the model-bound UNAPPROVED draft (shared non-GUI implementation)."""
    from components.model.readiness import bind_readiness_draft
    model=Path(model_script).resolve()
    if template is None:
        import components.model.readiness as _r
        for root in (Path(_r.__file__).resolve().parents[2],model.parent,Path.cwd()):
            template=root/'OpenSees_Model_Readiness_Template_V116.json'
            if template.is_file():break
        else:raise FileNotFoundError('OpenSees_Model_Readiness_Template_V116.json not found')
    return bind_readiness_draft(template,model)


def available_evidence(model_script, *, with_metadata=False):
    """Inventory saved facts; presence never certifies review or calibration.

    with_metadata=True additionally returns a local-only mapping of requirement
    keys to source paths. Historical GUI hint strings remain unchanged.
    """
    model=Path(model_script).resolve();folder=model.parent;out=folder/'OpenSees_Analysis_Results';result={};discovered={}
    from components.inputs.project_workbooks import analysis_output_folder
    def add(key,paths,note):
        found=[str(p.resolve()) for p in paths if p.is_file()]
        if found:
            result[key]='AVAILABLE FOR REVIEW: '+note+' | '+'; '.join(found)
            discovered[key]=found
    add('etabs_topology_and_story_mapping_reviewed',[folder/'OpenSees_Complete_Model_Data_V118.json',folder/'OpenSees_Complete_Story_Masters_V118.csv'],'source geometry / story mapping')
    add('wall_opening_and_coupling_beam_mesh_reviewed',[folder/'OpenSees_Area_Section_Assignment_Audit.json'],'area geometry audit; opening/coupling mesh still needs review')
    add('area_and_frame_gravity_loads_reconciled_to_etabs',[folder/'OpenSees_Load_Conversion_Audit.json',folder/'Gravity_Storey_Load_Breakdown_V131.json'],'load inventory only; load-set completeness and ETABS comparison required')
    add('seismic_mass_reconciled_to_etabs_by_storey',[folder/'OpenSees_Complete_Model_Data_V118.json'],'nodal mass inventory; independent ETABS reconciliation required')
    add('support_conditions_and_foundation_assumptions_reviewed',[folder/'OpenSees_Source_Model_Metadata_V118.json'],'exported restraints; foundation assumptions not certified')
    add('p_delta_and_gravity_preload_completed',[folder/'OpenSees_Complete_Gravity_Check_V118.json'],'saved gravity result; verify nonlinear model identity and P-Delta basis')
    modal_stage=folder/'04_MODAL'/'RUNS'
    modal_canonical=[
        item for state in ('ULS','SLS')
        for item in sorted(modal_stage.glob(
            state+'/*/*/02_RESULTS/NBC105_Modal_V111.json'))[:30]
    ]
    add('modal_periods_modes_and_mass_participation_reviewed',[
        analysis_output_folder(folder,state)/('Modal_'+state)/'NBC105_Modal_V111.json'
        for state in ('ULS','SLS')
    ]+[out/'Modal_ULS/NBC105_Modal_V111.json',out/'Modal_SLS/NBC105_Modal_V111.json']
      +modal_canonical,
        'saved elastic modal results; not nonlinear initial-stiffness validation')
    add('brace_fvd_brb_case_matches_selected_scenario',[folder/'OpenSees_Complete_Model_Config_V118.json'],'configuration available; scenario needs review')
    add('slab_and_diaphragm_idealization_compatible',[folder/'OpenSees_Complete_Model_Config_V118.json',folder/'LOAD_PATH_AND_DIAPHRAGM_AUDIT_V130.json'],'configured slab modifiers and constraints; compatibility needs engineering review')
    pdelta_stage=folder/'02_GRAVITY'
    pdelta_candidates=(list(out.glob('*PDelta*.json'))
                       +list(pdelta_stage.glob('RUNS/**/*PDelta*.json'))[:50])
    add('is16700_initial_pdelta_plus_minus_cases_completed',
        pdelta_candidates,'saved files only; verify both signed cases and convergence')
    lth_stage=folder/'06_LINEAR_TIME_HISTORY'
    add('record_pair_units_scales_and_nbc_limits_reviewed',
        list(out.glob('LTH*/*RunConfig*.json'))
        +list(lth_stage.glob('RUNS/*/*/*/00_INPUT_SOURCE/*RunConfig*.json'))[:50],
        'saved input configuration; unit/spectrum compatibility requires review')
    cfg=folder/'OpenSees_Complete_Model_Config_V118.json'
    if cfg.is_file():
        config=json.loads(cfg.read_text(encoding='utf-8-sig'));material=config.get('nonlinear_materials_file')
        if material:
            path=Path(material);path=path if path.is_absolute() else folder/path
            add('wall_nonlinear_materials_and_reinforcement_cited_calibrated',[path],'material definitions found; calibration not inferred')
            add('frame_concrete_and_rebar_materials_reviewed',[path],'material definitions found; reinforcement calibration not inferred')
    # The exploratory builder constructs these laws dynamically; its
    # Research_Material_Assignment is NOT a model-bound production material
    # file nor an experimentally calibrated project reinforcement schedule.
    historical=(list(out.glob('**/Research_Material_Assignment_V161.json'))
        +list((folder/'07_NONLINEAR_TIME_HISTORY').glob(
            'RUNS/**/Research_Material_Assignment_V161.json'))[:50])
    if historical:
        result['research_material_transfer_reference_only']=(
            'AVAILABLE FOR REVIEW ONLY: exploratory research-material assignment, '
            'not a calibrated production mapping | '+str(historical[-1]))
    return (result,discovered) if with_metadata else result


def evidence_inventory(model_script):
    """[REF docs/source/components/model/readiness_gui.py.md]
    Read-only evidence index; source existence and SHA are NOT review or approval.
    
    Modal results are compared to the serialized model JSON SHA, not the
    nonlinear Python-builder SHA (different files with different identities).
    """
    from components.model.readiness import READINESS_CHECK_KEYS
    model=Path(model_script).expanduser().resolve()
    if not model.is_file():
        raise FileNotFoundError("No selected nonlinear builder: "+str(model))
    serialized=model.with_name("OpenSees_Complete_Model_Data_V118.json")
    payload_sha=hashlib.sha256(serialized.read_bytes()).hexdigest() if serialized.is_file() else None
    hints,sources=available_evidence(model,with_metadata=True)
    output={}
    for key in READINESS_CHECK_KEYS:
        items=[]
        for raw in sources.get(key,[]):
            path=Path(raw)
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            identity="NOT_ASSERTED"
            if path.name.startswith("NBC105_Modal") and path.suffix.lower()==".json":
                try:
                    source=json.loads(path.read_text(encoding="utf-8-sig"))
                    claim=source.get("model_sha256") if isinstance(source,dict) else None
                except (OSError,ValueError,UnicodeError):
                    claim=None
                identity=("MATCHING_SERIALIZED_MODEL" if payload_sha and claim==payload_sha
                          else "MISMATCH" if payload_sha and claim
                          else "UNVERIFIED_NO_MODEL_HASH")
            items.append({"path":str(path),"sha256":digest,"bytes":path.stat().st_size,
                          "model_identity":identity})
        output[key]={"status":"AVAILABLE_NOT_REVIEWED" if items else "MISSING",
                     "files":items,"review_status":"HUMAN_REVIEW_REQUIRED",
                     "hint":hints.get(key,"No source evidence found")}
    return {"schema":"NLTHA_EVIDENCE_INVENTORY_V1",
            "model_script":str(model),
            "model_script_sha256":hashlib.sha256(model.read_bytes()).hexdigest(),
            "serialized_model_sha256":payload_sha,
            "approved_for_nltha":False,"approval_unchanged":True,
            "purpose":"DISCOVERY_ONLY_NOT_ANALYSIS_OR_ENGINEERING_APPROVAL",
            "checks":output}


def launch(parent,model_script,readiness_variable):
    import tkinter as tk
    from tkinter import ttk,messagebox
    model=Path(model_script).resolve();path=prepare(model);data=json.loads(path.read_text(encoding='utf-8-sig'))
    if str(Path(data['model_script']).resolve())!=str(model):raise ValueError('Draft bound to another model; select the correct draft')
    # prepare() keeps a draft whose model SHA is unchanged even if the config, material file or FSAM tags
    # changed since approval: reset approval/checks (pure helper) and persist before showing the form.
    from components.model.readiness import rebind_if_binding_changed,binding_change_notice
    binding_mismatches=rebind_if_binding_changed(data,model)
    if binding_mismatches:path.write_text(json.dumps(data,indent=2),encoding='utf-8')
    win=tk.Toplevel(parent);win.title('Nonlinear model readiness — evidence and model binding');win.geometry('1180x820');readiness_variable.set(str(path))
    ttk.Label(win,text='Selected nonlinear builder: '+str(model)+'\nChecklist: '+str(path)+'\nThis is a draft, not automatic approval. A source/material model must exist and checks require real evidence.',wraplength=1120).pack(anchor='w')
    cfg=model.with_name('OpenSees_Complete_Model_Config_V118.json')
    if cfg.exists():
        config=json.loads(cfg.read_text(encoding='utf-8-sig'));ttk.Label(win,text='PRODUCTION MODEL: nonlinear_parameters_reviewed='+str(config.get('nonlinear_parameters_reviewed'))+'; approved model-bound materials file='+str(config.get('nonlinear_materials_file') or 'NOT CONFIGURED')+'; wall FSAM property mappings='+str(len(config.get('nonlinear_wall_fsam_tags',{})))+'. Exploratory PEER materials are assigned dynamically in a separate model and cannot be treated as approved source reinforcement.',wraplength=1100,foreground='#9a3e1d').pack(anchor='w')
    from components.model.readiness import diagnose_nonlinear_readiness,material_prerequisite_notice
    notice=material_prerequisite_notice(diagnose_nonlinear_readiness({'model_script':str(model),'model_readiness_json':str(path)}))
    if notice:ttk.Label(win,text=notice,wraplength=1100,foreground='#9a3e1d').pack(anchor='w')
    change_notice=binding_change_notice(binding_mismatches)
    if change_notice:ttk.Label(win,text=change_notice,wraplength=1100,foreground='#b00020').pack(anchor='w')
    from components.model.readiness import runtime_copy_notice
    stale_notice=runtime_copy_notice(model)
    if stale_notice:ttk.Label(win,text=stale_notice,wraplength=1100,foreground='#b00020').pack(anchor='w')
    from OpenSees_Research_UI_V123 import scrollable_form
    footer=ttk.Frame(win);footer.pack(side='bottom',fill='x',padx=8,pady=8)
    body=ttk.Frame(win);body.pack(fill='both',expand=True);form=scrollable_form(body,min_width=850)
    checks={};evidence={};reviewers={};review_dates={};hints={}
    from components.model.readiness import READINESS_CHECK_KEYS
    checked_data=data.get('checks') or {};raw_evidence=data.get('evidence') or {}
    previous_reviews=data.get('review_metadata') or {}
    for key in READINESS_CHECK_KEYS:
        record=previous_reviews.get(key,{}) if isinstance(previous_reviews,dict) else {}
        checks[key]=tk.BooleanVar(value=checked_data.get(key) is True)
        evidence[key]=tk.StringVar(value=raw_evidence.get(key,'') if isinstance(raw_evidence,dict) else '')
        reviewers[key]=tk.StringVar(value=record.get('reviewer',''))
        review_dates[key]=tk.StringVar(value=record.get('reviewed_on',''))
        hints[key]=tk.StringVar(value='No evidence indexed; refresh discovery.')
        ttk.Checkbutton(form,text=key.replace('_',' '),variable=checks[key]).pack(anchor='w',pady=(5,0))
        ttk.Label(form,text='Available evidence (not reviewed, does not fill sign-off):').pack(anchor='w')
        ttk.Entry(form,textvariable=hints[key],state='readonly').pack(fill='x')
        ttk.Label(form,text='Reviewer-cited source / calculation / evidence reference:').pack(anchor='w')
        ttk.Entry(form,textvariable=evidence[key]).pack(fill='x')
        person=ttk.Frame(form);person.pack(fill='x')
        ttk.Label(person,text='Reviewer').pack(side='left',padx=(0,4))
        ttk.Entry(person,textvariable=reviewers[key],width=35).pack(side='left',padx=(0,18))
        ttk.Label(person,text='Review date (YYYY-MM-DD)').pack(side='left',padx=(0,4))
        ttk.Entry(person,textvariable=review_dates[key],width=16).pack(side='left')
    def refresh_evidence():
        # Discovery is not sign-off: NEVER set editable evidence/reviewer fields.
        available=available_evidence(model)
        for key,var in hints.items():
            var.set(available.get(key,'INPUT / REVIEW REQUIRED: No source-specific evidence discovered.'))
        win._available_evidence=available
        return len(available)
    ttk.Button(footer,text='Refresh evidence suggestions (does not change review)',command=refresh_evidence).pack(anchor='w')
    def export_evidence_index():
        from tkinter import filedialog
        try:
            index=evidence_inventory(model)
            target=filedialog.asksaveasfilename(parent=win,title='Save local unapproved readiness evidence index',
                initialfile='NLTHA_Readiness_Evidence_UNAPPROVED.json',
                defaultextension='.json',filetypes=[('JSON','*.json')])
            if not target:return
            Path(target).write_text(json.dumps(index,indent=2),encoding='utf-8')
            messagebox.showinfo('Local evidence index saved',
                'Discovery only: source hashes and model identity recorded; no check approved.\\n'+str(target),parent=win)
        except Exception as exc:
            messagebox.showerror('Evidence index export',str(exc),parent=win)
    ttk.Button(footer,text='Export local evidence index JSON (unapproved)',
               command=export_evidence_index).pack(anchor='w')

    def load_available_project_values():
        """Read real project/PEER research numbers, never tick human review."""
        from tkinter.scrolledtext import ScrolledText
        from components.model.readiness_available_values import collect_available_project_values
        try:
            snapshot=collect_available_project_values(model)
            viewer=tk.Toplevel(win)
            viewer.title("Available project and PEER literature values — UNAPPROVED")
            viewer.geometry("1040x720")
            ttk.Label(viewer,text=("Source values are taken directly from this selected model's export "
                "and the installed cited PEER research cards. No checklist item or material-config "
                "approval is changed. Missing inputs remain explicit."),
                wraplength=990,foreground="#8a3412").pack(anchor='w',padx=9,pady=8)
            area=ScrolledText(viewer,wrap='none',font=('Consolas',10))
            area.pack(fill='both',expand=True,padx=8,pady=4)
            area.insert('1.0',json.dumps(snapshot,indent=2))
            area.configure(state='disabled')
            def save_values():
                from components.model.readiness_available_values import attach_available_values_to_draft
                try:
                    saved=attach_available_values_to_draft(model,path)
                    # Reflect only this unapproved snapshot in GUI's local state.
                    data['available_project_values']=snapshot
                    messagebox.showinfo("Existing values bound to draft",
                        "Stored source-backed values in the current UNAPPROVED readiness draft.\n"+
                        str(saved)+"\n\nNo material or checklist review flags changed.",parent=viewer)
                except Exception as exc:
                    messagebox.showerror("Cannot attach existing values",str(exc),parent=viewer)
            ttk.Button(viewer,text="Use these available values in UNAPPROVED draft",
                       command=save_values).pack(anchor='w',padx=9,pady=9)
        except Exception as exc:
            messagebox.showerror("Source values unavailable",str(exc),parent=win)
    ttk.Button(footer,text='Load existing project + PEER research values (no manual re-entry)',
               command=load_available_project_values).pack(anchor='w')

    ttk.Button(footer,text='Available parameter values + how to obtain missing inputs',command=lambda:__import__('OpenSees_Workflow_V144').launch(win,model.parent)).pack(anchor='w')
    refresh_evidence()
    approved=tk.BooleanVar(value=data.get('approved_for_nltha') is True);ttk.Checkbutton(footer,text='I have reviewed the evidence and approve this specific nonlinear model for NLTHA',variable=approved).pack(anchor='w')
    def rebind_draft():
        data.update(model_script_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),approved_for_nltha=False,checks={k:False for k in checks})
        from components.model.readiness import record_binding
        record_binding(data,model)
        for var in checks.values():var.set(False)
        approved.set(False)
        path.write_text(json.dumps(data,indent=2),encoding='utf8')
        messagebox.showinfo('Draft rebound','Current script fingerprint saved. Existing evidence retained; approvals reset because the model changed.',parent=win)
    ttk.Button(footer,text='Rebind changed model as UNAPPROVED draft',command=rebind_draft).pack(anchor='w')
    def save():
        try:
            issues=review_metadata_problems(
                {k:v.get() for k,v in checks.items()},
                {k:v.get() for k,v in evidence.items()},
                {k:v.get() for k,v in reviewers.items()},
                {k:v.get() for k,v in review_dates.items()})
            if issues:raise ValueError('Human source review is incomplete:\\n'+'\\n'.join(issues))
            if approved.get() and not all(v.get() for v in checks.values()):raise ValueError('Approval requires every prerequisite checked and evidenced')
            if approved.get():
                from components.model.readiness import approval_binding_problems
                bp=approval_binding_problems(model)
                if bp:raise ValueError('Approval cannot be bound: '+'; '.join(bp))
            late=rebind_if_binding_changed(data,model)  # inputs changed while this window was open
            if late:
                for var in checks.values():var.set(False)
                approved.set(False);path.write_text(json.dumps(data,indent=2),encoding='utf-8')
                raise ValueError(binding_change_notice(late)+'\nNothing was approved; review and save again.')
            data.update(model_script=str(model),model_script_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),approved_for_nltha=approved.get(),checks={k:v.get() for k,v in checks.items()},evidence={k:v.get().strip() for k,v in evidence.items()},review_metadata={k:{'reviewer':reviewers[k].get().strip(),'reviewed_on':review_dates[k].get().strip()} for k in checks})
            from components.model.readiness import record_binding
            record_binding(data,model);path.write_text(json.dumps(data,indent=2),encoding='utf-8');readiness_variable.set(str(path));messagebox.showinfo('Readiness saved','Draft saved. Missing model/material prerequisites are not bypassed.',parent=win)
        except Exception as e:messagebox.showerror('Readiness input',str(e),parent=win)
    ttk.Button(footer,text='Save model-bound checklist',command=save).pack(anchor='w')
    def prepare_peer_draft():
        """[REF R01 PEER 2015/12; docs/source/components/nonlinear_time_history/material_draft.py.md]
        Create research-only PEER wall material and FSAM mappings as a copy.
        Does not promote the draft to a production NLTHA approval.
        """
        from datetime import datetime
        from tkinter import messagebox
        from components.nonlinear_time_history.material_draft import prepare as create_draft
        folder=model.parent
        from components.inputs.output_layout import owned_run_destination
        destination=owned_run_destination(
            folder,"SOFTWARE_DIAGNOSTICS","PEER_RESEARCH_MATERIAL_DRAFT")/(
            'PEER_2015_12_RESEARCH_MATERIAL_DRAFT_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
        try:
            card=create_draft(folder,destination,
                basis='PEER_2015_12_SINGLE_SOURCE',
                steelmpf_transition='PEER_APPENDIX_EXACT')
            messagebox.showinfo('Research material draft created',
                'CREATED UNAPPROVED COPY ONLY: '+str(destination)+
                '\\n\\nIt contains Research_Wall_Materials.py, '
                'Research_Wall_Parameters.json and source geometry/config copies. '
                'Source EDB and production export remain unchanged. '
                'This does NOT complete material calibration, reinforcement '
                'schedules, P-Delta or thesis readiness.\\n\\n'
                'Basis: '+str(card['basis']),parent=win)
        except Exception as exc:
            messagebox.showerror('Cannot create PEER research material draft',
                                 str(exc),parent=win)
    ttk.Button(footer,text='Create isolated PEER 2015/12 material/FSAM draft (not approval)',
               command=prepare_peer_draft).pack(anchor='w')
    ttk.Button(footer,text='Open separate literature demo / material cards',command=lambda:__import__('OpenSees_Literature_Demo_GUI_V137').launch(win)).pack(anchor='w')
    win._readiness_checks=checks;win._readiness_evidence=evidence
    return win

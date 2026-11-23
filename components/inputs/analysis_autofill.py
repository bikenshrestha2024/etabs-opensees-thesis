"""Populate known inputs with provenance; never reinterpret empirical T as eigen T."""

__release__ = '134'
from pathlib import Path
import hashlib
import json
import math


def _runtime_repo_root():
    """Repository/runtime root in both direct-module and exec facade contexts.

    Root-level compatibility facades set _component_source to the actual
    components/<package>/<module>.py. __file__ alone then names the facade
    and its parents[2] would point outside the active project.
    """
    from components.shared.repository_paths import runtime_repo_root
    return runtime_repo_root(__file__, globals().get("_component_source"))



def workbook_adopted_period(height_m, aw_m2, rayleigh_s, factor=1.25):
    """[REF NBC105-2025 §5.1, printed p. 28]
    Return ``(period_s, note)``: lesser of Rayleigh and 1.25 x empirical.

    A workbook factor other than the fixed NBC 105:2025 §5.1.3 value of 1.25
    is not applied: the period is None and the note is a DEVIATION message.
    """
    from components.nbc105.clause_05_dynamic_characteristics import (
        amplified_period_s, empirical_period_s, period_factor_deviation)
    deviation = period_factor_deviation(factor)
    if deviation:
        return None, deviation + '; period field left unset'
    empirical = empirical_period_s(height_m, 'concrete shear-wall', aw_m2)
    return min(amplified_period_s(empirical), float(rayleigh_s)), None


def matching_modal_reference(folder, state, model_sha, *,
                             support_case=None, seismic_mass_policy=None):
    """[REF docs/source/components/inputs/analysis_autofill.py.md]
    Read a saved modal result only for this model, state and selected policies.

    Both support restraints and seismic mass operator affect eigenmodes.
    A legacy result without required policy evidence is not compatible with
    a current LTHA selected policy; no filename/mtime fallback can override it.
    """
    from components.inputs.output_layout import result_roots
    state=str(state).upper()
    if state not in ("ULS","SLS") or not model_sha:
        return None
    candidates=set()
    for root in result_roots(folder,stages=("MODAL",)):
        candidates.update(root.rglob("NBC105_Modal_V111.json"))
        candidates.update(root.rglob(f"NBC105_Modal_{state}_V127.json"))
    excluded={"review_snapshots","organized_results","seismic_review_packages",
              "07_export_zip","90_upload_packages"}
    eligible=[]
    for path in candidates:
        if any(part.casefold() in excluded for part in path.parts):
            continue
        try:
            data=json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError,ValueError,TypeError):
            continue
        if (not isinstance(data,dict)
                or data.get("model_sha256")!=model_sha
                or data.get("limit_state")!=state
                or not isinstance(data.get("rows"),list)
                or not data["rows"]):
            continue
        if support_case is not None:
            from components.model.support_case_contract import normalize_support_case
            selected=normalize_support_case(support_case)
            evidence=data.get("selected_support_case_verification")
            if (not isinstance(evidence,dict)
                    or evidence.get("selected_profile")!=selected
                    or evidence.get("status")!="MATCHED_SELECTED_CASE_NOT_NATIVE_EQUIVALENT"):
                continue
        if seismic_mass_policy is not None:
            selected_mass=str(seismic_mass_policy).strip().upper()
            if (selected_mass not in ("SOURCE_DISTRIBUTED","STORY_LUMPED_NBC")
                    or data.get("seismic_mass_policy")!=selected_mass):
                continue
        eligible.append(path)
    return (max(eligible,key=lambda p:(p.stat().st_mtime_ns,str(p)))
            if eligible else None)


def populate_linear(gui, folder):
    from OpenSees_Project_Inputs_V123 import import_project_inputs
    folder=Path(folder)
    for attr in ('t1x','t1y','p1','p2','tnx','tny'):getattr(gui,attr).set('')
    inputs=import_project_inputs(_runtime_repo_root(),folder,gui.ls.get())
    gui.project_input_audit=inputs;v=inputs['values']
    for axis in ('x','y'):
        value=v.get('workbook_adopted_t'+axis)
        if value is not None:
            getattr(gui,'t1'+axis).set(str(value));inputs['notes'].append(axis.upper()+' T1 imported as workbook adopted design-period reference; confirm for this current model.')
    datafile=folder/'OpenSees_Complete_Model_Data_V118.json'
    if datafile.is_file():
        data=json.loads(datafile.read_text(encoding='utf-8-sig'))
        H=max(p[2] for p in data['nodes'].values())-data['base_z_m']
        for axis in ('x','y'):
            if 'aw'+axis in v and 'rayleigh_t'+axis in v:
                period,deviation=workbook_adopted_period(H,v['aw'+axis],v['rayleigh_t'+axis],v.get('period_factor',1.25))
                if deviation:
                    getattr(gui,'t1'+axis).set('')
                    inputs['notes'].append(axis.upper()+' '+deviation)
                else:getattr(gui,'t1'+axis).set(f'{period:.9g}')
    model_sha=hashlib.sha256(datafile.read_bytes()).hexdigest() if datafile.is_file() else None
    modal=matching_modal_reference(
        folder,gui.ls.get(),model_sha,
        support_case=gui.support_case.get() if hasattr(gui,"support_case") else "PHYSICAL_32",
        seismic_mass_policy=(gui.seismic_mass_policy.get()
                             if hasattr(gui,"seismic_mass_policy")
                             else "SOURCE_DISTRIBUTED"))
    if modal is None:
        inputs['notes'].append(
            'NO MATCHING SAVED MODAL REFERENCE: source model SHA and limit state '
            'and selected support/mass policy must match; no unrelated elastic Tn/damping reference imported.')
    if modal is not None and modal.is_file() and datafile.is_file():
        result=json.loads(modal.read_text(encoding='utf-8-sig'))
        inputs['notes'].append('Modal input reference: '+str(modal))
        from OpenSees_Model_Audit_V130 import implementation_digest
        reference_sha=result.get('implementation_sha256')
        compatibility_path=_runtime_repo_root()/'NUMERICAL_INPUT_COMPATIBILITY_V132.json'
        compatibility=json.loads(compatibility_path.read_text(encoding='utf-8-sig')) if compatibility_path.is_file() else {}
        from OpenSees_Model_Audit_V130 import modal_numeric_digest
        implementation_matches=result.get('modal_numeric_sha256')==modal_numeric_digest(_runtime_repo_root()) or result.get('modal_numeric_sha256') in compatibility or reference_sha==implementation_digest(_runtime_repo_root()) or reference_sha in compatibility
        if reference_sha in compatibility:inputs['notes'].append('Imported known-compatible V'+str(compatibility[reference_sha]['release'])+' modal reference with exact model-payload match; the transient runner rechecks fresh eigenmode damping.')
        state_matches=result.get('limit_state','ULS')==gui.ls.get()
        model_matches=result.get('model_sha256')==model_sha and model_sha is not None
        gui.modal_reference_status=dict(path=str(modal),state_matches=state_matches,model_matches=model_matches,implementation_matches=bool(implementation_matches),usage='VERIFIED ELASTIC REFERENCE' if state_matches and model_matches and implementation_matches else 'UNVERIFIED ELASTIC STARTING REFERENCE; nonlinear initial stiffness not validated')
        inputs['modal_reference_status']=gui.modal_reference_status
        if not (state_matches and model_matches and implementation_matches):
            # [REF docs/source/components/inputs/analysis_autofill.py.md]
            # Periods of a different geometry/stiffness code or limit state
            # cannot be used to calibrate production nonlinear Rayleigh damping.
            inputs['notes'].append(
                'ELASTIC MODAL SOURCE REJECTED for Tn/damping: model SHA, state, '
                'or numerical-implementation fingerprint does not match. '
                'No TnX/TnY, damping P1/P2 auto-populated. Rerun Modal on the '
                'exact selected model and check NONLINEAR initial-tangent modes.')
        else:
            rows=[r for r in result.get('rows',[]) if math.isfinite(float(r.get('period_s',0))) and float(r.get('period_s',0))>0]
            for axis in ('x','y'):
                reached=next((r for r in rows if float(r.get('U'+axis.upper()+'_cumulative_percent',0) or 0)>=90),None)
                if reached:
                    getattr(gui,'tn'+axis).set(str(reached['period_s']))
                    inputs['notes'].append(axis.upper()+' Tn from MODE '+str(reached.get('mode','?'))+
                        ' reaching 90% cumulative '+axis.upper()+' mass ('+
                        str(reached.get('U'+axis.upper()+'_cumulative_percent'))+
                        '%). Elastic-modal reference only; independently recompute nonlinear initial tangent.')
                else:inputs['notes'].append(axis.upper()+' 90% mass threshold absent; directional Tn remains required.')
            selected=rows[:int(gui.nmodes.get())]
            if selected:
                gui.p1.set(str(max(float(r['period_s']) for r in selected)));gui.p2.set(str(min(float(r['period_s']) for r in selected)))
            inputs['notes'].append('Saved elastic eigenperiod band imported for Rayleigh calibration; this is distinct from the static Rayleigh-method design period.')
            if not model_matches or not implementation_matches:
                inputs['notes'].append('UNVERIFIED STARTING REFERENCE: saved modal model/code fingerprint differs or is absent. Values are visible for inspection, not certified current. Rerun Modal audit for this selected export/state; nonlinear initial eigenanalysis and readiness checks remain required.')
            else:inputs['notes'].append('Model and numerical implementation fingerprints match the selected elastic modal case. Nonlinear initial stiffness is still checked separately.')
    # The MRSM and LTH windows must use the same NBC §5.1.3 adopted
    # directional T1 source. Previously this window cleared T1 X/Y, then
    # relied on project inputs that can be blank when an EDB path differs.
    # [REF components/response_spectrum/model_analysis.py mrsm_period_defaults]
    # [REF NBC105-2025 §5.1.2–5.1.3] Empirical periods are NOT modal eigenperiods.
    try:
        from components.response_spectrum.model_analysis import mrsm_period_defaults
        directional, period_note = mrsm_period_defaults(folder, v, gui.ls.get())
        for axis in ('x', 'y'):
            candidate = directional.get('T1_' + axis.upper())
            if candidate not in (None, ''):
                number = float(candidate)
                if math.isfinite(number) and number > 0:
                    getattr(gui, 't1' + axis).set(format(number, '.12g'))
        inputs['notes'].append('Linear TH directional adopted T1: ' + period_note)
        if 'research comparison only' in period_note.casefold():
            inputs['notes'].append(
                'RESEARCH ONLY: original linked workbook T1 was not derived '
                'from a fresh current-model Rayleigh run. Validate the EDB '
                'identity, Aw and directional periods before accepting TH.')
        if not all(getattr(gui, 't1' + axis).get().strip()
                   for axis in ('x', 'y')):
            inputs['notes'].append(
                'BLOCKED T1: no complete source-reviewed X/Y periods; '
                'run ESM preliminary Rayleigh X/Y and refresh this window.')
    except Exception as exc:
        inputs['notes'].append(
            'Directional period synchronization failed; T1 fields require '
            'manual reviewed input: ' + str(exc))
    gui.project_input_audit=inputs
    return inputs


def populate_spectrum(app, gui):
    inputs=populate_linear(gui,Path(gui.model.get()).parent)
    values=inputs['values']
    for target,source in [('soil','soil'),('z','Z'),('imp','I'),('rmu','rmu'),('omega','omegau')]:
        if source in values:getattr(app,target).set(str(values[source]))
    if hasattr(app,'omegas') and 'omegas' in values:app.omegas.set(str(values['omegas']))
    for attr in ('t1x','t1y','tnx','tny'):getattr(app,attr).set(getattr(gui,attr).get())
    if hasattr(app,'source_folder'):
        app.source_folder.set(str(Path(gui.model.get()).expanduser().parent))
    if hasattr(app,'period_source'):
        app.period_source.set('Adopted X/Y T1 transferred from selected history-model source; '
                              'NBC §5.1.3 provenance is in the history input audit. '
                              'Elastic modal Tn is independent of adopted T1.')
    app.status.set('Imported current project parameters and matching analysis periods. Review soil evidence and record matching procedure. '+ ' '.join(inputs['notes']))


def populate_available(gui,folder=None,role='linear_model_script'):
    from OpenSees_Complete_Export_V118 import autoselect_inputs
    folder=Path(folder or (Path(gui.model.get()).parent if hasattr(gui,'model') and gui.model.get() else r'D:/Thesis Opensees/Etabs Nodes Export'))
    try:
        old_output=gui.output.get() if hasattr(gui,'output') else ''
        output_is_automatic=bool(getattr(gui,'_output_is_automatic',False))
        if output_is_automatic and hasattr(gui,'output'):
            from components.inputs.project_workbooks import analysis_output_folder
            gui.output.set(str(analysis_output_folder(folder,gui.ls.get())))
        # The auto-selector only locates files. It cannot be relied upon to
        # recompute NBC §5.1 directional T1 from the current export/state.
        # Always synchronize period fields after selecting the model, including
        # when the auto-selector returns True. Do not equate Rayleigh damping
        # calibration eigenperiods (p1/p2) with adopted design T1 X/Y.
        selected = bool(autoselect_inputs(gui,folder,role))
        model_path = Path(gui.model.get()) if hasattr(gui,'model') and gui.model.get() else None
        if model_path is not None and model_path.is_file():
            # The selected model owns the period source, not the initial
            # project folder from which the chooser was launched.
            populate_linear(gui,model_path.resolve().parent)
        if old_output and hasattr(gui,'output') and not output_is_automatic:gui.output.set(old_output)
        if hasattr(gui,'log') and hasattr(gui.log,'insert'):
            notes=getattr(gui,'project_input_audit',{}).get('notes',[])
            if role=='nonlinear_model_script':notes=notes+['Imported modal values are elastic baseline references; validate nonlinear initial stiffness and retain the calibration/readiness gate.']
            gui.log.insert('end','[INPUT SOURCES] '+str(folder)+'\n'+'\n'.join(notes)+'\n')
    except Exception as exc:
        if hasattr(gui,'log') and hasattr(gui.log,'insert'):gui.log.insert('end','[AUTOFILL] '+str(exc)+'\n')


def populate_site(app,folder=None):
    """[REF docs/source/components/inputs/analysis_autofill.py.md]
    Load site-spectrum T1 from the SAME selected source/state as MRSM.

    NBC-adopted T1 is not an eigenperiod. Never use an unrelated legacy
    workbook value, stale GUI value, or first available modal result.
    """
    from OpenSees_Project_Inputs_V123 import import_project_inputs
    from components.inputs.project_workbooks import source_limit_state
    from components.response_spectrum.model_analysis import mrsm_period_defaults
    if folder is None:
        raise ValueError('Select a current ETABS/OpenSees export folder to load periods.')
    folder=Path(folder).expanduser()
    if not folder.is_dir():
        raise FileNotFoundError('Selected site-spectrum source folder does not exist: '+str(folder))
    source_state,source_note=source_limit_state(folder)
    state=source_state or 'ULS'
    inputs=import_project_inputs(_runtime_repo_root(),folder,state)
    v=inputs['values']
    if hasattr(app,'source_folder'):
        app.source_folder.set(str(folder))
    for target in ('t1x','t1y','tnx','tny'):
        getattr(app,target).set('')
    if hasattr(app,'omegas') and 'omegas' in v:
        app.omegas.set(str(v['omegas']))
    for target,source in (('soil','soil'),('z','Z'),('imp','I'),
                          ('rmu','rmu'),('omega','omegau')):
        if source in v and v[source] not in (None,''):
            getattr(app,target).set(str(v[source]))
    adopted,note=mrsm_period_defaults(folder,v,state)
    for axis in ('X','Y'):
        candidate=adopted.get('T1_'+axis)
        if candidate not in (None,''):
            try:
                numeric=float(candidate)
            except (TypeError,ValueError) as exc:
                raise ValueError('Invalid source-adopted period T1 '+axis+': '+str(candidate)) from exc
            if not math.isfinite(numeric) or numeric<=0:
                raise ValueError('NBC-adopted T1 '+axis+' must be finite and positive.')
            getattr(app,'t1'+axis.lower()).set(format(numeric,'.15g'))
    if source_state is None:
        inputs['notes'].append('Source EDB limit state unclassified; using ULS as a '
                               'provisional diagnostic only: '+source_note)
    inputs['notes'].append('NBC §5.1.3 adopted X/Y design periods: '+note)
    if any(not getattr(app,'t1'+axis).get() for axis in ('x','y')):
        inputs['notes'].append('T1 unavailable from the selected source; run '
                               'the appropriate ESM/Rayleigh audit or supply '
                               'reviewed current-model parameters.')
    model=folder/'OpenSees_Complete_Model_Data_V118.json'
    model_sha=hashlib.sha256(model.read_bytes()).hexdigest() if model.is_file() else None
    modal=matching_modal_reference(folder,state,model_sha)
    if modal is not None:
        result=json.loads(modal.read_text(encoding='utf-8-sig'))
        for axis in ('X','Y'):
            row=next((r for r in result.get('rows',[]) if
                      float(r.get('U'+axis+'_cumulative_percent') or 0)>=90),None)
            if row:
                value=float(row['period_s'])
                if math.isfinite(value) and value>0:
                    getattr(app,'tn'+axis.lower()).set(str(value))
        inputs['notes'].append('Tn from model-SHA/state-matched '+state+
                               ' elastic modal file: '+str(modal)+
                               '. This is NOT the NBC-adopted design period.')
    else:
        inputs['notes'].append('No model-SHA/state-matched '+state+
                               ' modal reference; Tn remains empty.')
    if hasattr(app,'period_source'):
        app.period_source.set('NBC §5.1.3 T1 ['+state+']: '+note)
    app.status.set('Current export: '+str(folder)+' | '+state+' | '+
                   ' '.join(inputs['notes']))
    app.project_input_audit=inputs
    return inputs



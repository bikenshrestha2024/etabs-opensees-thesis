"""Populate known inputs with provenance; never reinterpret empirical T as eigen T."""

__release__ = '134'
from pathlib import Path
import hashlib
import json
import math


def populate_linear(gui, folder):
    from OpenSees_Project_Inputs_V123 import import_project_inputs
    folder=Path(folder)
    for attr in ('t1x','t1y','p1','p2','tnx','tny'):getattr(gui,attr).set('')
    inputs=import_project_inputs(Path(__file__).resolve().parents[2],folder,gui.ls.get())
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
                period=min(v.get('period_factor',1.25)*.075*H**.75/math.sqrt(v['aw'+axis]),v['rayleigh_t'+axis])
                getattr(gui,'t1'+axis).set(f'{period:.9g}')
    from components.inputs.project_workbooks import analysis_output_folder
    bases=[analysis_output_folder(folder,gui.ls.get()),folder/'OpenSees_Analysis_Results',Path(gui.output.get())]
    candidates=[base/('Modal_'+gui.ls.get())/'NBC105_Modal_V111.json' for base in bases]+[base/f'NBC105_Modal_{gui.ls.get()}_V127.json' for base in bases]+[base/'NBC105_Modal_V111.json' for base in bases]
    existing=[path for path in candidates if path.is_file()]
    model_sha=hashlib.sha256(datafile.read_bytes()).hexdigest() if datafile.is_file() else None
    def matches(path):
        try:
            result=json.loads(path.read_text(encoding='utf-8-sig'));return result.get('model_sha256')==model_sha and result.get('limit_state','ULS')==gui.ls.get()
        except Exception:return False
    modal=next((path for path in existing if matches(path)),existing[0] if existing else candidates[0])
    if modal.is_file() and datafile.is_file():
        result=json.loads(modal.read_text(encoding='utf-8-sig'))
        inputs['notes'].append('Modal input reference: '+str(modal))
        from OpenSees_Model_Audit_V130 import implementation_digest
        reference_sha=result.get('implementation_sha256')
        compatibility_path=Path(__file__).parent/'NUMERICAL_INPUT_COMPATIBILITY_V132.json'
        compatibility=json.loads(compatibility_path.read_text(encoding='utf-8-sig')) if compatibility_path.is_file() else {}
        from OpenSees_Model_Audit_V130 import modal_numeric_digest
        implementation_matches=result.get('modal_numeric_sha256')==modal_numeric_digest(Path(__file__).parent) or result.get('modal_numeric_sha256') in compatibility or reference_sha==implementation_digest(Path(__file__).parent) or reference_sha in compatibility
        if reference_sha in compatibility:inputs['notes'].append('Imported known-compatible V'+str(compatibility[reference_sha]['release'])+' modal reference with exact model-payload match; the transient runner rechecks fresh eigenmode damping.')
        state_matches=result.get('limit_state','ULS')==gui.ls.get()
        model_matches=result.get('model_sha256')==model_sha and model_sha is not None
        gui.modal_reference_status=dict(path=str(modal),state_matches=state_matches,model_matches=model_matches,implementation_matches=bool(implementation_matches),usage='VERIFIED ELASTIC REFERENCE' if state_matches and model_matches and implementation_matches else 'UNVERIFIED ELASTIC STARTING REFERENCE; nonlinear initial stiffness not validated')
        inputs['modal_reference_status']=gui.modal_reference_status
        if not state_matches:
            inputs['notes'].append('Saved modal stiffness state differs from the selected state. No directional Tn/damping periods imported; run Modal audit for this state.')
        else:
            rows=[r for r in result.get('rows',[]) if math.isfinite(float(r.get('period_s',0))) and float(r.get('period_s',0))>0]
            for axis in ('x','y'):
                reached=next((r for r in rows if float(r.get('U'+axis.upper()+'_cumulative_percent',0) or 0)>=90),None)
                if reached:getattr(gui,'tn'+axis).set(str(reached['period_s']))
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
    from OpenSees_Project_Inputs_V123 import import_project_inputs
    folder=Path(folder or r'D:/Thesis Opensees/Etabs Nodes Export');inputs=import_project_inputs(Path(__file__).resolve().parents[2],folder);v=inputs['values']
    if hasattr(app,'omegas') and 'omegas' in v:app.omegas.set(str(v['omegas']))
    for target,source in [('soil','soil'),('z','Z'),('imp','I'),('rmu','rmu'),('omega','omegau'),('t1x','workbook_adopted_tx'),('t1y','workbook_adopted_ty')]:
        if source in v:getattr(app,target).set(str(v[source]))
    state='ULS'
    from components.inputs.project_workbooks import analysis_output_folder
    modal=analysis_output_folder(folder,state)/('Modal_'+state)/'NBC105_Modal_V111.json'
    if not modal.is_file():modal=folder/'OpenSees_Analysis_Results'/('Modal_'+state)/'NBC105_Modal_V111.json'
    if modal.is_file():
        result=json.loads(modal.read_text(encoding='utf-8-sig'))
        for axis in ('X','Y'):
            row=next((r for r in result['rows'] if (r.get('U'+axis+'_cumulative_percent') or 0)>=90),None)
            if row:getattr(app,'tn'+axis.lower()).set(str(row['period_s']))
        inputs['notes'].append('Tn shown from saved ULS modal file as a scaling reference; verify current model match before adoption.')
    app.status.set('Imported available project/source references: '+str(folder)+' | '+' '.join(inputs['notes']));return inputs

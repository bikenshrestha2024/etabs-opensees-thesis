"""ETABS/OpenSees comparison contract: explicit units, cases and result bases."""
from pathlib import Path
import csv,json,math,time
FIELDS=['method','limit_state','case','axis','location','metric','unit','basis']
GUIDE='Export ETABS tables for the SAME model, mass source, effective stiffness, diaphragm, restraints, gravity/P-Delta, modes, damping, spectrum units, eccentricity and combinations. Normalize rows to this template. Modes must be paired by shape/participation, not only mode number. MRSM CQC envelopes are not signed simultaneous actions. No reinforcement-demand engine is claimed.'

def source_execution_identity(document, expected_support_case='PHYSICAL_32',
                              expected_mass_policy='SOURCE_DISTRIBUTED'):
    """Assess MRSM execution configuration separately from geometric model SHA.

    [REF engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md]
    Older V132 records include the model SHA but omit the executed 32/76/97
    restraint profile and actual seismic mass operator. Never infer those
    from model filename, JSON case name, or matching base shear.
    """
    if not isinstance(document,dict):
        return 'MISSING_EXECUTED_SUPPORT_OR_MASS_POLICY'
    support=document.get('support_case')
    mass=document.get('seismic_mass_policy')
    if not support or not mass:
        return 'MISSING_EXECUTED_SUPPORT_OR_MASS_POLICY'
    if support!=expected_support_case:
        return ('DIAGNOSTIC_SUPPORT_CASE_NOT_PRIMARY_32'
                if expected_support_case=='PHYSICAL_32' and support in ('SOURCE_76','WALL_BASE_97')
                else 'MISMATCHED_SELECTED_SUPPORT_CASE')
    if mass!=expected_mass_policy:
        return 'MISMATCHED_SELECTED_MASS_OPERATOR'
    evidence=document.get('support_case_evidence') or {}
    if evidence.get('status')!='MATCHED_SELECTED_CASE_NOT_NATIVE_EQUIVALENT':
        return 'MISSING_ACTUAL_RUNTIME_SUPPORT_VERIFICATION'
    return 'SOURCE_IDENTIFIED_NOT_NATIVE_ETABS_APPROVED'


def collect(folder, issues=None, *, results_root=None, expected_support_case='PHYSICAL_32', expected_mass_policy='SOURCE_DISTRIBUTED'):
    """Collect ONLY current-model, source-state-matched result evidence.

    Historical model outputs without a model hash remain on disk but are not
    silently imported. A result with a different hash is excluded. Separate
    model and limit-state identity is more important than a filename match.
    """
    import hashlib
    from components.inputs.project_workbooks import (
        analysis_output_folder, source_limit_state)
    folder=Path(folder)
    root=(Path(results_root).expanduser().resolve() if results_root is not None
          else folder/'OpenSees_Analysis_Results')
    rows=[]
    issues=[] if issues is None else issues
    model=folder/'OpenSees_Complete_Model_Data_V118.json'
    if not model.is_file():
        raise FileNotFoundError('Cannot compare saved results without current assembled model: '+str(model))
    expected=hashlib.sha256(model.read_bytes()).hexdigest()
    selected_state,state_note=source_limit_state(folder)
    if selected_state is None:
        raise ValueError('Cannot prove one-model/one-state ETABS comparison: '+state_note)
    # Search the selected output root and the canonical source-bound root.
    # Existing strict model hash/limit-state gates still reject stale evidence.
    from components.inputs.output_layout import result_roots
    # Search stage-owned result roots plus historical shared outputs.
    # Saved-case model SHA and ULS/SLS checks below remain mandatory.
    scan_roots = [root]
    candidates=(
        *result_roots(folder, stages=('GRAVITY','ESM','MODAL','MRSM',
                                      'LTHA','NLTHA'), include_legacy=True),
        analysis_output_folder(folder, selected_state, stage='ESM'),
        analysis_output_folder(folder, selected_state),
        folder / 'OpenSees_Analysis_Results',
    )
    for candidate in candidates:
        candidate = Path(candidate).resolve()
        if candidate.is_dir() and candidate not in scan_roots:
            scan_roots.append(candidate)
    def scan(pattern):
        seen = set()
        for base in scan_roots:
            if not base.is_dir():
                continue
            for path in sorted(base.rglob(pattern)):
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    yield path
    def add(method,state,case,axis,loc,metric,unit,basis,value,file,execution_status=None):
        if value is not None and math.isfinite(float(value)):
            rows.append(dict(method=method,limit_state=state,case=case,axis=axis,
                location=str(loc),metric=metric,unit=unit,basis=basis,
                value=float(value),source_file=str(file),
                source_execution_status=execution_status or '',
                status=('SOURCE_EXECUTION_NOT_VERIFIED'
                        if execution_status and execution_status!='SOURCE_IDENTIFIED_NOT_NATIVE_ETABS_APPROVED'
                        else ''))) 
    def accepted(document,path,state):
        if state!=selected_state:
            issues.append(str(path)+': rejected opposite-state '+str(state))
            return False
        actual=document.get('model_sha256') if isinstance(document,dict) else None
        if actual!=expected:
            issues.append(str(path)+': missing or mismatched assembled model SHA256; not imported')
            return False
        return True
    state=selected_state
    # A review ZIP is a snapshot of already recorded responses, not a
    # second independent solver run. Exclude all extracted package copies
    # from normalized comparisons to avoid false duplicate cases.
    def current_result(path):
        return not any(part.startswith((
            'Seismic_Review_Packages','ESM_Validation_Evidence_',
            'Gravity_Evidence_Upload','Gravity_ETABS_OpenSees_Evidence',
            'Organized_Results','ETABS_Comparison_V148'))
            for part in Path(path).parts)
    p=analysis_output_folder(folder,state)/('Modal_'+state)/'NBC105_Modal_V111.json'
    if not p.is_file():
        p=root/('Modal_'+state)/'NBC105_Modal_V111.json'
    if p.is_file():
        d=json.loads(p.read_text(encoding='utf-8-sig'))
        if accepted(d,p,d.get('limit_state',state)):
            for r in d.get('rows',[]):
                add('MODAL',state,'MODAL','',r['mode'],'period','s','eigen',r['period_s'],p)
                for axis in ('X','Y'):
                    add('MODAL',state,'MODAL',axis,r['mode'],'individual_mass',
                        'percent','modal_mass',r.get('U'+axis+'_participation_percent'),p)
            for axis in ('X','Y'):
                add('MODAL',state,'MODAL',axis,'ALL','cumulative_mass','percent','modal_mass',
                    d.get('cumulative_U'+axis+'_percent'),p)
    for p in scan('MRSM_Results_V132.json'):
        if not current_result(p):continue
        document=json.loads(p.read_text(encoding='utf-8-sig'))
        if not isinstance(document,dict):
            issues.append(str(p)+': unexpected MRSM structure')
            continue
        for case,d in document.items():
            if not accepted(d,p,d.get('limit_state')):
                continue
            axis=d['axis']
            execution=source_execution_identity(d,expected_support_case,expected_mass_policy)
            if execution!='SOURCE_IDENTIFIED_NOT_NATIVE_ETABS_APPROVED':
                issues.append(str(p)+': '+case+' '+execution+
                              '; geometrical model SHA alone is not proof of selected '+expected_support_case+
                              ' support / '+expected_mass_policy+' mass.')
            add('MRSM',state,case,axis,'BASE','base_shear','kN',
                'CQC_force_scaled',d.get('scaled_modal_base_shear_kN'),p,execution)
            for r in d['stories']:
                add('MRSM',state,case,axis,r['story_number'],'story_shear',
                    'kN','CQC_force_scaled',r.get('scaled_story_shear_kN'),p,execution)
                # This is a master-node or extrapolated diaphragm response,
                # not a reviewed exact ETABS point/displacement location.
                add('MRSM',state,case,axis,r['story_number'],'displacement',
                    'm','CQC_design_unscaled_by_7_5',r.get('design_displacement_m'),p,execution)
                add('MRSM',state,case,axis,r['story_number'],'drift_ratio',
                    'ratio','CQC_design_unscaled_by_7_5',r.get('design_drift_ratio'),p,execution)
    for p in scan('NBC105_ESM_OpenSees_Response_*.json'):
        if not current_result(p):continue
        if 'Response_META_' in p.name:continue
        document=json.loads(p.read_text(encoding='utf-8-sig'))
        if isinstance(document,list):
            meta=p.with_name(p.name.replace('OpenSees_Response_',
                                            'OpenSees_Response_META_'))
            if not meta.is_file():
                issues.append(str(p)+': legacy ESM list lacks matching model SHA256 sidecar; not imported')
                continue
            proof=json.loads(meta.read_text(encoding='utf-8-sig'))
            rr=document
        elif isinstance(document,dict):
            proof=document
            rr=document.get('rows',document.get('stories',[]))
        else:
            issues.append(str(p)+': non-object/list ESM response')
            continue
        if not accepted(proof,p,proof.get('limit_state')):
            continue
        for record in rr:
            # Keep applied cumulative floor force separate from the
            # recovered ETABS story-section shear; they are not identical.
            loc=record.get('story_number')
            if loc is None:
                issues.append(str(p)+': response row without story_number excluded')
                continue
            case=record.get('response_case',proof.get('response_case',p.stem))
            axis=proof.get('axis',record.get('direction',''))
            add('ESM',state,case,axis,loc,'displacement','m',
                'static_design',record.get('U_design_m'),p)
            add('ESM',state,case,axis,loc,'drift_ratio','ratio',
                'static_design',record.get('design_drift_ratio'),p)
            add('ESM',state,case,axis,loc,'story_shear','kN',
                'applied_floor_force_cumulative_NOT_recovered',
                record.get('story_shear_kN'),p)
    # Optional full-node static displacement comparison. The ETABS point
    # name is the only supported location key; generated mesh nodes without
    # native ETABS counterparts remain in raw CSV, not invented matches.
    for p in scan('NBC105_ESM_All_Node_Displacements_*.csv'):
        if not current_result(p):continue
        with p.open('r',newline='',encoding='utf-8-sig') as f:
            records=list(csv.DictReader(f))
        if not records:continue
        first=records[0]
        if not accepted({'model_sha256':first.get('model_sha256')},
                        p,first.get('limit_state')):
            continue
        for record in records:
            if record.get('model_sha256')!=expected:
                issues.append(str(p)+': mixed model hash at node '+str(record.get('opensees_node_tag')))
                continue
            point=record.get('etabs_point_name')
            if not point:continue
            case=record.get('response_case','')
            axis='X' if '_X' in case else 'Y' if '_Y' in case else ''
            if not axis:
                issues.append(str(p)+': missing X/Y direction for node '+str(point))
                continue
            key='du_x_m' if axis=='X' else 'du_y_m'
            design_key='design_du_x_m' if axis=='X' else 'design_du_y_m'
            add('ESM',state,case,axis,point,'displacement','m',
                'static_elastic_increment',record.get(key),p)
            add('ESM',state,case,axis,point,'displacement','m',
                'static_design_increment',record.get(design_key),p)
    return rows

def compare(rows, etabs, policy=None):
    """Compare exact normalized response bases with explicit evidence gates."""
    from components.validation.etabs_equivalence_report import evaluate
    results=evaluate(rows, etabs, FIELDS, policy)
    for row in results:
        identity=row.get('source_execution_status')
        if identity and identity!='SOURCE_IDENTIFIED_NOT_NATIVE_ETABS_APPROVED':
            row['status']='NOT_COMPARABLE'
            row['note']='Executed MRSM support/mass identity requires review: '+identity+'. '+row.get('note','')
            row['percent_difference']=None
    return results


def save(folder,etabs_path=None,etabs_rows=None,policy=None,*,results_root=None, expected_support_case='PHYSICAL_32', expected_mass_policy='SOURCE_DISTRIBUTED'):
    """Export source-normalized CSV and Excel comparisons.

    Existing CSV users remain supported. Direct ETABS API results are passed
    as etabs_rows and never require hand-editing a normalized input CSV.
    Programmatic confidence is limited to software checks; comparability
    is gated by the explicitly approved policy, not assumed.
    """
    start=time.perf_counter();folder=Path(folder)
    out=(Path(results_root).expanduser().resolve() if results_root is not None
         else folder/'OpenSees_Analysis_Results')/'ETABS_Comparison_V148'
    out.mkdir(parents=True,exist_ok=True)
    source_issues=[]
    rows=collect(folder,source_issues,results_root=results_root,
                 expected_support_case=expected_support_case,
                 expected_mass_policy=expected_mass_policy)
    if not rows:
        source_issues.append('ZERO_SOURCE_MATCHED_ROWS: Check result location, '
                             'model SHA, limit state and completed solver outputs.')
    (out/'Comparison_Source_Exclusions.json').write_text(json.dumps(source_issues,indent=2),encoding='utf-8')
    def write(p,rr,fields):
        with p.open('w',newline='',encoding='utf-8-sig') as h:
            w=csv.DictWriter(h,fieldnames=fields,extrasaction='ignore')
            w.writeheader();w.writerows(rr)
    write(out/'OpenSees_Normalized.csv',rows,FIELDS+['value','source_file'])
    template=out/'ETABS_Normalized_Input.csv'
    if not template.exists():
        write(template,[{**{k:r[k] for k in FIELDS},'value':''} for r in rows],
              FIELDS+['value'])
    if etabs_rows is not None and etabs_path:
        raise ValueError('Choose either direct API rows or an imported CSV, not both.')
    if etabs_path:
        with Path(etabs_path).open(encoding='utf-8-sig') as h:
            etabs_rows=list(csv.DictReader(h))
    if etabs_rows is not None:
        write(out/'ETABS_API_Normalized.csv',etabs_rows,
              FIELDS+['value','source_file','etabs_source_case',
                      'etabs_step_type','etabs_step_number'])
        compared=compare(rows,etabs_rows,policy)
        fields=list(dict.fromkeys(FIELDS+['value','source_file','etabs_value','difference',
                                       'percent_difference','status','note','matching_key']))
        write(out/'Comparison.csv',compared,fields)
        from components.validation.etabs_equivalence_report import export_excel
        export_excel(out,rows,etabs_rows,compared,policy or {})
        result=compared
    else:
        result=rows
        write(out/'Comparison.csv',rows,FIELDS+['value','source_file'])
    (out/'Comparison_Guide.txt').write_text(GUIDE,encoding='utf-8')
    (out/'Comparison_Execution_Profile.json').write_text(json.dumps(dict(support_case=expected_support_case,seismic_mass_policy=expected_mass_policy,source_identity_status='REVIEW_EACH_ROW'),indent=2),encoding='utf-8')
    (out/'run.json').write_text(json.dumps(
        dict(elapsed_s=time.perf_counter()-start,row_count=len(result),
             etabs_file=str(etabs_path or ''),direct_api=bool(etabs_rows and not etabs_path),
             evidence_verified=bool((policy or {}).get('assumptions_verified')),
             scope=GUIDE),indent=2),encoding='utf-8')
    return result,out


def verify_native_bundle(root, edb, expected_model_sha256):
    """Verify one immutable-identity native API evidence set before auto-reuse.

    [REF engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md §C]
    Never auto-accept a hand-edited reference CSV, stale model hash,
    opposite EDB path or a merely named 6 m-wall workbook.
    """
    from components.validation.etabs_direct_api import fingerprint, validate_mapping
    root=Path(root)
    csv_path=root/'ETABS_API_Normalized.csv'
    provenance=root/'ETABS_API_Provenance.json'
    mapping_file=root/'ETABS_API_Mapping_SELECTED.json'
    if not all(p.is_file() for p in (csv_path,provenance,mapping_file)):
        return None,'Missing approved native ETABS CSV, mapping or provenance'
    try:
        evidence=json.loads(provenance.read_text(encoding='utf-8-sig'))
        mapping=json.loads(mapping_file.read_text(encoding='utf-8-sig'))
        if not isinstance(evidence,dict) or not isinstance(mapping,dict):
            return None,'Native ETABS mapping/provenance must be JSON objects'
        if not mapping.get('assumptions_verified') is True:
            return None,'Native ETABS mapping is not approved'
        validate_mapping(mapping)
        same_source=(Path(str(evidence.get('edb_path',''))).resolve()==Path(edb).resolve()
                     and Path(str(mapping.get('source_edb',''))).resolve()==Path(edb).resolve()
                     and evidence.get('edb_sha256')==fingerprint(edb))
        if not same_source:
            return None,'Original source EDB path/SHA mismatch'
        if not expected_model_sha256 or evidence.get('source_model_sha256')!=expected_model_sha256:
            return None,'Assembled model SHA does not match verified ETABS mapping export'
        if evidence.get('native_csv_sha256')!=fingerprint(csv_path):
            return None,'Native ETABS CSV SHA mismatch or missing provenance; re-read same EDB'
        with csv_path.open(encoding='utf-8-sig',newline='') as stream:
            values=list(csv.DictReader(stream))
        if not values:
            return None,'Native ETABS CSV has zero analyzed result rows'
        required=tuple(k for k in FIELDS if k!='axis')+('value',)
        for row in values:
            if any(not str(row.get(k,'')).strip() for k in required):
                return None,'ETABS normalized CSV has blank source/response identity fields'
            if row.get('method')!='MODAL' and not str(row.get('axis','')).strip():
                return None,'Directional ETABS normalized CSV has missing axis'
            if not math.isfinite(float(row['value'])):
                return None,'ETABS native row has nonfinite numerical value'
        return csv_path,'Source EDB, assembled model, mapping and native CSV SHA verified'
    except (OSError,ValueError,TypeError,OverflowError,KeyError) as exc:
        return None,'Native source verification failed: '+str(exc)


def find_verified_etabs_csv(source_folder, results_root):
    """Auto-select approved live API evidence from current or source-owned runs.

    No filename similarity is ever used as a source-identity assertion.
    Only SHA-matched source EDB, assembled model and reference files qualify.
    """
    import hashlib
    from components.inputs.project_workbooks import _source_edb_path
    from components.inputs.output_layout import export_root_for
    folder=Path(source_folder)
    edb=_source_edb_path(folder)
    model=folder/'OpenSees_Complete_Model_Data_V118.json'
    if not edb or not Path(edb).is_file():
        return None,'Current original source EDB inaccessible; live API can read only exact EDB'
    if not model.is_file():
        return None,'Current assembled model file missing; cannot establish source SHA'
    expected_model=hashlib.sha256(model.read_bytes()).hexdigest()
    root=Path(results_root).expanduser().resolve()
    stage=export_root_for(folder)
    candidates=[
        root/'ETABS_Comparison_V148',
        stage/'05_COMPARISONS'/'ETABS_Comparison_V148',
        folder/'05_COMPARISONS'/'ETABS_Comparison_V148',
        folder/'OpenSees_Analysis_Results'/'ETABS_Comparison_V148',
    ]
    if root.name=='02_RESULTS':
        candidates.append(root.parent/'05_COMPARISONS'/'ETABS_Comparison_V148')
    reasons=[]
    used=set()
    for location in candidates:
        resolved=location.resolve()
        if resolved in used:continue
        used.add(resolved)
        data,note=verify_native_bundle(resolved,edb,expected_model)
        if data:
            return data,'Verified native ETABS data auto-selected: '+str(data)
        reasons.append(resolved.name+': '+note)
    return None,'No SHA-verified same-model ETABS API data; '+(' | '.join(reasons[:3]) or 'no sources')


def find_native_reference_csv(source_folder, results_root):
    """Find source-bound native reference data without approving case equivalence.

    [REF docs/source/components/validation/etabs_comparison.py.md]
    """
    from components.inputs.project_workbooks import _source_edb_path
    from components.validation.etabs_direct_api import fingerprint
    root=Path(results_root)
    if root.name!='02_RESULTS':
        return None
    directory=root.parent/'05_COMPARISONS'/'ETABS_NATIVE_REFERENCE'
    csv_path=directory/'ETABS_Native_Reference.csv'
    provenance=directory/'ETABS_Native_Reference_Provenance.json'
    if not (csv_path.is_file() and provenance.is_file()):
        return None
    try:
        evidence=json.loads(provenance.read_text(encoding='utf-8-sig'))
        edb=_source_edb_path(source_folder)
        if (isinstance(evidence,dict) and edb and
            evidence.get('run_id')==root.parent.name and
            Path(evidence['source_edb']).resolve()==Path(edb).resolve() and
            evidence.get('source_edb_sha256')==fingerprint(edb) and
            evidence.get('csv_sha256')==fingerprint(csv_path)):
            return csv_path
    except (OSError,ValueError,TypeError,KeyError):
        pass
    return None


def launch(parent,folder,results_root=None):
 import tkinter as tk
 from tkinter import ttk,filedialog,messagebox
 win=tk.Toplevel(parent);win.title('ETABS comparison — verified source / cases');win.geometry('1200x750')
 path=tk.StringVar();status=tk.StringVar()
 support_filter=tk.StringVar(value='PHYSICAL_32')
 mass_filter=tk.StringVar(value='SOURCE_DISTRIBUTED')
 latest={'rows':None,'out':None,'etabs_rows':None,'policy':None}
 bar=ttk.Frame(win,padding=5);bar.pack(fill='x')
 filter_row=ttk.Frame(bar);filter_row.pack(fill='x',pady=(0,4))
 ttk.Label(filter_row,text='Actual OpenSees foundation case:').pack(side='left')
 ttk.Combobox(filter_row,textvariable=support_filter,
              values=('PHYSICAL_32','SOURCE_76','WALL_BASE_97'),
              state='readonly',width=19).pack(side='left',padx=(4,16))
 ttk.Label(filter_row,text='Executed seismic mass operator:').pack(side='left')
 ttk.Combobox(filter_row,textvariable=mass_filter,
              values=('SOURCE_DISTRIBUTED','STORY_LUMPED_NBC'),
              state='readonly',width=22).pack(side='left',padx=5)
 ttk.Label(filter_row,text='Older 76-restraint MRSM JSON without identity stays NOT_COMPARABLE.',
           foreground='#953b19').pack(side='left',padx=8)
 file_row=ttk.Frame(bar);file_row.pack(fill='x',pady=(0,4))
 ttk.Label(file_row,text='Native ETABS normalized CSV (optional):').pack(side='left',padx=(0,5))
 ttk.Entry(file_row,textvariable=path,width=65).pack(side='left',fill='x',expand=True)
 actions=ttk.Frame(bar);actions.pack(fill='x')
 def browse():
  p=filedialog.askopenfilename(parent=win,title='Normalized ETABS CSV',filetypes=[('CSV','*.csv')])
  if p:
   path.set(p)
   refresh()
 ttk.Button(actions,text='Load native ETABS CSV',command=browse).pack(side='left')
 comparison_root=(Path(results_root).expanduser().resolve() if results_root is not None
                  else Path(folder)/'OpenSees_Analysis_Results')
 auto_file,auto_note=find_verified_etabs_csv(folder,comparison_root)
 native_file=None if auto_file else find_native_reference_csv(folder,comparison_root)
 if auto_file:path.set(str(auto_file))
 elif native_file:path.set(str(native_file))
 status.set('SOURCE: '+auto_note)
 def template_for_current_edb():
  """Create discoverable INCOMPLETE source-bound mapping, never a verified file."""
  from components.inputs.project_workbooks import _source_edb_path
  from components.validation.etabs_direct_api import mapping_template
  known=_source_edb_path(folder)
  chosen=(str(Path(known).resolve()) if known and Path(known).is_file() else
          filedialog.askopenfilename(parent=win,title='Select exact source ETABS EDB',
                                     filetypes=[('ETABS model','*.edb')]))
  if not chosen:return
  destination=comparison_root/'ETABS_Comparison_V148'/'ETABS_API_Mapping_TEMPLATE.json'
  destination.parent.mkdir(parents=True,exist_ok=True)
  if not destination.exists():
   destination.write_text(
       json.dumps(mapping_template(chosen),indent=2),encoding='utf-8')
  status.set('INCOMPLETE MAPPING TEMPLATE (NOT VERIFIED): '+str(destination))
  messagebox.showinfo('ETABS case/story mapping template',
      'Template location:\n'+str(destination)+
      '\n\nFill real ETABS case names, exact story IDs and comparison basis. '
      'Keep source_edb equal to the selected original EDB; verify matching SHA. '
      'Never select OpenSees_Source_Model_Metadata_V118.json as a case mapping.',
      parent=win)
 ttk.Button(actions,text='Create / locate mapping TEMPLATE',
            command=template_for_current_edb).pack(side='left',padx=3)
 def _mapping_file_is_selected_source(path,chosen):
  """Only JSON objects with exact source EDB are eligible for selection."""
  try:
   data=json.loads(Path(path).read_text(encoding='utf-8-sig'))
   if not isinstance(data,dict):
    return False
   return Path(str(data.get('source_edb',''))).resolve()==Path(chosen).resolve()
  except (OSError,ValueError,TypeError):
   return False
 def direct_api(auto=False):
  """Attach to the selected, already-open source .EDB in a COM STA thread."""
  import threading
  from components.inputs.project_workbooks import _source_edb_path
  known=_source_edb_path(folder)
  if auto and (not known or not Path(known).is_file()):
   status.set('AUTO: original source EDB missing; read-only ETABS API not attempted.')
   return
  chosen=(str(Path(known).resolve()) if known and Path(known).is_file() else
          filedialog.askopenfilename(parent=win,title='Select exact source ETABS EDB',
                                     filetypes=[('ETABS model','*.edb')]))
  if not chosen:return
  mapping_dir=(Path(results_root).expanduser().resolve() if results_root is not None
               else Path(folder)/'OpenSees_Analysis_Results')/'ETABS_Comparison_V148'
  previous=mapping_dir/'ETABS_API_Mapping_SELECTED.json'
  if auto:
   provenance=mapping_dir/'ETABS_API_Provenance.json'
   from components.validation.etabs_direct_api import fingerprint
   recorded=(json.loads(provenance.read_text(encoding='utf-8-sig'))
             if provenance.is_file() else {})
   source_hash=fingerprint(chosen)
   if (not previous.is_file() or
       not _mapping_file_is_selected_source(previous,chosen) or
       recorded.get('edb_sha256')!=source_hash):
    status.set('AUTO: no prior SHA-verified ETABS API mapping for this exact '
               'EDB; use Direct ETABS API once to review case mapping.')
    return
  config=(str(previous) if previous.is_file() and
          _mapping_file_is_selected_source(previous,chosen)
          else filedialog.askopenfilename(
              parent=win,title='Select verified case-and-story mapping JSON',
              filetypes=[('Mapping JSON','*.json')]))
  if auto and not config:
   status.set('AUTO: source-specific mapping not available.')
   return
  if not config:
   template=mapping_dir/'ETABS_API_Mapping_TEMPLATE.json'
   template.parent.mkdir(parents=True,exist_ok=True)
   from components.validation.etabs_direct_api import mapping_template
   template.write_text(json.dumps(mapping_template(chosen),indent=2),encoding='utf-8')
   messagebox.showinfo('ETABS mapping needed','INCOMPLETE TEMPLATE created at '+str(template)+'\nEnter actual ETABS cases, story mapping and matched results basis before running Direct API; do not select generic model metadata JSON.',parent=win)
   return
  def worker():
   from components.validation.etabs_direct_api import connect_and_extract
   try:
    import comtypes
    comtypes.CoInitialize()
    try:
     mapping=json.loads(Path(config).read_text(encoding='utf-8-sig'))
     from components.validation.etabs_direct_api import validate_mapping
     validate_mapping(mapping)
     if Path(mapping['source_edb']).resolve()!=Path(chosen).resolve():
      raise ValueError('Selected EDB and mapping JSON source_edb differ. '
                       'EDB: '+str(Path(chosen).resolve())+
                       ' | mapping source: '+str(Path(mapping['source_edb']).resolve())+
                       '. Do not disable source-identity verification.')
     if not mapping.get('assumptions_verified'):
      raise ValueError('This case/story mapping remains a TEMPLATE (not verified). '
                       'Complete the true ETABS cases, matching story IDs, modal pairing '
                       'and basis checks before using Direct ETABS API.')
     extracted=connect_and_extract(folder,mapping)
     compared,out=save(folder,etabs_rows=extracted,policy=mapping,
                      results_root=results_root,
                      expected_support_case=support_filter.get(),
                      expected_mass_policy=mass_filter.get())
     from components.validation.etabs_direct_api import fingerprint
     provenance={"edb_path":str(Path(chosen).resolve()),"edb_sha256":fingerprint(chosen),
                 "mapping_path":str(Path(config).resolve()),
                 "row_count":len(extracted),"assumptions_verified":bool(mapping.get('assumptions_verified'))}
     (out/'ETABS_API_Provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
     (out/'ETABS_API_Mapping_SELECTED.json').write_text(
         json.dumps(mapping,indent=2),encoding='utf-8')
    finally:comtypes.CoUninitialize()
    def done():
     latest.update(rows=compared,out=out,etabs_rows=extracted,policy=mapping)
     show_rows(compared)
     counts={k:sum(row.get('status')==k for row in compared) for k in ('PASS','FAIL','NOT_COMPARABLE','MISSING_ETABS','MISSING_OPENSEES')}
     status.set('Direct ETABS API complete. '+str(counts)+' | Excel/chart: '+str(out/'ETABS_OpenSees_Equivalence.xlsx'))
    win.after(0,done)
   except Exception as exc:
    win.after(0,lambda error=str(exc):messagebox.showerror('ETABS direct API not comparable',error,parent=win))
  status.set('Reading the matching already-open EDB; files remain read-only…')
  threading.Thread(target=worker,daemon=True).start()
 ttk.Button(bar,text='Direct ETABS API / EDB…',command=direct_api).pack(side='left')
 def observe_native(auto=False):
  """Show read-only native ETABS values even before mapping is approved.

  Raw signed BaseReact quantities are NOT silently relabelled CQC scaled
  data; reviewed case/point mapping is still required to populate
  etabs_value / percent_difference for physical comparison.
  """
  import threading
  from components.inputs.project_workbooks import _source_edb_path
  known=_source_edb_path(folder)
  if auto and (not known or not Path(known).is_file()):
   return
  chosen=(str(Path(known).resolve()) if known and Path(known).is_file() else
          ('' if auto else filedialog.askopenfilename(
            parent=win,title='Choose current exact ETABS source .EDB',
            filetypes=[('ETABS EDB','*.edb')])))
  if not chosen:return
  def worker():
   try:
    import comtypes
    comtypes.CoInitialize()
    try:
     from OpenSees_Project_Inputs_V123 import connect_etabs
     from components.validation.etabs_direct_api import discover_native_base_reactions
     evidence=discover_native_base_reactions(
         connect_etabs().SapModel,chosen)
     from datetime import datetime,timezone
     snapshot=(comparison_root/'ETABS_Comparison_V148'/'Native_Observed'/
               datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ'))
     snapshot.mkdir(parents=True,exist_ok=False)
     metadata=snapshot/'ETABS_Native_Observed.json'
     metadata.write_text(json.dumps(evidence,indent=2),encoding='utf-8')
     columns=('etabs_case','case_kind','step_type','step_number','Fx_kN','Fy_kN','Fz_kN','Mx_kNm','My_kNm','Mz_kNm')
     write_rows=snapshot/'ETABS_Native_Observed.csv'
     with write_rows.open('w',newline='',encoding='utf-8-sig') as output:
      writer=csv.DictWriter(output,fieldnames=columns,extrasaction='ignore')
      writer.writeheader();writer.writerows(evidence['rows'])
    finally:
     comtypes.CoUninitialize()
    def done():
     latest['native_observations']=evidence
     status.set('LIVE ETABS SOURCE OBSERVED: '+str(len(evidence['rows']))+
                ' raw reaction rows from exact EDB; '+str(len(evidence['excluded']))+
                ' case read exceptions. NOT case/basis matched. '+str(snapshot))
     panel=tk.Toplevel(win);panel.title('Actual native ETABS BaseReact — RAW observations, not mapped comparison')
     panel.geometry('1060x530')
     ttk.Label(panel,text='Read-only native EDB / SHA256: '+str(evidence['source_edb_sha256'])+
               ' | Unpaired signed ETABS reactions. To fill verified etabs_value, use reviewed Direct ETABS API case/story map.',
               wraplength=1000).pack(fill='x',padx=8,pady=7)
     frame=ttk.Frame(panel);frame.pack(fill='both',expand=True,padx=6,pady=5)
     table=ttk.Treeview(frame,columns=columns,show='headings')
     vertical=ttk.Scrollbar(frame,orient='vertical',command=table.yview)
     horizontal=ttk.Scrollbar(frame,orient='horizontal',command=table.xview)
     table.configure(yscrollcommand=vertical.set,xscrollcommand=horizontal.set)
     frame.rowconfigure(0,weight=1);frame.columnconfigure(0,weight=1)
     table.grid(row=0,column=0,sticky='nsew');vertical.grid(row=0,column=1,sticky='ns');horizontal.grid(row=1,column=0,sticky='ew')
     for col in columns:table.heading(col,text=col);table.column(col,width=125,stretch=False)
     for row in evidence['rows']:
      table.insert('','end',values=[row.get(col,'') for col in columns])
     def preview_link():
      """Attach actual signed native force to one selected BASE row as UNVERIFIED PREVIEW."""
      source_selected=table.selection()
      target_selected=tree.selection()
      if len(source_selected)!=1 or len(target_selected)!=1:
       messagebox.showwarning('Select both response rows',
         'Select one actual ETABS native row above and one OpenSees MRSM BASE base_shear row in the comparison table behind this window.',
         parent=panel)
       return
      ref=table.item(source_selected[0],'values')
      item=tree.item(target_selected[0],'values')
      native=dict(zip(columns,ref))
      current=dict(zip(cols,item))
      if current.get('method')!='MRSM' or current.get('metric')!='base_shear' or current.get('location')!='BASE' or current.get('axis') not in ('X','Y'):
       messagebox.showerror('Unsupported comparison preview',
         'Raw ETABS BaseReact can only be preview-linked to an OpenSees MRSM BASE base_shear row. Story response, modal modes and drift need their exact source/mapping.',
         parent=panel)
       return
      direction=current['axis']
      native_component='Fx_kN' if direction=='X' else 'Fy_kN'
      raw_value=float(native[native_component])
      # Record the ACTUAL RAW signed ETABS reaction, with no fictitious
      # CQC/NBC force normalization, percentage comparison or PASS status.
      tree.set(target_selected[0],'etabs_value',format(raw_value,'.9g'))
      tree.set(target_selected[0],'percent_difference','')
      tree.set(target_selected[0],'status','RAW_ETABS_PREVIEW_NOT_COMPARABLE')
      status.set('RAW PREVIEW ONLY: OpenSees '+str(current.get('case'))+
                ' shown alongside '+str(native['etabs_case'])+'/'+str(native['step_type'])+
                ' native '+native_component+'. No response-basis approval; exact mapping and CQC/force-scaling review required.')
     ttk.Button(panel,text='Preview-link selected ETABS base reaction to highlighted MRSM BASE row (NOT verified)',
                command=preview_link).pack(anchor='w',padx=8,pady=5)
     ttk.Label(panel,text='Source snapshot: '+str(write_rows),wraplength=1040).pack(anchor='w',padx=8,pady=4)
     ttk.Button(panel,text='Close',command=panel.destroy).pack(anchor='e',padx=8,pady=4)
    win.after(0,done)
   except Exception as exc:
    if not auto:
     win.after(0,lambda error=str(exc):
       messagebox.showerror('Native ETABS observation unavailable',error,parent=win))
    else:
     win.after(0,lambda error=str(exc):
       status.set('AUTO LIVE ETABS READ UNAVAILABLE: '+error+
                  ' | Use Read native ETABS values when source EDB and ETABS are ready.'))
  status.set('Reading native analyzed base reactions from the exact already-open ETABS EDB; not modifying EDB…')
  threading.Thread(target=worker,daemon=True).start()

 ttk.Button(bar,text='Read native ETABS values (live, read-only)',command=observe_native).pack(side='left',padx=3)

 ttk.Label(win,text=GUIDE,wraplength=1150).pack(fill='x');ttk.Label(win,textvariable=status).pack(fill='x')
 frame=ttk.Frame(win);frame.pack(fill='both',expand=True);cols=FIELDS+['value','etabs_value','percent_difference','status'];tree=ttk.Treeview(frame,columns=cols,show='headings');sy=ttk.Scrollbar(frame,command=tree.yview);sx=ttk.Scrollbar(frame,orient='horizontal',command=tree.xview);tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set);tree.grid(row=0,column=0,sticky='nsew');sy.grid(row=0,column=1,sticky='ns');sx.grid(row=1,column=0,sticky='ew');frame.rowconfigure(0,weight=1);frame.columnconfigure(0,weight=1)
 for c in cols:tree.heading(c,text=c);tree.column(c,width=150,stretch=False)
 def show_rows(rows):
  tree.delete(*tree.get_children())
  for row in sorted(rows,key=lambda r:r.get('etabs_value') is None):
   tree.insert('','end',values=[row.get(c,'') for c in cols])
 def refresh():
  try:
   rows,out=(save(folder,path.get(),results_root=results_root,
                  expected_support_case=support_filter.get(),expected_mass_policy=mass_filter.get()) if path.get() else
             (save(folder,etabs_rows=latest['etabs_rows'],policy=latest['policy'],
                   results_root=results_root,
                   expected_support_case=support_filter.get(),
                   expected_mass_policy=mass_filter.get()) if latest['etabs_rows'] is not None
              else save(folder,results_root=results_root,
                        expected_support_case=support_filter.get(),
                        expected_mass_policy=mass_filter.get())))
   show_rows(rows)
   if not rows:
    audit=out/'Comparison_Source_Exclusions.json'
    reasons=json.loads(audit.read_text(encoding='utf-8')) if audit.is_file() else []
    status.set('NO COMPARABLE SAVED RESULTS. Check model SHA256, limit state, response-run completion and export folder. Exclusions: '+str(audit))
    tree.insert('','end',values=('NO_DATA','','','','','No source-matched OpenSees responses','','','', '', '', 'NOT_COMPARABLE'))
    (out/'NO_COMPARABLE_RESULTS.txt').write_text(
        'No source-model and limit-state-matched OpenSees response was imported.\\n'
        'Do not interpret an empty comparison as zero structural response.\\n'
        'Check excluded files in Comparison_Source_Exclusions.json.\\n'
        'Reasons: '+json.dumps(reasons,indent=2),encoding='utf-8')
   else:
    native_count=sum(r.get('etabs_value') is not None for r in rows)
    status.set(f'{native_count} ETABS values shown | {len(rows)} total rows | Report: {out}')
  except Exception as e:messagebox.showerror('Comparison inputs',str(e),parent=win)
 def plot():
  selected=tree.selection()
  if not selected:messagebox.showinfo('Select quantity','Select a comparison row first.',parent=win);return
  key=tree.item(selected[0],'values')
  rows=(save(folder,path.get(),results_root=results_root,expected_support_case=support_filter.get(),expected_mass_policy=mass_filter.get())[0] if path.get() else
        latest['rows'] if latest['rows'] is not None
        else save(folder,results_root=results_root,expected_support_case=support_filter.get(),expected_mass_policy=mass_filter.get())[0])
  subset=[r for r in rows if all(str(r.get(k,''))==key[cols.index(k)] for k in ('method','limit_state','case','axis','metric','unit','basis'))]
  if not subset:
   messagebox.showwarning('No solved response','No verified source-matched response series for this selection. Review Comparison_Source_Exclusions.json; do not plot invented zeros.',parent=win)
   return
  from matplotlib.figure import Figure
  from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
  panel=tk.Toplevel(win);panel.title('Exact case comparison: '+key[2]);panel.geometry('950x650');fig=Figure(figsize=(9,6),layout='constrained');ax=fig.add_subplot();x=list(range(len(subset)));ax.plot(x,[r['value'] for r in subset],marker='o',label='OpenSees')
  if any(r.get('etabs_value') is not None for r in subset):ax.plot(x,[r.get('etabs_value') if r.get('etabs_value') is not None else float('nan') for r in subset],marker='x',label='ETABS')
  ax.set(xlabel='Location / mode',ylabel=key[5]+' ('+key[6]+')',title=key[0]+' '+key[1]+' '+key[2]+' | '+key[7]);ax.set_xticks(x,[r['location'] for r in subset],rotation=60);ax.legend();ax.grid(alpha=.2);canvas=FigureCanvasTkAgg(fig,master=panel);canvas.get_tk_widget().pack(fill='both',expand=True);NavigationToolbar2Tk(canvas,panel);canvas.draw()
 ttk.Button(bar,text='Plot selected case / metric',command=plot).pack(side='left')
 ttk.Button(bar,text='Refresh / export CSV' ,command=refresh).pack(side='left')
 def retry_auto():
  candidate,note=find_verified_etabs_csv(folder,comparison_root)
  if candidate:
   path.set(str(candidate))
   refresh()
   status.set('VERIFIED ETABS SOURCE: '+str(candidate)+
              ' | match still requires the same structural response basis')
  else:
   status.set('AUTO-SELECTION NOT AVAILABLE: '+note)
 ttk.Button(bar,text='Auto-select verified ETABS CSV',command=retry_auto).pack(side='left')
 refresh()
 if native_file:
  status.set('Native ETABS reference loaded | Case equivalence unverified | '+str(native_file))
 elif not auto_file:
  status.set('SOURCE: '+auto_note+
             ' | Do not select OpenSees normalized CSV as native ETABS evidence')
 if not native_file:
  win.after(400,lambda:direct_api(auto=True))
 return win

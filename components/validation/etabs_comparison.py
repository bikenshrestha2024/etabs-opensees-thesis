"""ETABS/OpenSees comparison contract: explicit units, cases and result bases."""
from pathlib import Path
import csv,json,math,time
FIELDS=['method','limit_state','case','axis','location','metric','unit','basis']
GUIDE='Export ETABS tables for the SAME model, mass source, effective stiffness, diaphragm, restraints, gravity/P-Delta, modes, damping, spectrum units, eccentricity and combinations. Normalize rows to this template. Modes must be paired by shape/participation, not only mode number. MRSM CQC envelopes are not signed simultaneous actions. No reinforcement-demand engine is claimed.'

def collect(folder, issues=None, *, results_root=None):
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
    scan_roots = [root]
    for candidate in (analysis_output_folder(folder, selected_state),
                      folder / 'OpenSees_Analysis_Results'):
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
    def add(method,state,case,axis,loc,metric,unit,basis,value,file):
        if value is not None and math.isfinite(float(value)):
            rows.append(dict(method=method,limit_state=state,case=case,axis=axis,
                location=str(loc),metric=metric,unit=unit,basis=basis,
                value=float(value),source_file=str(file)))
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
            add('MRSM',state,case,axis,'BASE','base_shear','kN',
                'CQC_force_scaled',d.get('scaled_modal_base_shear_kN'),p)
            for r in d['stories']:
                add('MRSM',state,case,axis,r['story_number'],'story_shear',
                    'kN','CQC_force_scaled',r.get('scaled_story_shear_kN'),p)
                # This is a master-node or extrapolated diaphragm response,
                # not a reviewed exact ETABS point/displacement location.
                add('MRSM',state,case,axis,r['story_number'],'displacement',
                    'm','CQC_design_unscaled_by_7_5',r.get('design_displacement_m'),p)
                add('MRSM',state,case,axis,r['story_number'],'drift_ratio',
                    'ratio','CQC_design_unscaled_by_7_5',r.get('design_drift_ratio'),p)
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
    return evaluate(rows, etabs, FIELDS, policy)


def save(folder,etabs_path=None,etabs_rows=None,policy=None,*,results_root=None):
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
    rows=collect(folder,source_issues,results_root=results_root)
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
    (out/'run.json').write_text(json.dumps(
        dict(elapsed_s=time.perf_counter()-start,row_count=len(result),
             etabs_file=str(etabs_path or ''),direct_api=bool(etabs_rows and not etabs_path),
             evidence_verified=bool((policy or {}).get('assumptions_verified')),
             scope=GUIDE),indent=2),encoding='utf-8')
    return result,out


def find_verified_etabs_csv(source_folder, results_root):
    """Auto-reuse only native ETABS API CSV with matching EDB SHA and approved map.

    [REF docs/source/components/validation/etabs_comparison.py.md]
    A generated OpenSees_Normalized.csv or unfilled ETABS template is NOT
    evidence of native ETABS analysis; review ZIPs are not live API sources.
    """
    from components.inputs.project_workbooks import _source_edb_path
    from components.validation.etabs_direct_api import fingerprint
    edb=_source_edb_path(source_folder)
    if not edb or not Path(edb).is_file():
        return None,'Current original source EDB inaccessible'
    root=Path(results_root)/'ETABS_Comparison_V148'
    meta=root/'ETABS_API_Provenance.json'
    mapfile=root/'ETABS_API_Mapping_SELECTED.json'
    csv_path=root/'ETABS_API_Normalized.csv'
    if not all(p.is_file() for p in (meta,mapfile,csv_path)):
        return None,'No approved native ETABS CSV; run Direct ETABS API once'
    try:
        evidence=json.loads(meta.read_text(encoding='utf-8-sig'))
        mapping=json.loads(mapfile.read_text(encoding='utf-8-sig'))
        if (evidence.get('edb_sha256')!=fingerprint(edb) or
            Path(evidence.get('edb_path','')).resolve()!=Path(edb).resolve() or
            Path(mapping.get('source_edb','')).resolve()!=Path(edb).resolve()):
            return None,'Previous ETABS source path or SHA differs'
        if not mapping.get('assumptions_verified'):
            return None,'Native mapping is not approved for physical comparison'
        with csv_path.open(encoding='utf-8-sig',newline='') as f:
            values=list(csv.DictReader(f))
        if not values or any(not all(str(row.get(k,'')).strip() for k in FIELDS+['value']) for row in values):
            return None,'Saved normalized native ETABS CSV is incomplete'
        return csv_path,'Verified native ETABS CSV auto-selected'
    except (OSError,ValueError,TypeError,KeyError) as exc:
        return None,'ETABS source evidence failed verification: '+str(exc)


def launch(parent,folder,results_root=None):
 import tkinter as tk
 from tkinter import ttk,filedialog,messagebox
 win=tk.Toplevel(parent);win.title('ETABS comparison - modal / ESM / MRSM');win.geometry('1200x750');path=tk.StringVar();status=tk.StringVar();latest={'rows':None,'out':None,'etabs_rows':None,'policy':None};bar=ttk.Frame(win);bar.pack(fill='x');ttk.Entry(bar,textvariable=path,width=75).pack(side='left')
 def browse():
  p=filedialog.askopenfilename(parent=win,title='Normalized ETABS CSV',filetypes=[('CSV','*.csv')])
  if p:path.set(p)
 ttk.Button(bar,text='Manual ETABS CSV (advanced)',command=browse).pack(side='left')
 comparison_root=(Path(results_root).expanduser().resolve() if results_root is not None
                  else Path(folder)/'OpenSees_Analysis_Results')
 auto_file,auto_note=find_verified_etabs_csv(folder,comparison_root)
 if auto_file:path.set(str(auto_file))
 status.set('SOURCE: '+auto_note)
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
       json.loads(previous.read_text(encoding='utf-8-sig')).get('source_edb')!=str(chosen) or
       recorded.get('edb_sha256')!=source_hash):
    status.set('AUTO: no prior SHA-verified ETABS API mapping for this exact '
               'EDB; use Direct ETABS API once to review case mapping.')
    return
  config=(str(previous) if previous.is_file() and
          json.loads(previous.read_text(encoding='utf-8-sig')).get('source_edb')==str(chosen)
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
   messagebox.showinfo('ETABS mapping needed','Template created at '+str(template)+'\nEnter the real ETABS cases, story mapping and matched results basis; then use Direct ETABS API again.',parent=win)
   return
  def worker():
   from components.validation.etabs_direct_api import connect_and_extract
   try:
    import comtypes
    comtypes.CoInitialize()
    try:
     mapping=json.loads(Path(config).read_text(encoding='utf-8-sig'))
     if Path(mapping.get('source_edb','')).resolve()!=Path(chosen).resolve():
      raise ValueError('Selected EDB and mapping JSON source_edb differ.')
     extracted=connect_and_extract(folder,mapping)
     compared,out=save(folder,etabs_rows=extracted,policy=mapping,
                      results_root=results_root)
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
     tree.delete(*tree.get_children())
     for row in compared:tree.insert('','end',values=[row.get(c,'') for c in cols])
     counts={k:sum(row.get('status')==k for row in compared) for k in ('PASS','FAIL','NOT_COMPARABLE','MISSING_ETABS','MISSING_OPENSEES')}
     status.set('Direct ETABS API complete. '+str(counts)+' | Excel/chart: '+str(out/'ETABS_OpenSees_Equivalence.xlsx'))
    win.after(0,done)
   except Exception as exc:
    win.after(0,lambda error=str(exc):messagebox.showerror('ETABS direct API not comparable',error,parent=win))
  status.set('Reading the matching already-open EDB; files remain read-only…')
  threading.Thread(target=worker,daemon=True).start()
 ttk.Button(bar,text='Direct ETABS API / EDB…',command=direct_api).pack(side='left')
 ttk.Label(win,text=GUIDE,wraplength=1150).pack(fill='x');ttk.Label(win,textvariable=status).pack(fill='x')
 frame=ttk.Frame(win);frame.pack(fill='both',expand=True);cols=FIELDS+['value','etabs_value','percent_difference','status'];tree=ttk.Treeview(frame,columns=cols,show='headings');sy=ttk.Scrollbar(frame,command=tree.yview);sx=ttk.Scrollbar(frame,orient='horizontal',command=tree.xview);tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set);tree.grid(row=0,column=0,sticky='nsew');sy.grid(row=0,column=1,sticky='ns');sx.grid(row=1,column=0,sticky='ew');frame.rowconfigure(0,weight=1);frame.columnconfigure(0,weight=1)
 for c in cols:tree.heading(c,text=c);tree.column(c,width=150,stretch=False)
 def refresh():
  try:
   rows,out=(save(folder,path.get(),results_root=results_root) if path.get() else
             (save(folder,etabs_rows=latest['etabs_rows'],policy=latest['policy'],
                   results_root=results_root) if latest['etabs_rows'] is not None
              else save(folder,results_root=results_root)))
   tree.delete(*tree.get_children())
   for r in rows:tree.insert('','end',values=[r.get(c,'') for c in cols])
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
    status.set(str(len(rows))+' saved quantities. Template and report: '+str(out))
  except Exception as e:messagebox.showerror('Comparison inputs',str(e),parent=win)
 def plot():
  selected=tree.selection()
  if not selected:messagebox.showinfo('Select quantity','Select a comparison row first.',parent=win);return
  key=tree.item(selected[0],'values')
  rows=(save(folder,path.get(),results_root=results_root)[0] if path.get() else
        latest['rows'] if latest['rows'] is not None
        else save(folder,results_root=results_root)[0])
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
 if not auto_file:
  status.set('SOURCE: '+auto_note+
             ' | Do not select OpenSees normalized CSV as native ETABS evidence')
 win.after(400,lambda:direct_api(auto=True))
 return win

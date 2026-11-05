"""ETABS/OpenSees comparison contract: explicit units, cases and result bases."""
from pathlib import Path
import csv,json,math,time
FIELDS=['method','limit_state','case','axis','location','metric','unit','basis']
GUIDE='Export ETABS tables for the SAME model, mass source, effective stiffness, diaphragm, restraints, gravity/P-Delta, modes, damping, spectrum units, eccentricity and combinations. Normalize rows to this template. Modes must be paired by shape/participation, not only mode number. MRSM CQC envelopes are not signed simultaneous actions. No reinforcement-demand engine is claimed.'

def collect(folder):
 folder=Path(folder);root=folder/'OpenSees_Analysis_Results';rows=[]
 from components.inputs.project_workbooks import analysis_output_folder
 def add(method,state,case,axis,loc,metric,unit,basis,value,file):
  if value is not None and math.isfinite(float(value)):rows.append(dict(method=method,limit_state=state,case=case,axis=axis,location=str(loc),metric=metric,unit=unit,basis=basis,value=float(value),source_file=str(file)))
 for state in ('ULS','SLS'):
  p=analysis_output_folder(folder,state)/('Modal_'+state)/'NBC105_Modal_V111.json'
  if not p.is_file():p=root/('Modal_'+state)/'NBC105_Modal_V111.json'
  if p.exists():
   d=json.loads(p.read_text(encoding='utf-8-sig'))
   for r in d.get('rows',[]):add('MODAL',state,'MODAL','',r['mode'],'period','s','eigen',r['period_s'],p)
   for axis in ('X','Y'):add('MODAL',state,'MODAL',axis,'ALL','cumulative_mass','percent','modal_mass',d.get('cumulative_U'+axis+'_percent'),p)
 for p in root.rglob('MRSM_Results_V132.json'):
  for case,d in json.loads(p.read_text(encoding='utf-8-sig')).items():
   state=d['limit_state'];axis=d['axis'];add('MRSM',state,case,axis,'BASE','base_shear','kN','CQC_force_scaled',d.get('scaled_modal_base_shear_kN'),p)
   for r in d['stories']:
    add('MRSM',state,case,axis,r['story_number'],'story_shear','kN','CQC_force_scaled',r['scaled_story_shear_kN'],p)
    add('MRSM',state,case,axis,r['story_number'],'displacement','m','CQC_design_unscaled_by_7_5',r.get('design_displacement_m'),p)
    add('MRSM',state,case,axis,r['story_number'],'drift_ratio','ratio','CQC_design_unscaled_by_7_5',r['design_drift_ratio'],p)
 for p in root.rglob('NBC105_ESM_OpenSees_Response_*.json'):
  document=json.loads(p.read_text(encoding='utf-8-sig'))
  rr=document if isinstance(document,list) else document.get('rows',document.get('stories',[]))
  for r in rr:
   for key,metric,unit in [('U_design_m','displacement','m'),('design_drift_ratio','drift_ratio','ratio'),('story_shear_kN','story_shear','kN')]:
    add('ESM',r.get('limit_state','UNKNOWN'),r.get('response_case',p.stem),r.get('direction',''),r.get('height_m',''),metric,unit,'static_design',r.get(key),p)
 return rows

def compare(rows, etabs, policy=None):
    """Compare exact normalized response bases with explicit evidence gates."""
    from components.validation.etabs_equivalence_report import evaluate
    return evaluate(rows, etabs, FIELDS, policy)


def save(folder,etabs_path=None,etabs_rows=None,policy=None):
    """Export source-normalized CSV and Excel comparisons.

    Existing CSV users remain supported. Direct ETABS API results are passed
    as etabs_rows and never require hand-editing a normalized input CSV.
    Programmatic confidence is limited to software checks; comparability
    is gated by the explicitly approved policy, not assumed.
    """
    start=time.perf_counter();folder=Path(folder)
    out=folder/'OpenSees_Analysis_Results/ETABS_Comparison_V148'
    out.mkdir(parents=True,exist_ok=True)
    rows=collect(folder)
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


def launch(parent,folder):
 import tkinter as tk
 from tkinter import ttk,filedialog,messagebox
 win=tk.Toplevel(parent);win.title('ETABS comparison - modal / ESM / MRSM');win.geometry('1200x750');path=tk.StringVar();status=tk.StringVar();bar=ttk.Frame(win);bar.pack(fill='x');ttk.Entry(bar,textvariable=path,width=75).pack(side='left')
 def browse():
  p=filedialog.askopenfilename(parent=win,title='Normalized ETABS CSV',filetypes=[('CSV','*.csv')])
  if p:path.set(p)
 ttk.Button(bar,text='Select ETABS CSV',command=browse).pack(side='left')
 def direct_api():
  """Attach to the selected, already-open source .EDB in a COM STA thread."""
  import threading
  chosen=filedialog.askopenfilename(parent=win,title='Select the exact source ETABS EDB',filetypes=[('ETABS model','*.edb')])
  if not chosen:return
  config=filedialog.askopenfilename(parent=win,title='Select verified case-and-story mapping JSON',filetypes=[('Mapping JSON','*.json')])
  if not config:
   template=Path(folder)/'OpenSees_Analysis_Results/ETABS_Comparison_V148/ETABS_API_Mapping_TEMPLATE.json'
   template.parent.mkdir(parents=True,exist_ok=True)
   from components.validation.etabs_direct_api import mapping_template
   template.write_text(json.dumps(mapping_template(chosen),indent=2),encoding='utf-8')
   messagebox.showinfo('ETABS mapping needed','Template created at '+str(template)+'\\nEnter the real ETABS cases, story mapping and matched results basis; then use Direct ETABS API again.',parent=win)
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
     compared,out=save(folder,etabs_rows=extracted,policy=mapping)
     from components.validation.etabs_direct_api import fingerprint
     provenance={"edb_path":str(Path(chosen).resolve()),"edb_sha256":fingerprint(chosen),
                 "mapping_path":str(Path(config).resolve()),
                 "row_count":len(extracted),"assumptions_verified":bool(mapping.get('assumptions_verified'))}
     (out/'ETABS_API_Provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    finally:comtypes.CoUninitialize()
    def done():
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
   rows,out=save(folder,path.get() or None);tree.delete(*tree.get_children())
   for r in rows:tree.insert('','end',values=[r.get(c,'') for c in cols])
   status.set(str(len(rows))+' saved quantities. Template and report: '+str(out))
  except Exception as e:messagebox.showerror('Comparison inputs',str(e),parent=win)
 def plot():
  selected=tree.selection()
  if not selected:messagebox.showinfo('Select quantity','Select a comparison row first.',parent=win);return
  key=tree.item(selected[0],'values');rows,_=save(folder,path.get() or None)
  subset=[r for r in rows if all(str(r.get(k,''))==key[cols.index(k)] for k in ('method','limit_state','case','axis','metric','unit','basis'))]
  from matplotlib.figure import Figure
  from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
  panel=tk.Toplevel(win);panel.title('Exact case comparison: '+key[2]);panel.geometry('950x650');fig=Figure(figsize=(9,6),layout='constrained');ax=fig.add_subplot();x=list(range(len(subset)));ax.plot(x,[r['value'] for r in subset],marker='o',label='OpenSees')
  if any(r.get('etabs_value') is not None for r in subset):ax.plot(x,[r.get('etabs_value') if r.get('etabs_value') is not None else float('nan') for r in subset],marker='x',label='ETABS')
  ax.set(xlabel='Location / mode',ylabel=key[5]+' ('+key[6]+')',title=key[0]+' '+key[1]+' '+key[2]+' | '+key[7]);ax.set_xticks(x,[r['location'] for r in subset],rotation=60);ax.legend();ax.grid(alpha=.2);canvas=FigureCanvasTkAgg(fig,master=panel);canvas.get_tk_widget().pack(fill='both',expand=True);NavigationToolbar2Tk(canvas,panel);canvas.draw()
 ttk.Button(bar,text='Plot selected case / metric',command=plot).pack(side='left')
 ttk.Button(bar,text='Refresh / export CSV' ,command=refresh).pack(side='left');refresh();return win

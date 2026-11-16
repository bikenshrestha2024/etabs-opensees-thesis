#!/usr/bin/env python3
"""Independent ETABS/OpenSeesPy benchmark studio. No network, no repository mutation.

CLI:
  python ETABS_OpenSees_Verification_Studio.py --self-test
  python ETABS_OpenSees_Verification_Studio.py --run-all --output OUTPUT
  python ETABS_OpenSees_Verification_Studio.py --worker case_id --output OUTPUT --tolerance 0.01
GUI: python ETABS_OpenSees_Verification_Studio.py
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import html
import json
import math
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import traceback
import uuid

APP_VERSION = '2.0.0'
GRAVITY = 9.80665
CASES = [
 ('B01', 'CSI Example 01, Case II — propped beam', 'STATIC FRAME', 'Published CSI reaction and moment (component benchmark)'),
 ('B02', 'Beam subdivision invariance — 1/2/4/8 segments', 'FEM CONNECTIVITY', 'Derived Euler-Bernoulli analytic benchmark'),
 ('B03', 'Axial truss — closed-form solution', 'BRACE / UNITS', 'Derived from axial EA/L element theory, not a CSI example'),
 ('B04', 'ShellMITC4 wall — gravity equilibrium / mesh series', 'WALL / SHELL', 'Independent wall patch; NOT reproduction of CSI Example 15'),
]
# B05-B12 are independent component-level checks, not native CSI ETABS reruns.
CASES += [
 ('B05','Root rigid-end segment under tip force','FRAME END ZONE','Independent high-stiffness rigid-offset idealization'),
 ('B06','6 x 6 m shell slab and four edge beams','SLAB / FRAME','Shared solver nodes and symmetric gravity equilibrium, MESH_04/08/16'),
 ('B07','Wall supported on two columns','WALL / FRAME','Elastic shell-to-column vertical force transfer'),
 ('B08','Wall with geometric opening','WALL / OPENING','Net shell area and gravity equilibrium'),
 ('B09','Parallel wall/frame stiffness sharing','FOUNDATION FORCE SHARING','Independent EA/L-based two-support benchmark'),
 ('B10','Two-bay three-column frame','GRAVITY FRAME','Independent full-frame equilibrium, not full CSI Example 01'),
 ('B11','Single DOF axial oscillator','MODAL / MASS','Analytical eigenvalue and mass-units check'),
 ('B12','FVD power-law constitutive equation','DAMPER / ANALYTICAL','Analytical only, NOT native OpenSees link or CSI Example 11'),
]
REFERENCE_INDEX = [
 ('01','Plane frame — static gravity','component benchmark B01'),
 ('02','Three-storey frame — response spectrum / rigid offsets','REFERENCE ONLY; future native benchmark'),
 ('03','Three-storey historical seismic and wind','REFERENCE ONLY'),
 ('04','3D response spectrum','REFERENCE ONLY'),
 ('05','Three-storey braced frame response spectrum','REFERENCE ONLY'),
 ('06','Nine-storey eigenvalue analysis','REFERENCE ONLY'),
 ('07','Seven-storey frame gravity/static/dynamic','REFERENCE ONLY'),
 ('08','Two-storey 3D response spectrum','REFERENCE ONLY'),
 ('09','Two-storey 3D asymmetric response','REFERENCE ONLY'),
 ('10','ADAS device nonlinear response','REFERENCE ONLY'),
 ('11','Viscous dampers nonlinear time history','REFERENCE ONLY'),
 ('12','Gap/pounding nonlinear time history','REFERENCE ONLY'),
 ('13','Hysteretic base isolator','REFERENCE ONLY'),
 ('14','Friction pendulum isolator','REFERENCE ONLY'),
 ('15','Wall object static lateral response','REFERENCE ONLY; wall patch B04 and B07 are not CSI 15'),
]

def _metric(name, actual, expected, rel_tol, *, abs_tol=1e-7, source='ANALYTICAL', unit='', note=''):
    actual=float(actual); expected=float(expected)
    if not (math.isfinite(actual) and math.isfinite(expected)):
        raise ValueError('Non-finite benchmark result: '+name)
    delta=actual-expected
    scale=max(abs(expected),abs_tol)
    err=abs(delta)/scale
    return {'metric':name,'actual':actual,'expected':expected,'difference':delta,
            'relative_error':err,'tolerance':float(rel_tol),'passed':abs(delta)<=max(abs_tol,rel_tol*abs(expected)),
            'reference_type':source,'unit':unit,'note':note}

def _linear_static(ops):
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral')
    ops.test('NormUnbalance', 1e-10, 25); ops.algorithm('Newton')
    ops.integrator('LoadControl',1.0); ops.analysis('Static')
    rc=ops.analyze(1)
    if rc!=0: raise RuntimeError('OpenSees static analysis failed: '+str(rc))
    ops.reactions()

def _propped(ops,n):
    # CSI Example 01, Case II — B1 isolates a pinned-to-fixed 18-ft beam under 10 kip/ft.
    # Original source is a 2-bay, 3-column frame; we validate the equivalent propped-beam component,
    # not the entire CSI geometry.
    L=216.0; w=10.0/12.0; E=3000.0; I=12.0*30.0**3/12.0
    ops.wipe(); ops.model('basic','-ndm',2,'-ndf',3)
    for j in range(n+1): ops.node(j+1,L*j/n,0.)
    ops.fix(1,1,1,0);ops.fix(n+1,1,1,1)
    ops.geomTransf('Linear',1)
    for j in range(1,n+1):
        ops.element('elasticBeamColumn',j,j,j+1,1e9,E,I,1) # axial stiffness high; immaterial here
    ops.timeSeries('Linear',1);ops.pattern('Plain',1,1)
    for j in range(1,n+1): ops.eleLoad('-ele',j,'-type','-beamUniform',-w)
    _linear_static(ops)
    rx1=ops.nodeReaction(1,2);rx2=ops.nodeReaction(n+1,2)
    moment=ops.nodeReaction(n+1,3)
    mid=ops.nodeDisp(n//2+1,2) if n%2==0 else None
    exact_mid=-w*L**4/(192.0*E*I)
    return {'R_pin':rx1,'R_fixed':rx2,'M_fixed_abs':abs(moment),'R_sum':rx1+rx2,
            'mid':mid,'exact_mid':exact_mid,'n':n,'L':L,'w':w,'EI':E*I}

def _run_case(ops,case,tol):
    metrics=[];detail={}
    if case=='B01':
        s=_propped(ops,1);detail={'beam':s,'source':'CSI Software Verification Example 01, Table 1-1, Case II, 18-ft B1',
              'scope':'Propped beam component only; no full three-column frame reproduction',
              'reference_units':'kip, inch, second'}
        for name,got,exp,unit in [
            ('Pinned-end vertical reaction',s['R_pin'],67.5,'kip'),
            ('Fixed-end vertical reaction',s['R_fixed'],112.5,'kip'),
            ('Fixed-end moment magnitude',s['M_fixed_abs'],4860.0,'kip-in'),
            ('Total applied versus reactions',s['R_sum'],180.0,'kip')]:
            metrics.append(_metric(name,got,exp,tol,source='CSI_EX01_CASEII',unit=unit))
    elif case=='B02':
        states={str(n):_propped(ops,n) for n in (1,2,4,8)};detail={'segments':states,'source':'Euler-Bernoulli propped beam; direct shared FEM node continuity'}
        for n in (1,2,4,8):
            s=states[str(n)]
            metrics.append(_metric(f'{n} segment(s) pin reaction',s['R_pin'],67.5,tol,unit='kip'))
            metrics.append(_metric(f'{n} segment(s) fixed reaction',s['R_fixed'],112.5,tol,unit='kip'))
        for n in (2,4,8):
            s=states[str(n)]
            metrics.append(_metric(f'{n} segment(s) midpoint UY',s['mid'],s['exact_mid'],tol,unit='in',note='Closed-form Euler-Bernoulli beam deflection'))
    elif case=='B03':
        ops.wipe();ops.model('basic','-ndm',2,'-ndf',2)
        L=6.0; A=0.01; E=200e6; F=120.0
        ops.node(1,0.,0.);ops.node(2,L,0.);ops.fix(1,1,1);ops.fix(2,0,1)
        ops.uniaxialMaterial('Elastic',1,E)
        ops.element('truss',1,1,2,A,1)
        ops.timeSeries('Linear',1);ops.pattern('Plain',1,1);ops.load(2,F,0.)
        _linear_static(ops)
        u=ops.nodeDisp(2,1);r=ops.nodeReaction(1,1)
        detail={'L_m':L,'A_m2':A,'E_kN_m2':E,'F_kN':F,'analytic_u_m':F*L/(E*A), 'scope':'axial stiffness and reaction, not ETABS Example 05 full model'}
        metrics.extend([_metric('Axial displacement',u,F*L/(E*A),tol,unit='m'),_metric('Anchor reaction',r,-F,tol,unit='kN')])
    elif case=='B04':
        states={}
        for n in (1,2,4):
            ops.wipe();ops.model('basic','-ndm',3,'-ndf',6)
            E=25e6; nu=.2; t=.3; width=6.; height=3.; total=1200.
            for j in range(n+1):
                for i in range(n+1):
                    tag=1+j*(n+1)+i
                    ops.node(tag,width*i/n,0.,height*j/n)
                    if j==0:ops.fix(tag,1,1,1,1,1,1)
            ops.section('ElasticMembranePlateSection',1,E,nu,t,0.0)
            k=1
            for j in range(n):
                for i in range(n):
                    a=1+j*(n+1)+i;b=a+1;c=b+(n+1);d=a+(n+1)
                    ops.element('ShellMITC4',k,a,b,c,d,1);k+=1
            ops.timeSeries('Linear',1);ops.pattern('Plain',1,1)
            for i in range(n+1):
                top=1+n*(n+1)+i
                ops.load(top,0,0,-total*(.5 if i in (0,n) else 1.)/n,0,0,0)
            _linear_static(ops)
            R=sum(ops.nodeReaction(1+i,3) for i in range(n+1))
            mid=ops.nodeDisp(1+n*(n+1)+(n//2),3)
            states[str(n)]={'bottom_reaction_kN':R,'top_Uz_m':mid,'mesh_cells':n*n}
            metrics.append(_metric(f'{n}x{n} wall total base reaction',R,total,tol,unit='kN',source='EQUILIBRIUM_ONLY'))
        detail={'states':states,'scope':'2D wall shell in 3D, uniform top gravity; demonstrates equilibrium only. NOT ETABS Example 15 lateral wall verification.'}
    else: raise ValueError('Unknown benchmark '+case)
    return {'case_id':case,'title':next(c[1] for c in CASES if c[0]==case),
            'status':'PASS' if all(m['passed'] for m in metrics) else 'FAIL',
            'metrics':metrics,'details':detail}

# Preserve the user-tested v1 B01-B04 implementation unchanged.
_run_legacy_case = _run_case

def _run_case(ops,case,tol):
    if case in ('B01','B02','B03','B04'):
        result=_run_legacy_case(ops,case,tol)
        result['verification_scope']='INDEPENDENT_COMPONENT_BENCHMARK'
        result['etabs_native_equivalence']='NOT_VERIFIED'
        return result
    import expanded_benchmarks
    return expanded_benchmarks.run(case,ops,tol)

def run_worker(case, tolerance, destination):
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    try:
        if case=='B12':
            # B12 intentionally tests only analytical constitutive signs/units.
            result=_run_case(None,case,tolerance)
            result['solver']='NONE_ANALYTICAL_ONLY'
            result['solver_version']='NOT_APPLICABLE'
        else:
            import openseespy.opensees as ops
            result=_run_case(ops,case,tolerance)
            result['solver']='OpenSeesPy';result['solver_version']=str(ops.version()) if hasattr(ops,'version') else 'unavailable'
    except ImportError as exc:
        result={'case_id':case,'title':next(c[1] for c in CASES if c[0]==case),'status':'BLOCKED',
                'reason':'OpenSeesPy is not installed in the selected Python environment: '+str(exc), 'metrics':[]}
    except Exception as exc:
        result={'case_id':case,'title':next(c[1] for c in CASES if c[0]==case),'status':'ERROR',
                'reason':str(exc),'traceback':traceback.format_exc(), 'metrics':[]}
    import hashlib
    result['source_sha256']={name:hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()
                             for name in ('ETABS_OpenSees_Verification_Studio.py','expanded_benchmarks.py')
                             if (Path(__file__).parent/name).is_file()}
    result['timestamp']=dt.datetime.now(dt.timezone.utc).isoformat()
    result['tolerance_relative']=tolerance
    result['software_version']=APP_VERSION
    (destination/(case+'.json')).write_text(json.dumps(result,indent=2,default=str),encoding='utf-8')
    print(json.dumps({'case_id':case,'status':result['status'],'metrics':len(result['metrics']),'reason':result.get('reason','')}),flush=True)
    return result

def _write_reports(folder, results, provenance):
    folder=Path(folder); folder.mkdir(parents=True,exist_ok=True)
    (folder/'manifest.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    (folder/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    cols=['case_id','case_status','metric','actual','expected','difference','relative_error','tolerance','passed','unit','reference_type','note']
    with (folder/'metrics.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for r in results:
            for m in r.get('metrics',[]):w.writerow({'case_id':r['case_id'],'case_status':r['status'],**{k:m.get(k,'') for k in cols if k not in ('case_id','case_status')}})
    rows=[]
    for r in results:
        rows.append(f'<tr><td>{html.escape(r["case_id"])}</td><td>{html.escape(r["title"])}</td><td>{html.escape(r["status"])}</td><td>{len(r.get("metrics",[]))}</td><td>{html.escape(r.get("reason", ""))}</td></tr>')
    page='''<!DOCTYPE html><html lang="en"><meta charset="utf-8"><title>OpenSeesPy Verification Report</title><style>
body{font:15px system-ui,Arial;max-width:1100px;margin:44px auto;padding:0 16px;color:#162839}h1{font-size:26px}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:10px;border-bottom:1px solid #ddd}th{background:#f2f5f8}
.warning{background:#fff1d8;padding:16px;border-radius:6px}code{font-size:12px}</style>
<h1>ETABS–OpenSeesPy Independent Verification</h1><p class="warning">PASS means only the listed native component benchmark passed; ANALYTICAL_PASS is not a solver run. It does not verify the full CSI ETABS example, the ETABS native solver, or the thesis model. BLOCKED/ERROR are not PASS.</p>
<p>Run provenance: <code>'''+html.escape(json.dumps(provenance))+'''</code></p><table><tr><th>Case</th><th>Benchmark</th><th>Status</th><th>Metrics</th><th>Diagnostic</th></tr>'''+''.join(rows)+'</table><p>See metrics.csv, results.json and individual per-case JSON for full numerical details.</p></html>'
    (folder/'report.html').write_text(page,encoding='utf-8')

def compare_support_csv(source,output_dir):
    # User provided explicitly mapped source and target IDs. Never match by equal integer name.
    source=Path(source);output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    with source.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    required={'opensees_node','etabs_unique_name','source_primary32','original_ETABS_FZ_kN','opensees_32_Rz_kN'}
    if not rows or not required.issubset(rows[0]):raise ValueError('Input CSV must have exact verified source/target ID and reaction columns')
    selected=[r for r in rows if str(r['source_primary32']).strip().lower() in ('true','1','yes')]
    if len(selected)!=32:raise ValueError(f'Expected exactly 32 mapped foundation reaction records, got {len(selected)}')
    def unique(vals,name):
        if len(set(vals))!=32:raise ValueError('Nonunique '+name+' mapping')
    unique([r['opensees_node'] for r in selected],'OpenSees nodes');unique([r['etabs_unique_name'] for r in selected],'ETABS source points')
    data=[]
    for r in selected:
        e=float(r['original_ETABS_FZ_kN']);o=float(r['opensees_32_Rz_kN'])
        if not all(map(math.isfinite,(e,o))):raise ValueError('Nonfinite reaction data')
        data.append({'etabs_point':r['etabs_unique_name'],'opensees_node':r['opensees_node'],'etabs_kN':e,'opensees_kN':o,'delta_kN':o-e,'abs_delta_kN':abs(o-e),'relative_percent':100*(o-e)/abs(e) if abs(e)>1e-9 else None})
    data.sort(key=lambda r:-r['abs_delta_kN'])
    with (output_dir/'support32_mapped_comparison.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    summary={'source_file':str(source),'count':32,'etabs_sum_kN':sum(r['etabs_kN'] for r in data),
             'opensees_sum_kN':sum(r['opensees_kN'] for r in data),'absolute_difference_sum_kN':sum(r['abs_delta_kN'] for r in data),
             'max_absolute_difference_kN':max(r['abs_delta_kN'] for r in data),
             'status':'DATA_COMPARISON_ONLY_NOT_EQUIVALENCE_PASSED'}
    (output_dir/'support32_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return summary

def run_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    root=tk.Tk();root.title('ETABS ↔ OpenSeesPy | Independent Verification Studio');root.geometry('1120x740');root.minsize(890,600)
    style=ttk.Style(root)
    if 'clam' in style.theme_names():style.theme_use('clam')
    container=ttk.Frame(root,padding=14);container.pack(fill='both',expand=True)
    ttk.Label(container,text='ETABS ↔ OpenSeesPy Verification Studio',font=('Segoe UI',19,'bold')).pack(anchor='w')
    ttk.Label(container,text='Standalone benchmark runner  •  never edits the source ETABS model or thesis solver  •  outputs isolated per run').pack(anchor='w',pady=(2,12))
    controls=ttk.Frame(container);controls.pack(fill='x')
    python_var=tk.StringVar(value=sys.executable);output_var=tk.StringVar(value=str(Path.cwd()/'VERIFICATION_RUNS'))
    tolerance_var=tk.StringVar(value='0.01');selection=tk.StringVar(value='')
    ttk.Label(controls,text='Solver Python:').grid(row=0,column=0,sticky='w',pady=3)
    ttk.Entry(controls,textvariable=python_var).grid(row=0,column=1,sticky='ew',padx=7)
    ttk.Button(controls,text='Browse',command=lambda: python_var.set(filedialog.askopenfilename(filetypes=[('Python executable','python.exe'),('All files','*')]) or python_var.get())).grid(row=0,column=2)
    ttk.Label(controls,text='Output root:').grid(row=1,column=0,sticky='w',pady=3)
    ttk.Entry(controls,textvariable=output_var).grid(row=1,column=1,sticky='ew',padx=7)
    ttk.Button(controls,text='Browse',command=lambda: output_var.set(filedialog.askdirectory() or output_var.get())).grid(row=1,column=2)
    ttk.Label(controls,text='Relative tolerance:').grid(row=2,column=0,sticky='w',pady=3)
    ttk.Entry(controls,textvariable=tolerance_var,width=13).grid(row=2,column=1,sticky='w',padx=7)
    controls.columnconfigure(1,weight=1)
    hint='0.01 = 1%; component benchmark default for this diagnostic. Tighten when solver equivalence is established.'
    ttk.Label(container,text=hint,foreground='#485b70').pack(anchor='w',pady=(4,10))
    notebook=ttk.Notebook(container);notebook.pack(fill='both',expand=True)
    tab=ttk.Frame(notebook,padding=8);notebook.add(tab,text='Executable Benchmarks')
    ref=ttk.Frame(notebook,padding=8);notebook.add(ref,text='CSI Verification Catalog (15)')
    logtab=ttk.Frame(notebook,padding=8);notebook.add(logtab,text='Progress / Results')
    tree=ttk.Treeview(tab,columns=('category','source'),show='tree headings',selectmode='extended',height=9)
    tree.heading('#0',text='Benchmark');tree.column('#0',width=340)
    tree.heading('category',text='Verification category');tree.column('category',width=180)
    tree.heading('source',text='Scope / reference');tree.column('source',width=450)
    for cid,name,category,source in CASES:tree.insert('', 'end',iid=cid,text=cid+' — '+name,values=(category,source))
    tree.pack(fill='both',expand=True)
    ttk.Label(tab,text='Select one or more benchmarks (Ctrl/Shift). Only implemented tests can receive PASS. The 15 published CSI cases are not implicitly reproduced.').pack(anchor='w',pady=10)
    cat=ttk.Treeview(ref,columns=('topic','scope'),show='tree headings',height=16)
    for k,v,width in [('#0','CSI example',105),('topic','Published subject',360),('scope','Implementation status',470)]:
        cat.heading(k,text=v);cat.column(k,width=width)
    for n,title,scope in REFERENCE_INDEX:cat.insert('', 'end',text='Example '+n,values=(title,scope))
    cat.pack(fill='both',expand=True)
    ttk.Label(ref,text='Sources: uploaded CSI Example 01–15 PDFs. These reference-only entries have not been executed.').pack(anchor='w',pady=6)
    log=tk.Text(logtab,height=12,wrap='word',state='disabled',font=('Consolas',10));log.pack(fill='both',expand=True)
    state={'working':False,'thread':None,'last_output':None};events=queue.Queue()
    def append(msg):
        log.configure(state='normal');log.insert('end',msg+'\n');log.see('end');log.configure(state='disabled')
    def poll():
        try:
            while True:
                kind,data=events.get_nowait()
                if kind=='log':append(data)
                elif kind=='done':state['working']=False;state['last_output']=data;append('Report: '+str(Path(data)/'report.html'));set_controls('normal')
        except queue.Empty:pass
        root.after(125,poll)
    def set_controls(v):
        for b in (runselected,runall,compbtn):b.configure(state=v)
    def do_run(cids):
        if state['working']:return
        try:
            tol=float(tolerance_var.get());assert math.isfinite(tol) and 0<tol<1
            py=Path(python_var.get()).expanduser();assert py.is_file()
            root_out=Path(output_var.get()).expanduser();root_out.mkdir(parents=True,exist_ok=True)
        except (ValueError,AssertionError,OSError):
            messagebox.showerror('Invalid inputs','Specify an existing Python interpreter, writable output directory, and tolerance between 0 and 1.');return
        folder=root_out/(dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6]);folder.mkdir()
        state['working']=True;set_controls('disabled');notebook.select(logtab)
        def worker():
            results=[]
            for cid in cids:
                events.put(('log','RUN '+cid))
                cmd=[str(py),str(Path(__file__).resolve()),'--worker',cid,'--output',str(folder/'cases'),'--tolerance',str(tol)]
                try:
                    result=subprocess.run(cmd,capture_output=True,text=True,timeout=180,check=False)
                    if result.stdout:events.put(('log',result.stdout.strip()))
                    if result.stderr:events.put(('log','Solver diagnostic: '+result.stderr.strip()[-1200:]))
                    path=folder/'cases'/(cid+'.json')
                    data=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'case_id':cid,'title':cid,'status':'ERROR','metrics':[],'reason':'No worker result; '+result.stderr[-1200:]}
                except Exception as exc:
                    data={'case_id':cid,'title':cid,'status':'ERROR','metrics':[],'reason':str(exc)}
                results.append(data);events.put(('log','STATUS '+cid+' = '+data['status']))
            prov={'tool_version':APP_VERSION,'timestamp':dt.datetime.now(dt.timezone.utc).isoformat(), 'python':str(py),
                  'tolerance':tol,'requested_cases':cids,'scope':'Benchmark verification only; source model untouched'}
            _write_reports(folder,results,prov);events.put(('done',str(folder)))
        state['thread']=threading.Thread(target=worker,daemon=True);state['thread'].start()
    buttons=ttk.Frame(container);buttons.pack(fill='x',pady=(10,0))
    runselected=ttk.Button(buttons,text='Run selected',command=lambda:do_run(list(tree.selection())) if tree.selection() else messagebox.showinfo('Choose benchmarks','Select at least one benchmark'))
    runselected.pack(side='left',padx=(0,7))
    runall=ttk.Button(buttons,text='Run all 12 benchmarks',command=lambda:do_run([c[0] for c in CASES]));runall.pack(side='left',padx=(0,7))
    def compare():
        file=filedialog.askopenfilename(title='Choose verified 32/76/97 mapped reaction CSV',filetypes=[('CSV','*.csv')]);
        if not file:return
        try:
            folder=Path(output_var.get()).expanduser()/(dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_support32_compare')
            summary=compare_support_csv(file,folder)
            notebook.select(logtab);append('32-support comparison: '+json.dumps(summary,indent=2))
            append('Comparison file: '+str(folder/'support32_mapped_comparison.csv'))
        except Exception as e:messagebox.showerror('Reaction CSV error',str(e))
    compbtn=ttk.Button(buttons,text='Audit mapped 32-support CSV…',command=compare);compbtn.pack(side='left')
    ttk.Button(buttons,text='Open last report',command=lambda:os.startfile(str(Path(state['last_output'])/'report.html')) if state['last_output'] and hasattr(os,'startfile') else messagebox.showinfo('Report location',str(state['last_output'] or 'No report generated'))).pack(side='right')
    ttk.Label(container,text='PASS = native numerical benchmark  | ANALYTICAL_PASS = equation only | BLOCKED = missing solver | ERROR = failure',foreground='#485b70').pack(anchor='w',pady=(8,0))
    root.after(125,poll);root.mainloop()

def self_test():
    s=_metric('test',10.,10.,1e-3);assert s['passed']
    s=_metric('test',9.,10.,1e-3);assert not s['passed']
    # Analytic consistency for Example 01 loads and geometry and beam midspan formula
    L=216.;w=10./12.;E=3000.;I=27000.
    assert abs(3*w*L/8-67.5)<1e-10
    assert abs(5*w*L/8-112.5)<1e-10
    assert abs(w*L*L/8-4860.)<1e-10
    assert -w*L**4/(192*E*I)<0
    assert len(REFERENCE_INDEX)==15 and len(CASES)==12
    print('SELF-TEST PASS: 12 case registry, v1 formulas, source catalog and status logic. Expanded OpenSeesPy runs NOT tested here.')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--worker',choices=[x[0] for x in CASES]);p.add_argument('--run-all',action='store_true')
    p.add_argument('--cases',nargs='+',choices=[x[0] for x in CASES],help='Run selected benchmark IDs in headless mode')
    p.add_argument('--list-cases',action='store_true',help='Print all executable benchmark IDs and scopes')
    p.add_argument('--self-test',action='store_true');p.add_argument('--output',default='VERIFICATION_RUNS')
    p.add_argument('--tolerance',type=float,default=.01);p.add_argument('--compare-32',metavar='CSV')
    args=p.parse_args()
    if not math.isfinite(args.tolerance) or not 0<args.tolerance<1:
        p.error('--tolerance must be a finite number greater than 0 and less than 1')
    if args.list_cases:
        for c in CASES:print(f'{c[0]} | {c[1]} | {c[3]}')
        return 0
    if args.self_test:self_test();return 0
    if args.compare_32:
        print(json.dumps(compare_support_csv(args.compare_32,args.output),indent=2));return 0
    if args.worker:
        result=run_worker(args.worker,args.tolerance,args.output)
        return 0 if result['status'] in ('PASS','FAIL','BLOCKED','ANALYTICAL_PASS','ANALYTICAL_FAIL') else 1
    if args.run_all or args.cases:
        selected=[c for c in CASES if args.run_all or c[0] in args.cases]
        root=Path(args.output)/(dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6]);root.mkdir(parents=True)
        results=[run_worker(c[0],args.tolerance,root/'cases') for c in selected]
        _write_reports(root,results,{'tool_version':APP_VERSION,'python':sys.executable,'tolerance':args.tolerance,'status':'native solver execution' if any(r['status']=='PASS' for r in results) else 'unverified'})
        print('Reports: '+str(root))
        return 0 if all(x['status'] in ('PASS','ANALYTICAL_PASS') for x in results) else 2
    run_gui();return 0

if __name__=='__main__':sys.exit(main())
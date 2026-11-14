"""Compare saved responses and expose combination/preload coverage without inventing runs."""
from pathlib import Path
import json,csv,os

def collect(folder):
    from OpenSees_Design_Checks_V135 import scan_drift,combinations
    folder=Path(folder)
    # A case-local V142 launcher may be passed the export folder, the legacy
    # OpenSees_Analysis_Results folder, or a single ULS/SLS case directory.
    # Resolve actual sources; do not invent responses from force ledgers.
    from components.inputs.output_layout import export_root_for
    export_root=export_root_for(folder)
    legacy=export_root/'OpenSees_Analysis_Results'
    roots=[legacy] if legacy.is_dir() else []
    if folder.is_dir() and folder!=legacy and folder!=export_root:
        roots.append(folder)
    for stage in ('03_ESM','04_MODAL','05_MRSM','06_LINEAR_TIME_HISTORY',
                  '07_NONLINEAR_TIME_HISTORY'):
        stage_path=export_root/stage
        if stage_path.is_dir() and stage_path not in roots:
            roots.append(stage_path)
    rows=[];issues=[]
    for root in roots:
        new_rows,new_issues=scan_drift(root)
        rows.extend(new_rows);issues.extend(new_issues)
    if not roots:
        issues.append(dict(status='MISSING_RESULTS_ROOT',
                           reason='Neither legacy nor canonical analysis stage outputs were found; run compatible seismic analysis first.',
                           file=str(export_root)))
    profiles=[]
    for path in folder.rglob('Gravity_Profile_*_V142.json'):
        item=json.loads(path.read_text(encoding='utf-8-sig'));profiles.append(dict(file=str(path),limit_state=item.get('limit_state'),**item.get('gravity_context',{})))
    deflections=[]
    for root in roots:
      for path in root.rglob('Floor_Edge_Drift_*.csv'):
        with path.open(encoding='utf-8-sig',newline='') as stream:
            for row in csv.DictReader(stream):
                if row.get('floor_displacement_m') not in (None,''):deflections.append(dict(file=str(path),case=path.stem,limit_state=row.get('limit_state',''),storey=row.get('story_number'),axis=row.get('axis',''),displacement_m=float(row['floor_displacement_m']),scope='Saved floor-edge response; verify source model and combination before comparison'))
    for root in roots:
      for path in root.rglob('Deformation_*.json'):
        try:
            item=json.loads(path.read_text(encoding='utf-8-sig')); state=item.get('limit_state','')
            if state not in ('ULS','SLS'):continue
            levels={}
            for tag,xyz in item.get('nodes',{}).items():
                u=item.get('displacements',{}).get(str(tag),[])
                if len(u)<2:continue
                z=round(float(xyz[2]),7)
                for i,axis in enumerate(('X','Y')):levels[z,axis]=max(levels.get((z,axis),0.),abs(float(u[i])))
            for (z,axis),value in levels.items():deflections.append(dict(file=str(path),case=path.stem,limit_state=state,storey=z,axis=axis,displacement_m=value,scope='Maximum absolute saved nodal component at elevation (m); CQC envelopes are non-concurrent; no force-only scale applied'))
        except (ValueError,KeyError,TypeError) as exc:issues.append(dict(file=str(path),error=str(exc)))
    coverage=[]
    for case in combinations(nonparallel=True):
        for method in ('ESM','MRSM','LTH'):
            coverage.append(dict(case=case['case'],limit_state=case['limit_state'],method=method,factors=json.dumps(case['factors']),status='REQUIRES CASE-SPECIFIC RESULT / IDENTITY REVIEW',note='Existing similar state/direction files do not prove this full combination was solved; CQC envelopes cannot be treated as concurrent signed actions.'))
    # The V142 chart must never silently represent absent data as a zero drift.
    # A gravity-only run legitimately has no seismic interstorey drift.
    if not rows:
        issues.append(dict(status='NO_SAVED_SEISMIC_DRIFT',
                           reason='No recognized ULS/SLS Drift_Check_, Floor_Edge_Drift_ or MRSM_Results_V132 response found. Gravity/P-Delta preload alone does not calculate seismic design drift.',
                           searched_paths=[str(p) for p in roots]))
    if not deflections:
        issues.append(dict(status='NO_SAVED_LATERAL_DEFLECTION',
                           reason='No recognized floor-edge displacement or deformation results found. Do not treat an empty chart as zero response.',
                           searched_paths=[str(p) for p in roots]))
    return dict(drift=rows,deflection=deflections,issues=issues,
                searched_paths=[str(p) for p in roots],
                preload_profiles=profiles,combination_coverage=coverage)


def export(folder):
    from openpyxl import Workbook
    folder=Path(folder);result=collect(folder);out=folder/'OpenSees_Analysis_Results/Case_Review_V142';out.mkdir(parents=True,exist_ok=True)
    wb=Workbook();wb.remove(wb.active)
    for key,title in [('drift','Saved drift'),('deflection','Saved deflection'),('preload_profiles','PDelta preload provenance'),('combination_coverage','Combination coverage'),('issues','Read errors')]:
        ws=wb.create_sheet(title);items=result[key]
        if items:
            keys=list(dict.fromkeys(k for r in items for k in r));ws.append(keys)
            for item in items:ws.append([json.dumps(item.get(k)) if isinstance(item.get(k),(dict,list)) else item.get(k) for k in keys])
            ws.auto_filter.ref=ws.dimensions;ws.freeze_panes='A2'
    rootsheet=wb.create_sheet('Searched result paths');rootsheet.append(['Path scanned','Found']);
    for scanned in result.get('searched_paths',[]):rootsheet.append([scanned,Path(scanned).is_dir()]);
    note=wb.create_sheet('Read first');note.append(['Missing combination results are not PASS. Profiles select gravity preloads for future fresh model runs, with original seismic mass retained.'])
    note.append(['AS_CONFIGURED = source configured preload; GRAVITY_1.0D_1.0L = 100% dead + 100% live comparison; GRAVITY_1.2D_1.5L; UPLIFT_0.9D. Snow/liquid/earth/wind/vertical earthquake applicability still requires project action data.'])
    note.append(['Linear time history is a linear transient model about a selected preloaded state. It is not a full nonlinear PDelta time-history solution. Positive CQC component envelopes are not concurrent deformed shapes.'])
    wb.save(out/'All_Case_Review_V142.xlsx');(out/'All_Case_Review_V142.json').write_text(json.dumps(result,indent=2),encoding='utf-8');return result,out


def launch(parent,folder):
    import tkinter as tk
    from tkinter import ttk,messagebox
    from matplotlib.figure import Figure
    from OpenSees_Research_UI_V123 import embed_figures
    win=tk.Toplevel(parent);win.title('V142 saved drift / deflection and combination coverage');win.geometry('1200x800');controls=ttk.Frame(win);controls.pack(fill='x')
    profile=tk.StringVar(value=os.environ.get('OPENSEES_GRAVITY_PROFILE','AS_CONFIGURED'));ttk.Label(controls,text='Gravity preload for subsequent analysis runs:').pack(side='left');ttk.Combobox(controls,textvariable=profile,values=['AS_CONFIGURED','GRAVITY_1.0D_1.0L','GRAVITY_1.2D_1.5L','UPLIFT_0.9D'],state='readonly',width=28).pack(side='left')
    def apply():os.environ['OPENSEES_GRAVITY_PROFILE']=profile.get();messagebox.showinfo('Preload selected','Subsequent fresh analysis processes inherit this preload, including modal and time-history runs. Existing results and assembly-time storey/formula ledgers are not recalculated. The standalone gravity expected-load input must match the selected profile. Mass factors remain unchanged. Restore AS_CONFIGURED after the comparison.',parent=win)
    ttk.Button(controls,text='Apply to subsequent runs',command=apply).pack(side='left')
    text=tk.StringVar();ttk.Label(win,textvariable=text,wraplength=1150).pack(fill='x');body=ttk.Frame(win);body.pack(fill='both',expand=True)
    def refresh():
        try:
            result,out=export(folder);fig=Figure(figsize=(11,7),layout='constrained');axes=fig.subplots(2,2)
            for col,state in enumerate(('ULS','SLS')):
                grouped={}
                for row in result['drift']:
                    if row['limit_state']==state:grouped.setdefault(row['case']+' '+row.get('axis',''),[]).append(row)
                for case,items in grouped.items():
                    valid=[r for r in items if str(r['storey']).replace('.','',1).isdigit()]
                    valid.sort(key=lambda r:float(r['storey']))
                    if valid:axes[0,col].plot([r['demand'] for r in valid],[float(r['storey']) for r in valid],label=case)
                axes[0,col].axvline(.025 if state=='ULS' else .006,color='red',ls='--');axes[0,col].set(title=state+' saved drift',xlabel='Design drift ratio',ylabel='Storey')
                grouped={}
                for row in result['deflection']:
                    if row['limit_state']==state:grouped.setdefault(row['case']+' '+row.get('axis',''),[]).append(row)
                for case,items in grouped.items():
                    valid=[r for r in items if str(r['storey']).replace('.','',1).isdigit()];valid.sort(key=lambda r:float(r['storey']))
                    if valid:axes[1,col].plot([abs(r['displacement_m'])*1000 for r in valid],[float(r['storey']) for r in valid],label=case)
                axes[1,col].set(title=state+' saved deflection (case envelope)',xlabel='Absolute displacement (mm)',ylabel='Storey / elevation (see source workbook)')
            for ax in axes.flat:ax.grid(alpha=.25)
            embed_figures(body,[('ULS / SLS saved responses',fig)]);fig.savefig(out/'Drift_Deflection_Comparison_V142.png',dpi=150)
            if not result['drift'] and not result['deflection']:
                fig.suptitle('NO SAVED SEISMIC RESPONSE — NOT ZERO DRIFT; CHECK CASE RESULTS AND IDENTITY',
                             color='#a13c23',fontsize=11)
            text.set(str(len(result['drift']))+' saved drift rows; '+str(len(result['deflection']))+
                     ' saved deflection rows. '+('NO VERIFIED RESPONSE: open Read errors worksheet and check analysis source paths. ' if not result['drift'] and not result['deflection'] else '')+
                     'Full combination coverage remains subject to explicit case/identity verification. Workbook: '+str(out/'All_Case_Review_V142.xlsx'))
        except Exception as exc:messagebox.showerror('Case review',str(exc),parent=win)
    ttk.Button(controls,text='Refresh / export comparison',command=refresh).pack(side='left');refresh();return win

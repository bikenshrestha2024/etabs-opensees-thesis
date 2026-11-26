"""Compare saved responses and expose combination/preload coverage without inventing runs."""
from pathlib import Path
import json,csv,os,math,tempfile
from components.nbc105.clause_05_dynamic_characteristics import drift_limit_ratio

def collect(folder):
    from OpenSees_Design_Checks_V135 import scan_drift,combinations
    from components.inputs.output_layout import export_root_for, result_roots
    folder=Path(folder)
    export_root=export_root_for(folder)
    # Source-compatible reader: both canonical and archived result roots.
    # The helper avoids scanning a selected case twice through its parent.
    roots=result_roots(folder, stages=("ESM", "MRSM", "LTHA", "NLTHA"))
    rows=[];issues=[]
    for root in roots:
        new_rows,new_issues=scan_drift(root)
        rows.extend(new_rows);issues.extend(new_issues)
    if not roots:
        issues.append(dict(status='MISSING_RESULTS_ROOT',
                           reason='Neither legacy nor canonical analysis stage outputs were found; run compatible seismic analysis first.',
                           file=str(export_root)))
    # All compatible source files are read; duplicate path/row identities from
    # overlapping aliases must never become extra plotted response values.
    distinct=set()
    unique=[]
    for row in rows:
        key=tuple((k,json.dumps(v,sort_keys=True,default=str)) for k,v in sorted(row.items()))
        if key not in distinct:
            unique.append(row)
            distinct.add(key)
    rows=unique
    profiles=[]
    for path in folder.rglob('Gravity_Profile_*_V142.json'):
        if path.is_symlink():
            issues.append(dict(status='LINKED_GRAVITY_PROFILE_REFUSED',file=str(path)))
            continue
        try:
            item=json.loads(path.read_text(encoding='utf-8-sig'))
            if not isinstance(item,dict) or not isinstance(item.get('gravity_context',{}),dict):
                raise ValueError('Gravity profile/context must be JSON objects')
            profiles.append(dict(file=str(path),limit_state=item.get('limit_state'),
                                 **item.get('gravity_context',{})))
        except (OSError,ValueError,TypeError) as exc:
            issues.append(dict(status='INVALID_GRAVITY_PROFILE',file=str(path),error=str(exc)))
    deflections=[]
    for root in roots:
      for path in root.rglob('Floor_Edge_Drift_*.csv'):
        if path.is_symlink():
            issues.append(dict(status='LINKED_FLOOR_EDGE_DRIFT_REFUSED',file=str(path)))
            continue
        try:
            with path.open(encoding='utf-8-sig',newline='') as stream:
                for row in csv.DictReader(stream):
                    if row.get('floor_displacement_m') in (None,''):
                        continue
                    number=float(row['floor_displacement_m'])
                    if not math.isfinite(number):
                        raise ValueError('Nonfinite floor-edge displacement')
                    deflections.append(dict(file=str(path),case=path.stem,
                        limit_state=row.get('limit_state',''),
                        storey=row.get('story_number'),axis=row.get('axis',''),
                        displacement_m=number,
                        scope='Saved floor-edge response; verify source model and combination before comparison'))
        except (OSError,ValueError,TypeError,OverflowError,csv.Error) as exc:
            issues.append(dict(status='INVALID_FLOOR_EDGE_DRIFT',file=str(path),error=str(exc)))
            deflections=[row for row in deflections if row.get('file')!=str(path)]
    for root in roots:
      for path in root.rglob('Deformation_*.json'):
        if path.is_symlink():
            issues.append(dict(status='LINKED_DEFORMATION_REFUSED',file=str(path)))
            continue
        try:
            item=json.loads(path.read_text(encoding='utf-8-sig'))
            if not isinstance(item,dict):
                raise ValueError('Deformation document must be a JSON object')
            state=item.get('limit_state','')
            if state not in ('ULS','SLS'):continue
            nodes=item.get('nodes',{})
            displacements=item.get('displacements',{})
            if not isinstance(nodes,dict) or not isinstance(displacements,dict):
                raise ValueError('Deformation nodes/displacements must be objects')
            levels={}
            for tag,xyz in nodes.items():
                u=displacements.get(str(tag),[])
                if len(u)<2:continue
                z=float(xyz[2])
                components=[float(u[idx]) for idx in (0,1)]
                if not all(math.isfinite(v) for v in (z,*components)):
                    raise ValueError('Nonfinite deformation elevation/displacement')
                z=round(z,7)
                for idx,axis in enumerate(('X','Y')):
                    levels[z,axis]=max(levels.get((z,axis),0.),abs(components[idx]))
            for (z,axis),value in levels.items():
                deflections.append(dict(file=str(path),case=path.stem,
                    limit_state=state,storey=z,axis=axis,displacement_m=value,
                    scope='Maximum absolute saved nodal component at elevation (m); CQC envelopes are non-concurrent; no force-only scale applied'))
        except (OSError,ValueError,KeyError,TypeError,IndexError,OverflowError) as exc:
            issues.append(dict(status='INVALID_DEFORMATION_RESULT',file=str(path),error=str(exc)))
    coverage=[]
    for case in combinations(nonparallel=True):
        for method in ('ESM','MRSM','LTH'):
            coverage.append(dict(case=case['case'],limit_state=case['limit_state'],method=method,factors=json.dumps(case['factors']),status='REQUIRES CASE-SPECIFIC RESULT / IDENTITY REVIEW',note='Existing similar state/direction files do not prove this full combination was solved; CQC envelopes cannot be treated as concurrent signed actions.'))
    distinct_deflections={}
    for item in deflections:
        key=(item.get('file'),item.get('case'),item.get('storey'),
             item.get('axis'),item.get('displacement_m'))
        distinct_deflections.setdefault(key,item)
    deflections=list(distinct_deflections.values())
    from components.validation.saved_case_identity import (
        current_export_model_sha,identity_screen)
    selected_model_sha=current_export_model_sha(export_root)
    rows,drift_source_issues=identity_screen(
        rows,expected_model_sha=selected_model_sha)
    deflections,deflection_source_issues=identity_screen(
        deflections,expected_model_sha=selected_model_sha)
    issues.extend(drift_source_issues)
    issues.extend(deflection_source_issues)
    # Search results may reference different model configurations. A scan is
    # not authority to blend them into a validated ULS/SLS design envelope.
    issues.append(dict(status='SOURCE_IDENTITIES_REQUIRE_REVIEW',
                       reason='Result locations alone do not verify model SHA, loading, support case or ULS/SLS compatibility. Do not combine unlike source cases.'))
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
                selected_serialized_model_sha256=selected_model_sha,
                source_mismatch_excluded_count=len(drift_source_issues)+len(deflection_source_issues),
                searched_paths=[str(p) for p in roots],
                preload_profiles=profiles,combination_coverage=coverage)


def export(folder):
    from openpyxl import Workbook
    from components.inputs.output_layout import export_root_for
    folder=Path(folder)
    result=collect(folder)
    # Derived review, not a source model or a seismic solver case. Publish in
    # one diagnostics module regardless of whether launched from export or case.
    out=export_root_for(folder)/'09_SOFTWARE_DIAGNOSTICS'/'CASE_REVIEW_V142'
    # A linked diagnostics folder must not redirect private engineering
    # evidence outside the selected export root.
    if out.parent.is_symlink() or out.is_symlink():
        raise ValueError('Refusing linked case-review output directory')
    out.mkdir(parents=True,exist_ok=True)
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
    from components.inputs.output_contract import style_workbook, atomic_json
    style_workbook(wb)
    # Preserve the historical GUI workbook name but publish it atomically,
    # so a failed save cannot replace a previously usable report with a
    # truncated XLSX. The JSON writer already uses an atomic replacement.
    fd,temp_name=tempfile.mkstemp(prefix='.case_review_',suffix='.xlsx',dir=out)
    os.close(fd)
    staged=Path(temp_name)
    try:
        wb.save(staged)
        os.replace(staged,out/'All_Case_Review_V142.xlsx')
    finally:
        staged.unlink(missing_ok=True)
    atomic_json(out/'All_Case_Review_V142.json',result)
    return result,out


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
                axes[0,col].axvline(drift_limit_ratio(state),color='red',ls='--');axes[0,col].set(title=state+' saved drift',xlabel='Design drift ratio',ylabel='Storey')
                grouped={}
                for row in result['deflection']:
                    if row['limit_state']==state:grouped.setdefault(row['case']+' '+row.get('axis',''),[]).append(row)
                for case,items in grouped.items():
                    valid=[r for r in items if str(r['storey']).replace('.','',1).isdigit()];valid.sort(key=lambda r:float(r['storey']))
                    if valid:axes[1,col].plot([abs(r['displacement_m'])*1000 for r in valid],[float(r['storey']) for r in valid],label=case)
                axes[1,col].set(title=state+' saved deflection (case envelope)',xlabel='Absolute displacement (mm)',ylabel='Storey / elevation (see source workbook)')
            for ax in axes.flat:ax.grid(alpha=.25)
            embed_figures(body,[('ULS / SLS saved responses',fig)])
            if not result['drift'] and not result['deflection']:
                fig.suptitle('NO SAVED SEISMIC RESPONSE — NOT ZERO DRIFT; CHECK CASE RESULTS AND IDENTITY',
                             color='#a13c23',fontsize=11)
            fig.savefig(out/'Drift_Deflection_Comparison_V142.png',dpi=150)
            text.set(str(len(result['drift']))+' saved drift rows; '+str(len(result['deflection']))+
                     ' saved deflection rows. '+('NO VERIFIED RESPONSE: open Read errors worksheet and check analysis source paths. ' if not result['drift'] and not result['deflection'] else '')+
                     'Full combination coverage remains subject to explicit case/identity verification. Workbook: '+str(out/'All_Case_Review_V142.xlsx'))
        except Exception as exc:messagebox.showerror('Case review',str(exc),parent=win)
    ttk.Button(controls,text='Refresh / export comparison',command=refresh).pack(side='left');refresh();return win

"""Distinct library, device guidance and persisted analysis viewers."""

__release__ = '134'
from pathlib import Path
import json,csv,tkinter as tk
from tkinter import ttk,messagebox,filedialog

def library_window(parent,folder):
    """View and export identical, live model-scoped source/material tables."""
    from components.sections.library_excel import (
        library_tables, export_material_section_library,
    )
    tables = library_tables(folder)
    win=tk.Toplevel(parent);win.title('OpenSees material and section library');win.geometry('1200x720')
    toolbar=ttk.Frame(win,padding=(6,5))
    toolbar.pack(fill='x')
    status=tk.StringVar(value='Source parameters and uncalibrated research templates — not approval for NLTHA.')
    def excel_export():
        try:
            import os
            path=export_material_section_library(folder,tables=library_tables(folder))
            status.set('FINISHED | Excel workbook created: '+path)
            try:os.startfile(path)
            except (AttributeError,OSError):
                messagebox.showinfo('Material + section Excel workbook','Saved workbook:\n'+path,parent=win)
        except Exception as exc:
            status.set('BLOCKED | Workbook not exported: '+str(exc))
            messagebox.showerror('Material + section Excel export',str(exc),parent=win)
    ttk.Button(toolbar,text='Export / open complete Excel library',command=excel_export).pack(side='left',padx=3)
    ttk.Label(toolbar,text='All four tabs • source units • citations • validation flags • timestamped snapshot').pack(side='left',padx=8)
    tabs=ttk.Notebook(win);tabs.pack(fill='both',expand=True)
    for title,rows in tables:
        frame=ttk.Frame(tabs);tabs.add(frame,text=title)
        keys=list(dict.fromkeys(k for r in rows for k in r))
        tree=ttk.Treeview(frame,columns=keys,show='headings')
        for key in keys:tree.heading(key,text=key);tree.column(key,width=210)
        for row in rows:tree.insert('','end',values=[str(row.get(k,'')) for k in keys])
        sy=ttk.Scrollbar(frame,command=tree.yview);sy.pack(side='right',fill='y');tree.configure(yscrollcommand=sy.set)
        sx=ttk.Scrollbar(frame,orient='horizontal',command=tree.xview);sx.pack(side='bottom',fill='x');tree.configure(xscrollcommand=sx.set)
        tree.pack(fill='both',expand=True)
        detail=tk.Text(frame,height=7,wrap='word');detail.pack(fill='x')
        def show_detail(event,tree=tree,detail=detail,keys=keys):
            selected=tree.selection()
            if not selected:return
            detail.delete('1.0','end')
            detail.insert('end','\\n'.join(k+': '+str(v) for k,v in zip(keys,tree.item(selected[0],'values'))))
        tree.bind('<<TreeviewSelect>>',show_detail)
        def open_source(tree=tree,keys=keys):
            import re,webbrowser
            selected=tree.selection()
            if not selected:return
            values=dict(zip(keys,tree.item(selected[0],'values')))
            match=re.search(r'https?://[^\\s|;]+',str(values.get('source','')))
            if match:webbrowser.open(match.group(0))
            elif Path(str(values.get('source',''))).is_file():__import__('os').startfile(str(values['source']))
        ttk.Button(frame,text='Open selected source',command=open_source).pack(anchor='w')
    ttk.Label(win,textvariable=status).pack(anchor='w')
    return win

def device_guide(parent,folder):
    win=tk.Toplevel(parent);win.title('FVD / BRB replacement guide');win.geometry('950x650')
    text=tk.Text(win,wrap='word',font=('Segoe UI',11));text.pack(fill='both',expand=True)
    text.insert('end',"""FVD / BRB brace replacement workflow

1. Open Section mapping and filter BRACE. Expand the source property to inspect individual ETABS objects and solver segments.
2. Keep ordinary members as KEEP_SOURCE_ELASTIC or the reviewed SHS target. Assign FVD_MAXWELL or BRB_STEEL02 only to the selected physical device locations.
3. Supply project parameters in kN-m-s and a traceable test/manufacturer calibration citation. FVD needs finite spring K, Cd and alpha. BRB needs calibrated core area, Fy, E0, hardening and cyclic parameters.
4. Review brace/device self-weight, seismic mass and connection load path. A segmented brace needs exact solver-segment selection. Do not replace several segments with independent devices unless the physical assembly warrants it.
5. Save inactive candidates first. Review the Excel Device selections sheet. Activate only for a calibrated nonlinear scenario; active devices cannot run in the elastic baseline.

The library's published damper example is reference-only. It does not calibrate this building. Separate the elastic baseline validation from nonlinear device validation.

The mapping screen edits assignments; the material library shows values and citations; this guide explains the workflow.
""")
    text.configure(state='disabled')
    def mapping():
        from OpenSees_Mapping_GUI_V125 import launch
        gui=launch(parent,folder);gui.category.set('BRACE')
    ttk.Button(win,text='Open brace assignments',command=mapping).pack(side='left',padx=8,pady=8)
    ttk.Button(win,text='Open device library and citations',command=lambda:library_window(parent,folder)).pack(side='left')
    return win

def modal_classification(row):
    scores=[float(row.get(k,0.) or 0.) for k in ('UX_participation_percent','UY_participation_percent','RZ_participation_percent')]
    order=sorted(range(3),key=lambda i:scores[i],reverse=True)
    if scores[order[0]]<1.:return 'Other / low horizontal participation'
    label=['Translation X','Translation Y','Rotation Z'][order[0]]
    return ('Mixed ' if scores[order[1]]>=.5*scores[order[0]] else '')+label



def saved_modal_result(folder, state):
    """[REF docs/source/components/ui/results.py.md]
    Locate a real saved modal JSON in canonical or historical directories.

    The selected ETABS export owns all candidates. Case/state mismatches,
    snapshot copies and unrecognised result structures are excluded.
    This is a viewer locator, not model-source equivalence certification.
    """
    from components.inputs.output_layout import result_roots
    state=str(state).strip().upper()
    if state not in ("ULS","SLS"):
        raise ValueError("Modal result requires explicit ULS or SLS")
    candidates=[]
    for root in result_roots(folder,stages=("MODAL",)):
        for p in root.rglob("NBC105_Modal_V111.json"):
            if any(x.casefold() in {"review_snapshots","organized_results",
                    "zip_exports","seismic_review_packages"} for x in p.parts):
                continue
            inferred=next((x[-3:].upper() for x in p.parts if x.upper() in
                           ("MODAL_ULS","MODAL_SLS")),None)
            try:
                d=json.loads(p.read_text(encoding="utf-8-sig"))
            except (ValueError,OSError):
                continue
            actual=str(d.get("limit_state",inferred or "")).upper()
            if actual!=state or not isinstance(d.get("rows"),list):
                continue
            candidates.append(p)
        for p in root.rglob(f"NBC105_Modal_{state}_V127.json"):
            if any(x.casefold() in {"review_snapshots","organized_results",
                    "zip_exports","seismic_review_packages"} for x in p.parts):
                continue
            try:
                d=json.loads(p.read_text(encoding="utf-8-sig"))
            except (ValueError,OSError):
                continue
            if str(d.get("limit_state",state)).upper()==state and isinstance(d.get("rows"),list):
                candidates.append(p)
    if not candidates:
        return None
    candidates=sorted(set(candidates),key=lambda p:(p.stat().st_mtime_ns,str(p)),reverse=True)
    return candidates[0]


def modal_results(parent,folder):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
    folder=Path(folder)
    from components.inputs.project_workbooks import analysis_output_folder
    export_folder=next((path for path in (folder,*folder.parents)
                        if (path/'OpenSees_Element_Connectivity.json').is_file()),None)
    def modal_path(state):
        return saved_modal_result(export_folder or folder,state)
    win=tk.Toplevel(parent);win.title('Modal audit results — ULS / SLS');win.geometry('1160x760')
    ttk.Button(win,text='Open ULS / SLS comparison chart',command=lambda:modal_comparison(win,folder)).pack(anchor='w')
    tabs=ttk.Notebook(win);tabs.pack(fill='both',expand=True)
    compare_frame=ttk.Frame(tabs);tabs.add(compare_frame,text='ULS / SLS comparison')
    compare_fig=Figure(figsize=(11,5),layout='constrained');compare_axes=compare_fig.subplots(1,2)
    for state,style in [('ULS','-'),('SLS','--')]:
        reference=modal_path(state)
        if reference is not None and reference.is_file():
            records=json.loads(reference.read_text(encoding='utf-8-sig')).get('rows',[]);modes=[r['mode'] for r in records]
            compare_axes[0].plot(modes,[r['period_s'] for r in records],ls=style,label=state)
            for key,label,color in [('UX_cumulative_percent','X','tab:blue'),('UY_cumulative_percent','Y','tab:orange'),('RZ_cumulative_percent','Rz','tab:green')]:compare_axes[1].plot(modes,[r.get(key,0) or 0 for r in records],ls=style,color=color,label=state+' '+label)
    compare_axes[0].set(title='ULS / SLS eigenperiod comparison',xlabel='Mode',ylabel='Period (s)');compare_axes[1].set(title='ULS / SLS cumulative participation',xlabel='Mode',ylabel='Participation (%)',ylim=(0,105));compare_axes[1].axhline(90,color='black',ls=':')
    for ax in compare_axes:
        ax.grid(alpha=.25)
        if ax.lines:ax.legend()
    compare_chart=FigureCanvasTkAgg(compare_fig,master=compare_frame);compare_chart.get_tk_widget().pack(fill='both',expand=True);NavigationToolbar2Tk(compare_chart,compare_frame)
    ttk.Button(compare_frame,text='Export comparison PNG',command=lambda:compare_fig.savefig(folder/'Modal_Comparison_V146.png',dpi=180)).pack(anchor='w')
    for state in ('ULS','SLS'):
        frame=ttk.Frame(tabs);tabs.add(frame,text=state+' modal audit')
        path=modal_path(state)
        if not path.is_file():ttk.Label(frame,text=f'No saved {state} modal result. Run this stiffness case to populate the tab.').pack();continue
        result=json.loads(path.read_text(encoding='utf-8-sig'));rows=result['rows']
        ttk.Label(frame,text=f'{state} | '+str(path)).pack(anchor='w')
        fig=Figure(figsize=(10,4),layout='constrained');axes=fig.subplots(1,2);x=[r['mode'] for r in rows]
        axes[0].plot(x,[r['period_s'] for r in rows],'o-');axes[0].set(title=f'{state} eigenperiods',xlabel='Mode',ylabel='Period (s)')
        for key,label in [('UX_cumulative_percent','X'),('UY_cumulative_percent','Y'),('RZ_cumulative_percent','Rotation Z')]:axes[1].plot(x,[r.get(key,0.) or 0. for r in rows],'o-',label=label)
        axes[1].axhline(90,color='black',ls='--',label='90%');axes[1].set(title=f'{state} cumulative mass',xlabel='Mode',ylabel='Participation (%)',ylim=(0,105));axes[1].legend()
        for ax in axes:ax.grid(alpha=.25)
        chart=FigureCanvasTkAgg(fig,master=frame);chart.get_tk_widget().pack(fill='both',expand=True);NavigationToolbar2Tk(chart,frame)
        grid=ttk.Frame(frame);grid.pack(fill='x')
        table=ttk.Treeview(grid,columns=('mode','period','frequency','classification','UX mode %','UY mode %','RZ mode %','X cumulative','Y cumulative'),show='headings',height=6)
        for k in table['columns']:table.heading(k,text=k);table.column(k,width=155,stretch=False)
        for r in rows:table.insert('','end',values=(r['mode'],r['period_s'],r.get('frequency_Hz',''),r.get('classification_candidate') or modal_classification(r),r.get('UX_participation_percent'),r.get('UY_participation_percent'),r.get('RZ_participation_percent'),r['UX_cumulative_percent'],r['UY_cumulative_percent']))
        sy=ttk.Scrollbar(grid,command=table.yview);sx=ttk.Scrollbar(grid,orient='horizontal',command=table.xview);table.configure(yscrollcommand=sy.set,xscrollcommand=sx.set);grid.columnconfigure(0,weight=1);grid.rowconfigure(0,weight=1);table.grid(row=0,column=0,sticky='nsew');sy.grid(row=0,column=1,sticky='ns');sx.grid(row=1,column=0,sticky='ew')
    return win

def history_viewer(parent,folder):
    from OpenSees_History_Inspection_V133 import launch
    return launch(parent,folder)


def esm_comparison(parent,folder):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
    win=tk.Toplevel(parent);win.title('ESM comparison — common X/Y axes');win.geometry('1150x730')
    actions=ttk.Frame(win);actions.pack(fill='x')
    ttk.Button(actions,text='Side-by-side ULS / SLS force profiles',command=lambda:esm_side_by_side(win,folder)).pack(side='left')
    tabs=ttk.Notebook(win);tabs.pack(fill='both',expand=True)
    for limit in ('ULS','SLS'):
        frame=ttk.Frame(tabs);tabs.add(frame,text=limit+' X / Y comparison')
        fig=Figure(figsize=(10,5),layout='constrained');axes=fig.subplots(1,2);summary=[]
        for axis in ('X','Y'):
            path=Path(folder)/f'NBC105_ESM_Storey_Forces_{limit}_{axis}+_E+_V111.csv'
            if not path.is_file():continue
            with path.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
            heights=[float(r['height_m']) for r in rows]
            axes[0].plot([float(r['floor_force_kN']) for r in rows],heights,'o-',label=axis)
            axes[1].plot([float(r['storey_shear_kN']) for r in rows],heights,label=axis)
            calc=Path(folder)/f'NBC105_ESM_Calculation_{limit}_{axis}+_E+_V111.json'
            if calc.is_file():
                r=json.loads(calc.read_text(encoding='utf-8-sig'));summary.append(f"{axis}: T={r['period_s']:.6g} s; V={r['base_shear_kN']:.3f} kN; k={r['period_exponent_k']:.5g}")
        if not any(ax.lines for ax in axes):
            heading='No saved '+limit+' equivalent-static cases'
            ttk.Label(frame,text=heading,font=('Segoe UI',15,'bold')).pack(anchor='w',padx=20,pady=20)
            explanation=('This tab displays equivalent-static load calculations, not modal eigenanalysis or time-history results. '
                         'A successful ULS modal run does not create ULS ESM floor forces. '
                         'For the supplied 95 m building and periods above 0.5 s, ULS ESM is design-ineligible; V132 can calculate explicitly marked ULS comparison cases under NBC 105:2025 section 3.2.1. '
                         'Use the completed Modal_ULS results for modal diagnostics, and a permitted dynamic method for ULS actions. '
                         'If another model is selected, inspect its own eligibility report. Run Calculate + export to populate comparison floor forces.') if limit=='ULS' else 'Calculate SLS X/Y cases first, or select their saved output folder.'
            ttk.Label(frame,text=explanation,wraplength=1000,justify='left').pack(anchor='w',padx=20,pady=10)
            ttk.Button(frame,text='Open separate SLS / ULS modal results',command=lambda:modal_results(parent,folder)).pack(anchor='w',padx=20)
            continue
        ttk.Label(frame,text=' | '.join(summary)).pack(anchor='w')
        for ax,label in zip(axes,('Floor force (kN)','Storey shear (kN)')):
            ax.set(xlabel=label,ylabel='Height (m)',xlim=(0,None));ax.grid(alpha=.25)
            if ax.lines:ax.legend()
        chart=FigureCanvasTkAgg(fig,master=frame);chart.get_tk_widget().pack(fill='both',expand=True);NavigationToolbar2Tk(chart,frame)
    return win


def summary_figure(result):
    from matplotlib.figure import Figure
    fig=Figure(figsize=(11,7),layout='constrained');axes=fig.subplots(2,2)
    rows=result['records'];pairs=list(dict.fromkeys(r['pair_id'] for r in rows));labels=['P'+str(pairs.index(r['pair_id'])+1).zfill(2)+' '+r.get('orientation',r['case'].replace(r['pair_id']+'_','')) for r in rows]
    fig.suptitle(__import__('textwrap').fill(str(result.get('limit_state_context',''))+' | '+result.get('analysis','Time history')+' | '+ ' ; '.join('P'+str(i+1).zfill(2)+'='+pair for i,pair in enumerate(pairs)),110),fontsize=10)
    for i,axis in enumerate(('X','Y')):
        axes[i,0].bar(labels,[r['peak_roof_U'+axis+'_m']*1000 for r in rows],color='#315b8a')
        axes[i,0].set(title='Peak relative roof displacement '+axis,ylabel='mm')
        axes[i,1].bar(labels,[r['peak_story_drift_'+axis] for r in rows],color='#bb4a55')
        axes[i,1].set(title='Peak interstorey drift '+axis,ylabel='ratio')
        for ax in axes[i]:ax.grid(axis='y',alpha=.25)
    fig.suptitle(str(result.get('limit_state_context',''))+' | '+result.get('assessment_scope','Saved run summary'))
    return fig

def history_summary(parent,folder):
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
    folder=Path(folder);paths=[p for p in folder.glob('*Time_History_Summary*.json') if not p.name.endswith('.processing.json')]
    path=paths[0] if len(paths)==1 else filedialog.askopenfilename(parent=parent,initialdir=str(folder),title='Select completed run summary',filetypes=[('Run summary','*Summary*.json')])
    if not path:return
    try:
        result=json.loads(Path(path).read_text(encoding='utf-8-sig'))
        win=tk.Toplevel(parent);win.title('Time-history summary — both axes and orientations');win.geometry('1150x800')
        ttk.Label(win,text=str(path)).pack(anchor='w')
        fig=summary_figure(result);chart=FigureCanvasTkAgg(fig,master=win);chart.get_tk_widget().pack(fill='both',expand=True);NavigationToolbar2Tk(chart,win)
    except Exception as exc:messagebox.showerror('Run summary',str(exc),parent=parent)


def esm_side_by_side(parent,folder):
    """Matching case signs/eccentricity, common scales and interactive curves."""
    from matplotlib.figure import Figure
    from OpenSees_Research_UI_V123 import embed_figures
    win=tk.Toplevel(parent);win.title('ULS / SLS side-by-side force profiles');win.geometry('1250x850')
    from OpenSees_Case_Review_V142 import launch as response_comparison
    ttk.Button(win,text='Compare saved drift + deflection (ESM / MRSM / histories)',command=lambda:response_comparison(win,Path(folder).parent if Path(folder).name=='OpenSees_Analysis_Results' else folder)).pack(anchor='w')
    controls=ttk.Frame(win);controls.pack(fill='x');polarity=tk.StringVar(value='+');ecc=tk.StringVar(value='0')
    for label,var,choices in [('Force sign',polarity,['+','-']),('Eccentricity',ecc,['0','+','-'])]:
        ttk.Label(controls,text=label).pack(side='left');ttk.Combobox(controls,textvariable=var,values=choices,state='readonly',width=8).pack(side='left')
    status=tk.StringVar();ttk.Label(win,textvariable=status,wraplength=1180).pack(anchor='w');body=ttk.Frame(win);body.pack(fill='both',expand=True)
    def refresh():
        fig=Figure(figsize=(12,7),layout='constrained');axes=fig.subplots(2,2,sharey=True,sharex='row');missing=[]
        for col,state in enumerate(('ULS','SLS')):
            for axis,color in [('X','#2563eb'),('Y','#b91c1c')]:
                name=f'NBC105_ESM_Storey_Forces_{state}_{axis}{polarity.get()}_E{ecc.get()}_V111.csv';path=Path(folder)/name
                if not path.is_file():missing.append(state+' '+axis);continue
                with path.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
                z=[float(r['height_m']) for r in rows]
                for row,key in enumerate(('floor_force_kN','storey_shear_kN')):axes[row,col].plot([float(r[key]) for r in rows],z,label=axis,color=color)
            axes[0,col].set_title(state+' | signed force '+polarity.get()+' | e='+ecc.get())
            for row,label in enumerate(('Floor force (kN)','Storey shear (kN)')):
                ax=axes[row,col];ax.set(xlabel=label,ylabel='Height (m)',xlim=(0,None));ax.grid(alpha=.25)
                if ax.lines:ax.legend()
                else:ax.text(.5,.5,'No matching saved cases',transform=ax.transAxes,ha='center')
        status.set('Same horizontal scales in each row. ULS ESM may be a comparison-only reference; inspect its eligibility report. '+('Missing: '+', '.join(missing) if missing else 'Both states loaded.'))
        embed_figures(body,[('ULS left / SLS right',fig)])
    ttk.Button(controls,text='Refresh comparison',command=refresh).pack(side='left');refresh();return win


def modal_comparison(parent,folder):
    from matplotlib.figure import Figure
    from OpenSees_Research_UI_V123 import embed_figures
    import tkinter as tk
    win=tk.Toplevel(parent);win.title('ULS then SLS modal comparison');win.geometry('1200x750')
    fig=Figure(figsize=(12,7),layout='constrained');axes=fig.subplots(2,2,sharex='row')
    for col,state in enumerate(('ULS','SLS')):
        path=saved_modal_result(folder,state)
        if path is None:
            axes[0,col].text(.1,.5,'No saved '+state+' modal result — NOT ZERO RESPONSE',
                             transform=axes[0,col].transAxes)
            continue
        rows=json.loads(path.read_text(encoding='utf-8-sig'))['rows'];x=[r['mode'] for r in rows]
        axes[0,col].plot(x,[r['period_s'] for r in rows],'o-');axes[0,col].set(title=state+' eigenperiods',ylabel='Period (s)')
        for key,label in [('UX_cumulative_percent','X'),('UY_cumulative_percent','Y'),('RZ_cumulative_percent','Rz')]:axes[1,col].plot(x,[r.get(key,0) or 0 for r in rows],label=label)
        axes[1,col].set(xlabel='Mode',ylabel='Cumulative participation (%)',ylim=(0,105));axes[1,col].axhline(90,color='black',ls='--');axes[1,col].legend()
    for row in axes:
        for ax in row:ax.grid(alpha=.25)
    embed_figures(win,[('ULS left / SLS right',fig)])
    from components.inputs.output_layout import export_root_for
    output=export_root_for(folder)/'04_MODAL'/'REVIEW_SNAPSHOTS'
    output.mkdir(parents=True,exist_ok=True)
    fig.savefig(output/'Modal_ULS_SLS_Comparison_V143.png',dpi=180)
    return win

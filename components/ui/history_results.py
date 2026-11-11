"""Open completed history graphics, Excel and unit audit without rerunning analysis."""
from pathlib import Path
import json,csv


def launch(parent,folder,summary_path=None):
    import tkinter as tk
    from tkinter import ttk,messagebox
    from OpenSees_Results_UI_V127 import summary_figure
    from OpenSees_Research_UI_V123 import embed_figures
    folder=Path(folder);paths=sorted((p for p in folder.rglob('*Time_History_Summary*.json') if not p.name.endswith('.processing.json')),key=lambda p:p.stat().st_mtime,reverse=True)
    win=tk.Toplevel(parent);win.title('Completed history results — charts, Excel and acceleration units');win.geometry('1250x850');choice=tk.StringVar();bar=ttk.Frame(win);bar.pack(fill='x');box=ttk.Combobox(bar,textvariable=choice,values=[str(p) for p in paths],state='readonly',width=110);box.pack(fill='x',expand=True)
    note=tk.StringVar();ttk.Label(win,textvariable=note,wraplength=1170).pack(anchor='w');buttons=ttk.Frame(win);buttons.pack(fill='x');units=ttk.Treeview(win,columns=['Record/component','Input unit','Motion scale','Unit conversion','Total Path factor','Applied PGA (model units)'],show='headings',height=3)
    for key in units['columns']:units.heading(key,text=key);units.column(key,width=190,stretch=True)
    units.pack(fill='x')
    # Matplotlib figures can exceed the window height. Keep a real scrolling
    # viewport (and explicit scroll buttons for touchpads/remote desktops).
    view=ttk.Frame(win);view.pack(fill='both',expand=True)
    canvas=tk.Canvas(view,highlightthickness=0)
    ybar=ttk.Scrollbar(view,orient='vertical',command=canvas.yview)
    xbar=ttk.Scrollbar(view,orient='horizontal',command=canvas.xview)
    canvas.configure(yscrollcommand=ybar.set,xscrollcommand=xbar.set)
    view.grid_rowconfigure(0,weight=1);view.grid_columnconfigure(0,weight=1)
    canvas.grid(row=0,column=0,sticky='nsew')
    ybar.grid(row=0,column=1,sticky='ns');xbar.grid(row=1,column=0,sticky='ew')
    body=ttk.Frame(canvas);canvas.create_window((0,0),window=body,anchor='nw',tags='body')
    body.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
    canvas.bind('<Configure>',lambda e:canvas.itemconfigure('body',width=max(e.width,body.winfo_reqwidth())))
    canvas.bind('<MouseWheel>',lambda e:canvas.yview_scroll(-int(e.delta/120) if e.delta else 0,'units'))
    canvas.bind('<Button-4>',lambda e:canvas.yview_scroll(-1,'units'))
    canvas.bind('<Button-5>',lambda e:canvas.yview_scroll(1,'units'))
    def load(*unused):
        if not choice.get():return
        path=Path(choice.get());result=json.loads(path.read_text(encoding='utf-8-sig'));note.set(str(result.get('limit_state_context',''))+' | '+result.get('directional_scope','')+' | Ux/Uy in metres. Record scale is dimensionless; g-to-SI conversion is separate and applied once in Path TimeSeries. Saved graphics can be inspected without recalculation.')
        units.delete(*units.get_children());audit=next(path.parent.glob('*Input_Record_Audit*.csv'),None)
        if audit:
            with audit.open(encoding='utf-8-sig',newline='') as stream:
                for r in csv.DictReader(stream):
                    scale=float(r['scale_factor']);factor=float(r['path_acceleration_factor_to_model_units']);units.insert('','end',values=[r['record_or_pair_id']+' '+r['component'],r['source_units'],scale,f'{factor/scale:.7g} '+r['model_acceleration_units']+'/input',f'{factor:.7g}',f"{float(r['peak_abs_acceleration_input'])*factor:.7g} {r['model_acceleration_units']}"])
        for widget in body.winfo_children():widget.destroy()
        embed_figures(body,[('X/Y displacement and drift',summary_figure(result))])
        body.update_idletasks();canvas.configure(scrollregion=canvas.bbox('all'));canvas.yview_moveto(0)
        win._history_summary=result
    def open_excel():
        path=Path(choice.get()).parent if choice.get() else folder;files=list(path.glob('*Time_History*.xlsx'))
        if files:__import__('os').startfile(str(files[0]))
        else:messagebox.showinfo('Excel','No saved workbook found in '+str(path),parent=win)
    ttk.Button(buttons,text='Open saved Excel',command=open_excel).pack(side='left');ttk.Button(buttons,text='Full input / response data and playback',command=lambda:__import__('OpenSees_History_Inspection_V133').launch(win,Path(choice.get()).parent if choice.get() else folder)).pack(side='left')
    ttk.Button(buttons,text='Scroll ▲',command=lambda:canvas.yview_scroll(-4,'units')).pack(side='left',padx=(8,0))
    ttk.Button(buttons,text='Scroll ▼',command=lambda:canvas.yview_scroll(4,'units')).pack(side='left')
    from components.ui.history_review_tools import export_review_zip_dialog
    ttk.Button(buttons,text='Export selected run ZIP',
               command=lambda:export_review_zip_dialog(win,Path(choice.get()).parent if choice.get() else folder,
                                                       'nonlinear' if 'Nonlinear' in Path(choice.get()).name else 'linear')).pack(side='left',padx=8)
    box.bind('<<ComboboxSelected>>',load)
    if summary_path:choice.set(str(summary_path));load()
    elif paths:choice.set(str(paths[0]));load()
    else:note.set('No completed history summary under this output folder. Choose the correct output folder or wait for completion.')
    return win

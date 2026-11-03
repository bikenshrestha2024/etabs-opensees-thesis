"""Additional native materials in the existing V149 Tk visual workbench.

Four extra panels use the established eight-model catalog/parameter-study engine.
All simulations are isolated subprocesses, never the active building domain.
References: PEER 2015/12, Kolozvari et al. (2023) doi:10.1016/j.engstruct.2023.116700,
OpenSees Concrete02/CM, SteelMPF, FSAM and ViscousDamper manuals.
"""
from __future__ import annotations
import csv
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import webbrowser

ROOT=Path(__file__).resolve().parents[2]
ALL_MODELS=("Concrete01","Concrete02","ConcreteCM","Steel02","SteelMPF","FVD","BRB","SFI_MVLEM_3D")
EXTRA_MODELS=("Concrete02","ConcreteCM","SteelMPF","SFI_MVLEM_3D")

def catalog_for(model, entries=None):
    from components.validation.material_catalog import profiles
    return [x for x in (profiles() if entries is None else entries) if x.get("model")==model]

def source_card(model,entry=None):
    from components.validation.material_catalog import read_profile
    from components.validation.parameter_studies import card,check
    data=read_profile(entry) if entry else card(model)
    if data.get("model")!=model:raise ValueError("Card model mismatch")
    check(data)
    return data

def validate_measured_csv(path):
    import math
    with Path(path).open(newline="",encoding="utf-8-sig") as stream:
        reader=csv.DictReader(stream)
        if not reader.fieldnames or not {"x","y"}.issubset(reader.fieldnames):
            raise ValueError("Measured reference CSV needs x,y columns")
        rows=list(reader)
    if len(rows)<3:raise ValueError("At least 3 ordered measured rows required")
    for i,r in enumerate(rows):
        if any(not math.isfinite(float(r[k])) for k in ("x","y")):
            raise ValueError("Nonfinite measured entry at row "+str(i))
    return len(rows)

def add_material_tab(book,frames,win,model):
    import tkinter as tk
    from tkinter import ttk,filedialog,messagebox
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
    from components.validation.material_catalog import FORMULAS,commands
    from components.validation.visual_workbench import playback
    name="E-SFI / wall materials" if model=="SFI_MVLEM_3D" else model
    frame=ttk.Frame(book)
    book.add(frame,text=name)
    frames[model]=frame
    items=catalog_for(model)
    labels=["Illustrative starting parameters"]+[x["id"]+" | "+x.get("status","UNVERIFIED") for x in items]
    selected=tk.StringVar(value=labels[0])
    status=tk.StringVar(value="No component calculation performed")
    top=ttk.Frame(frame);top.pack(fill="x")
    ttk.Label(top,text="Research source:").pack(side="left")
    menu=ttk.Combobox(top,textvariable=selected,values=labels,state="readonly",width=55)
    menu.pack(side="left",fill="x",expand=True)
    ttk.Label(frame,textvariable=status,wraplength=1100).pack(fill="x")
    pane=ttk.Notebook(frame);pane.pack(fill="both",expand=True)
    graph=ttk.Frame(pane);detail=ttk.Frame(pane);logtab=ttk.Frame(pane)
    pane.add(graph,text="Native response plots")
    pane.add(detail,text="Source / parameters / citations")
    pane.add(logtab,text="Report / logs")
    fig=Figure(figsize=(10,6),layout="constrained")
    canvas=FigureCanvasTkAgg(fig,master=graph)
    canvas.get_tk_widget().pack(fill="both",expand=True)
    NavigationToolbar2Tk(canvas,graph)
    notes=tk.Text(detail,wrap="word")
    notes.pack(fill="both",expand=True)
    logs=tk.Text(logtab,wrap="none")
    logs.pack(fill="both",expand=True)
    state={"card":None,"path":None,"busy":False}
    def setcard(_event=None):
        try:
            idx=labels.index(selected.get())
            data=source_card(model,items[idx-1] if idx else None)
            state["card"]=data
            notes.delete("1.0","end")
            notes.insert("end","SOURCE CLASSIFICATION: "+str(data.get("parameter_basis",""))+
                "\nSOURCE: "+str(data.get("source",""))+
                "\nCITATION: "+str(data.get("citation",""))+
                "\nSPECIMEN: "+str(data.get("specimen_id",""))+
                "\n\nFORMULATION\n"+FORMULAS.get(model,"")+
                "\n\nNATIVE COMMANDS (kN/m/s where applicable)\n"+
                commands(data)+"\n\nCOMPLETE CARD\n"+json.dumps(data,indent=2))
            status.set("Selected "+model+"; NOT experimentally or project validated")
        except Exception as exc:
            status.set("CARD ERROR: "+str(exc))
    menu.bind("<<ComboboxSelected>>",setcard)
    def display(path):
        folder=Path(path)
        state["path"]=folder
        logs.delete("1.0","end")
        for entry in ("report.json","failure.json","run.log"):
            p=folder/entry
            if p.is_file():
                logs.insert("end","== "+entry+" ==\n"+
                            p.read_text(encoding="utf-8-sig",errors="replace")[-30000:]+"\n")
        fig.clear()
        a=fig.add_subplot(121);b=fig.add_subplot(122)
        f=folder/"response.csv"
        if not f.is_file():
            a.text(.1,.5,"Missing response.csv — inspect report/log")
            status.set("INCOMPLETE/FAILED: "+str(folder))
        else:
            with f.open(newline="",encoding="utf-8-sig") as fh:
                rows=list(csv.DictReader(fh))
            if not rows:raise ValueError("Empty response.csv")
            x=[float(r["x"]) for r in rows]
            y=[float(r["y"]) for r in rows]
            t=[float(r.get("time_s") or r.get("step",i)) for i,r in enumerate(rows)]
            physical=model=="SFI_MVLEM_3D"
            a.plot(x,y,label="Native")
            b.plot(t,y,label="Native")
            if "measured_y" in rows[0]:
                a.plot(x,[float(r["measured_y"]) for r in rows],ls="--",
                       label="Measured — same protocol")
            a.set(xlabel="Wall displacement (m)" if physical else "Strain",
                  ylabel="Force (kN)" if physical else "Stress (MPa)",
                  title=model+" cyclic response")
            b.set(xlabel="Time (s) / protocol step",title="Recorded numerical history")
            a.legend()
            for axis in (a,b):axis.grid(alpha=.25)
            status.set("Numerical study only | "+str(folder))
        canvas.draw_idle()
        pane.select(graph)
    def run_selected():
        if state["busy"]:return
        try:
            from components.validation.parameter_studies import check
            card=json.loads(json.dumps(state["card"]))
            check(card)
            stamp=datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            folder=ROOT/"Material_Parameter_Studies"/model/("Run_"+stamp)
            folder.mkdir(parents=True,exist_ok=False)
            filename=folder/"input.json"
            filename.write_text(json.dumps(card,indent=2),encoding="utf-8")
        except Exception as exc:
            messagebox.showerror("Native input",str(exc),parent=win)
            return
        state["busy"]=True
        status.set("RUNNING separate native "+model+" process")
        def worker():
            try:
                with (folder/"run.log").open("w",encoding="utf-8") as log:
                    process=subprocess.run(
                        [sys.executable,"-u","-m","components.validation.parameter_studies",
                         str(filename),str(folder)],cwd=ROOT,stdout=log,
                        stderr=subprocess.STDOUT,check=False,
                        creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
                def completed():
                    state["busy"]=False
                    try:display(folder)
                    except Exception as e:status.set("DISPLAY ERROR: "+str(e))
                    if process.returncode:
                        status.set("NATIVE FAILURE; inspect saved logs: "+str(folder))
                win.after(0,completed)
            except Exception as exc:
                error=str(exc)
                def fail():
                    state["busy"]=False
                    status.set("EXECUTION FAILURE: "+error)
                win.after(0,fail)
        threading.Thread(target=worker,daemon=True).start()
    def browse():
        folder=filedialog.askdirectory(parent=win,title="Choose "+model+" result directory")
        if folder:
            try:display(folder)
            except Exception as exc:messagebox.showerror("Result",str(exc),parent=win)
    def source():
        url=(state["card"] or {}).get("source")
        if isinstance(url,str) and url.startswith("https://"):webbrowser.open(url)
        else:messagebox.showinfo("Paper","Source URL unavailable",parent=win)
    def setup():
        from components.validation.parameter_gui import launch
        launch(win,initial_card=state["card"])
    def play():
        p=state["path"]
        if not p or not (p/"response.csv").exists():
            messagebox.showinfo("Playback","Run or open a saved case first",parent=win)
            return
        force=model=="SFI_MVLEM_3D"
        playback(win,p/"response.csv","Displacement (m)" if force else "Strain",
                 "Force (kN)" if force else "Stress (MPa)",model)
    ttk.Button(top,text="Run selected",command=run_selected).pack(side="left")
    actions=ttk.Frame(frame);actions.pack(fill="x")
    for label,fn in [
        ("Open saved result",browse),("Edit / measured data / fit",setup),
        ("Playback / GIF",play),("Official source",source)]:
        ttk.Button(actions,text=label,command=fn).pack(side="left")
    setcard()
    return state

def install_extra_tabs(book,frames,win,output,set_status):
    import tkinter as tk
    from tkinter import ttk,filedialog,messagebox
    panels={model:add_material_tab(book,frames,win,model) for model in EXTRA_MODELS}
    tools=ttk.Frame(book)
    book.add(tools,text="Full library / calibration")
    frames["Full library / calibration"]=tools
    ttk.Label(tools,text="Eight-component research suite: Concrete01 / Concrete02 / ConcreteCM / Steel02 / SteelMPF / FVD / BRB / SFI-MVLEM-3D.\nPaper inputs, numerical examples and project-verified parameters are NOT equivalent.",wraplength=1100).pack(fill="x",pady=15,padx=10)
    def open_catalog():
        from components.validation.material_catalog import launch
        launch(win)
    def open_setup():
        from components.validation.parameter_gui import launch
        launch(win)
    def open_results():
        from components.validation.research_results_gui import launch
        launch(win)
    def tool_process(cmd,where,title):
        folder=Path(where).resolve()
        folder.mkdir(parents=True,exist_ok=True)
        set_status(title+" — native process running")
        def work():
            try:
                with (folder/"Workbench_Tool.log").open("w",encoding="utf-8") as logfile:
                    p=subprocess.run(cmd,cwd=ROOT,stdout=logfile,
                        stderr=subprocess.STDOUT,check=False,
                        creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
                result="COMPLETED" if p.returncode==0 else "FAILED — inspect Workbench_Tool.log"
                win.after(0,lambda:set_status(title+" "+result+" | "+str(folder)))
            except Exception as e:
                msg=str(e)
                win.after(0,lambda:set_status("FAILED "+title+" "+msg))
        threading.Thread(target=work,daemon=True).start()
    def native_devices():
        folder=filedialog.askdirectory(parent=win,title="Select FVD/BRB native output folder")
        if folder:
            tool_process([sys.executable,str(ROOT/"29_NATIVE_DEVICE_BENCHMARK.py"),
                          "--output",folder],folder,"Native device recorder benchmark")
    def fit_fvd():
        src=filedialog.askopenfilename(parent=win,title="Measured FVD time-displacement-force CSV",filetypes=[("CSV","*.csv")])
        if not src:return
        folder=filedialog.askdirectory(parent=win,title="Calibration results folder")
        if folder:
            tool_process([sys.executable,str(ROOT/"30_CALIBRATE_FVD_FROM_TEST.py"),
                          src,"--output",folder],folder,"Measured FVD fit")
    for name,func in [
        ("Open every catalog material card",open_catalog),
        ("Edit and tune all eight material models",open_setup),
        ("Open eight-component saved results",open_results),
        ("Native FVD / BRB element recorder test",native_devices),
        ("Calibrate FVD against measured CSV",fit_fvd)]:
        ttk.Button(tools,text=name,command=func).pack(fill="x",padx=12,pady=4)
    return panels

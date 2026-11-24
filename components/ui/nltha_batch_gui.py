"""GUI for independent research NLTHA jobs using existing Requested_Config files."""
from pathlib import Path
import datetime
import json
import subprocess
import sys
import uuid

def launch(parent, model_folder):
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    from components.inputs.output_layout import owned_run_destination
    from components.nonlinear_time_history import batch_execution
    win=tk.Toplevel(parent)
    win.title("NLTHA research batch — independent processes")
    win.geometry("1000x580")
    ttk.Label(win,text="Select saved Requested_Config.json files (one per model/record/orientation job). "
        "Use separate XY/YX configurations if you want those orientations to run concurrently. "
        "Each process rebuilds its own domain; no engineering approval is implied.",
        wraplength=940).pack(anchor="w",padx=10,pady=8)
    selected=[]
    status=tk.StringVar(value="No configurations selected")
    workers=tk.StringVar(value="1")
    active={"proc":None,"output":None,"log":None,"closing":False}
    bar=ttk.Frame(win);bar.pack(fill="x",padx=10)
    def select():
        paths=filedialog.askopenfilenames(parent=win,title="Select saved NLTHA job configurations",
                                        filetypes=[("JSON","*.json")])
        if paths:
            selected[:]=paths
            status.set(str(len(selected))+" configurations selected")
    choose=ttk.Button(bar,text="Select configurations",command=select);choose.pack(side="left")
    ttk.Label(bar,text="Independent workers (RAM permitting):").pack(side="left",padx=8)
    selector=ttk.Combobox(bar,textvariable=workers,values=("1","2","3","4"),state="readonly",width=4)
    selector.pack(side="left")
    tree=ttk.Treeview(win,columns=("job","model","state","status"),show="headings",height=14)
    for key,title,width in (("job","Job",150),("model","Model / variant",320),
                            ("state","State / orientation",180),("status","Status",230)):
        tree.heading(key,text=title);tree.column(key,width=width)
    tree.pack(fill="both",expand=True,padx=10,pady=8)
    ttk.Label(win,textvariable=status,wraplength=940).pack(anchor="w",padx=10)
    def start():
        if active["proc"] is not None:return
        if not selected:
            messagebox.showwarning("Batch inputs","Select at least one saved configuration.",parent=win);return
        try:
            parent_dir=owned_run_destination(model_folder,"NLTHA","RESEARCH_BATCH")
            parent_dir.mkdir(parents=True,exist_ok=True)
            label=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+"_"+uuid.uuid4().hex[:8]
            dest=parent_dir/label
            plan=parent_dir/(label+"_Plan.json")
            plan.write_text(json.dumps({"jobs":selected},indent=2),encoding="utf-8")
            root=Path(batch_execution.__file__).resolve().parents[2]
            log=parent_dir/(label+"_Scheduler.log")
            # Validate inputs before launching; scheduler repeats the same checks.
            batch_execution.prepare_jobs(plan,dest)
            with log.open("w",encoding="utf-8") as stream:
                proc=subprocess.Popen([sys.executable,"-u","-m",
                    "components.nonlinear_time_history.batch_execution","--plan",str(plan),
                    "--output",str(dest),"--workers",workers.get()],cwd=str(root),
                    stdout=stream,stderr=subprocess.STDOUT)
            active.update(proc=proc,output=dest,log=log)
            choose.configure(state="disabled");selector.configure(state="disabled");run.configure(state="disabled")
            status.set("Batch running: "+str(dest))
        except Exception as exc:
            messagebox.showerror("Batch inputs",str(exc),parent=win)
    def stop():
        if active["proc"] is None:return
        dest=active["output"]
        if dest.is_dir():
            (dest/"STOP_REQUESTED").touch()
            status.set("Cancellation requested; partial results retained.")
        else:
            status.set("Scheduler is initializing; cancellation will be sent when ready.")
            active["closing"]=True
    def poll():
        proc=active["proc"]
        if proc is not None:
            dest=active["output"]
            if active["closing"] and dest.is_dir():
                (dest/"STOP_REQUESTED").touch()
            target=dest/"Batch_Status.json"
            if target.is_file():
                try:
                    data=json.loads(target.read_text(encoding="utf-8"))
                    for item in tree.get_children():tree.delete(item)
                    for job in data["jobs"]:
                        cfg=job["config"]
                        tree.insert("", "end",values=(job["id"],cfg.get("variant_id") or cfg["model_folder"],
                            str(cfg.get("limit_state","ULS"))+" / "+",".join(cfg.get("orientations",["XY","YX"])),
                            job["status"]))
                except (OSError,ValueError,KeyError):pass
            if proc.poll() is not None:
                status.set("Scheduler exit "+str(proc.returncode)+" | "+str(dest)+" | Log: "+str(active["log"]))
                active["proc"]=None
                choose.configure(state="normal");selector.configure(state="readonly");run.configure(state="normal")
        if win.winfo_exists():win.after(1000,poll)
    buttons=ttk.Frame(win);buttons.pack(fill="x",padx=10,pady=8)
    run=ttk.Button(buttons,text="Run independent batch",command=start);run.pack(side="left")
    ttk.Button(buttons,text="Stop all active jobs",command=stop).pack(side="left",padx=8)
    def close():
        if active["proc"] is not None:
            messagebox.showinfo("Batch active","Stop the batch and wait for its exit status before closing this window.",parent=win)
            return
        win.destroy()
    win.protocol("WM_DELETE_WINDOW",close)
    win.after(1000,poll)
    return win

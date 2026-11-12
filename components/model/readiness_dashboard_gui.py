"""Tk readiness evidence dashboard for the active ETABS->OpenSees project.

This GUI is an inspection/export tool. It cannot approve a model, change material
parameters, or bypass the production NLTHA model-bound readiness gate.
"""
from __future__ import annotations

import json
import os
import queue
import threading
from pathlib import Path
import subprocess
import sys
import webbrowser

from components.model.readiness_dashboard import audit, export_report, discover_project_model


def launch(parent, folder):
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    from tkinter.scrolledtext import ScrolledText

    project = Path(folder).expanduser().resolve()
    win = tk.Toplevel(parent)
    win.title("NLTHA Readiness | Evidence and Calibration Dashboard")
    win.geometry("1230x825")
    win.minsize(920, 610)
    win.transient(parent)

    outer = ttk.Frame(win, padding=12)
    outer.pack(fill="both", expand=True)
    ttk.Label(
        outer,
        text="NONLINEAR ANALYSIS READINESS — MODEL-BOUND EVIDENCE",
        font=("Segoe UI", 14, "bold")
    ).pack(anchor="w")
    ttk.Label(
        outer,
        text="File discovery is not numerical validation. Diagnostic tests remain "
             "available; thesis-qualified NLTHA requires separately reviewed "
             "model, material, wall and device evidence.",
        wraplength=1130
    ).pack(fill="x", pady=(3, 9))

    location = ttk.Frame(outer)
    location.pack(fill="x", pady=3)
    ttk.Label(location, text="Project folder:").pack(side="left")
    project_var = tk.StringVar(value=str(project))
    ttk.Entry(location, textvariable=project_var).pack(side="left", fill="x", expand=True, padx=6)

    model_row = ttk.Frame(outer)
    model_row.pack(fill="x", pady=3)
    ttk.Label(model_row, text="Model builder:").pack(side="left")
    discovered_model, discovered_status = discover_project_model(project)
    model_var = tk.StringVar(value=str(discovered_model) if discovered_model else "")
    model_selection_status = tk.StringVar(
        value=("Auto-detected standard nonlinear builder for inspection only; "
               "not an approved model."
               if discovered_model else
               "No standard nonlinear builder found; choose the model explicitly.")
    )
    ttk.Entry(model_row, textvariable=model_var).pack(side="left", fill="x", expand=True, padx=6)

    ttk.Label(
        outer, textvariable=model_selection_status, foreground="#9a6318",
        wraplength=1120
    ).pack(anchor="w", pady=2)
    overview = tk.StringVar(value="No source-model audit completed")
    ttk.Label(outer, textvariable=overview, font=("Segoe UI", 10, "bold"),
              wraplength=1120).pack(anchor="w", pady=(7, 6))

    body = ttk.PanedWindow(outer, orient="horizontal")
    body.pack(fill="both", expand=True)
    left = ttk.Frame(body)
    right = ttk.Frame(body)
    body.add(left, weight=3)
    body.add(right, weight=2)

    columns = ("status", "evidence", "review")
    table = ttk.Treeview(left, columns=columns, show="tree headings", height=16)
    table.heading("#0", text="Workstream")
    table.heading("status", text="Evidence status")
    table.heading("evidence", text="Files")
    table.heading("review", text="Signed?")
    table.column("#0", width=280, minwidth=180)
    table.column("status", width=220, minwidth=170)
    table.column("evidence", width=60, stretch=False, anchor="center")
    table.column("review", width=75, stretch=False, anchor="center")
    vert = ttk.Scrollbar(left, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=vert.set)
    table.pack(side="left", fill="both", expand=True)
    vert.pack(side="left", fill="y")
    table.tag_configure("MISSING_EVIDENCE", foreground="#9c3030")
    table.tag_configure("EVIDENCE_FOUND_REVIEW_REQUIRED", foreground="#98601b")
    table.tag_configure("REVIEWED_SIGNOFF_CLAIM", foreground="#17664b")

    detail = ScrolledText(right, wrap="word", width=55)
    detail.pack(fill="both", expand=True)
    detail.insert("end", "Select a workstream to inspect source paths and fingerprints.\n")
    detail.configure(state="disabled")
    state = {"report": None}

    def choose_project():
        path = filedialog.askdirectory(parent=win, title="Select ETABS export project folder")
        if path:
            project_var.set(path)
            discovered, _ = discover_project_model(path)
            model_var.set(str(discovered) if discovered else "")
            model_selection_status.set(
                "Auto-detected standard nonlinear builder for inspection only."
                if discovered else
                "Model not detected in this project folder; choose model explicitly.")
            refresh()

    def choose_model():
        path = filedialog.askopenfilename(
            parent=win, title="Choose actual nonlinear model-builder .py file",
            filetypes=[("Python model-builder", "*.py"), ("All files", "*.*")])
        if path:
            model_var.set(path)
            model_selection_status.set("Model manually selected; model review is still required.")
            refresh()

    # Hashing large project evidence may take noticeable time. Do it outside
    # Tk's event loop, and apply only the newest requested result on Tk's thread.
    # No worker is allowed to touch widgets or approve an engineering model.
    result_queue = queue.SimpleQueue()
    state["request_id"] = 0
    state["busy"] = False

    def refresh():
        folder_name = project_var.get().strip()
        model_name = model_var.get().strip()
        state["request_id"] += 1
        request_id = state["request_id"]
        state["report"] = None
        state["busy"] = True
        overview.set("Checking model and evidence in background — controls remain responsive.")
        def worker():
            try:
                if not folder_name:
                    raise ValueError("Select a project export folder")
                folder_path = Path(folder_name).expanduser().resolve()
                if not folder_path.is_dir():
                    raise FileNotFoundError(folder_path)
                if model_name and not Path(model_name).is_file():
                    raise FileNotFoundError(model_name)
                result_queue.put((request_id, audit(folder_path, model_name or None), None))
            except Exception as exc:
                result_queue.put((request_id, None, str(exc)))
        threading.Thread(target=worker, daemon=True, name="readiness-evidence-audit").start()

    def poll_results():
        try:
            # Drain stale results without updating widgets; a recent project
            # selection always wins even if an older disk scan finishes later.
            latest = None
            while True:
                try:
                    item = result_queue.get_nowait()
                except queue.Empty:
                    break
                if item[0] == state["request_id"]:
                    latest = item
            if latest is not None:
                _, result, error = latest
                state["busy"] = False
                if error is not None:
                    overview.set("AUDIT ERROR: " + error)
                    messagebox.showerror("Readiness evidence", error, parent=win)
                else:
                    state["report"] = result
                    for item in table.get_children():
                        table.delete(item)
                    for g in result["groups"]:
                        table.insert("", "end", iid=g["id"], text=g["title"],
                                     values=(g["status"], len(g["evidence"]),
                                             "Yes*" if g["review_claim_present"] else "No"),
                                     tags=(g["status"],))
                    counts = result["counts"]
                    overview.set(
                        "READINESS: " + result["readiness_level"] +
                        " | Reviewed claims: " + str(counts["REVIEWED_SIGNOFF_CLAIM"]) +
                        " | Available for review: " + str(counts["EVIDENCE_FOUND_REVIEW_REQUIRED"]) +
                        " | Missing: " + str(counts["MISSING_EVIDENCE"]) +
                        " | Draft: " + result["draft_state"])
                    detail.configure(state="normal")
                    detail.delete("1.0", "end")
                    detail.insert("end",
                        "Project: " + result["project_folder"] + "\n" +
                        "Model: " + str(result["model_script"]) + "\n" +
                        "SHA256: " + str(result["model_sha256"]) + "\n\n" +
                        "A sign-off claim is not a verified physical model.\n\n" +
                        "Choose a workstream for file paths and next actions.")
                    detail.configure(state="disabled")
            win.after(100, poll_results)
        except tk.TclError:
            # Window was closed: no worker attempts to operate on Tk.
            return

    def show_selection(_event=None):
        selected = table.selection()
        report = state["report"]
        if not selected or not report:
            return
        g = next((item for item in report["groups"]
                  if item["id"] == selected[0]), None)
        if not g:
            return
        display = [
            g["title"], "", "STATUS: " + g["status"], "",
            g["description"], "",
            "Required model-bound reviewer checks:",
            *[" • " + key for key in g["required_review_keys"]],
            "", "Evidence discovered (available for review only):"
        ]
        for item in g["evidence"]:
            display += ["", item["path"], "SHA256: " + item["sha256"],
                        "Size: " + str(item["bytes"]) + " bytes"]
        if not g["evidence"]:
            display.append("No candidate evidence found in current export folders.")
        display += ["", "NEXT: " + g["next_action"]]
        detail.configure(state="normal")
        detail.delete("1.0", "end")
        detail.insert("end", "\n".join(display))
        detail.configure(state="disabled")

    table.bind("<<TreeviewSelect>>", show_selection)

    def export():
        try:
            if not state["report"]:
                raise ValueError("Refresh and assess before exporting")
            target = Path(project_var.get()) / "OpenSees_Analysis_Results" / "Readiness_Audit"
            js, md = export_report(state["report"], target)
            messagebox.showinfo("Readiness exported",
                "Read-only evidence audit saved:\n" + str(js) + "\n" + str(md) +
                "\n\nNo engineering approval was granted.", parent=win)
        except Exception as exc:
            messagebox.showerror("Readiness export", str(exc), parent=win)

    def open_model_review():
        try:
            model = model_var.get().strip()
            if not model:
                raise ValueError("Select the exact nonlinear model builder first")
            from components.model.readiness_gui import launch as launch_review
            approved_var = tk.StringVar(value="")
            launch_review(win, model, approved_var)
        except Exception as exc:
            messagebox.showerror("Model-bound review", str(exc), parent=win)

    def open_preflight():
        try:
            from components.model.nonlinear_preflight import launch as launch_preflight
            launch_preflight(win, project_var.get().strip())
        except Exception as exc:
            messagebox.showerror("Dependency inventory", str(exc), parent=win)

    def open_project():
        folder_path = Path(project_var.get()).expanduser().resolve()
        if not folder_path.is_dir():
            messagebox.showwarning("Missing project", str(folder_path), parent=win)
            return
        if os.name == "nt":
            os.startfile(str(folder_path))
        else:
            webbrowser.open(folder_path.as_uri())

    # Open corresponding safe tools without marking the current model ready.
    # These start isolated diagnostics and save their own logs and outputs.
    def _spawn_tool(args, description):
        from tkinter import messagebox
        root = Path(__file__).resolve().parents[2]
        script = root / args[0]
        if not script.is_file():
            raise FileNotFoundError("Required launcher is missing: " + str(script))
        destination = Path(project_var.get()).resolve() / "OpenSees_Analysis_Results" / "Readiness_Diagnostics"
        destination.mkdir(parents=True, exist_ok=True)
        logfile = destination / (script.stem + ".log")
        # The log remains attached to the child until it exits; no fabricated
        # success and no accidental reuse of the selected project's source.
        with logfile.open("w", encoding="utf-8") as handle:
            subprocess.Popen(
                [sys.executable, str(script), *args[1:]], cwd=str(root),
                stdout=handle, stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        messagebox.showinfo(
            description,
            "Started a separate diagnostic process. Inspect its actual log and "
            "output before assessing readiness.\n" + str(logfile),
            parent=win)

    def open_materials():
        try:
            _spawn_tool(["06_MATERIAL_DEVICE_VALIDATION.py"], "Material and device validation")
        except Exception as exc:
            messagebox.showerror("Material workbench", str(exc), parent=win)

    def generate_wall_probes():
        try:
            source = filedialog.askopenfilename(
                parent=win, title="Choose actual exploratory RunConfig JSON",
                filetypes=[("JSON", "*.json")])
            if not source:
                return
            destination = Path(project_var.get()).resolve() / "OpenSees_Analysis_Results" / "Wall_Probes"
            _spawn_tool(["21_NLTHA_TRIAGE.py", "--config", source,
                         "--output", str(destination)],
                        "Wall first-step diagnostic configurations")
        except Exception as exc:
            messagebox.showerror("Wall diagnostics", str(exc), parent=win)

    def run_device_benchmark():
        try:
            destination = Path(project_var.get()).resolve() / "OpenSees_Analysis_Results" / "Native_Device_Benchmark"
            _spawn_tool(["29_NATIVE_DEVICE_BENCHMARK.py", "--output", str(destination)],
                        "Isolated native FVD/BRB benchmark")
        except Exception as exc:
            messagebox.showerror("Device diagnostics", str(exc), parent=win)

    buttons = ttk.Frame(outer)
    buttons.pack(fill="x", pady=(10, 0))
    for caption, callback in (
        ("Select project", choose_project), ("Choose model", choose_model),
        ("Refresh evidence", refresh), ("Model-bound review", open_model_review),
        ("Dependency details", open_preflight), ("Export JSON + Markdown", export),
        ("Open project", open_project)
    ):
        ttk.Button(buttons, text=caption, command=callback).pack(side="left", padx=3)
    actions = ttk.Frame(outer)
    actions.pack(fill="x", pady=(7, 0))
    for caption, callback in (
        ("Material validation", open_materials),
        ("Generate wall X/Y probes", generate_wall_probes),
        ("Native FVD/BRB test", run_device_benchmark)
    ):
        ttk.Button(actions, text=caption, command=callback).pack(side="left", padx=3)
    ttk.Button(buttons, text="Close", command=win.destroy).pack(side="right", padx=3)

    win.after(100, poll_results)
    refresh()
    win._readiness_report = state
    return win

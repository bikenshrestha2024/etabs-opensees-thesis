"""Offline ETABS complete 76-point versus OpenSees 76/97 support audit.

Reads FINISHED ETABS Joint Reactions and saved OpenSees solver JSON.
Never launches ETABS, never reruns analysis and never edits source files.

[REF docs/review/GRAVITY_ETABS_COMPARISON.md]
"""
from __future__ import annotations
import argparse
from pathlib import Path
from components.validation.gravity_etabs_offline import (
    compare_etabs_export,export_offline_comparison)


def run_offline(etabs_xlsx,mapping_json,source_json,continuous_json,output_dir):
    """Build auditable offline three-way comparison, fail-closed on missing inputs.

    [REF components/validation/gravity_etabs_offline.py]
    """
    paths=[Path(p).expanduser().resolve() for p in
           (etabs_xlsx,mapping_json,source_json,continuous_json)]
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError("Missing required native evidence: "+str(path))
    data=compare_etabs_export(*paths)
    out=export_offline_comparison(data,output_dir)
    print("ETABS source worksheet:", paths[0])
    print("ETABS base joint records:",data["etabs_joint_records"])
    print("Unique mapped support nodes:",data["matched_source_nodes"])
    print("Unmapped source reactions:",data["unmapped_or_missing_reactions"])
    print("New continuous-wall-only supports:",len(data["continuous_only_nodes"]))
    print("OpenSees - ETABS gravity difference (kN):",
          data["difference_opensees_minus_etabs_kN"])
    print("Workbook:",out/"ETABS_Offline_Gravity_Comparison.xlsx")
    print("JSON:",out/"ETABS_Offline_Gravity_Comparison.json")
    print("CSV:",out/"ETABS_Offline_Joint_Reaction_Differences.csv")
    print("This report is diagnostic; structural acceptance not established.")
    return out


def gui():
    """Windows/Spyder file chooser; no ETABS COM interaction.

    [REF docs/review/GRAVITY_ETABS_COMPARISON.md]
    """
    import tkinter as tk
    from tkinter import ttk,filedialog,messagebox
    root=tk.Tk()
    root.title("Completed ETABS Joint Reactions ↔ OpenSees 76/97 Support Audit")
    root.geometry("1100x460")
    frame=ttk.Frame(root,padding=16)
    frame.pack(fill="both",expand=True)
    fields=[
        ("Original completed ETABS full table XLSX / Joint Reactions CSV",False),
        ("OpenSees_Element_Connectivity.json (source ID mapping)",False),
        ("ETABS_SOURCE_SUPPORTS/Gravity_Result_V110.json",False),
        ("CONTINUOUS_WALL_BASE_FIXED/Gravity_Result_V110.json",False),
        ("Output directory (new separate audit folder)",True)]
    values=[]
    for i,(name,isfolder) in enumerate(fields):
        value=tk.StringVar()
        values.append(value)
        ttk.Label(frame,text=name).grid(row=i,column=0,sticky="w",pady=8)
        ttk.Entry(frame,textvariable=value,width=77).grid(row=i,column=1,sticky="ew",padx=8)
        def choose(v=value,directory=isfolder):
            path=filedialog.askdirectory() if directory else filedialog.askopenfilename(
                filetypes=[("ETABS and OpenSees evidence","*.xlsx *.xlsm *.csv *.json"),
                           ("All files","*.*")])
            if path:v.set(path)
        ttk.Button(frame,text="Browse",command=choose).grid(row=i,column=2)
    frame.columnconfigure(1,weight=1)
    status=tk.StringVar(value="Offline only: no RunAnalysis, ETABS COM, or structural model changes.")
    ttk.Label(frame,textvariable=status,wraplength=900).grid(row=6,column=0,columnspan=3,pady=16)
    def submit():
        try:
            if any(not v.get().strip() for v in values):
                raise ValueError("All five source paths are required")
            status.set("Reading completed ETABS table and two saved OpenSees analyses...")
            root.update_idletasks()
            out=run_offline(*(v.get().strip() for v in values))
            status.set("Saved review workbook: "+str(out))
            messagebox.showinfo("Offline review complete",
                "Workbook and CSV/JSON saved in:\n"+str(out),parent=root)
        except Exception as exc:
            status.set("Blocked: "+str(exc))
            messagebox.showerror("Evidence audit blocked",str(exc),parent=root)
    ttk.Button(frame,text="Compare completed ETABS ↔ both OpenSees runs",
               command=submit).grid(row=5,column=0,columnspan=3,pady=10)
    root.mainloop()


def main():
    """Command line with optional Spyder GUI.

    [REF docs/review/GRAVITY_ETABS_COMPARISON.md]
    """
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--etabs-xlsx",help="Original completed ETABS XLSX or filtered CSV")
    parser.add_argument("--mapping-json",help="Original OpenSees_Element_Connectivity.json")
    parser.add_argument("--source-json",help="Completed 76-source-support Gravity_Result_V110.json")
    parser.add_argument("--continuous-json",help="Completed 97-fixed-support Gravity_Result_V110.json")
    parser.add_argument("--output",help="Separate output folder")
    args=parser.parse_args()
    if not any((args.etabs_xlsx,args.mapping_json,args.source_json,
                args.continuous_json,args.output)):
        gui()
        return
    if not all((args.etabs_xlsx,args.mapping_json,args.source_json,
                args.continuous_json,args.output)):
        parser.error("All five paths are required, or run with no arguments for the GUI.")
    run_offline(args.etabs_xlsx,args.mapping_json,args.source_json,
                args.continuous_json,args.output)


if __name__=="__main__":
    main()

"""Run the offline 3D base-reaction audit with a file picker (Spyder compatible).

Does not launch ETABS, change restraints, or change the model.
Requires: conda install -c conda-forge plotly
"""
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from components.validation.gravity_reactions_3d import create_audit

def main():
    root = tk.Tk()
    root.withdraw()
    source = filedialog.askopenfilename(
        title="Select ETABS_OpenSees_All_76_Nodal_Reactions.csv",
        filetypes=[("CSV", "*.csv")])
    if not source:
        return
    native = messagebox.askyesno(
        "Native ETABS restraint evidence",
        "Do you have a native ETABS GetRestraint CSV for these points?\n"
        "Select No if unsure; node restraint states will be UNVERIFIED.")
    evidence = None
    if native:
        evidence = filedialog.askopenfilename(
            title="Select native ETABS point restraints CSV",
            filetypes=[("CSV", "*.csv")])
        if not evidence:
            return
    default = str(Path(source).parent / "Gravity_3D_Review")
    output = filedialog.askdirectory(
        title="Choose output folder", initialdir=str(Path(source).parent))
    if not output:
        output = default
    try:
        summary = create_audit(source, output, evidence)
    except Exception as exc:
        messagebox.showerror("Audit failed", str(exc))
        raise
    messagebox.showinfo(
        "3D support reaction audit created",
        "Output: "+str(output)+"\nStatus: "+summary["validation"]+
        "\nOpen Gravity_Base_Reactions_3D.html in your browser.")

if __name__ == "__main__":
    main()

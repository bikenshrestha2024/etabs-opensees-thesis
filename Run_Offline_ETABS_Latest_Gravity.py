# -*- coding: utf-8 -*-
"""Offline ETABS 1. DL + LL versus OpenSees 32/76/97 support cases.

Spyder-compatible, read-only analysis of source evidence. No ETABS COM,
solver execution, force adjustment, or automatic engineering acceptance.
Requires openpyxl (conda-forge). Select the original FINISHED ETABS full-table
Excel, OpenSees_Element_Connectivity.json and Gravity_Case_Reaction_Index.json.
Source paths are taken from the index, NEVER inferred from the node count.
Outputs are written under the chosen output directory.

[REF components/validation/gravity_etabs_offline.py]
"""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from components.validation.gravity_etabs_offline import (
    compare_etabs_export, export_offline_comparison)

PROFILE = "GRAVITY_1.0D_1.0L"
PRIMARY = "ETABS_NONZERO_REACTION_DIAGNOSTIC"
SOURCE = "ETABS_SOURCE_SUPPORTS"
CONTINUOUS = "CONTINUOUS_WALL_BASE_FIXED"


def _hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for data in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def _indexed_result(index, strategy, expected_nodes):
    key = strategy + "|" + PROFILE
    entry = index.get(key)
    if not isinstance(entry, dict):
        raise ValueError("Missing case registry entry: " + key)
    if entry.get("scenario") != strategy or entry.get("profile") != PROFILE:
        raise ValueError("Incorrect case identity in registry: " + key)
    if entry.get("status") != "SOLVED_REACTIONS_NOT_ETABS_VALIDATED":
        raise ValueError("Case is not a completed documented gravity run: " + key)
    tags = entry.get("support_tags", [])
    if len(tags) != expected_nodes or len(set(tags)) != expected_nodes:
        raise ValueError("Expected %d unique supports for %s" % (expected_nodes, strategy))
    path = Path(entry["result_path"]).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError("Registry points to missing native result: " + str(path))
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not data.get("ok") or data.get("wall_support_strategy") != strategy:
        raise ValueError("Registry/solver evidence disagrees for " + strategy)
    if data.get("gravity_profile") != PROFILE:
        raise ValueError("Gravity profile mismatch in " + str(path))
    solved_tags = {str(v["node_tag"]) for v in data.get("reactions", [])}
    if solved_tags != {str(v) for v in tags}:
        raise ValueError("Registry support tags differ from solved reactions: " + strategy)
    return path


def run(etabs_xlsx, connectivity_json, case_index_json, output_folder):
    paths = [Path(x).expanduser().resolve() for x in
             (etabs_xlsx, connectivity_json, case_index_json)]
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError("Required existing evidence missing: " + str(path))
    case_index = json.loads(paths[2].read_text(encoding="utf-8-sig"))
    p32 = _indexed_result(case_index, PRIMARY, 32)
    p76 = _indexed_result(case_index, SOURCE, 76)
    p97 = _indexed_result(case_index, CONTINUOUS, 97)
    # Guard against comparing source runs made from different converter inputs.
    ids = [case_index[k + "|" + PROFILE].get("input_sha256")
           for k in (PRIMARY, SOURCE, CONTINUOUS)]
    if any(not x for x in ids) or ids[0] != ids[1] or ids[0] != ids[2]:
        raise ValueError("Different or missing model-input hashes across 32/76/97 runs")
    expected_model = paths[1].parent / "OpenSees_Complete_Gravity_Model.py"
    if not expected_model.is_file():
        raise FileNotFoundError("Source-export model missing beside mapping: " + str(expected_model))
    actual_model_sha = _hash(expected_model)
    for strategy in (PRIMARY, SOURCE, CONTINUOUS):
        entry = case_index[strategy + "|" + PROFILE]
        if Path(entry.get("model_path", "")).expanduser().resolve() != expected_model.resolve():
            raise ValueError("Mapping folder and registered model differ for " + strategy)
        if entry.get("model_sha256") != actual_model_sha:
            raise ValueError("Registered model SHA256 differs from current export for " + strategy)
        for name, expected_hash in entry["input_sha256"].items():
            candidate = paths[1].parent / name
            if candidate.is_file() and _hash(candidate) != expected_hash:
                raise ValueError("Current source file changed since gravity run: " + str(candidate))
    out = Path(output_folder).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    reports = {}
    for label, result, expected in (("PRIMARY_32", p32, PRIMARY),
                                     ("ETABS_NODE_POSITION_76", p76, SOURCE)):
        report = compare_etabs_export(
            paths[0], paths[1], result, p97, source_strategy=expected)
        folder = export_offline_comparison(report, out / label)
        reports[label] = {
            "source_strategy": expected,
            "source_result": str(result),
            "folder": str(folder),
            "mapped_rows": report["matched_source_nodes"],
            "missing_rows": report["unmapped_or_missing_reactions"],
            "etabs_total_kN": report["sum_etabs_base_joint_FZ_kN"],
            "opensees_total_kN": report["opensees_source_total_reaction_kN"],
            "difference_kN": report["difference_opensees_minus_etabs_kN"]
        }
    summary = {
        "version": "2026-11-09",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "DIAGNOSTIC_NOT_STRUCTURALLY_VALIDATED",
        "case": "1. DL + LL",
        "sources": [{"path": str(x), "sha256": _hash(x)} for x in
                    (paths[0], paths[1], paths[2], p32, p76, p97)],
        "results": reports,
        "notes": [
            "The ETABS base table includes mapped points with zero FZ.",
            "The 32-node strategy is a restraint sensitivity diagnostic, not a proof of ETABS model equivalence.",
            "Zero reactions are not grounds to remove an ETABS restraint in a physical foundation model.",
            "Wall-region sums should be reviewed separately from individual wall mesh nodes.",
            "Check end-offset weight, object/section stiffness modifiers and shell connectivity independently.",
            "A global force balance pass alone does not validate individual reactions."
        ]
    }
    (out / "OFFLINE_GRAVITY_32_76_97_INDEX.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    (out / "README_FIRST.txt").write_text(
        "OFFLINE ETABS / OPENSEES GRAVITY REACTION REVIEW\n"
        "1. Open PRIMARY_32/ETABS_Offline_Gravity_Comparison.xlsx\n"
        "2. Open ETABS_NODE_POSITION_76/ETABS_Offline_Gravity_Comparison.xlsx\n"
        "3. Compare critical nodes and foundation regions; inspect 97-node case.\n"
        "4. Original ETABS full export was read; ETABS COM was not used.\n"
        "5. Run evidence confirms equilibrium, not structural equivalence.\n"
        "6. No nodal reaction or applied force has been adjusted.\n",
        encoding="utf-8")
    print("OFFLINE OUTPUT:", out)
    print("Primary 32-node difference (kN):", reports["PRIMARY_32"]["difference_kN"])
    print("Source 76-node difference (kN):", reports["ETABS_NODE_POSITION_76"]["difference_kN"])
    print("STRUCTURAL VALIDATION: NOT ESTABLISHED")
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--etabs", help="Completed ETABS full export xlsx / Joint Reactions csv")
    parser.add_argument("--mapping", help="OpenSees_Element_Connectivity.json")
    parser.add_argument("--registry", help="Gravity_Case_Reaction_Index.json")
    parser.add_argument("--output", help="New offline comparison output directory")
    args, _ = parser.parse_known_args()  # Spyder may pass kernel arguments.
    values = (args.etabs, args.mapping, args.registry, args.output)
    if any(values):
        if not all(values):
            parser.error("All four paths required, or run with no arguments for the GUI")
        run(*values)
        return
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    root = tk.Tk()
    root.title("Offline ETABS ↔ OpenSees | current 32 / 76 / 97 gravity evidence")
    root.geometry("1120x390")
    frame = ttk.Frame(root, padding=15)
    frame.pack(fill="both", expand=True)
    prompts = ("Original FINISHED ETABS Joint Reactions XLSX / CSV",
               "OpenSees_Element_Connectivity.json",
               "Gravity_Case_Reaction_Index.json",
               "Output directory (e.g. current dual-run/ETABS_Full_Table_Offline_Comparison)")
    variables = []
    for i, name in enumerate(prompts):
        v = tk.StringVar()
        variables.append(v)
        ttk.Label(frame, text=name).grid(row=i, column=0, sticky="w", pady=10)
        ttk.Entry(frame, textvariable=v, width=80).grid(
            row=i, column=1, sticky="ew", padx=7)
        def choose(var=v, is_dir=(i == 3)):
            path = filedialog.askdirectory() if is_dir else filedialog.askopenfilename()
            if path:
                var.set(path)
        ttk.Button(frame, text="Browse", command=choose).grid(row=i, column=2)
    frame.columnconfigure(1, weight=1)
    status = tk.StringVar(value="Read-only comparison. No ETABS COM, no new analysis.")
    ttk.Label(frame, textvariable=status).grid(
        row=5, column=0, columnspan=3, sticky="w", pady=12)
    def execute():
        try:
            if not all(x.get().strip() for x in variables):
                raise ValueError("Select all three evidence inputs and an output directory")
            output = run(*(x.get().strip() for x in variables))
            status.set("Saved: " + str(output))
            messagebox.showinfo("Offline comparison", "Saved evidence in:\n" + str(output))
        except Exception as exc:
            status.set("BLOCKED: " + str(exc))
            messagebox.showerror("Evidence mismatch", str(exc))
    ttk.Button(frame, text="Compare 32 and 76 to ETABS, include 97-node sensitivity",
               command=execute).grid(row=4, column=0, columnspan=3, pady=10)
    root.mainloop()


if __name__ == "__main__":
    main()

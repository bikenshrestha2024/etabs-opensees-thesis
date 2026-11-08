# -*- coding: utf-8 -*-
"""ETABS -> OpenSees gravity comparison, offline, single-file, Spyder compatible.

Inputs:
  1 Original FINISHED ETABS Excel full-table export (Joint Reactions), or CSV
  2 OpenSees_Element_Connectivity.json (actual ETABS unique-name -> node map)
  3 ETABS_SOURCE_SUPPORTS/Gravity_Result_V110.json
  4 CONTINUOUS_WALL_BASE_FIXED/Gravity_Result_V110.json
  5 Output directory

Never launches ETABS, edits the EDB, runs a solver or adjusts results to match.
Requires: conda install -c conda-forge openpyxl
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
from datetime import datetime


CASE = "1. DL + LL"
FIELDS = ["ETABS Unique Name", "ETABS Label", "OpenSees Node Tag",
          "X (m)", "Y (m)", "Z (m)", "ETABS FZ (kN)",
          "OpenSees source FZ (kN)", "OpenSees continuous FZ (kN)",
          "OS source - ETABS (kN)", "OS continuous - ETABS (kN)",
          "OS continuous - source (kN)", "Abs source difference (kN)",
          "Percent source difference", "Mapping Status", "Notes"]


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(2**20), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def numeric(value, label):
    try:
        value = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError("%s is not numeric: %r" % (label, value)) from exc
    if not math.isfinite(value):
        raise ValueError("%s is not finite" % label)
    return value


def read_etabs(path):
    """Keep all Base records, including zero-force reactions. No Excel filter."""
    path = Path(path)
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        from openpyxl import load_workbook
        wb = load_workbook(path, read_only=True, data_only=True)
        names = [x for x in wb.sheetnames if x.strip().lower() == "joint reactions"]
        if len(names) != 1:
            wb.close()
            raise ValueError("Exactly one 'Joint Reactions' sheet is required")
        rows = wb[names[0]].iter_rows(values_only=True)
    elif path.suffix.lower() == ".csv":
        wb = None
        fp = path.open("r", encoding="utf-8-sig", newline="")
        rows = csv.reader(fp)
    else:
        raise ValueError("ETABS input must be .xlsx, .xlsm or .csv")
    output = {}
    header = None
    try:
        for row in rows:
            if header is None:
                h = {str(v or "").strip().lower().split("\n", 1)[0].strip(): i
                     for i, v in enumerate(row)}
                if all(x in h for x in ("story", "label", "unique name", "output case", "fz")):
                    header = h
                continue
            def field(key):
                i = header[key]
                return row[i] if i < len(row) else None
            if str(field("story") or "").strip().lower() != "base":
                continue
            if str(field("output case") or "").strip() != CASE:
                continue
            name = str(field("unique name") or "").strip()
            if not name:
                raise ValueError("ETABS Base record has no Unique Name")
            if name in output:
                raise ValueError("Duplicate ETABS Base record for Unique Name %s" % name)
            output[name] = dict(label=str(field("label") or "").strip(),
                                fz=numeric(field("fz"), "ETABS FZ for " + name))
    finally:
        if wb is not None:
            wb.close()
        else:
            fp.close()
    if header is None or not output:
        raise ValueError("No exact ETABS Base Joint Reactions for '%s'" % CASE)
    return output


def load_map(path):
    data = load_json(path)
    mapping = {}
    for row in data.get("node_map", []):
        point = row.get("etabs_point_name")
        tag = row.get("opensees_node_tag")
        if point is None or tag is None:
            continue
        key = str(point).strip()
        value = str(tag).strip()
        if key in mapping and mapping[key] != value:
            raise ValueError("Ambiguous mapped ETABS Unique Name: " + key)
        mapping[key] = value
    if not mapping:
        raise ValueError("Topology contains no node_map entries with ETABS Unique Names")
    return mapping


def load_gravity(path, expected):
    data = load_json(path)
    if data.get("ok") is not True:
        raise ValueError("Gravity run is not completed: " + str(path))
    if data.get("wall_support_strategy") != expected:
        raise ValueError("Wrong wall strategy: %s" % path)
    if data.get("gravity_profile") != "GRAVITY_1.0D_1.0L":
        raise ValueError("Wrong load profile; use actual 100% DL+LL: " + str(path))
    reactions = {}
    for r in data.get("reactions", []):
        tag = str(r["node_tag"])
        if tag in reactions:
            raise ValueError("Duplicate OpenSees reaction node " + tag)
        reactions[tag] = numeric(r["rz_kN"], "OpenSees Rz")
    nodes = {str(n["tag"]): n for n in data.get("nodes", [])}
    if not reactions or not nodes:
        raise ValueError("Missing node positions or reactions: " + str(path))
    return data, reactions, nodes


def compare(etabs_path, map_path, source_path, continuous_path, out_path):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.formatting.rule import ColorScaleRule

    inputs = [Path(v).expanduser().resolve() for v in
              (etabs_path, map_path, source_path, continuous_path)]
    for path in inputs:
        if not path.is_file():
            raise FileNotFoundError(str(path))
    etabs = read_etabs(inputs[0])
    mapping = load_map(inputs[1])
    source, sr, sn = load_gravity(inputs[2], "ETABS_SOURCE_SUPPORTS")
    continuous, cr, cn = load_gravity(inputs[3], "CONTINUOUS_WALL_BASE_FIXED")
    total_e = sum(r["fz"] for r in etabs.values())
    total_s = numeric(source["report"]["support_vertical_reaction_kN"], "source total")
    total_c = numeric(continuous["report"]["support_vertical_reaction_kN"], "continuous total")
    applied_s = numeric(source["report"]["applied_vertical_load_kN"], "source applied load")
    applied_c = numeric(continuous["report"]["applied_vertical_load_kN"], "continuous applied load")
    if abs(applied_s-applied_c) > 0.01:
        raise ValueError("OpenSees cases do not have the same applied gravity load")
    rows = []
    used = set()
    for key, item in etabs.items():
        tag = mapping.get(key)
        xyz = sn.get(tag, {}) if tag else {}
        a = sr.get(tag) if tag else None
        b = cr.get(tag) if tag else None
        if tag: used.add(tag)
        diff = a-item["fz"] if a is not None else None
        cdiff = b-item["fz"] if b is not None else None
        note = ("Three-wall intersection: audit wall mesh, area modifiers, "
                "openings and integrated pier reactions" if key == "264" else "")
        status = ("UNMAPPED" if tag is None else
                  "MAPPED_NO_SOURCE_REACTION" if a is None else
                  "MATCHED_SUPPORT")
        rows.append([key, item["label"], tag, xyz.get("x_m"), xyz.get("y_m"),
                     xyz.get("z_m"), item["fz"], a, b, diff, cdiff,
                     b-a if a is not None and b is not None else None,
                     abs(diff) if diff is not None else None,
                     abs(diff)/abs(item["fz"])*100 if diff is not None and item["fz"] else None,
                     status, note])
    rows.sort(key=lambda x: (-1 if x[12] is None else 0,
                             -(x[12] or 0)))
    # Additional restrained nodes are not ETABS source supports.
    added = []
    for tag in sorted(set(cr)-set(sr), key=lambda x: int(x) if x.isdigit() else x):
        pos = cn.get(tag, {})
        added.append([tag, pos.get("x_m"), pos.get("y_m"), pos.get("z_m"),
                      cr[tag], "ADDITIONAL_FIXED_NODE_NO_ETABS_1_TO_1"])
    run = Path(out_path).expanduser().resolve()
    run.mkdir(parents=True, exist_ok=True)
    book = Workbook()
    ws = book.active
    ws.title = "Executive summary"
    summary = [
        ("Case", CASE),
        ("ETABS full-table base joints", len(etabs)),
        ("Matched source supports", sum(r[14] == "MATCHED_SUPPORT" for r in rows)),
        ("Unmatched ETABS points", sum(r[14] != "MATCHED_SUPPORT" for r in rows)),
        ("OpenSees source supports", len(sr)),
        ("OpenSees continuous supports", len(cr)),
        ("Continuous-only supports", len(added)),
        ("ETABS sum FZ (kN)", total_e),
        ("OpenSees source total (kN)", total_s),
        ("OpenSees continuous total (kN)", total_c),
        ("OpenSees - ETABS (kN)", total_s-total_e),
        ("OpenSees - ETABS (%)", (total_s-total_e)/abs(total_e)*100 if total_e else None),
        ("OpenSees equilibrium source error (kN)", total_s-applied_s),
        ("OpenSees equilibrium continuous error (kN)", total_c-applied_c),
        ("Weight/double-counting check", "NOT VERIFIED BY REACTIONS"),
        ("Section/object modifiers check", "NOT VERIFIED BY REACTIONS"),
        ("Structural validation status", "NOT VALIDATED"),
        ("Model correspondence", "VERIFY EDB/export identity independently"),
    ]
    for a,b in summary: ws.append([a,b])
    all_ws = book.create_sheet("All ETABS Base joints")
    all_ws.append(FIELDS)
    for row in sorted(rows, key=lambda r: int(r[0]) if r[0].isdigit() else r[0]):
        all_ws.append(row)
    critical = book.create_sheet("Critical reaction differences")
    critical.append(FIELDS)
    for row in sorted((r for r in rows if r[12] is not None),
                      key=lambda r: r[12], reverse=True):
        critical.append(row)
    added_ws = book.create_sheet("21 extra wall supports")
    added_ws.append(["OpenSees tag","X m","Y m","Z m","RZ kN","Status"])
    for row in added: added_ws.append(row)
    core = book.create_sheet("ETABS 264 OS 41")
    core.append(FIELDS)
    hits = [r for r in rows if r[0] == "264" or r[2] == "41"]
    for row in hits: core.append(row)
    core.append(["OBSERVATION", "Point 264 is reported as a three-wall junction; "
                 "node 41 is at the wall base. Single-node reactions are not "
                 "integrated wall-region reactions."])
    core.append(["CHECK", "Compare foundation wall-group total, vertical forces "
                 "on each connected wall segment, wall-shell mesh topology, "
                 "wall openings, axial/membrane modifiers and base constraints."])
    checks = book.create_sheet("Provenance & limitations")
    checks.append(["Input", "Absolute path", "SHA256"])
    for title,path in zip(("ETABS full-table export", "ETABS to OpenSees topology",
                           "OS 76 support result", "OS 97 support result"), inputs):
        checks.append([title,str(path),sha256_file(path)])
    checks.append(["LIMIT", "No direct ETABS COM run is attempted"])
    checks.append(["LIMIT", "Only original ETABS unique IDs, not display labels, are mapped"])
    checks.append(["LIMIT", "No ETABS support FZ is synthesized from OpenSees results"])
    checks.append(["LIMIT", "No inferred zero at missing reaction records"])
    checks.append(["LIMIT", "Point-level comparison can differ from shell-mesh integrated wall forces"])
    checks.append(["LIMIT", "Stiffness modifiers and self-weight cannot be proven from reactions alone"])
    for sheet in book:
        sheet.freeze_panes = "A2"
        sheet.sheet_view.showGridLines = False
        sheet.column_dimensions["A"].width = 28
        sheet.column_dimensions["B"].width = 30
        if sheet in (all_ws, critical, core):
            sheet.auto_filter.ref = "A1:P%d" % max(1,sheet.max_row)
            for c in sheet[1]:
                c.fill = PatternFill("solid", fgColor="14395B")
                c.font = Font(color="FFFFFF", bold=True)
            for c in "CDEFGHIJKLMNOP":
                sheet.column_dimensions[c].width = 19
        else:
            sheet.column_dimensions["B"].width = 72
            sheet.column_dimensions["C"].width = 69
    for sheet in (all_ws,critical):
        if sheet.max_row>2:
            sheet.conditional_formatting.add(
                "M2:M%d"%sheet.max_row,
                ColorScaleRule(start_type="min",start_color="F4F8FD",
                               end_type="max",end_color="F7A8A8"))
    target = run/"ETABS_OpenSees_76_97_Nodal_Gravity_Comparison.xlsx"
    book.save(target)
    with (run/"ETABS_OpenSees_All_76_Nodal_Reactions.csv").open(
             "w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.writer(fp);writer.writerow(FIELDS);writer.writerows(rows)
    info = {"schema":"offline-etabs-opensees-76-97-v1",
            "created_at":datetime.now().astimezone().isoformat(),
            "case": CASE, "etabs_total_kN":total_e, "source_total_kN":total_s,
            "continuous_total_kN":total_c, "global_difference_kN":total_s-total_e,
            "etabs_rows":len(rows), "matched_rows":sum(r[14]=="MATCHED_SUPPORT" for r in rows),
            "additional_fixed_nodes":len(added), "engineering_acceptance":"NOT_VALIDATED"}
    (run/"ETABS_OpenSees_Comparison_Summary.json").write_text(
        json.dumps(info,indent=2),encoding="utf-8")
    (run/"README_RESULTS.txt").write_text(
        "OFFLINE 1.0 DEAD + 1.0 LIVE COMPARISON\n"
        "Upload the Excel workbook, all 76-node CSV, summary JSON and the "
        "original model configuration plus source ETABS full-table export "
        "for an engineering review.\n"
        "Point 264 ↔ node 41 is separately highlighted. Reactions alone "
        "cannot prove correct stiffness or absence of double-counting.\n",
        encoding="utf-8")
    return target


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--etabs",help="Original ETABS full-table XLSX or Joint Reactions CSV")
    parser.add_argument("--mapping",help="OpenSees_Element_Connectivity.json")
    parser.add_argument("--source",help="ETABS_SOURCE_SUPPORTS/Gravity_Result_V110.json")
    parser.add_argument("--continuous",help="CONTINUOUS_WALL_BASE_FIXED/Gravity_Result_V110.json")
    parser.add_argument("--output",help="New output directory")
    args=parser.parse_args()
    vals=[args.etabs,args.mapping,args.source,args.continuous,args.output]
    if any(vals):
        if not all(vals): parser.error("All five arguments are needed")
        print("WROTE",compare(*vals))
        return
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    root=tk.Tk();root.title("Offline ETABS ↔ OpenSees 76 / 97 Gravity Node Comparison")
    root.geometry("1100x420")
    frame=ttk.Frame(root,padding=15);frame.pack(fill="both",expand=True)
    names=["ETABS finished full-table XLSX / Joint Reactions CSV",
           "OpenSees_Element_Connectivity.json",
           "ETABS_SOURCE_SUPPORTS / Gravity_Result_V110.json",
           "CONTINUOUS_WALL_BASE_FIXED / Gravity_Result_V110.json",
           "Output folder"]
    variables=[]
    for i,label in enumerate(names):
        v=tk.StringVar();variables.append(v)
        ttk.Label(frame,text=label).grid(row=i,column=0,sticky="w",pady=9)
        ttk.Entry(frame,textvariable=v,width=77).grid(row=i,column=1,padx=8,sticky="ew")
        def browse(var=v,folder=i==4):
            p=filedialog.askdirectory() if folder else filedialog.askopenfilename()
            if p: var.set(p)
        ttk.Button(frame,text="Browse",command=browse).grid(row=i,column=2)
    frame.columnconfigure(1,weight=1)
    status=tk.StringVar(value="Offline only — original files remain unchanged.")
    ttk.Label(frame,textvariable=status).grid(row=6,column=0,columnspan=3,pady=10)
    def execute():
        try:
            if not all(v.get().strip() for v in variables):
                raise ValueError("Select all four inputs and the output directory")
            result=compare(*(v.get().strip() for v in variables))
            status.set("DONE: "+str(result))
            messagebox.showinfo("Comparison saved",str(result))
        except Exception as exc:
            status.set("ERROR: "+str(exc))
            messagebox.showerror("Comparison blocked",str(exc))
    ttk.Button(frame,text="Generate mapped Excel + 76-node CSV + critical point 264",
               command=execute).grid(row=5,column=0,columnspan=3,pady=12)
    root.mainloop()


if __name__=="__main__":
    main()

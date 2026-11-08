"""Offline 3D gravity reaction audit; never modifies OpenSees restraints or loads.

Input: ETABS_OpenSees_All_76_Nodal_Reactions.csv from offline comparison.
Optional --restraints CSV: columns 'ETABS Unique Name', 'restraint_verified',
'uz_restrained' (true/false); derived from original native ETABS EDB, NOT FZ.
Requirements: plotly for HTML, standard library for CSV/JSON. No internet needed.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path

SOURCE_FIELDS = ("ETABS FZ (kN)", "OpenSees source FZ (kN)",
                 "OpenSees continuous FZ (kN)")
ID_FIELD = "ETABS Unique Name"


def _number(row, field):
    try:
        v = float(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Missing or invalid {field}: {row.get(ID_FIELD)}") from exc
    if not math.isfinite(v):
        raise ValueError(f"Nonfinite {field}: {row.get(ID_FIELD)}")
    return v


def _truth(v):
    v = str(v).strip().casefold()
    if v in ("true", "1", "yes", "y"): return True
    if v in ("false", "0", "no", "n"): return False
    raise ValueError("Expected explicit true/false: "+repr(v))


def load_rows(path, restraint_path=None):
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("Empty node-reaction table")
    ids = [str(r.get(ID_FIELD, "")).strip() for r in rows]
    if any(not i for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("Missing or duplicate ETABS unique names")
    checked = {}
    if restraint_path:
        with Path(restraint_path).open(newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                k = str(r.get(ID_FIELD, "")).strip()
                if k in checked:
                    raise ValueError("Duplicate native ETABS restraint record: "+k)
                checked[k] = dict(verified=_truth(r["restraint_verified"]),
                                  uz=_truth(r["uz_restrained"]))
    out = []
    for r in rows:
        node = {
            "etabs_unique": str(r[ID_FIELD]).strip(),
            "etabs_label": str(r.get("ETABS Label", "")),
            "opensees_node": int(r["OpenSees Node Tag"]),
            "xyz_m": [_number(r, p) for p in ("X (m)", "Y (m)", "Z (m)")],
            "etabs_kN": _number(r, SOURCE_FIELDS[0]),
            "source_kN": _number(r, SOURCE_FIELDS[1]),
            "continuous_kN": _number(r, SOURCE_FIELDS[2]),
        }
        k = node["etabs_unique"]
        meta = checked.get(k)
        node["native_restraint"] = ("UZ_FIXED" if meta and meta["verified"] and meta["uz"]
            else "UZ_FREE" if meta and meta["verified"] else "UNVERIFIED")
        node["source_minus_etabs_kN"] = node["source_kN"]-node["etabs_kN"]
        node["continuous_minus_etabs_kN"] = node["continuous_kN"]-node["etabs_kN"]
        if abs(node["etabs_kN"]) < 1e-9:
            node["zero_reaction_note"] = "ETABS FZ=0 does not establish that UZ is free"
        else:
            node["zero_reaction_note"] = ""
        out.append(node)
    if len({r["opensees_node"] for r in out}) != len(out):
        raise ValueError("Duplicate OpenSees mapped node tags")
    return out


def create_audit(input_csv, output_dir, native_restraints=None):
    rows = load_rows(input_csv, native_restraints)
    dest = Path(output_dir)
    dest.mkdir(parents=True, exist_ok=True)
    totals = {key: sum(r[key] for r in rows)
              for key in ("etabs_kN", "source_kN", "continuous_kN")}
    status_counts = {s: sum(r["native_restraint"] == s for r in rows)
                     for s in ("UZ_FIXED", "UZ_FREE", "UNVERIFIED")}
    contradictory = [r for r in rows
                     if r["native_restraint"] == "UZ_FREE"
                     and abs(r["source_kN"]) > 1e-6]
    manifest = {
        "schema": "gravity-3d-support-restraint-audit-v1",
        "analysis": "1.0DL+1.0LL; reactions, not applied nodal loads",
        "node_count": len(rows),
        "totals_kN": totals,
        "native_restraint_counts": status_counts,
        "zero_etabs_reaction_count": sum(abs(r["etabs_kN"]) < 1e-9 for r in rows),
        "unrestrained_but_source_reacting": [
            {"etabs_unique": r["etabs_unique"],
             "opensees_node": r["opensees_node"], "source_kN": r["source_kN"]}
            for r in contradictory
        ],
        "validation": "NOT_VALIDATED" if (status_counts["UNVERIFIED"] or contradictory or
            abs(totals["source_kN"]-totals["etabs_kN"]) > 0.005*max(1, abs(totals["etabs_kN"])))
            else "SCREENING_ONLY_REQUIRES_MECHANICAL_REVIEW",
        "warning": "Never change supports from zero ETABS FZ alone. Verify the native ETABS restraints and shell edge meshing. Continuous supports remain an independent sensitivity model."
    }
    (dest/"Gravity_3D_Restraint_Audit.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8")
    fields = ["etabs_unique", "etabs_label", "opensees_node", "native_restraint",
              "etabs_kN", "source_kN", "continuous_kN",
              "source_minus_etabs_kN", "continuous_minus_etabs_kN", "zero_reaction_note"]
    with (dest/"Gravity_3D_Restraint_Audit.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    try:
        import plotly.graph_objects as go
        from plotly.offline import plot
    except ImportError as exc:
        raise RuntimeError("3D HTML requires plotly; install via conda-forge: conda install -c conda-forge plotly") from exc

    figs = []
    descriptions = [
        ("ETABS", "etabs_kN"),
        ("OpenSees ETABS_SOURCE_SUPPORTS", "source_kN"),
        ("OpenSees CONTINUOUS_WALL_BASE_FIXED", "continuous_kN"),
        ("Source minus ETABS", "source_minus_etabs_kN"),
        ("Continuous minus ETABS", "continuous_minus_etabs_kN")
    ]
    scale = max(1, max(abs(r[k]) for r in rows for _, k in descriptions))
    for index, (title, key) in enumerate(descriptions):
        xs, ys, zs = [], [], []
        for r in rows:
            x,y,z = r["xyz_m"]
            xs.append(x);ys.append(y);zs.append(z)
        # Reaction magnitude controls marker color/size; physical coordinates stay unaltered.
        values = [r[key] for r in rows]
        hover = [
            f"ETABS {r['etabs_unique']} (label {r['etabs_label']})<br>"
            f"OpenSees node {r['opensees_node']}<br>"
            f"XYZ {r['xyz_m']} m<br>"
            f"ETABS FZ {r['etabs_kN']:,.3f} kN<br>"
            f"OS source FZ {r['source_kN']:,.3f} kN<br>"
            f"OS continuous FZ {r['continuous_kN']:,.3f} kN<br>"
            f"Native ETABS UZ restraint {r['native_restraint']}"
            for r in rows
        ]
        figs.append(go.Scatter3d(
            x=xs, y=ys, z=zs, text=hover, hoverinfo="text", mode="markers+text",
            text=[r["etabs_unique"] if abs(r[key]) > 0.02*scale else "" for r in rows],
            textposition="top center",
            marker=dict(size=[5+13*math.sqrt(abs(v)/scale) for v in values],
                        color=values, colorscale="RdBu", cmin=-scale, cmax=scale,
                        colorbar=dict(title="FZ or ΔFZ (kN)") if index==0 else None),
            name=title, visible=(index==0)))
    buttons = [dict(label=title, method="update",
                    args=[{"visible": [j==i for j in range(len(figs))]},
                          {"title": title+" — base reaction at actual mapped XY,Z"}])
               for i,(title,_) in enumerate(descriptions)]
    fig = go.Figure(data=figs)
    fig.update_layout(
        title="ETABS — base reactions (1.0D + 1.0L)",
        scene=dict(xaxis_title="X (m)", yaxis_title="Y (m)", zaxis_title="Z (m)",
                   aspectmode="data"),
        updatemenus=[dict(type="dropdown", buttons=buttons, x=0, y=1.18)],
        margin=dict(t=125,b=0,l=0,r=0),
        annotations=[dict(text="Markers at REAL node coordinates; color/size encode reaction. "
                          "Zero ETABS FZ is not proof of an unrestrained point. "
                          "Native restraint status is in hover.",
                          showarrow=False,xref="paper",yref="paper",x=0,y=1.08,xanchor="left")]
    )
    plot(fig, filename=str(dest/"Gravity_Base_Reactions_3D.html"),
         auto_open=False, include_plotlyjs=True)
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("reactions_csv")
    p.add_argument("output_dir")
    p.add_argument("--restraints", help="Native ETABS GetRestraint export, explicit reviewed UZ flags")
    a=p.parse_args()
    print(json.dumps(create_audit(a.reactions_csv, a.output_dir, a.restraints), indent=2))


if __name__ == "__main__":
    main()

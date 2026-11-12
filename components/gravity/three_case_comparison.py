"""Compare independently solved 32/76/97 gravity cases, without changing fixities.

All three source files must pass the existing SHA256, load-profile and support-tag
registry checks. Missing runs stay missing; never relabel one run as another.
"""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path

from components.gravity.reaction_case_registry import current_case, SCENARIO_SUPPORTS

CASES = (
    ("ETABS_NONZERO_REACTION_DIAGNOSTIC", "32"),
    ("ETABS_SOURCE_SUPPORTS", "76"),
    ("CONTINUOUS_WALL_BASE_FIXED", "97"),
)


def collect_cases(output_root, model_path, profile="GRAVITY_1.0D_1.0L"):
    """[REF docs/source/components/gravity/three_case_comparison.py.md] Source contract and engineering limitations in linked guide."""
    available = {}
    missing = []
    for strategy, label in CASES:
        entry = current_case(output_root, model_path, scenario=strategy, profile=profile)
        if entry is None:
            missing.append(label + " supports: no current model-fingerprint-matched solved case")
            continue
        path = Path(entry["result_path"])
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if not data.get("ok") or len(data.get("reactions", [])) != SCENARIO_SUPPORTS[strategy]:
            raise ValueError("Incomplete gravity result for " + label + " supports")
        available[label] = (entry, data)
    if not available:
        raise ValueError("No current separately solved 32/76/97 support cases. Run gravity first.")
    loads = [float(entry["applied_load_kN"]) for entry, _ in available.values()]
    if max(loads) - min(loads) > max(0.01, max(loads) * 1e-7):
        raise ValueError("Cases have different applied gravity totals; comparison rejected.")
    return available, missing


def export_case_comparison(output_root, model_path, profile="GRAVITY_1.0D_1.0L"):
    """[REF docs/source/components/gravity/three_case_comparison.py.md]

    Write comparisons and plots from real registered solver responses only."""
    available, missing = collect_cases(output_root, model_path, profile)
    root = Path(output_root) / "Gravity_Case_Comparison"
    root.mkdir(parents=True, exist_ok=True)
    summary = []
    nodes_by_case = {}
    reactions_by_case = {}
    for label, (entry, payload) in available.items():
        nodes = {int(n["tag"]): n for n in payload["nodes"]}
        reactions = {int(r["node_tag"]): r for r in payload["reactions"]}
        if len(nodes) != len(payload["nodes"]) or len(reactions) != len(payload["reactions"]):
            raise ValueError("Duplicate node tags in solved case " + label)
        nodes_by_case[label] = nodes
        reactions_by_case[label] = reactions
        uz = [float(n["uz_m"]) for n in nodes.values()]
        if not uz or not all(math.isfinite(v) for v in uz):
            raise ValueError("Invalid saved displacement data: " + label)
        summary.append({
            "case": label, "support_count": len(reactions),
            "applied_kN": entry["applied_load_kN"],
            "solved_reaction_kN": entry["summed_reaction_kN"],
            "equilibrium_error_percent": entry["equilibrium_error_percent"],
            "min_uz_m": min(uz), "max_uz_m": max(uz),
            "result_path": entry["result_path"],
            "status": "SOLVER_EQUILIBRIUM_ONLY_NOT_ETABS_EQUIVALENCE"
        })
    all_tags = sorted(set().union(*(r.keys() for r in reactions_by_case.values())))
    reaction_rows = []
    for tag in all_tags:
        row = {"node_tag": tag}
        for _strategy, label in CASES:
            r = reactions_by_case.get(label, {}).get(tag)
            row["rz_" + label + "_kN"] = float(r["rz_kN"]) if r else None
        if row.get("rz_32_kN") is not None and row.get("rz_76_kN") is not None:
            row["delta_76_minus_32_kN"] = row["rz_76_kN"] - row["rz_32_kN"]
        else:
            row["delta_76_minus_32_kN"] = None
        reaction_rows.append(row)
    common_nodes = sorted(set.intersection(*(set(v) for v in nodes_by_case.values())))
    displacement_rows = []
    for tag in common_nodes:
        row = {"node_tag": tag}
        for strategy, label in CASES:
            # CASES stores (solver_strategy, display_count). The source
            # node lookup uses "32"/"76"/"97", while public CSV columns
            # retain the existing stable solver-strategy identifiers.
            # Reversing the lookup previously made every column blank.
            n = nodes_by_case.get(label, {}).get(tag)
            for dof in ("ux_m", "uy_m", "uz_m"):
                row[dof + "_" + strategy] = float(n[dof]) if n else None
        displacement_rows.append(row)
    report = {"model_script": str(Path(model_path).resolve()),
              "gravity_profile": profile, "available_cases": list(available),
              "missing_cases": missing, "summary": summary,
              "common_node_count": len(common_nodes),
              "interpretation": "Boundary-condition sensitivity, not physical ETABS equivalence"}
    (root / "Case_Comparison.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    def write_csv(filename, rows):
        if not rows:
            return
        with (root / filename).open("w", encoding="utf-8-sig", newline="") as fp:
            writer = csv.DictWriter(fp, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    write_csv("Support_Reactions_32_76_97.csv", reaction_rows)
    write_csv("Common_Node_Displacements_32_76_97.csv", displacement_rows)
    from openpyxl import Workbook
    wb = Workbook()
    for sheet_name, rows in (
        ("Case summary", summary),
        ("Support reactions", reaction_rows),
        ("Common node displacement", displacement_rows),
    ):
        ws = wb.active if sheet_name == "Case summary" else wb.create_sheet(sheet_name)
        ws.title = sheet_name
        if rows:
            ws.append(list(rows[0]))
            for row in rows:
                ws.append(list(row.values()))
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
    checks = wb.create_sheet("Evidence status")
    checks.append(["Model", str(Path(model_path).resolve())])
    checks.append(["Profile", profile])
    checks.append(["Interpretation", report["interpretation"]])
    for reason in missing:
        checks.append(["MISSING", reason])
    wb.save(root / "Gravity_32_76_97_Comparison.xlsx")
    from matplotlib.figure import Figure
    fig = Figure(figsize=(11, 6), layout="constrained")
    left, right = fig.subplots(1, 2)
    for label, (_, data) in available.items():
        reactions = sorted(data["reactions"], key=lambda r: int(r["node_tag"]))
        left.plot([int(r["node_tag"]) for r in reactions],
                  [float(r["rz_kN"]) for r in reactions], ".", label=label + " supports")
        nodes = sorted(data["nodes"], key=lambda n: float(n["z_m"]))
        levels = sorted(set(float(n["z_m"]) for n in nodes))
        shortening = [min(float(n["uz_m"]) for n in nodes if float(n["z_m"]) == z) * 1000
                      for z in levels]
        right.plot(shortening, levels, label=label + " supports")
    left.set(xlabel="OpenSees support node tag", ylabel="Solved vertical reaction (kN)",
             title="Native solver reactions (not ETABS equivalence)")
    right.set(xlabel="Most negative nodal Uz at level (mm)", ylabel="Elevation (m)",
              title="Solved gravity shortening")
    for ax in (left, right):
        ax.grid(alpha=0.3)
        ax.legend()
    for extension in ("png", "pdf"):
        fig.savefig(root / ("Gravity_32_76_97_Comparison." + extension), dpi=180)
    return report, root, fig

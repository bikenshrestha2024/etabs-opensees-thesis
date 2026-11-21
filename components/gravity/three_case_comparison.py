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



def join_source_etabs_reactions(available, reaction_rows):
    """Join the exact 32-case source-restraint audit to all 32/76/97 tags.

    [REF docs/source/components/gravity/three_case_comparison.py.md]
    Missing native ETABS FZ evidence is marked unavailable; no guessed values.
    """
    if "32" not in available:
        return [], {"status": "NO_CURRENT_PRIMARY32_CASE", "source_support_count": 0}
    _entry, payload = available["32"]
    path = Path(_entry["result_path"]).parent / "ETABS_Nonzero_Reaction_Support_Audit.json"
    if not path.is_file() or path.is_symlink():
        return [], {"status": "SOURCE_ETABS_SUPPORT_AUDIT_NOT_FOUND", "source_support_count": 0}
    audit = json.loads(path.read_text(encoding="utf-8-sig"))
    if (audit.get("mode") != "ETABS_NONZERO_REACTION_DIAGNOSTIC"
            or audit.get("case") != "1. DL + LL"
            or int(audit.get("original_support_count", -1)) != 76
            or int(audit.get("kept_support_count", -1)) != 32):
        raise ValueError("Exact 32-case ETABS source audit identity/support counts disagree")
    mapping = {}
    for source in audit.get("mapping", []):
        tag = int(source["opensees_node"])
        if tag in mapping:
            raise ValueError("Duplicate ETABS source-support mapping at " + str(tag))
        value = float(source["etabs_FZ_kN"])
        if not math.isfinite(value):
            raise ValueError("Nonfinite ETABS source support reaction: " + str(tag))
        flags = source["source_restraints"]
        if (not isinstance(flags, list) or len(flags) != 6 or
                any(flag not in (0, 1, False, True) for flag in flags)):
            raise ValueError("Malformed native six-DOF support at " + str(tag))
        mapping[tag] = source
    if len(mapping) != 76:
        raise ValueError("Source ETABS audit is missing or duplicating restrained points")
    # A 32-only solved run legitimately omits the 44 released source points.
    # Retain these source rows with NULL solver reactions rather than
    # crashing or implicitly fabricating results for the missing 76/97 cases.
    row_by_tag = {}
    for row in reaction_rows:
        tag = int(row["node_tag"])
        if tag in row_by_tag:
            raise ValueError("Duplicate solved support reaction row at " + str(tag))
        row_by_tag[tag] = row
    if not set(mapping).intersection(row_by_tag):
        raise ValueError("No ETABS source-support tags occur in solved reactions")
    expected32 = {tag for tag, source in mapping.items() if source["selected"]}
    saved32 = {int(row["node_tag"]) for row in payload["reactions"]}
    if expected32 != saved32:
        raise ValueError("Source ETABS primary32 support set disagrees with solved run")
    audit_total = float(audit["etabs_total_FZ_kN"])
    computed_total = sum(float(x["etabs_FZ_kN"]) for x in mapping.values())
    if abs(audit_total - computed_total) > max(0.01, abs(audit_total)*1e-7):
        raise ValueError("ETABS source 76-support reactions disagree with declared total")
    rows = []
    for tag in sorted(set(mapping) | set(row_by_tag)):
        row = row_by_tag.get(tag, {})
        source = mapping.get(tag)
        original = float(source["etabs_FZ_kN"]) if source else None
        values = [row.get("rz_"+label+"_kN") for label in ("32", "76", "97")]
        differences = [(v-original if v is not None and original is not None
                        else None) for v in values]
        rows.append(dict(
            opensees_node=tag,
            etabs_unique_name=(str(source["etabs_unique"]) if source else ""),
            source_dof=("".join(str(int(x)) for x in source["source_restraints"])
                        if source else ""),
            source_primary32=(bool(source["selected"]) if source else False),
            original_ETABS_FZ_kN=original,
            opensees_32_Rz_kN=values[0],
            opensees_76_Rz_kN=values[1],
            opensees_97_Rz_kN=values[2],
            delta_32_minus_ETABS_kN=differences[0],
            delta_76_minus_ETABS_kN=differences[1],
            delta_97_minus_ETABS_kN=differences[2],
            status=("SOURCE_RESTRAINED_ZERO_ETABS_REACTION"
                    if source and abs(original) <= float(audit.get("tolerance_kN", 1e-6))
                    else "SOURCE_RESTRAINED" if source else
                    "NON_SOURCE_97_POINT_NO_ETABS_NODE_REACTION")))
    # Unsolved scenarios are NULL, never reported as misleading zero error.
    has_32 = any(x["opensees_32_Rz_kN"] is not None for x in rows)
    has_76 = any(x["opensees_76_Rz_kN"] is not None for x in rows)
    abs32 = (sum(abs(x["delta_32_minus_ETABS_kN"]) for x in rows
                 if x["delta_32_minus_ETABS_kN"] is not None)
             if has_32 else None)
    abs76 = (sum(abs(x["delta_76_minus_ETABS_kN"]) for x in rows
                 if x["delta_76_minus_ETABS_kN"] is not None)
             if has_76 else None)
    additional44 = [x for x in rows if x["status"] ==
                    "SOURCE_RESTRAINED_ZERO_ETABS_REACTION"]
    summary = {
        "status": "SOURCE_NODE_MAPPED_REACTIONS_NOT_STRUCTURAL_EQUIVALENCE",
        "source_support_count": len(mapping),
        "source_fixed_released_in_32": sum(not x["selected"] for x in mapping.values()),
        "source_rows_without_any_solved_reaction": sum(
            tag not in row_by_tag for tag in mapping),
        "available_solved_case_columns": [
            label for label in ("32", "76", "97")
            if any(row.get("rz_"+label+"_kN") is not None
                   for row in row_by_tag.values())],
        "etabs_total_FZ_kN": computed_total,
        "sum_abs_delta_primary_32_kN": abs32,
        "sum_abs_delta_source_76_kN": abs76,
        "opensees_76_reaction_at_source_zero_ETABS_points_kN": (
            sum(x["opensees_76_Rz_kN"] or 0 for x in additional44)
            if has_76 else None),
        "warning": "ETABS zero FZ at a fixed point is not proof of a free DOF; "
                   "compare original 6 DOF, shell/rigid-zone load paths, and "
                   "source-identical analysis before accepting any reaction match.",
        "audit_file": str(path)
    }
    return rows, summary


def export_case_comparison(output_root, model_path, profile="GRAVITY_1.0D_1.0L"):
    """[REF docs/source/components/gravity/three_case_comparison.py.md]

    Write comparisons and plots from real registered solver responses only."""
    available, missing = collect_cases(output_root, model_path, profile)
    from components.gravity.output_ownership import section
    root = section(output_root,"COMPARISONS",create=True) / "Gravity_Case_Comparison"
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

    def write_csv(filename, rows):
        if not rows:
            return
        with (root / filename).open("w", encoding="utf-8-sig", newline="") as fp:
            writer = csv.DictWriter(fp, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    write_csv("Support_Reactions_32_76_97.csv", reaction_rows)
    write_csv("Common_Node_Displacements_32_76_97.csv", displacement_rows)
    joined, native_summary = join_source_etabs_reactions(available, reaction_rows)
    report["etabs_source_support_comparison"] = native_summary
    if joined:
        write_csv("ETABS_OpenSees_All_76_Source_Support_Reactions.csv", joined)
    (root / "Case_Comparison.json").write_text(
        json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
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
    if joined:
        detail = wb.create_sheet("ETABS vs OpenSees all")
        detail.append(list(joined[0]))
        for row in joined:
            detail.append(list(row.values()))
        detail.freeze_panes = "A2"
        detail.auto_filter.ref = detail.dimensions
    checks = wb.create_sheet("Evidence status")
    for key, value in native_summary.items():
        if key != "audit_file":
            if isinstance(value, list):
                value = ", ".join(map(str, value))
            checks.append(["ETABS_SOURCE_"+key, value])
    checks.append(["Model", str(Path(model_path).resolve())])
    checks.append(["Profile", profile])
    checks.append(["Interpretation", report["interpretation"]])
    for reason in missing:
        checks.append(["MISSING", reason])
    from components.gravity.workbook_publishing import publish_workbook
    publish_workbook(wb, root / "Gravity_32_76_97_Comparison.xlsx")
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

"""Attribute ETABS-vs-OpenSees gravity support-reaction deltas to modelling assumptions.

[REF docs/source/tools/gravity_reaction_attribution.py.md]
[REF docs/validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md]

Post-processing diagnostic only. It reads saved comparison CSV files, never
opens an EDB, imports no solver and changes no model, load, mass or stiffness.
Units: kN for forces, m for coordinates and displacements.

What it reports for each reaction-bearing support:
* the OpenSees - ETABS reaction delta;
* a tributary-statics benchmark (applied nodal loads assigned to the nearest
  reaction-bearing support in plan, ties split equally; a Voronoi tributary
  area, not a flexibility solution);
* the residual left after scaling each support group (for example core walls
  and perimeter columns) by its own OpenSees/ETABS total ratio;
* optional axial-stiffness indicator per group from vertical displacements:
  EA_os/EA_etabs ~ (N_os/N_etabs) / (uz_os/uz_etabs);
* the modelling assumption each delta is consistent with.

Status is always DIAGNOSTIC_NOT_ENGINEERING_ACCEPTANCE.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STATUS = "DIAGNOSTIC_NOT_ENGINEERING_ACCEPTANCE"
SCHEMA = "gravity-reaction-attribution-v1"

ASSUMPTIONS = {
    "GROUP_AXIAL_STIFFNESS_SPLIT": (
        "Group-wide redistribution between support groups (for example core walls vs "
        "perimeter columns). Consistent with a different relative axial stiffness: shell "
        "membrane modifiers f11/f22/f12, column AMod, rigid end-zone treatment. Test by "
        "rebuilding with the ETABS elastic comparison settings."),
    "SUPPORT_TOPOLOGY": (
        "ETABS point is restrained but carries no reaction while the OpenSees node does. "
        "Consistent with a different base-support or wall-edge connectivity, not with load "
        "or stiffness of the superstructure."),
    "LOCAL_REDISTRIBUTION": (
        "Residual after group scaling. Consistent with local load-path assumptions: slab "
        "load transfer (ETABS floor meshing vs OpenSees shell mesh), beam rigid end zones, "
        "wall-base support topology inside a group. Needs native element forces to decide."),
    "WITHIN_TOLERANCE": "Delta below the stated tolerance.",
}


def _float(value, name):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Nonfinite value for " + name)
    return number


def _rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def load_support_reactions(path):
    """Read matched supports (x_m, y_m, etabs_global_rz_kN, opensees_rz_kN).

    [REF docs/source/tools/gravity_reaction_attribution.py.md]
    Accepts Gravity_All_Support_Nodes.csv from the direct gravity comparison.
    A blank OpenSees reaction (unmatched support) is read as None.
    """
    out = []
    for row in _rows(path):
        os_raw = row.get("opensees_rz_kN", "")
        out.append(dict(
            label=str(row.get("etabs_point") or row.get("point") or len(out)),
            x=_float(row["x_m"], "x_m"), y=_float(row["y_m"], "y_m"),
            etabs=_float(row["etabs_global_rz_kN"], "etabs_global_rz_kN"),
            opensees=None if os_raw in ("", None) else _float(os_raw, "opensees_rz_kN")))
    if not out:
        raise ValueError("No support rows")
    return out


def load_applied_loads(path):
    """Read applied nodal gravity (x_m, y_m, fz_kN, gravity_factor); downward positive.

    [REF docs/source/tools/gravity_reaction_attribution.py.md]
    The direct comparison writes fz negative downward and the factor already
    applied in the run; the gravity_factor column is multiplied in if present.
    """
    out = []
    for row in _rows(path):
        factor = row.get("gravity_factor")
        factor = 1.0 if factor in ("", None) else _float(factor, "gravity_factor")
        out.append((_float(row["x_m"], "x_m"), _float(row["y_m"], "y_m"),
                    -_float(row["fz_kN"], "fz_kN") * factor))
    if not out:
        raise ValueError("No applied load rows")
    return out


def load_vertical_displacements(model_nodes_csv, etabs_joint_csv, z_ref, *, z_tol=1e-3):
    """Join OpenSees nodal Uz with ETABS joint Uz at elevation z_ref.

    [REF docs/source/tools/gravity_reaction_attribution.py.md]
    model_nodes_csv: Gravity_All_Model_Nodes.csv (etabs_point_id, x_m, y_m, z_m,
    opensees_Uz_m). etabs_joint_csv: ETABS native "Joint Displacements" table
    (UniqueName, Uz) for the same load combination. Returns {(x, y): (uz_os, uz_etabs)}.
    """
    etabs = {}
    for row in _rows(etabs_joint_csv):
        etabs[str(row["UniqueName"])] = _float(row["Uz"], "Uz")
    out = {}
    for row in _rows(model_nodes_csv):
        key = str(row.get("etabs_point_id") or "")
        if key not in etabs or abs(_float(row["z_m"], "z_m") - z_ref) > z_tol:
            continue
        out[(round(_float(row["x_m"], "x_m"), 6), round(_float(row["y_m"], "y_m"), 6))] = (
            _float(row["opensees_Uz_m"], "opensees_Uz_m"), etabs[key])
    return out


def tributary_benchmark(supports, loads, *, min_reaction_kN=1e-6, tie_tol_m2=1e-6):
    """Assign each applied load to the nearest reaction-bearing support in plan.

    [REF docs/source/tools/gravity_reaction_attribution.py.md]
    Reaction-bearing means |ETABS reaction| > min_reaction_kN. Equidistant
    supports share the load equally. Returns a list aligned with ``supports``
    (None for non-bearing supports). Hand statics only: no stiffness, no
    continuity, no vertical transfer.
    """
    bearing = [i for i, s in enumerate(supports) if abs(s["etabs"]) > min_reaction_kN]
    if not bearing:
        raise ValueError("No reaction-bearing support for the tributary benchmark")
    result = [None] * len(supports)
    for i in bearing:
        result[i] = 0.0
    for x, y, fz in loads:
        d2 = [((supports[i]["x"] - x) ** 2 + (supports[i]["y"] - y) ** 2, i) for i in bearing]
        dmin = min(d for d, _ in d2)
        near = [i for d, i in d2 if d <= dmin + tie_tol_m2]
        for i in near:
            result[i] += fz / len(near)
    return result


def group_scaling(supports, groups):
    """Scale ETABS reactions by each group's OpenSees/ETABS total ratio.

    [REF docs/source/tools/gravity_reaction_attribution.py.md]
    ``groups`` is a list of group names aligned with ``supports``. Only
    supports with both reactions are used. Returns ratios, residuals
    (OpenSees - ratio * ETABS, aligned list, None where unused) and the
    fraction of sum|OpenSees - ETABS| removed by the scaling.
    """
    totals = {}
    for s, g in zip(supports, groups):
        if s["opensees"] is None:
            continue
        et, os_ = totals.get(g, (0.0, 0.0))
        totals[g] = (et + s["etabs"], os_ + s["opensees"])
    ratios = {g: (os_ / et if abs(et) > 1e-9 else None) for g, (et, os_) in totals.items()}
    residuals, raw_sum, res_sum = [], 0.0, 0.0
    for s, g in zip(supports, groups):
        if s["opensees"] is None or ratios.get(g) is None:
            residuals.append(None)
            continue
        raw = s["opensees"] - s["etabs"]
        res = s["opensees"] - ratios[g] * s["etabs"]
        residuals.append(res)
        raw_sum += abs(raw)
        res_sum += abs(res)
    explained = 1.0 - res_sum / raw_sum if raw_sum > 0 else 1.0
    return dict(ratios=ratios, totals={g: dict(etabs_kN=t[0], opensees_kN=t[1])
                                       for g, t in totals.items()},
                residuals=residuals, sum_abs_raw_kN=raw_sum,
                sum_abs_residual_kN=res_sum, explained_fraction=explained)


def mirror_asymmetry(supports, *, mirror_x=None, mirror_y=None, tol_m=1e-6):
    """Return the largest |delta(p) - delta(mirror(p))| over matched mirror pairs.

    [REF docs/source/tools/gravity_reaction_attribution.py.md]
    A doubly symmetric delta pattern rules out causes that act on one side
    only (mis-mapped nodes, a missing member on one side, torsion).
    """
    deltas = {(round(s["x"], 6), round(s["y"], 6)): s["opensees"] - s["etabs"]
              for s in supports if s["opensees"] is not None}
    worst, pairs = 0.0, 0
    for (x, y), d in deltas.items():
        for mx, my in ((mirror_x, None), (None, mirror_y)):
            if mx is None and my is None:
                continue
            px = round(2 * mx - x, 6) if mx is not None else x
            py = round(2 * my - y, 6) if my is not None else y
            other = deltas.get((px, py))
            if other is None:
                continue
            pairs += 1
            worst = max(worst, abs(d - other))
    return dict(pairs_checked=pairs, max_asymmetry_kN=worst)


def axial_stiffness_indicator(supports, groups, displacements):
    """Estimate EA_os/EA_etabs per group from reactions and vertical displacements.

    [REF docs/source/tools/gravity_reaction_attribution.py.md]
    ratio = (sum N_os / sum N_etabs) / (mean uz_os / mean uz_etabs) over the
    group's support plan positions found in ``displacements``. A value near
    1 means both programs give the group the same axial flexibility; a value
    far from 1 points to a stiffness-basis difference. Estimate only: the
    base reaction ratio stands in for the axial-force profile up the height.
    """
    out = {}
    for g in sorted(set(groups)):
        members = [s for s, gg in zip(supports, groups) if gg == g and s["opensees"] is not None]
        uz = [displacements.get((round(s["x"], 6), round(s["y"], 6))) for s in members]
        uz = [u for u in uz if u is not None]
        n_et = sum(s["etabs"] for s in members)
        n_os = sum(s["opensees"] for s in members)
        if not uz or abs(n_et) < 1e-9:
            out[g] = None
            continue
        u_os = sum(u[0] for u in uz) / len(uz)
        u_et = sum(u[1] for u in uz) / len(uz)
        if abs(u_et) < 1e-12 or abs(u_os) < 1e-12:
            out[g] = None
            continue
        out[g] = dict(force_ratio=n_os / n_et, displacement_ratio=u_os / u_et,
                      axial_stiffness_ratio=(n_os / n_et) / (u_os / u_et),
                      displacement_points=len(uz))
    return out


def classify(support, residual, *, tolerance_kN=50.0, min_reaction_kN=1e-6,
             explained_share=0.5):
    """Name the assumption a single delta is consistent with.

    [REF docs/source/tools/gravity_reaction_attribution.py.md]
    Rules: zero ETABS and nonzero OpenSees reaction -> SUPPORT_TOPOLOGY;
    |delta| <= tolerance -> WITHIN_TOLERANCE; group scaling leaves at most
    ``explained_share`` of |delta| -> GROUP_AXIAL_STIFFNESS_SPLIT; otherwise
    LOCAL_REDISTRIBUTION.
    """
    if support["opensees"] is None:
        return "UNMATCHED"
    delta = support["opensees"] - support["etabs"]
    if abs(support["etabs"]) <= min_reaction_kN and abs(support["opensees"]) > tolerance_kN:
        return "SUPPORT_TOPOLOGY"
    if abs(delta) <= tolerance_kN:
        return "WITHIN_TOLERANCE"
    if residual is not None and abs(residual) <= explained_share * abs(delta):
        return "GROUP_AXIAL_STIFFNESS_SPLIT"
    return "LOCAL_REDISTRIBUTION"


def in_box(box):
    """Return a plan-box membership test for (x, y); box = (xmin, xmax, ymin, ymax).

    [REF docs/source/tools/gravity_reaction_attribution.py.md]
    """
    xmin, xmax, ymin, ymax = (float(v) for v in box)
    return lambda x, y: xmin - 1e-6 <= x <= xmax + 1e-6 and ymin - 1e-6 <= y <= ymax + 1e-6


def attribute(supports, loads, *, group_box, displacements=None, mirror_x=None,
              mirror_y=None, tolerance_kN=50.0):
    """Build the per-support attribution table and summary.

    [REF docs/source/tools/gravity_reaction_attribution.py.md]
    ``group_box`` defines the "core" group in plan; every other support is
    "perimeter". No defaults are invented for the box: the caller supplies it.
    """
    inside = in_box(group_box)
    groups = ["core" if inside(s["x"], s["y"]) else "perimeter" for s in supports]
    trib = tributary_benchmark(supports, loads)
    scaling = group_scaling(supports, groups)
    rows = []
    for s, g, t, r in zip(supports, groups, trib, scaling["residuals"]):
        delta = None if s["opensees"] is None else s["opensees"] - s["etabs"]
        tag = classify(s, r, tolerance_kN=tolerance_kN)
        rows.append(dict(
            label=s["label"], x_m=s["x"], y_m=s["y"], group=g,
            etabs_kN=s["etabs"], opensees_kN=s["opensees"], delta_os_minus_etabs_kN=delta,
            tributary_kN=t,
            etabs_minus_tributary_kN=None if t is None else s["etabs"] - t,
            opensees_minus_tributary_kN=None if (t is None or s["opensees"] is None)
            else s["opensees"] - t,
            residual_after_group_scaling_kN=r, consistent_with=tag))
    trib_groups = {}
    for g, t in zip(groups, trib):
        if t is not None:
            trib_groups[g] = trib_groups.get(g, 0.0) + t
    counts = {}
    for row in rows:
        counts[row["consistent_with"]] = counts.get(row["consistent_with"], 0) + 1
    worst = max((row for row in rows if row["delta_os_minus_etabs_kN"] is not None),
                key=lambda row: abs(row["delta_os_minus_etabs_kN"]), default=None)
    return dict(
        schema=SCHEMA, status=STATUS, units="kN, m",
        group_box_m=list(map(float, group_box)), tolerance_kN=tolerance_kN,
        applied_total_kN=sum(f for _, _, f in loads),
        tributary_by_group_kN=trib_groups,
        group_scaling={k: v for k, v in scaling.items() if k != "residuals"},
        symmetry=mirror_asymmetry(supports, mirror_x=mirror_x, mirror_y=mirror_y),
        axial_stiffness_indicator=(axial_stiffness_indicator(supports, groups, displacements)
                                   if displacements else None),
        largest_delta=worst, classification_counts=counts,
        assumptions=ASSUMPTIONS, supports=rows,
        limitations=[
            "Tributary benchmark is plan-nearest statics; it ignores continuity and vertical transfer.",
            "Group scaling identifies a pattern; it does not prove a cause.",
            "Axial-stiffness indicator uses base reactions as a proxy for the axial-force profile.",
            "Native ETABS element forces are needed to decide LOCAL_REDISTRIBUTION rows.",
        ])


COLUMNS = ("label", "x_m", "y_m", "group", "etabs_kN", "opensees_kN",
           "delta_os_minus_etabs_kN", "tributary_kN", "etabs_minus_tributary_kN",
           "opensees_minus_tributary_kN", "residual_after_group_scaling_kN", "consistent_with")


def write_run(report, export_dir, case_id, *, state="AS_CONFIGURED", model_sha256=None,
              inputs=()):
    """Write the report into a new run folder under the uniform output standard.

    [REF docs/OUTPUT_FOLDER_STANDARD.md]
    Creates <export>/02_GRAVITY/RUNS/<state>/<case>/<run id>/ via
    output_contract.create_case_run; JSON and CSV go to 05_COMPARISONS, input
    hashes to 00_INPUT_SOURCE. The case manifest keeps solver_status CREATED
    and structural_acceptance NOT_VERIFIED (no solver ran).
    """
    import hashlib
    from components.inputs.output_contract import atomic_json, create_case_run, write_table

    run = create_case_run(export_dir, "GRAVITY", case_id, state=state,
                          model_sha256=model_sha256)
    hashes = {}
    for path in inputs:
        p = Path(path)
        hashes[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    atomic_json(run / "00_INPUT_SOURCE" / "GRAVITY_REACTION_ATTRIBUTION_INPUTS.json",
                dict(status=STATUS, input_sha256=hashes))
    atomic_json(run / "05_COMPARISONS" / "GRAVITY_REACTION_ATTRIBUTION.json",
                dict(report, input_sha256=hashes))
    write_table(run / "05_COMPARISONS" / "GRAVITY_REACTION_ATTRIBUTION_SUPPORTS.csv",
                [{k: ("" if row[k] is None else row[k]) for k in COLUMNS}
                 for row in report["supports"]], columns=COLUMNS)
    return run


def main(argv=None):
    """CLI entry point; see the source guide for arguments.

    [REF docs/source/tools/gravity_reaction_attribution.py.md]
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--supports", required=True, help="Gravity_All_Support_Nodes.csv")
    ap.add_argument("--applied", required=True,
                    help="OpenSees_Applied_Nodal_Gravity_By_Pattern.csv")
    ap.add_argument("--core-box", required=True, nargs=4, type=float,
                    metavar=("XMIN", "XMAX", "YMIN", "YMAX"))
    ap.add_argument("--model-nodes", help="Gravity_All_Model_Nodes.csv (optional)")
    ap.add_argument("--etabs-joint-displacements",
                    help="ETABS native Joint Displacements table CSV (optional)")
    ap.add_argument("--z-ref", type=float, help="Elevation (m) for the displacement indicator")
    ap.add_argument("--mirror-x", type=float)
    ap.add_argument("--mirror-y", type=float)
    ap.add_argument("--tolerance-kN", type=float, default=50.0)
    ap.add_argument("--export-dir", help="ETABS export case root; omit to print only")
    ap.add_argument("--case-id", default="REACTION_ATTRIBUTION")
    ap.add_argument("--state", default="AS_CONFIGURED")
    args = ap.parse_args(argv)
    supports = load_support_reactions(args.supports)
    loads = load_applied_loads(args.applied)
    displacements = None
    inputs = [args.supports, args.applied]
    if args.model_nodes and args.etabs_joint_displacements:
        if args.z_ref is None:
            ap.error("--z-ref is required with displacement inputs")
        displacements = load_vertical_displacements(
            args.model_nodes, args.etabs_joint_displacements, args.z_ref)
        inputs += [args.model_nodes, args.etabs_joint_displacements]
    report = attribute(supports, loads, group_box=args.core_box, displacements=displacements,
                       mirror_x=args.mirror_x, mirror_y=args.mirror_y,
                       tolerance_kN=args.tolerance_kN)
    summary = {k: report[k] for k in ("status", "applied_total_kN", "tributary_by_group_kN",
                                      "group_scaling", "symmetry",
                                      "axial_stiffness_indicator", "classification_counts")}
    if args.export_dir:
        run = write_run(report, args.export_dir, args.case_id, state=args.state, inputs=inputs)
        summary["run_dir"] = str(run)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

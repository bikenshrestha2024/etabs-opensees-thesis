"""Audit q*A/4 slab-node loading against isoparametric consistent forces.

READ-ONLY source; reports only. Uses no OpenSees executable. See
docs/source/tools/audit_shell_gravity_transfer.py.md for physics/limitations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path


def quad_equivalent_nodal_forces(xy, pressure=1.0):
    """Integrate N_i q det(J) at four 2x2 Gauss points for a planar quad.

    Coordinates in metres, constant pressure in kN/m²; returns nodal Fz (kN).
    Counter-clockwise element order required; a reversed or inverted element
    raises instead of being quietly repaired, because element orientation
    may control OpenSees shell local axes and physical pressure direction.
    """
    if len(xy) != 4 or any(len(v) < 2 for v in xy):
        raise ValueError("Four planar quadrilateral nodes are required")
    points = [(float(row[0]), float(row[1])) for row in xy]
    if not all(math.isfinite(v) for row in points for v in row):
        raise ValueError("Nonfinite shell node coordinate")
    q = float(pressure)
    if not math.isfinite(q):
        raise ValueError("Nonfinite pressure")
    gp = 1.0 / math.sqrt(3.0)
    result = [0.0] * 4
    area = 0.0
    for xi in (-gp, gp):
        for eta in (-gp, gp):
            N = [(1-xi)*(1-eta)/4, (1+xi)*(1-eta)/4,
                 (1+xi)*(1+eta)/4, (1-xi)*(1+eta)/4]
            dx = [-(1-eta)/4, (1-eta)/4, (1+eta)/4, -(1+eta)/4]
            dy = [-(1-xi)/4, -(1+xi)/4, (1+xi)/4, (1-xi)/4]
            x_xi = sum(dx[i] * points[i][0] for i in range(4))
            x_eta = sum(dy[i] * points[i][0] for i in range(4))
            y_xi = sum(dx[i] * points[i][1] for i in range(4))
            y_eta = sum(dy[i] * points[i][1] for i in range(4))
            det = x_xi*y_eta - x_eta*y_xi
            if det <= 1e-12:
                raise ValueError("Degenerate or inverted floor quadrilateral")
            area += det
            for i in range(4):
                result[i] += q * N[i] * det
    return result, area


def review_export(model_json, *, report_limit=100):
    """Compare assembled equal-four-node allocation to consistent shell forces.

    A unit vertical pressure is used as a shape diagnostic only. This does
    NOT infer the original CSI uniform vs uniform-to-frame assignment type,
    nor certify shell-to-beam connectivity or actual gravity results.
    """
    model = Path(model_json).expanduser().resolve(strict=True)
    data = json.loads(model.read_text(encoding="utf-8-sig"))
    nodes = {int(k): v for k, v in data["nodes"].items()}
    checked = 0
    irregular = []
    invalid = []
    for i, shell in enumerate(data.get("shells", []), 1):
        if str(shell.get("category", "")).upper() != "FLOOR":
            continue
        tag = shell.get("object", str(i))
        tags = [int(n) for n in shell["nodes"]]
        try:
            if len(tags) != 4 or any(tag not in nodes for tag in tags):
                raise ValueError("Missing or non-quad shell connectivity")
            xyz = [list(map(float, nodes[n])) for n in tags]
            if max(v[2] for v in xyz) - min(v[2] for v in xyz) > 1e-6:
                raise ValueError("Nonhorizontal floor shell: projected-vs-actual area requires separate audit")
            consistent, area = quad_equivalent_nodal_forces(xyz)
            source_area = float(shell["area"])
            if abs(source_area-area) > max(1e-7, area*1e-5):
                raise ValueError("Exported shell area != integrated physical area")
            lump = source_area / 4.0
            difference = [c-lump for c in consistent]
            relative = max(abs(v) for v in difference) / max(area, 1e-12)
            checked += 1
            if relative > 1e-8:
                irregular.append({"source_object": str(tag),
                                  "node_tags": tags,
                                  "area_m2": area,
                                  "equal_share_unit_q_kN": lump,
                                  "consistent_unit_q_kN": consistent,
                                  "nodal_difference_unit_q_kN": difference,
                                  "maximum_fraction_of_total": relative})
        except (ValueError, KeyError, TypeError) as exc:
            invalid.append({"source_object": str(tag), "node_tags": tags,
                            "reason": str(exc)})
    sha = hashlib.sha256(model.read_bytes()).hexdigest()
    return {"source_model": str(model), "source_sha256": sha,
            "scope": "UNIFORM_PRESSURE_FLOOR_SHELL_LOAD_VECTOR_SCREENING_ONLY",
            "total_floor_shells": checked + len(invalid),
            "valid_floor_shells": checked,
            "nonuniform_nodal_share_cells": len(irregular),
            "invalid_or_unresolved_cells": len(invalid),
            "largest_shape_errors": sorted(
                irregular, key=lambda d: -d["maximum_fraction_of_total"])[:report_limit],
            "invalid_cells": invalid[:report_limit],
            "unlisted_issues": max(0, len(irregular) - report_limit) +
                               max(0, len(invalid) - report_limit),
            "solver_equivalence": "NOT_TESTED",
            "edb_load_assignment_type": "NOT_VERIFIED",
            "source_original_unchanged": True,
            "interpretation": (
                "For regular parallelogram cells q*A/4 is consistent. For a "
                "distorted quadrilateral the same total q*A can produce "
                "different nodal forces, affecting load path. This audit "
                "does not automatically change loads or mesh."),
            "status": "REVIEW_REQUIRED" if irregular or invalid else
                      "GEOMETRIC_LOAD_VECTOR_PATCH_PASS_ONLY"}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-json", help="OpenSees_Complete_Model_Data_V118.json")
    p.add_argument("--out", help="new .json file; existing reports refused")
    args = p.parse_args(argv)
    path = args.model_json
    if not path:
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()
        try:
            path = filedialog.askopenfilename(
                title="Select current OpenSees model data",
                filetypes=[("JSON", "*.json")])
        finally:
            root.destroy()
    if not path:
        raise SystemExit("No source selected; no changes made")
    out = (Path(args.out).expanduser().resolve() if args.out else
           Path(path).resolve().parent.parent /
           ("Shell_Load_Patch_Review_" +
            datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"))
    if out.exists():
        raise FileExistsError("Audit output already exists; no overwrite: " + str(out))
    report = review_export(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps({
        "output": str(out), "source_sha256": report["source_sha256"],
        "floor_shells": report["total_floor_shells"],
        "nonuniform_share_cells": report["nonuniform_nodal_share_cells"],
        "invalid_cells": report["invalid_or_unresolved_cells"],
        "status": report["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

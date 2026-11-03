"""Read-only preflight for nonlinear wall geometry and first-step failure suspects.

The audit cannot establish constitutive stability or the first failing element:
it checks source quadruple geometry prior to calling OpenSees. Wall model:
Kolozvari, Lopez & Massone (2023), doi:10.1016/j.engstruct.2023.116700.
All lengths are meters; numerical tolerances are geometric, not acceptance
limits for cyclic displacement or structural capacity.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

SUSPECT_SOURCE_OBJECTS = ("354", "482")


def _sub(a, b):
    return tuple(float(x) - float(y) for x, y in zip(a, b))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def _norm(v):
    return math.sqrt(sum(x*x for x in v))


def inspect_wall_geometry(model_data, *, tolerance_m=1e-7):
    """Inspect every source wall quad, record suspect objects and invalid cells.

    This audit expects the *assembled* model data with 3D nodal coordinates.
    Adjacent wall panels, openings and confinement are not validated here.
    """
    nodes = model_data.get("nodes", {})
    walls = [e for e in model_data.get("shells", [])
             if e.get("category") == "SHEAR WALL"]
    rows = []
    for index, element in enumerate(model_data.get("shells", [])):
        if element.get("category") != "SHEAR WALL":
            continue
        obj = str(element.get("object"))
        record = {"source_area": obj,
                  "estimated_solver_tag": 100001+len(model_data.get("frames", []))+index,
                  "node_tags": element.get("nodes"),
                  "suspected_from_v168": obj in SUSPECT_SOURCE_OBJECTS,
                  "status": "REVIEW_REQUIRED", "errors": []}
        tags = element.get("nodes", [])
        try:
            if len(tags) != 4 or len(set(map(str, tags))) != 4:
                raise ValueError("Wall element requires four distinct nodes")
            points = [tuple(float(x) for x in nodes[str(n)]) for n in tags]
            if any(len(p) != 3 or any(not math.isfinite(x) for x in p) for p in points):
                raise ValueError("Nonfinite/invalid 3D node coordinates")
            a, b = _sub(points[1], points[0]), _sub(points[3], points[0])
            cross = _cross(a, b)
            area = _norm(cross)
            if area <= tolerance_m*tolerance_m:
                raise ValueError("Degenerate wall quad has near-zero area")
            width = _norm(a)
            height = _norm(b)
            close = _norm(_sub(points[2],
                              tuple(points[1][k]+points[3][k]-points[0][k] for k in range(3))))
            if close > tolerance_m:
                raise ValueError("Quad is not a parallelogram")
            normal = tuple(c/area for c in cross)
            if abs(normal[2]) > 0.1:
                raise ValueError("Expected vertical wall; quad has significant Z normal component")
            thickness = float(element.get("properties", {}).get("thickness", 0))
            if not math.isfinite(thickness) or thickness <= 0:
                raise ValueError("Nonpositive wall thickness")
            record.update(area_m2=area, edge01_m=width, edge03_m=height,
                          thickness_m=thickness, normal=normal,
                          z_extent_m=max(p[2] for p in points)-min(p[2] for p in points),
                          status="GEOMETRY_SCREEN_PASSED")
        except (ValueError, TypeError, KeyError, IndexError) as exc:
            record["status"] = "INVALID_GEOMETRY"
            record["errors"].append(str(exc))
        rows.append(record)
    return {"status": "INVALID" if any(r["status"] == "INVALID_GEOMETRY" for r in rows)
            else "REVIEW_REQUIRED" if rows else "MISSING_WALLS",
            "wall_quads": len(rows),
            "suspect_source_areas": list(SUSPECT_SOURCE_OBJECTS),
            "panels": rows,
            "limitations": [
                "A geometry screen is not a material convergence test.",
                "Wall openings, adjacent mesh continuity, connected coupling beams, axial load and reinforcement require separate verification.",
                "Estimated element tags are only valid for the unchanged assembly tag ordering.",
                "Post-failure NaN does not establish the initiating element.",
            ]}


def write_wall_audit(model_data, target):
    report = inspect_wall_geometry(model_data)
    path = Path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    if report["status"] in ("INVALID", "MISSING_WALLS"):
        raise ValueError(f"Wall preflight {report['status']}: inspect {path}")
    return report

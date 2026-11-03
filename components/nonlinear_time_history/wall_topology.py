"""Model-geometry gate for declared rectangular wall openings.

Source geometry must come from independently checked ETABS opening schedules.
Detects whether a declared void intersects assembled wall quad interiors.
This does not validate wall materials, coupling-beam flexure, nor wall torsion.
Research context: DOI 10.1007/s10518-025-02353-0 (asymmetric openings).
"""
from __future__ import annotations
import json
import math
from pathlib import Path


def validate_openings(model_data, declarations, tol=1e-6):
    """Compare source-defined opening rectangles against wall elements.

    Rectangles are given in global x/y/z meters and must be a genuine
    vertical plane (constant x or constant y). This first-pass gate is
    intentionally conservative: non-rectangular/non-axis-aligned walls
    require a dedicated source mesh comparison, not automatic approval.
    """
    if not isinstance(declarations, list):
        raise ValueError("Opening declarations must be a list")
    nodes=model_data.get("nodes",{})
    shells=[e for e in model_data.get("shells",[])
            if e.get("category")=="SHEAR WALL"]
    report=[]
    for index,o in enumerate(declarations):
        fields=("id","plane","constant_m","horizontal_min_m",
                "horizontal_max_m","z_min_m","z_max_m","source")
        if any(not o.get(key) and o.get(key)!=0 for key in fields):
            raise ValueError(f"Opening {index}: missing required geometry/source field")
        plane=str(o["plane"]).upper()
        if plane not in ("XZ","YZ"):
            raise ValueError("Only axis-aligned vertical XZ/YZ opening planes are supported")
        x0,x1,z0,z1=[float(o[k]) for k in
             ("horizontal_min_m","horizontal_max_m","z_min_m","z_max_m")]
        c=float(o["constant_m"])
        if not all(math.isfinite(n) for n in (x0,x1,z0,z1,c)) or x1<=x0 or z1<=z0:
            raise ValueError(f"Opening {o['id']}: invalid coordinates")
        overlapping=[]
        bordering=[]
        for e in shells:
            try:
                ps=[[float(v) for v in nodes[str(tag)]] for tag in e["nodes"]]
                horizontal=[p[0 if plane=="XZ" else 1] for p in ps]
                transverse=[p[1 if plane=="XZ" else 0] for p in ps]
                vertical=[p[2] for p in ps]
            except (KeyError,TypeError,ValueError) as exc:
                raise ValueError("Incomplete assembled wall mesh") from exc
            if max(abs(a-c) for a in transverse)>tol:
                continue
            low,high=min(horizontal),max(horizontal)
            bottom,top=min(vertical),max(vertical)
            intersects=min(high,x1)-max(low,x0)>tol and min(top,z1)-max(bottom,z0)>tol
            if intersects:
                overlapping.append(str(e.get("object")))
            near=(abs(low-x1)<=tol or abs(high-x0)<=tol or
                  abs(top-z0)<=tol or abs(bottom-z1)<=tol)
            if near and min(high,x1)>=max(low,x0)-tol and min(top,z1)>=max(bottom,z0)-tol:
                bordering.append(str(e.get("object")))
        record={"id":str(o["id"]),"source":str(o["source"]),
                "plane":plane,"overlapping_wall_objects":overlapping,
                "bordering_wall_objects":bordering,
                "status":"BLOCKED_FILLED_OPENING" if overlapping else
                         "REVIEW_REQUIRED_NO_BORDER" if not bordering else "VOID_SCREEN_PASSED"}
        report.append(record)
    return {"status":"BLOCKED" if any(r["status"]!="VOID_SCREEN_PASSED" for r in report)
            else "GEOMETRY_SCREEN_PASSED",
            "openings":report,
            "limitations":["Rectangular void check only; not proof of coupling-beam nonlinear behavior.",
                           "Each opening must originate from ETABS source mesh/drawings.",
                           "A wall core can contain holes not declared here. Zero declarations is not verification."]}


def write_opening_report(model_data, input_manifest, output_path):
    with Path(input_manifest).open(encoding="utf-8-sig") as f:
        manifest=json.load(f)
    if not isinstance(manifest,dict) or "wall_openings" not in manifest:
        raise ValueError("Opening manifest requires wall_openings key")
    report=validate_openings(model_data,manifest["wall_openings"])
    report["declared_count"]=len(manifest["wall_openings"])
    report["source_manifest"]=str(Path(input_manifest).resolve())
    if not report["declared_count"]:
        report["status"]="UNVERIFIED_NO_DECLARATIONS"
    target=Path(output_path)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    if report["status"]=="BLOCKED":
        raise ValueError(f"Wall opening geometry mismatch: {target}")
    return report

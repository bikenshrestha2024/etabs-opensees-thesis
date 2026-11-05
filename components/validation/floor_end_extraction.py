"""Reproducible floor-end displacement mapping for NBC 105:2025 §5.4.2.

The code reference uses DIRECTIONAL (Ux for X; Uy for Y) horizontal
displacements at *opposite ends of the same floor* for CENTERED-CM loading.
Do NOT use sqrt(Ux²+Uy²), independent peak envelopes or mismatched times.
Do NOT assume an outrigger connection is a perimeter floor end.

Inputs are source-exported node geometry and nodal response CSVs, never
modified. Coordinates are in metres; displacements are signed metres.
Rows are tagged by model_state, case, axis, story and common step.
This module does not read .EDB binaries or pretend ETABS/OpenSees node IDs
are the same. Geometry node IDs must be explicitly mapped per program.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

from components.validation.torsion_check import check_torsional_irregularity

GEOMETRY_COLUMNS=("node_id","storey","x_m","y_m","z_m","is_perimeter")
RESULT_COLUMNS=("node_id","storey","limit_state","case","axis","step",
                "ux_m","uy_m","centered_cm_load","response_basis")
TRUE=("true","1","yes")
FALSE=("false","0","no")


def read_csv(path,required):
    with Path(path).open("r",newline="",encoding="utf-8-sig") as stream:
        reader=csv.DictReader(stream)
        missing=[c for c in required if c not in (reader.fieldnames or [])]
        if missing:raise ValueError(f"{path}: missing required columns {missing}")
        return list(reader)


def _bool(raw,name):
    text=str(raw).strip().lower()
    if text in TRUE:return True
    if text in FALSE:return False
    raise ValueError(f"{name}: explicitly set true/false; never infer physical evidence.")


def _finite(value,label):
    n=float(value)
    if not math.isfinite(n):
        raise ValueError(f"Non-finite {label}")
    return n


def sha256(path):
    digest=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda:stream.read(1048576),b""):digest.update(chunk)
    return digest.hexdigest()


def _candidate_pairs(nodes,axis,end_tol_m,alignment_tol_m):
    """Only perimeter nodes on opposite perpendicular-coordinate extremes.

    For X loading, compare Y-min to Y-max ends with similar longitudinal X.
    For Y loading, compare X-min to X-max ends with similar longitudinal Y.
    A re-entrant plan may lack a matching cross-plan end at some bays: these
    are NOT fabricated; a missing candidate means NOT EVALUATED.
    All eligible pairs are screened rather than assuming a single corner.
    """
    perpendicular="y_m" if axis=="X" else "x_m"
    longitudinal="x_m" if axis=="X" else "y_m"
    perimeters=[n for n in nodes if n["is_perimeter"]]
    if len(perimeters)<2:return []
    minimum=min(n[perpendicular] for n in perimeters)
    maximum=max(n[perpendicular] for n in perimeters)
    if maximum-minimum<=end_tol_m:
        return []
    near_min=[n for n in perimeters if n[perpendicular]-minimum<=end_tol_m]
    near_max=[n for n in perimeters if maximum-n[perpendicular]<=end_tol_m]
    return [(a,b) for a in near_min for b in near_max
            if a["node_id"]!=b["node_id"] and
            abs(a[longitudinal]-b[longitudinal])<=alignment_tol_m]


def map_floor_ends(geometry_rows,result_rows,*,limit_state,source,
                   end_tol_m=0.05,alignment_tol_m=0.10):
    """Produce reviewed opposite-end pairs and independent governing reports.

    Required centered reference cases have ONE step per (case,axis,storey);
    no independent-time maxima are allowed. Caller must assert source
    evidence in centered_cm_load and response_basis explicitly. For
    response-spectrum/time-history rows this function refuses NBC compliance
    inference; use those as separate exploratory analyses instead.
    """
    state=str(limit_state).upper()
    if state not in ("ULS","SLS"):raise ValueError("One source ULS or SLS is required")
    if source not in ("ETABS","OPENSEES"):raise ValueError("source is ETABS or OPENSEES")
    end_tol_m=_finite(end_tol_m,"end tolerance")
    alignment_tol_m=_finite(alignment_tol_m,"alignment tolerance")
    if min(end_tol_m,alignment_tol_m)<0:raise ValueError("Negative geometric tolerance")
    geometry={}
    for original in geometry_rows:
        node=str(original["node_id"]).strip()
        st=str(original["storey"]).strip()
        if not node or not st:raise ValueError("Missing node/storey identifier")
        key=(st,node)
        if key in geometry:raise ValueError(f"Duplicate geometry node {key}")
        geometry[key]={"node_id":node,"storey":st,
                       "x_m":_finite(original["x_m"],"x_m"),
                       "y_m":_finite(original["y_m"],"y_m"),
                       "z_m":_finite(original["z_m"],"z_m"),
                       "is_perimeter":_bool(original["is_perimeter"],"is_perimeter")}
    groups={}
    for original in result_rows:
        st=str(original["storey"]).strip()
        node=str(original["node_id"]).strip()
        if (st,node) not in geometry:
            raise ValueError("Displacement node has no geometric record: "+str((st,node)))
        found=str(original["limit_state"]).upper()
        if found!=state:raise ValueError("Cross-state result blocked: "+found+" vs "+state)
        axis=str(original["axis"]).upper()
        if axis not in ("X","Y"):raise ValueError("Axis X or Y required")
        case=str(original["case"]).strip()
        step=str(original["step"]).strip()
        if not case or not step:raise ValueError("Explicit case and analysis step required")
        if not _bool(original["centered_cm_load"],"centered_cm_load"):
            raise ValueError("NBC §5.4.2 requires a centered-CM load case, not ±eccentricity")
        basis=str(original["response_basis"]).strip()
        if basis!="signed_centered_linear_increment":
            raise ValueError("Only signed_centered_linear_increment response basis is a code-screen input")
        ux=_finite(original["ux_m"],"ux_m");uy=_finite(original["uy_m"],"uy_m")
        casekey=(st,axis,case)
        record=groups.setdefault(casekey,{"steps":set(),"nodes":{}})
        record["steps"].add(step)
        if node in record["nodes"]:raise ValueError("Duplicate response for node/case/story/axis")
        record["nodes"][node]=(ux,uy)
    per_floor={}
    for (st,axis,case),record in sorted(groups.items()):
        if len(record["steps"])!=1:
            raise ValueError("More than one response step in a centered-load case: do not combine different times")
        nodes=[n for (floor,_),n in geometry.items() if floor==st]
        pairs=_candidate_pairs(nodes,axis,end_tol_m,alignment_tol_m)
        detailed=[]
        for a,b in pairs:
            if a["node_id"] not in record["nodes"] or b["node_id"] not in record["nodes"]:
                continue
            index=0 if axis=="X" else 1
            ua=record["nodes"][a["node_id"]][index]
            ub=record["nodes"][b["node_id"]][index]
            verification=check_torsional_irregularity([{
                "limit_state":state,"axis":axis,"case":case,"storey":st,
                "end_a_m":ua,"end_b_m":ub,
                "centered_cm_load":True,"same_end_basis":True,
            }])[0]
            detailed.append(dict(source=source,limit_state=state,axis=axis,
                case=case,storey=st,step=next(iter(record["steps"])),
                node_a=a["node_id"],node_b=b["node_id"],
                x_a_m=a["x_m"],y_a_m=a["y_m"],
                x_b_m=b["x_m"],y_b_m=b["y_m"],
                signed_u_a_m=ua,signed_u_b_m=ub,
                separation_m=abs((b["y_m"]-a["y_m"]) if axis=="X" else
                                 (b["x_m"]-a["x_m"])),
                longitudinal_mismatch_m=abs((a["x_m"]-b["x_m"]) if axis=="X" else
                                         (a["y_m"]-b["y_m"])),
                ratio=verification["ratio"],status=verification["status"],
                design_acceptance_blocked=verification["design_acceptance_blocked"],
                reason=verification["reason"]))
        per_floor[(st,axis,case)]=detailed
    rows=[];governing=[]
    for (st,axis,case),details in sorted(per_floor.items()):
        rows+=details
        if not details:
            governing.append(dict(source=source,limit_state=state,axis=axis,
                case=case,storey=st,ratio=None,status="NOT EVALUATED",
                design_acceptance_blocked=True,
                reason="No reviewed opposite-perimeter ends with matched longitudinal coordinates and responses"))
        else:
            def priority(r):
                return math.inf if r["status"]=="UNBOUNDED" else (
                    float(r["ratio"]) if r["ratio"] is not None else -1)
            governing.append(dict(max(details,key=priority)))
    return rows,governing


def write_outputs(folder,geometry_file,displacement_file,*,limit_state,source,
                  end_tol_m=0.05,alignment_tol_m=0.10):
    """CSV and JSON audit with input hashes, never overwrite source inputs."""
    geometry_file=Path(geometry_file).resolve()
    displacement_file=Path(displacement_file).resolve()
    out=Path(folder).resolve();out.mkdir(parents=True,exist_ok=True)
    if geometry_file.parent==out or displacement_file.parent==out:
        # Output filenames are fixed; this check makes accidental source-file
        # overlap highly visible instead of overwriting imported evidence.
        if geometry_file.name in ("Floor_End_Pairs.csv","Floor_End_Governing.csv") or displacement_file.name in ("Floor_End_Pairs.csv","Floor_End_Governing.csv"):
            raise ValueError("Source filename conflicts with generated output")
    pairs,governing=map_floor_ends(read_csv(geometry_file,GEOMETRY_COLUMNS),
        read_csv(displacement_file,RESULT_COLUMNS),
        limit_state=limit_state,source=source,
        end_tol_m=end_tol_m,alignment_tol_m=alignment_tol_m)
    for name,table in (("Floor_End_Pairs.csv",pairs),("Floor_End_Governing.csv",governing)):
        target=out/name
        if target in (geometry_file,displacement_file):raise ValueError("Refusing to overwrite source CSV")
        cols=list(dict.fromkeys(k for row in table for k in row))
        if not cols:cols=["source","limit_state","axis","case","storey","status","reason"]
        with target.open("w",newline="",encoding="utf-8-sig") as stream:
            writer=csv.DictWriter(stream,fieldnames=cols,extrasaction="ignore")
            writer.writeheader();writer.writerows(table)
    manifest=dict(source=source,limit_state=limit_state,
        geometry_csv=str(geometry_file),geometry_sha256=sha256(geometry_file),
        displacements_csv=str(displacement_file),displacements_sha256=sha256(displacement_file),
        end_tol_m=end_tol_m,alignment_tol_m=alignment_tol_m,
        n_pairs=len(pairs),n_floors=len(governing),
        source_basis="NBC 105:2025 §§5.4.2.1–5.4.2.2 centered CM signed directional floor-end displacement",
        note="CSV nodes/perimeter labels and centered cases must be independently verified; no EDB or OpenSees native extraction claimed")
    (out/"Floor_End_Provenance.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return pairs,governing,manifest

"""Coordinate-based ETABS/OpenSees gravity support reaction audit.

[REF docs/review/GRAVITY_ETABS_COMPARISON.md] Geometry/provenance gates.
This compares *support reactions*, NOT the applied gravity load at each node.
Point-local ETABS F3 is NOT assumed to equal global Z when its axes differ.
"""
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def _xyz(row):
    """Read source node location in m.

    [REF components/validation/gravity_etabs_direct.py extract_from_sap]
    """
    return (float(row["x_m"]),float(row["y_m"]),float(row["z_m"]))


def _distance(a,b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))


def compare_support_nodes(etabs,opensees,*,tolerance_m=0.01):
    """Match supports one-to-one with coordinate, axis and ambiguity gates.

    [REF docs/review/GRAVITY_ETABS_COMPARISON.md] No false node matching:
    ambiguity, missing coordinates or non-global ETABS axes remain unverified.
    """
    tol=float(tolerance_m)
    if not math.isfinite(tol) or tol<=0 or tol>0.5:
        raise ValueError("Matching tolerance must be positive and <= 0.5 m")
    e_rows=etabs.get("joint_reactions",[])
    o_react=opensees.get("reactions",[])
    o_coords={}
    for n in opensees.get("nodes",[]):
        tag=str(n.get("tag"))
        if tag in o_coords:
            raise ValueError("Duplicate OpenSees coordinate tag "+tag)
        o_coords[tag]=_xyz(n)
    if not e_rows or not o_react or not o_coords:
        raise ValueError("ETABS reactions, OpenSees reactions and OpenSees nodes are required")
    ores=[]
    for row in o_react:
        tag=str(row.get("node_tag"))
        if tag not in o_coords:
            raise ValueError("OpenSees support "+tag+" missing geometry")
        ores.append((tag,o_coords[tag],float(row["rz_kN"])))
    eitems=[]
    for row in e_rows:
        loc=_xyz(row)
        point=str(row.get("point"))
        if row.get("rz_global_kN") is None:
            usable=False
            rz=None
        else:
            rz=float(row["rz_global_kN"])
            usable=math.isfinite(rz)
        eitems.append((point,loc,rz,usable,row.get("global_z_basis","UNVERIFIED")))
    candidates=[]
    e_candidates=defaultdict(list)
    o_candidates=defaultdict(list)
    for ei,(_tag,eloc,*_) in enumerate(eitems):
        for oi,(_tag2,oloc,*_) in enumerate(ores):
            dist=_distance(eloc,oloc)
            if dist<=tol:
                candidates.append((dist,ei,oi))
                e_candidates[ei].append(oi)
                o_candidates[oi].append(ei)
    # Only unique mutually matched pairs are comparable. A wall mesh split,
    # duplicate ETABS points or overlapping supports is not silently summed.
    matched_e=set()
    matched_o=set()
    details=[]
    for ei,(tag,loc,rz,usable,basis) in enumerate(eitems):
        options=e_candidates[ei]
        if len(options)==1 and len(o_candidates[options[0]])==1:
            oi=options[0]
            otag,oloc,or_z=ores[oi]
            matched_e.add(ei); matched_o.add(oi)
            if usable:
                delta=rz-or_z
                denom=max(abs(rz),abs(or_z))
                pct=abs(delta)/denom*100 if denom else 0.
                state="MATCHED_GLOBAL_Z"
            else:
                delta=pct=None
                state="MATCHED_AXES_UNVERIFIED"
            details.append(dict(status=state,etabs_point=tag,
                opensees_node=otag,x_m=loc[0],y_m=loc[1],z_m=loc[2],
                separation_m=_distance(loc,oloc),
                etabs_global_rz_kN=rz if usable else None,
                opensees_rz_kN=or_z,delta_etabs_minus_opensees_kN=delta,
                abs_delta_kN=abs(delta) if delta is not None else None,
                difference_percent=pct,etabs_axis_basis=basis))
        elif options:
            details.append(dict(status="AMBIGUOUS_GEOMETRY",etabs_point=tag,
                opensees_node=None,x_m=loc[0],y_m=loc[1],z_m=loc[2],
                candidates=[ores[i][0] for i in options],
                etabs_global_rz_kN=rz,opensees_rz_kN=None,
                delta_etabs_minus_opensees_kN=None))
        else:
            details.append(dict(status="UNMATCHED_ETABS",etabs_point=tag,
                opensees_node=None,x_m=loc[0],y_m=loc[1],z_m=loc[2],
                etabs_global_rz_kN=rz,opensees_rz_kN=None,
                delta_etabs_minus_opensees_kN=None))
    for oi,(tag,loc,rz) in enumerate(ores):
        if oi in matched_o:continue
        status="AMBIGUOUS_GEOMETRY" if o_candidates[oi] else "UNMATCHED_OPENSEES"
        details.append(dict(status=status,etabs_point=None,
            opensees_node=tag,x_m=loc[0],y_m=loc[1],z_m=loc[2],
            candidates=[eitems[j][0] for j in o_candidates[oi]],
            etabs_global_rz_kN=None,opensees_rz_kN=rz,
            delta_etabs_minus_opensees_kN=None))
    ranked=sorted((r for r in details if r.get("abs_delta_kN") is not None),
                  key=lambda r:r["abs_delta_kN"],reverse=True)
    matched_e_total=sum(r["etabs_global_rz_kN"] for r in ranked)
    matched_o_total=sum(r["opensees_rz_kN"] for r in ranked)
    return dict(schema="gravity-node-comparison-v1",
        interpretation="Support reaction differences only; not nodal applied load",
        acceptance="DIAGNOSTIC_NOT_ENGINEERING_ACCEPTANCE",
        match_tolerance_m=tol,etabs_support_reactions=len(eitems),
        opensees_support_reactions=len(ores),
        valid_one_to_one_global_z_count=len(ranked),
        axis_unverified_count=sum(x["status"]=="MATCHED_AXES_UNVERIFIED" for x in details),
        ambiguous_count=sum(x["status"]=="AMBIGUOUS_GEOMETRY" for x in details),
        etabs_unmatched_count=sum(x["status"]=="UNMATCHED_ETABS" for x in details),
        opensees_unmatched_count=sum(x["status"]=="UNMATCHED_OPENSEES" for x in details),
        matched_etabs_sum_kN=matched_e_total,matched_opensees_sum_kN=matched_o_total,
        matched_sum_difference_kN=matched_e_total-matched_o_total,
        unmatched_reactions_not_zeroed=True,
        top_discrepancies=ranked[:30],rows=details,
        diagnostic_hypotheses=[
            "Compare support geometry and mesh node duplication/splitting",
            "Compare column and wall sections at large-error locations",
            "Review ETABS versus OpenSees slab-shell load connectivity and beams",
            "Review self-weight, load patterns, dead-load duplication and openings",
            "Check restraints, point-local axes and nearby spring/link reactions",
            "Check differing EDB identities before interpreting any node difference"
        ])


def write_node_comparison(folder,report):
    """Save full CSV, ranked CSV and machine-readable JSON from real evidence.

    [REF components/gravity/comparison_bundle.py export_bundle]
    """
    dest=Path(folder)
    dest.mkdir(parents=True,exist_ok=True)
    json_path=dest/"Gravity_Node_Reaction_Comparison.json"
    json_path.write_text(json.dumps(report,indent=2,allow_nan=False),encoding="utf8")
    fields=["status","etabs_point","opensees_node","x_m","y_m","z_m",
            "separation_m","etabs_global_rz_kN","opensees_rz_kN",
            "delta_etabs_minus_opensees_kN","abs_delta_kN",
            "difference_percent","etabs_axis_basis","candidates"]
    for filename,rows in (("Gravity_All_Support_Nodes.csv",report["rows"]),
                          ("Gravity_Top_Node_Discrepancies.csv",report["top_discrepancies"])):
        with (dest/filename).open("w",newline="",encoding="utf-8-sig") as stream:
            writer=csv.DictWriter(stream,fieldnames=fields,extrasaction="ignore")
            writer.writeheader();writer.writerows(rows)
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font,PatternFill
        workbook=Workbook();ws=workbook.active;ws.title="Audit"
        for key,value in report.items():
            if not isinstance(value,(dict,list)):
                ws.append([key,value])
        for title,rows in (("All support nodes",report["rows"]),
                           ("Largest differences",report["top_discrepancies"])):
            sh=workbook.create_sheet(title);sh.append(fields)
            for record in rows:
                sh.append([str(record.get(k)) if isinstance(record.get(k),list)
                           else record.get(k) for k in fields])
            sh.freeze_panes="A2";sh.auto_filter.ref=sh.dimensions
            for cell in sh[1]:
                cell.font=Font(bold=True,color="FFFFFF")
                cell.fill=PatternFill("solid",fgColor="24415F")
        workbook.save(dest/"Gravity_Node_Reaction_Comparison.xlsx")
    except ImportError:
        pass
    return json_path

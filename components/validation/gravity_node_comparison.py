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


def all_model_node_rows(opensees, topology=None, etabs=None, report=None):
    """Return every OpenSees node with original ETABS ID and measured response.

    A non-support ETABS reaction is NOT implied by the absence of a support
    reaction record. The ETABS API extraction currently provides only 76
    restrained-point displacements; all other ETABS U3 cells stay empty.
    [REF docs/review/GRAVITY_ETABS_COMPARISON.md]
    """
    src={}
    source_points={}
    for item in (topology or {}).get("node_map",[]):
        tag=str(item.get("opensees_node_tag"))
        name=item.get("etabs_point_name")
        if name is not None:
            if tag in src and src[tag]!=str(name):
                raise ValueError("Conflicting source ETABS point mapping for OpenSees node "+tag)
            src[tag]=str(name)
            source_points[str(name)]=tag
    support={}
    for item in (opensees or {}).get("reactions",[]):
        tag=str(item.get("node_tag"))
        if tag in support:
            raise ValueError("Duplicate OpenSees support reaction "+tag)
        support[tag]=item
    etabs_support={str(r.get("point")):r for r in (etabs or {}).get("joint_reactions",[])}
    etabs_disp={str(r.get("point")):r for r in (etabs or {}).get("support_displacements",[])}
    comparison={}
    for row in (report or {}).get("rows",[]):
        tag=row.get("opensees_node")
        if tag is not None:
            comparison[str(tag)]=row
    nodes=(opensees or {}).get("nodes",[])
    if not isinstance(nodes,list):
        raise ValueError("OpenSees gravity nodes must be list of node records")
    out=[]
    for n in nodes:
        tag=str(n.get("tag"))
        point=src.get(tag)
        e=etabs_support.get(point) if point is not None else None
        d=etabs_disp.get(point) if point is not None else None
        c=comparison.get(tag) or {}
        rz=support.get(tag,{}).get("rz_kN")
        out.append(dict(
            opensees_node_tag=tag,
            etabs_point_id=point,
            x_m=n.get("x_m"),y_m=n.get("y_m"),z_m=n.get("z_m"),
            is_opensees_support=tag in support,
            is_etabs_restrained_point=point in etabs_support if point else False,
            opensees_Ux_m=n.get("ux_m"),opensees_Uy_m=n.get("uy_m"),
            opensees_Uz_m=n.get("uz_m"),
            opensees_Rx_rad=n.get("rx_rad"),opensees_Ry_rad=n.get("ry_rad"),
            opensees_Rz_rad=n.get("rz_rad"),
            etabs_U1_m=d.get("U1") if d else None,
            etabs_U2_m=d.get("U2") if d else None,
            etabs_U3_m=d.get("U3") if d else None,
            difference_Uz_m=(float(n["uz_m"])-float(d["U3"]))
              if d and d.get("U3") is not None and n.get("uz_m") is not None else None,
            etabs_support_Rz_kN=e.get("rz_global_kN") if e else None,
            opensees_support_Rz_kN=rz,
            support_Rz_difference_kN=(
                float(rz)-float(e["rz_global_kN"]))
              if e and e.get("rz_global_kN") is not None and rz is not None else None,
            comparison_status=c.get("status",
               "NO_ETABS_SUPPORT_REACTION" if tag not in support else
               "UNMATCHED_OR_NO_ETABS_EVIDENCE"),
            abs_support_difference_kN=c.get("abs_delta_kN"),
            diagnostic_only=True))
    return out


def write_node_comparison(folder,report,*,etabs=None,opensees=None,topology=None):
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
    inventory=(all_model_node_rows(opensees,topology,etabs,report)
               if opensees is not None else [])
    for filename,rows in (("Gravity_All_Support_Nodes.csv",report["rows"]),
                          ("Gravity_Top_Node_Discrepancies.csv",report["top_discrepancies"])):
        with (dest/filename).open("w",newline="",encoding="utf-8-sig") as stream:
            writer=csv.DictWriter(stream,fieldnames=fields,extrasaction="ignore")
            writer.writeheader();writer.writerows(rows)
    if inventory:
        with (dest/"Gravity_All_Model_Nodes.csv").open(
            "w",newline="",encoding="utf-8-sig") as stream:
            keys=list(inventory[0]);writer=csv.DictWriter(stream,fieldnames=keys)
            writer.writeheader();writer.writerows(inventory)
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
        if inventory:
            sh=workbook.create_sheet("All OpenSees nodes")
            cols=list(inventory[0]);sh.append(cols)
            for record in inventory:
                sh.append([record.get(k) for k in cols])
            sh.freeze_panes="D2"
            sh.auto_filter.ref=sh.dimensions
            for cell in sh[1]:
                cell.font=Font(bold=True,color="FFFFFF")
                cell.fill=PatternFill("solid",fgColor="24415F")
            sh.column_dimensions["A"].width=21
            sh.column_dimensions["B"].width=20
            for col in ("C","D","E"):
                sh.column_dimensions[col].width=15
            src_rows=[r for r in inventory if r.get("etabs_point_id")]
            source=workbook.create_sheet("ETABS ID mapping")
            source_cols=["etabs_point_id","opensees_node_tag","x_m","y_m","z_m",
                         "is_etabs_restrained_point","is_opensees_support",
                         "comparison_status"]
            source.append(source_cols)
            for row in src_rows:
                source.append([row.get(k) for k in source_cols])
            source.freeze_panes="C2"
            source.auto_filter.ref=source.dimensions
        workbook.save(dest/"Gravity_Node_Reaction_Comparison.xlsx")
    except ImportError:
        pass
    return json_path


def export_opensees_applied_nodal_loads(model_data_json,output_dir):
    """Export actual converted OpenSees equivalent nodal source loads by pattern.

    [REF components/model/assembly.py apply_gravity_profile]
    This is an applied-load ledger, not an ETABS-reaction comparison. Shell
    pressure and frame line loads may already have been converted to nodes.
    """
    source=Path(model_data_json)
    if not source.is_file():
        raise FileNotFoundError("OpenSees model-data JSON missing: "+str(source))
    data=json.loads(source.read_text(encoding="utf-8-sig"))
    patterns=data.get("unfactored_patterns")
    nodes=data.get("nodes")
    if not isinstance(patterns,dict) or not isinstance(nodes,dict):
        raise ValueError("Model data lacks nodal coordinates/unfactored source patterns")
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    dest=output_dir/"OpenSees_Applied_Nodal_Gravity_By_Pattern.csv"
    fields=["pattern","node_tag","x_m","y_m","z_m","fx_kN","fy_kN","fz_kN",
            "mx_kNm","my_kNm","mz_kNm","gravity_factor"]
    counts=defaultdict(int);totals=defaultdict(float)
    with dest.open("w",newline="",encoding="utf-8-sig") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        for pattern,records in patterns.items():
            if not isinstance(records,dict):
                raise ValueError("Pattern "+str(pattern)+" must contain node-force records")
            for tag,forces in records.items():
                loc=nodes.get(str(tag))
                if loc is None:
                    raise ValueError("Pattern "+str(pattern)+" missing node "+str(tag))
                if len(forces)!=6:
                    raise ValueError("Expected 6 force components at "+str(tag))
                row=dict(pattern=pattern,node_tag=tag,
                         x_m=float(loc[0]),y_m=float(loc[1]),z_m=float(loc[2]),
                         fx_kN=float(forces[0]),fy_kN=float(forces[1]),
                         fz_kN=float(forces[2]),mx_kNm=float(forces[3]),
                         my_kNm=float(forces[4]),mz_kNm=float(forces[5]),
                         gravity_factor=1.0)
                writer.writerow(row)
                counts[pattern]+=1
                totals[pattern]+=row["fz_kN"]
    summary=dict(status="SOURCE_APPLIED_NODAL_LOADS_NOT_ETABS_VERIFIED",
                 profile="GRAVITY_1.0D_1.0L",source=str(source),
                 negative_FZ_is_downward=True,
                 records_by_pattern=dict(counts),
                 vertical_applied_kN_by_pattern=dict(totals),
                 limitations=[
                   "Nodal forces are equivalent loads after conversion from frame/shell assignments",
                   "Not directly comparable to ETABS JointReact and not proof of local member load transfer",
                   "ETABS actual distributed load patterns and shell mesh connectivity must be compared independently"
                 ])
    (output_dir/"OpenSees_Applied_Nodal_Gravity_Summary.json").write_text(
        json.dumps(summary,indent=2,allow_nan=False),encoding="utf8")
    return summary

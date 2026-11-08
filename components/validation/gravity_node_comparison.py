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


def export_fixed_source_support_reactions(folder, opensees, topology, etabs=None,
                                          *, expected_tags=range(1,77),
                                          coordinate_tolerance_m=0.01):
    """Write every requested original OpenSees source-support node to Excel.

    [REF docs/review/GRAVITY_ETABS_COMPARISON.md]
    Never substitute another support scenario, generate missing ETABS reactions,
    or infer that same ETABS point name implies equal coordinate.
    The 1..76 range belongs to the user's SOURCE-support baseline, not the
    97-node continuously fixed wall sensitivity.
    """
    output=Path(folder);output.mkdir(parents=True,exist_ok=True)
    tags=[int(i) for i in expected_tags]
    if len(tags)!=len(set(tags)) or not tags:
        raise ValueError("Expected OpenSees support tags must be unique and nonempty")
    mapping={}
    for n in topology.get("node_map",[]):
        key=str(n.get("opensees_node_tag"))
        if key in mapping:raise ValueError("Duplicate source node mapping "+key)
        mapping[key]=n
    nodal={}
    for n in opensees.get("nodes",[]):
        key=str(n.get("tag"))
        if key in nodal:raise ValueError("Duplicate OpenSees node record "+key)
        nodal[key]=n
    reactions={}
    for n in opensees.get("reactions",[]):
        key=str(n.get("node_tag"))
        if key in reactions:raise ValueError("Duplicate OpenSees reaction "+key)
        reactions[key]=n
    etabs_by_point={}
    if isinstance(etabs,dict):
        for e in etabs.get("joint_reactions",[]):
            point=str(e.get("point"))
            if point in etabs_by_point:
                raise ValueError("Duplicate ETABS reaction point "+point)
            etabs_by_point[point]=e
    results=[]
    tol=float(coordinate_tolerance_m)
    if not math.isfinite(tol) or not 0<tol<=0.5:
        raise ValueError("Coordinate tolerance must be >0 and <=0.5 m")
    for tag in tags:
        k=str(tag)
        src=mapping.get(k)
        osnode=nodal.get(k)
        osreact=reactions.get(k)
        etpoint=str(src.get("etabs_point_name")) if src and src.get("etabs_point_name") is not None else None
        etrec=etabs_by_point.get(etpoint) if etpoint is not None else None
        source_xyz=src.get("coordinates_m") if src else None
        xyz=tuple(float(osnode[a]) for a in ("x_m","y_m","z_m")) if osnode else None
        source_dist=(_distance(source_xyz,xyz) if source_xyz is not None and xyz is not None else None)
        et_dist=(_distance(xyz,_xyz(etrec)) if xyz is not None and etrec is not None else None)
        o_rz=(float(osreact["rz_kN"]) if osreact and osreact.get("rz_kN") is not None else None)
        e_rz=(float(etrec["rz_global_kN"]) if etrec and etrec.get("rz_global_kN") is not None else None)
        status="MATCHED_GLOBAL_Z"
        if src is None or not etpoint:
            status="MISSING_ETABS_POINT_MAPPING"
        elif osnode is None:
            status="MISSING_OPENSEES_NODE_DATA"
        elif osreact is None:
            status="MISSING_OPENSEES_REACTION"
        elif source_dist is None or source_dist>tol:
            status="SOURCE_NODE_GEOMETRY_MISMATCH"
        elif etrec is None:
            status="MISSING_ETABS_REACTION"
        elif et_dist is None or et_dist>tol:
            status="ETABS_OPENSEES_COORDINATE_MISMATCH"
        elif e_rz is None or not math.isfinite(e_rz):
            status="ETABS_GLOBAL_Z_NOT_VERIFIED"
        elif o_rz is None or not math.isfinite(o_rz):
            status="OPENSEES_REACTION_NOT_FINITE"
        delta=o_rz-e_rz if status=="MATCHED_GLOBAL_Z" else None
        details=dict(
            opensees_node=tag,etabs_point=etpoint,
            x_m=xyz[0] if xyz else None,y_m=xyz[1] if xyz else None,
            z_m=xyz[2] if xyz else None,source_node_distance_m=source_dist,
            etabs_opensees_distance_m=et_dist,
            etabs_Rz_kN=e_rz,opensees_Rz_kN=o_rz,
            delta_opensees_minus_etabs_kN=delta,
            abs_difference_kN=abs(delta) if delta is not None else None,
            signed_percent_etabs=(100*delta/abs(e_rz) if delta is not None and abs(e_rz)>1e-12 else None),
            status=status,
            etabs_global_z_basis=etrec.get("global_z_basis") if etrec else None,
            etabs_source_point_xyz_m=list(source_xyz) if source_xyz is not None else None)
        results.append(details)
    ranked=sorted((x for x in results if x["status"]=="MATCHED_GLOBAL_Z"),
                  key=lambda x:x["abs_difference_kN"],reverse=True)
    op_total=sum(float(x["rz_kN"]) for x in reactions.values()
                 if x.get("rz_kN") is not None)
    et_total=(sum(float(x["rz_global_kN"]) for x in etabs_by_point.values()
                  if x.get("rz_global_kN") is not None)
              if etabs is not None and all(x.get("rz_global_kN") is not None
                      for x in etabs_by_point.values()) else None)
    matched=len(ranked)
    report=dict(schema="gravity-source-76-support-v1",
        source="OpenSees original ETABS_SOURCE_SUPPORTS gravity run, not continuous-wall sensitivity",
        expected_opensees_tags=tags,
        expected_count=len(tags),matched_count=matched,
        missing_or_unverified=len(tags)-matched,
        openSees_all_reaction_sum_kN=op_total,
        etabs_all_extracted_reaction_sum_kN=et_total,
        comparable_only_if_complete=matched==len(tags),
        model_equivalence="NOT_STRUCTURALLY_VALIDATED",
        sort="numerical node tags; critical ranking by absolute point reaction difference",
        rows=results,ranked=ranked)
    (output/"Gravity_76_Source_Support_Reactions.json").write_text(
        json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    keys=["opensees_node","etabs_point","x_m","y_m","z_m",
          "etabs_Rz_kN","opensees_Rz_kN","delta_opensees_minus_etabs_kN",
          "abs_difference_kN","signed_percent_etabs","status",
          "source_node_distance_m","etabs_opensees_distance_m",
          "etabs_global_z_basis"]
    def save_csv(name,rows):
        with (output/name).open("w",newline="",encoding="utf-8-sig") as fh:
            w=csv.DictWriter(fh,fieldnames=keys,extrasaction="ignore")
            w.writeheader();w.writerows(rows)
    save_csv("Gravity_76_Source_Support_Reactions.csv",results)
    save_csv("Gravity_76_Critical_Reaction_Nodes.csv",ranked)
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font,PatternFill
        from openpyxl.chart import BarChart,Reference
        wb=Workbook();ws=wb.active;ws.title="Review summary"
        for row in [
            ("Gravity reaction audit","ETABS_SOURCE_SUPPORTS only"),
            ("Expected OpenSees tags",f"{min(tags)}–{max(tags)} ({len(tags)} requested)"),
            ("Verified one-to-one comparison",matched),
            ("Missing / unverified",len(tags)-matched),
            ("OpenSees reaction sum kN",op_total),
            ("ETABS extracted reaction sum kN",et_total),
            ("Structural equivalence","NOT VALIDATED"),
            ("Condition","Do not assume ETABS non-restrained mesh nodes carry zero or force-point equivalence"),
        ]: ws.append(row)
        def sheet(title,records):
            sh=wb.create_sheet(title)
            sh.append(keys)
            for row in records:
                sh.append([row.get(k) for k in keys])
            sh.freeze_panes="C2";sh.auto_filter.ref=sh.dimensions
            for c in sh[1]:
                c.font=Font(color="FFFFFF",bold=True)
                c.fill=PatternFill("solid",fgColor="21446A")
            sh.column_dimensions["A"].width=19
            sh.column_dimensions["B"].width=20
            for col in ["F","G","H","I","J"]:sh.column_dimensions[col].width=21
            sh.column_dimensions["K"].width=38
            return sh
        sheet("Nodes 1-76",results)
        crit=sheet("Critical nodes ranked",ranked)
        if ranked:
            chart=BarChart();chart.type="bar";chart.title="Largest absolute reaction differences, kN"
            chart.y_axis.title="OpenSees node"
            n=min(20,len(ranked))
            chart.add_data(Reference(crit,min_col=9,min_row=1,max_row=n+1),titles_from_data=True)
            chart.set_categories(Reference(crit,min_col=1,min_row=2,max_row=n+1))
            crit.add_chart(chart,"P2")
        wb.save(output/"Gravity_76_Source_Support_Reactions.xlsx")
    except ImportError:
        report["excel_status"]="OPENPYXL_UNAVAILABLE_CSV_JSON_PRESERVED"
    return report


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

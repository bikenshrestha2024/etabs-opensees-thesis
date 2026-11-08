"""Conservative RCC volume ownership for ETABS-to-OpenSees self weight.

Source solids are bounding boxes ONLY for axis-aligned, centered RCC
rectangle frames and axis-aligned shell plates. NOT automatically applicable
to noncentroid ETABS insertions, rotated sections or diagonals.

Precedence for overlap ownership:
COLUMN > SHEAR WALL > FLOOR > BEAM; first source ID owns same-class overlap.
The FE stiffness mesh is NOT shortened by this module. Only equivalent
self-weight/mass load is partitioned from its geometric total.
[REF OpenSeesDocumentation eleLoad] Loads are user-assigned, not automatic.
[REF CSI ETABS End Length Offsets] Rigid-zone factor is not a weight factor.
"""
from __future__ import annotations
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ORDER={"COLUMN":0,"SHEAR WALL":1,"FLOOR":2,"BEAM":3}
EPS=1e-9


def _bounds(a,b):
    return tuple((min(float(x),float(y)),max(float(x),float(y)))
                 for x,y in zip(a,b))


def _volume(box):
    return math.prod(max(0.0,hi-lo) for lo,hi in box)


def _overlap(a,b):
    c=tuple((max(a[d][0],b[d][0]),min(a[d][1],b[d][1])) for d in range(3))
    return c if _volume(c)>EPS else None


def _subtract(box,cut):
    """Return nonoverlapping residual pieces of box minus cut.

    [REF https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm]
    """
    joint=_overlap(box,cut)
    if joint is None:return [box]
    x,y,z=box
    cx,cy,cz=joint
    pieces=[]
    def add(a,b,c):
        s=(a,b,c)
        if _volume(s)>EPS:pieces.append(s)
    add((x[0],cx[0]),y,z)
    add((cx[1],x[1]),y,z)
    add(cx,(y[0],cy[0]),z)
    add(cx,(cy[1],y[1]),z)
    add(cx,cy,(z[0],cz[0]))
    add(cx,cy,(cz[1],z[1]))
    return pieces


def _rectangle_box_for_frame(seg,nodes):
    """Only axis-aligned rectangular members: fail closed for other geometry."""
    if str(seg.get("category","")).upper() not in ("COLUMN","BEAM"):
        return None
    p=nodes[int(seg["nodes"][0])]
    q=nodes[int(seg["nodes"][1])]
    span=[abs(q[i]-p[i]) for i in range(3)]
    axis=max(range(3),key=lambda k:span[k])
    if sum(x>1e-7 for x in span)!=1:raise ValueError(
        "Frame "+str(seg["object"])+" not axis aligned; no invented volume")
    if axis==2 and seg["category"]!="COLUMN":
        raise ValueError("Vertical frame categorized as beam")
    if axis!=2 and seg["category"]!="BEAM":
        raise ValueError("Nonvertical frame categorized as column")
    # The original dimensions, not cracked stiffness modifiers, determine
    # physical volume. For columns with unequal sides exact local rotation
    # must be separately confirmed before activating corrected loads.
    length=float(seg["length"])
    A=float(seg["properties"]["A"])
    if A<=0 or length<=0:raise ValueError("Invalid frame dimensions")
    # b/h are recorded in source frame_properties for rectangular members;
    # section width-depth ambiguity is not guessed from A and I.
    width=seg.get("physical_width_m")
    depth=seg.get("physical_depth_m")
    if width is None or depth is None:raise ValueError(
        "Missing physical frame width/depth for "+str(seg["object"]))
    width=float(width);depth=float(depth)
    if abs(width*depth-A)>max(1e-8,A*1e-7):
        raise ValueError("Frame section is not a validated solid rectangle")
    c=[(float(p[i])+float(q[i]))/2 for i in range(3)]
    ext=[width,depth,length] if axis==2 else (
        [length,width,depth] if axis==0 else [width,length,depth])
    return tuple((c[k]-ext[k]/2,c[k]+ext[k]/2) for k in range(3))


def _plate_box(cell,nodes):
    p=[nodes[int(n)] for n in cell["nodes"]]
    ext=[max(r[i] for r in p)-min(r[i] for r in p) for i in range(3)]
    normal=[i for i,x in enumerate(ext) if x<1e-7]
    if len(normal)!=1:raise ValueError(
        "Shell "+str(cell["object"])+" is not a coordinate-plane rectangle")
    normal=normal[0]
    if cell["category"]=="FLOOR" and normal!=2:
        raise ValueError("Floor slab is not horizontal")
    if cell["category"]=="SHEAR WALL" and normal==2:
        raise ValueError("Wall shell is horizontal")
    thickness=float(cell["properties"]["thickness"])
    if thickness<=0:raise ValueError("Shell thickness is invalid")
    center=sum(r[normal] for r in p)/4
    mins=[min(r[i] for r in p) for i in range(3)]
    maxs=[max(r[i] for r in p) for i in range(3)]
    mins[normal]=center-thickness/2
    maxs[normal]=center+thickness/2
    box=tuple(zip(mins,maxs))
    expected=float(cell["area"])*thickness
    if abs(_volume(box)-expected)>max(1e-8,expected*1e-6):
        raise ValueError("Shell box mismatches physical area and thickness")
    return box


def build_joint_volume_ledger(frames,shells,nodes,*,geometry_verified=False,
                              policy="AUDIT_ONLY"):
    """Compute exact union of validated axis-aligned RCC solids.

    AUDIT_ONLY records potential overlap with zero applied changes.
    VERIFIED_SINGLE_OWNER requires user-reviewed insertion geometry and
    allows applying retained/gross ratios to actual nodal source loads.

    [REF components/model/assembly.py prepare_complete_export]
    """
    if policy not in ("AUDIT_ONLY","VERIFIED_SINGLE_OWNER"):
        raise ValueError("Unknown joint self-weight policy "+str(policy))
    if policy=="VERIFIED_SINGLE_OWNER" and geometry_verified is not True:
        raise ValueError("Cannot correct joint weight without source geometry/insertion-point review")
    candidates=[]
    omitted=[]
    for idx,seg in enumerate(frames):
        category=str(seg["category"]).upper()
        if category not in ("COLUMN","BEAM"):
            omitted.append(dict(kind="frame",object=str(seg["object"]),
                                reason="Not modeled as a solid RCC rectangle"))
            continue
        box=_rectangle_box_for_frame(seg,nodes)
        candidates.append(dict(kind="frame",index=idx,object=str(seg["object"]),
            category=category,box=box,gross_m3=_volume(box),
            unit_weight_kN_m3=float(seg["properties"]["weight"])))
    for idx,cell in enumerate(shells):
        category=str(cell["category"]).upper()
        if category not in ("SHEAR WALL","FLOOR"):
            omitted.append(dict(kind="shell",object=str(cell["object"]),
                                reason="Non-RCC panel category"))
            continue
        box=_plate_box(cell,nodes)
        candidates.append(dict(kind="shell",index=idx,object=str(cell["object"]),
            category=category,box=box,gross_m3=_volume(box),
            unit_weight_kN_m3=float(cell["properties"]["weight"])))
    candidates.sort(key=lambda x:(ORDER[x["category"]],
                                  x["object"],x["index"]))
    accepted=[]
    rows=[]
    bucket=defaultdict(set)
    grid_m=3.
    def keys(box):
        ranges=[]
        for lo,hi in box:
            first=math.floor(lo/grid_m)
            last=math.floor((hi-1e-10)/grid_m)
            ranges.append(range(first,last+1))
        for i in ranges[0]:
            for j in ranges[1]:
                for k in ranges[2]:
                    yield (i,j,k)
    for solid in candidates:
        boxes=[solid["box"]]
        possible=set()
        for key in keys(solid["box"]):possible.update(bucket[key])
        for i in sorted(possible):
            owner=accepted[i]
            if _overlap(owner["box"],solid["box"]) is None:continue
            pieces=[]
            for box in boxes:pieces.extend(_subtract(box,owner["box"]))
            boxes=pieces
            if not boxes:break
        net=sum(_volume(v) for v in boxes)
        gross=solid["gross_m3"]
        if net<-EPS or net>gross+1e-7:
            raise ValueError("Conservative union volume failure: "+solid["object"])
        row={k:solid[k] for k in ("kind","index","object","category",
                                  "gross_m3","unit_weight_kN_m3")}
        row.update(net_m3=max(0.,net),removed_m3=max(0.,gross-net),
                   gross_weight_kN=gross*solid["unit_weight_kN_m3"],
                   net_weight_kN=net*solid["unit_weight_kN_m3"],
                   removed_weight_kN=(gross-net)*solid["unit_weight_kN_m3"],
                   retained_ratio=min(1.,max(0.,net/gross)) if gross else 1.,
                   policy=policy)
        rows.append(row)
        accepted.append(solid)
        for key in keys(solid["box"]):bucket[key].add(len(accepted)-1)
    gross=sum(r["gross_weight_kN"] for r in rows)
    net=sum(r["net_weight_kN"] for r in rows)
    return dict(schema="joint-volume-ownership-v1",policy=policy,
        geometry_verified=bool(geometry_verified),
        priority=list(ORDER),
        exact_axis_aligned_RCC_subtraction=True,
        unsupported_items=omitted,
        rows=rows,gross_RCC_weight_kN=gross,net_RCC_weight_kN=net,
        potentially_duplicated_RCC_weight_kN=gross-net,
        caution=[
          "The rectangular solids must use validated ETABS insertion points and orientations",
          "Nonrectangular SHS braces and complex connections are not corrected",
          "Global volume partition is exact for represented boxes, not a native ETABS Auto self-weight replication",
          "When applied, net/gross weight scales each FE member's equivalent load uniformly; local load position is approximate",
          "Slab and wall shell structural stiffness and section properties are unchanged"
        ])


def export_joint_volume_ledger(folder,ledger):
    """Write persistent reviewable per-ETABS-object CSV/JSON audit.

    [REF docs/source/components/model/joint_volume_ownership.py.md]
    """
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    (folder/"OpenSees_Joint_Volume_Ownership_Audit.json").write_text(
        json.dumps(ledger,indent=2,allow_nan=False),encoding="utf8")
    rows=ledger["rows"]
    if rows:
        with (folder/"OpenSees_Joint_Volume_Ownership_Audit.csv").open(
            "w",encoding="utf-8-sig",newline="") as f:
            keys=list(rows[0]);w=csv.DictWriter(f,fieldnames=keys)
            w.writeheader();w.writerows(rows)
    return folder

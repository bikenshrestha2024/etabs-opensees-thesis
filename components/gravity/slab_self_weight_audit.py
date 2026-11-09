"""Independent RCC slab area, thickness, self-weight and junction overlap audit.

[REF docs/source/components/gravity/slab_self_weight_audit.py.md]
No model or load modification: exact sum of source mesh cells, original
polygon geometry and proposed three-dimensional solid-owner intersections.
"""
from __future__ import annotations
from collections import defaultdict
import csv
import json
import math
from pathlib import Path


def _area_quad(coords):
    """Return parallelogram area from original source quad coordinates.

    [REF docs/source/components/gravity/slab_self_weight_audit.py.md]
    """
    if len(coords)!=4:raise ValueError("Source area must have exactly four points")
    a=[coords[1][j]-coords[0][j] for j in range(3)]
    b=[coords[3][j]-coords[0][j] for j in range(3)]
    c=[a[1]*b[2]-a[2]*b[1],
       a[2]*b[0]-a[0]*b[2],
       a[0]*b[1]-a[1]*b[0]]
    area=math.sqrt(sum(x*x for x in c))
    if not math.isfinite(area) or area<=0:
        raise ValueError("Invalid source slab quadrilateral")
    diagonal=[coords[1][j]+coords[3][j]-coords[0][j] for j in range(3)]
    if math.dist(diagonal,coords[2])>1e-6:
        raise ValueError("Nonparallelogram source polygon requires native ETABS mesh")
    return area


def audit_slab_self_weight(shells,source_elements,source_nodes, *,
                           joint_volume_ledger=None,output_dir):
    """Confirm one source shell physical area * thickness * unit weight.

    [REF docs/source/components/gravity/slab_self_weight_audit.py.md]
    """
    # Assemble independent original ETABS polygon object areas, not mesh IDs.
    original={}
    for e in source_elements:
        if e.get("dimension")!="area_polygon" or e.get("category")!="FLOOR":
            continue
        obj=str(e["etabs_object"])
        if obj in original:raise ValueError("Duplicate original floor object "+obj)
        pts=[source_nodes[int(n)] for n in e["node_tags"]]
        original[obj]=_area_quad(pts)
    cells=defaultdict(list)
    for i,s in enumerate(shells):
        if s.get("category")=="FLOOR":
            cells[str(s["object"])].append((i,s))
    if set(original)!=set(cells):
        raise ValueError("Original floor objects and meshed floor objects differ. Missing="+
                         repr(sorted(set(original)-set(cells)))+
                         " extra="+repr(sorted(set(cells)-set(original))))
    if not original:raise ValueError("No original floor polygons exported")
    overlap={}
    if joint_volume_ledger is not None:
        for r in joint_volume_ledger.get("rows",[]):
            if r.get("kind")=="shell" and r.get("category")=="FLOOR":
                idx=int(r["index"])
                if idx in overlap:raise ValueError("Duplicate floor union ledger index")
                overlap[idx]=r
    records=[]
    for obj,parts in sorted(cells.items()):
        physical_area=original[obj]
        mesh_area=sum(float(cell["area"]) for _,cell in parts)
        if abs(physical_area-mesh_area)>max(1e-8,physical_area*1e-7):
            raise ValueError(
                "Duplicated/omitted mesh slab area for original ETABS object "+
                obj+f": source={physical_area:.9f} m2 mesh={mesh_area:.9f} m2")
        thicknesses={float(cell["properties"]["thickness"]) for _,cell in parts}
        densities={float(cell["properties"]["weight"]) for _,cell in parts}
        if len(thicknesses)!=1 or len(densities)!=1:
            raise ValueError("Inconsistent physical slab thickness/weight in mesh "+obj)
        thickness=next(iter(thicknesses))
        weight_density=next(iter(densities))
        if (not all(math.isfinite(v) and v>0 for v in
                    (physical_area,thickness,weight_density))):
            raise ValueError("Invalid physical slab geometry/unit weight "+obj)
        theoretical=physical_area*thickness*weight_density
        physical_mesh=sum(float(cell["area"])*thickness*weight_density
                          for _,cell in parts)
        if abs(theoretical-physical_mesh)>max(.001,theoretical*1e-8):
            raise ValueError("Slab physical self weight differs after meshing "+obj)
        net=0.
        by_owner=defaultdict(float)
        if overlap:
            for idx,_ in parts:
                if idx not in overlap:
                    raise ValueError("Missing slab intersection union record for "+obj)
                v=overlap[idx]
                expected=float(shells[idx]["area"])*thickness*weight_density
                if abs(float(v["gross_weight_kN"])-expected)>max(.01,expected*1e-7):
                    raise ValueError("Union ledger gross slab weight mismatch "+obj)
                net+=float(v["net_weight_kN"])
                for owner in ("COLUMN","SHEAR WALL","FLOOR","BEAM"):
                    by_owner[owner]+=float(v.get("overlap_with_"+owner+"_m3",0))*weight_density
        record=dict(
            etabs_area_object=obj,original_floor_area_m2=physical_area,
            mesh_floor_area_m2=mesh_area,cell_count=len(parts),
            physical_thickness_m=thickness,
            material_weight_density_kN_m3=weight_density,
            physical_slab_volume_m3=physical_area*thickness,
            gross_slab_self_weight_kN=theoretical,
            equivalent_nodal_self_weight_kN=physical_mesh,
            joint_overlap_slab_net_hypothesis_kN=net if overlap else None,
            potential_slab_overlap_with_column_kN=by_owner["COLUMN"] if overlap else None,
            potential_slab_overlap_with_wall_kN=by_owner["SHEAR WALL"] if overlap else None,
            potential_slab_overlap_with_other_floor_kN=by_owner["FLOOR"] if overlap else None,
            slab_bending_factor_affects_weight=False,
            application="full physical self weight before source load-pattern multiplier",
            status="MESH_AREA_AND_PHYSICAL_WEIGHT_CONSERVED")
        records.append(record)
    # The input shell area itself must not cover the same space twice:
    # any positive FLOOR_OVERLAPS_FLOOR is a real potential duplicate slab.
    physical_duplicate=0.
    if joint_volume_ledger is not None:
        physical_duplicate=float(joint_volume_ledger.get(
            "overlap_pair_weight_kN",{}).get("FLOOR_OVERLAPS_FLOOR",0))
    if physical_duplicate>1e-6:
        raise ValueError(f"OVERLAPPING source floor slabs: duplicated floor solid "
                         f"weight candidate {physical_duplicate:.6f} kN; "
                         "source slab polygons need ETABS review before accepting load")
    result=dict(schema="physical-slab-weight-audit-v1",
        slab_object_count=len(records),slab_mesh_cell_count=sum(x["cell_count"] for x in records),
        total_source_floor_area_m2=sum(x["original_floor_area_m2"] for x in records),
        gross_slab_self_weight_kN=sum(x["gross_slab_self_weight_kN"] for x in records),
        equivalent_nodal_slab_self_weight_kN=sum(x["equivalent_nodal_self_weight_kN"] for x in records),
        source_floor_overlap_floor_kN=physical_duplicate,
        slab_physical_weight_rule="Area of each original floor polygon * physical thickness * weight density",
        slab_mesh_load_rule="Each ShellMITC4 child has -gamma * thickness * cell area as a net vertical load, distributed to 4 cell nodes",
        default_slab_weight_correction="NONE",
        analyzed_joint_ownership="AUDIT_ONLY: source section insertion geometry not verified",
        full_beam_depth_m=.8,full_slab_thickness_m=.15,
        hypothetical_full_overlap_net_beam_depth_m=.65,
        depth_650_mm_status="CONDITIONAL_GEOMETRY_ONLY",
        caution=("A rectangular 800mm beam is reduced to 650mm below slab "
                 "ONLY when a physically 150mm slab occupies the full beam "
                 "top depth across a verified common length/width. This is "
                 "NOT established by beam end offsets, slab bending factor, "
                 "or a generic top-center insertion label. Do not subtract "
                 "the slab volume again from the slab."),
        records=records,
        acceptance="SLAB_AREA_WEIGHT_SOURCE_CHECK_ONLY_NOT_ETABS_EQUIVALENCE")
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/"Gravity_Slab_Self_Weight_Audit.json").write_text(
        json.dumps(result,indent=2,allow_nan=False),encoding="utf-8")
    columns=list(records[0])
    with (out/"Gravity_Slab_Self_Weight_Audit.csv").open(
        "w",newline="",encoding="utf-8-sig") as stream:
        w=csv.DictWriter(stream,fieldnames=columns)
        w.writeheader();w.writerows(records)
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill,Font
    wb=Workbook()
    ws=wb.active;ws.title="Per slab object"
    ws.append(columns)
    for row in records:ws.append([row[k] for k in columns])
    sums=wb.create_sheet("Slab weight totals")
    for k,v in result.items():
        if k!="records" and not isinstance(v,(dict,list)):
            sums.append([k,v])
    caveats=wb.create_sheet("Ownership and references")
    for a,b in [
        ("Net beam depth 800-150 mm","Only if actual 150mm slab occupies full beam top depth, exactly once"),
        ("Physical slab self weight","Original unmeshed polygon area * thickness * material weight density"),
        ("Slab bending modification","Changes stiffness, not slab physical weight"),
        ("Beam column slab junction","Physical 3D union, requires insertion/reference planes; no blanket 800-150 subtraction"),
        ("Beam wall slab junction","Physical 3D union of all three; shear wall pier/opening geometry retained"),
        ("Wall wall slab junction","Three-wall core junction is a 3D union, not 3 individually independent junction volumes"),
        ("CSI Analysis Reference","https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf"),
        ("OpenSees ShellMITC4","https://openseespydoc.readthedocs.io/en/latest/src/ShellMITC4.html"),
        ("NBC105:2025 cl 3.4 Table 3-1","Effective stiffness; not self weight reduction"),
        ("NBC105:2025 cl 5.2 Table 5-1","Seismic mass, distinct from full 1D+1L gravity")]:
        caveats.append([a,b])
    for sheet in wb:
        sheet.freeze_panes="A2"
        sheet.column_dimensions["A"].width=50
        sheet.column_dimensions["B"].width=70 if sheet.title!="Per slab object" else 26
        if sheet.max_row>1:sheet.auto_filter.ref=sheet.dimensions
        for c in sheet[1]:
            c.font=Font(color="FFFFFF",bold=True)
            c.fill=PatternFill("solid",fgColor="17365D")
    wb.save(out/"Gravity_Slab_Self_Weight_Audit.xlsx")
    return result

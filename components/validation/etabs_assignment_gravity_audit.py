"""Read-only ETABS native assignment workbook gravity audit.

Requires openpyxl. This is independent native material-list evidence, not a
model edit. Run from Spyder or through ETABS_GRAVITY_ASSIGNMENT_WORKBOOK.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import hashlib
import json
import math


def _rows(wb, name):
    stream=wb[name].iter_rows(values_only=True)
    next(stream)  # table title
    fields=[str(v).strip() if v is not None else "" for v in next(stream)]
    next(stream)  # source unit row
    return [{field:values[i] for i,field in enumerate(fields) if field}
            for values in stream
            if any(v is not None and v!="" for v in values)]


EDGE_TABLES=("Point Object Connectivity","Beam Object Connectivity",
             "Column Object Connectivity","Brace Object Connectivity",
             "Null Line Object Connectivity","Wall Object Connectivity",
             "Joint Assigns - Restraints","Area Assigns - Edge Constraints")


def _unique_rows(rows, field):
    result={}
    for row in rows:
        key=str(row.get(field) or "").strip()
        if not key or key in result:
            raise ValueError("Missing/duplicate source ID in "+field)
        result[key]=row
    return result


def _unit_scale(wb,name,fields):
    rows=wb[name].iter_rows(min_row=2,max_row=3,values_only=True)
    names=list(next(rows)); units=list(next(rows))
    scales={"m":1.0,"mm":0.001}
    result={}
    for field in fields:
        if names.count(field)!=1 or units[names.index(field)] not in scales:
            raise ValueError("Missing or unsupported length unit: "+name+" "+field)
        result[field]=scales[units[names.index(field)]]
    return result


def audit_base_wall_edges(wb,*,tolerance_m=1e-6):
    """[REF docs/source/components/validation/etabs_assignment_gravity_audit.py.md]

    Establish source-object edge candidates, NEVER impose native MPCs.

    Rigid-body affine translation and moment balance follow from the
    geometric interpolation weights; native rotational/constraint DOFs
    and analytical-element force recovery remain independent evidence.
    """
    missing=[name for name in EDGE_TABLES if name not in wb.sheetnames]
    if missing:
        return dict(status="MISSING_SOURCE_TABLES",missing_tables=missing,
                    engineering_acceptance="NOT_VERIFIED")
    if not math.isfinite(tolerance_m) or not 0<tolerance_m<=1e-3:
        raise ValueError("Invalid edge coordinate tolerance")
    coords=_unique_rows(_rows(wb,EDGE_TABLES[0]),"UniqueName")
    scale=_unit_scale(wb,EDGE_TABLES[0],("X","Y","Z"))
    xyz={k:tuple(float(row[d])*scale[d] for d in ("X","Y","Z"))
         for k,row in coords.items()}
    if not xyz or not all(math.isfinite(v) for p in xyz.values() for v in p):
        raise ValueError("Invalid native point coordinates")
    base_z=min(p[2] for p in xyz.values())
    base={k for k,p in xyz.items() if abs(p[2]-base_z)<=tolerance_m}
    physical=set()
    null_count=Counter()
    for name in EDGE_TABLES[1:5]:
        rows=_unique_rows(_rows(wb,name),"Unique Name")
        for row in rows.values():
            ends=[str(row[d]) for d in ("UniquePtI","UniquePtJ")]
            if not all(k in xyz for k in ends) or len(set(ends))!=2:
                raise ValueError("Invalid native line connectivity")
            if name==EDGE_TABLES[4]:
                null_count.update(ends)
            else:
                physical.update(ends)
    wall_corners=set()
    edges=[]
    walls=_unique_rows(_rows(wb,EDGE_TABLES[5]),"UniqueName")
    assignments=_unique_rows(_rows(wb,EDGE_TABLES[7]),"UniqueName")
    for wall,row in walls.items():
        corners=[str(row["UniquePt"+str(i)]) for i in range(1,5)]
        if not all(k in xyz for k in corners) or len(set(corners))!=4:
            raise ValueError("Unsupported wall polygon "+wall)
        wall_corners.update(corners)
        for i,a in enumerate(corners):
            b=corners[(i+1)%4]
            if a in base and b in base:
                edges.append((wall,a,b))
    restraints=_unique_rows(_rows(wb,EDGE_TABLES[6]),"UniqueName")
    candidates=base & (physical|wall_corners)
    rows=[]
    for k in sorted(base):
        p=xyz[k]
        flags=restraints.get(k)
        if flags is not None:
            dofs=[str(flags[d]) for d in ("UX","UY","UZ","RX","RY","RZ")]
            if any(v not in ("Yes","No") for v in dofs):
                raise ValueError("Invalid native restraint flags "+k)
        else:
            dofs=None
        matches=[]
        if k not in candidates:
            for wall,a,b in edges:
                u=xyz[a];v=xyz[b]
                d=[v[i]-u[i] for i in range(3)]
                length2=sum(x*x for x in d)
                if length2<=tolerance_m**2:
                    raise ValueError("Degenerate native wall edge "+wall)
                t=sum((p[i]-u[i])*d[i] for i in range(3))/length2
                error=math.dist(p,tuple(u[i]+t*d[i] for i in range(3)))
                if error<=tolerance_m and tolerance_m/math.sqrt(length2)<t<1-tolerance_m/math.sqrt(length2):
                    matches.append(dict(wall_object=wall,endpoint_i=a,endpoint_j=b,
                        weight_i=1-t,weight_j=t,coordinate_residual_m=error,
                        auto_edge_constraint=assignments.get(wall,{}).get("Constraint")))
        valid=(len(matches)==1 and null_count[k]==2
               and matches[0]["auto_edge_constraint"]=="Yes")
        role=("PHYSICAL_LOCATION_CANDIDATE" if k in candidates else
              "UNIQUE_WALL_EDGE_GEOMETRIC_CANDIDATE" if valid else
              "UNRESOLVED_BASE_POINT")
        rows.append(dict(point_id=k,xyz_m=p,role=role,source_restraint=dofs,
                         incident_null_lines=null_count[k],edge_candidates=matches))
    counts=Counter(row["role"] for row in rows)
    return dict(status="SOURCE_GEOMETRY_ONLY_NOT_NATIVE_MPC",
                engineering_acceptance="NOT_VERIFIED",base_elevation_m=base_z,
                base_points=len(base),role_counts=dict(counts),
                all_base_points_have_authored_restraint=all(r["source_restraint"] is not None for r in rows),
                rows=rows)


def audit_native_assignment_workbook(workbook_path, output_folder,
                                     beam_audit_path=None):
    """Record material weights, section lists, source-ID/offset consistency.

    DO NOT interpret 'Auto' as a user-verified beam self-weight rule.
    Source workbook and output are local; do not publish workbook bytes.
    
    [REF docs/source/components/validation/etabs_assignment_gravity_audit.py.md]
    """
    from openpyxl import load_workbook
    source=Path(workbook_path).expanduser().resolve()
    if not source.is_file():raise FileNotFoundError(str(source))
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    wb=load_workbook(source,read_only=True,data_only=True)
    try:
        materials=_rows(wb,"Material List by Object Type")
        sections=_rows(wb,"Material List by Section Prop")
        frames=_rows(wb,"Frame Assigns - Summary")
        offsets=_rows(wb,"Frame Assigns - End Len Offsets")
        insertions=_rows(wb,"Frame Assigns - Insertion Point")
        areas=_rows(wb,"Area Assigns - Insertion Point")
        patterns=_rows(wb,"Load Pattern Definitions")
        sets=_rows(wb,"Shell Uniform Load Sets")
        weights={}
        for row in materials:
            category=str(row["Object Type"]).upper()
            weight=float(row["Weight"])
            if category in weights or not math.isfinite(weight) or weight<=0:
                raise ValueError("Duplicate/invalid native material quantity "+category)
            weights[category]=weight
        if not {"BEAM","COLUMN","WALL","FLOOR","BRACE"}.issubset(weights):
            raise ValueError("Native material list has missing object categories")
        original={str(r["UniqueName"]):r for r in frames}
        offset_by_id={str(r["UniqueName"]):r for r in offsets}
        insertion_by_id={str(r["UniqueName"]):r for r in insertions}
        if (len(original)!=len(frames) or len(offset_by_id)!=len(offsets)
                or len(insertion_by_id)!=len(insertions)
                or set(original)!=set(offset_by_id)
                or set(original)!=set(insertion_by_id)):
            raise ValueError("Original frame object identity mismatch between ETABS tables")
        beams={tag:r for tag,r in original.items()
               if str(r.get("Design Type","")).upper()=="BEAM"}
        native_count=int(next(r["Number Pieces"] for r in materials
                              if str(r["Object Type"]).upper()=="BEAM"))
        if len(beams)!=native_count:
            raise ValueError("Beam source ID count differs from native material list")
        section_total=sum(float(r["Weight"]) for r in sections
                          if str(r.get("Object Type","")).upper()=="BEAM")
        if abs(section_total-weights["BEAM"])>0.02:
            raise ValueError("Native section material weight does not reconcile")
        multipliers={str(r["Name"]):float(r["Self Weight Multiplier"])
                     for r in patterns
                     if float(r.get("Self Weight Multiplier") or 0)!=0}
        if multipliers!={"Self Weight":1.0}:
            raise ValueError("Native self weight applied in multiple/invalid source patterns")
        result=dict(schema="native-etabs-assignment-gravity-v1",
            source_workbook_name=source.name,source_workbook_sha256=digest,
            weights_kN=weights,native_beam_objects=len(beams),
            beam_weight_kN=weights["BEAM"],
            beam_section_total_kN=section_total,
            beam_self_weight_options=dict(Counter(str(offset_by_id[k].get("Self Weight Option"))
                                                  for k in beams)),
            beam_insertions=dict(Counter(str(insertion_by_id[k].get("Cardinal Point"))
                                         for k in beams)),
            area_insertions=dict(Counter(str(r.get("Cardinal Point")) for r in areas)),
            self_weight_pattern_multipliers=multipliers,
            load_set_patterns_kN_m2={str(r["Load Pattern"]):float(r["Load Value"])
                                     for r in sets},
            native_material_list_status="SOURCE_ETABS_QUANTITY_CONFIRMED",
            opensees_beam_crosswalk_status="NOT_ATTEMPTED",
            physical_correction_activated=False,
            warning="ETABS Auto self-weight selection is not proven from offsets alone; native total is authoritative for this exact source workbook.")
        # Optional independent geometric evidence; existing quantity-only
        # workbooks remain compatible. Malformed geometry is explicitly blocked.
        try:
            result["base_wall_edge_geometry"]=audit_base_wall_edges(wb)
        except (ValueError,KeyError,TypeError) as exc:
            result["base_wall_edge_geometry"]=dict(
                status="INVALID_SOURCE_GEOMETRY",reason=str(exc),
                engineering_acceptance="NOT_VERIFIED")
        if beam_audit_path is not None:
            beam=json.loads(Path(beam_audit_path).read_text(encoding="utf-8-sig"))
            if beam.get("schema")!="beam-self-weight-end-offset-v1":
                raise ValueError("Incompatible OpenSees beam audit schema")
            rows=beam["rows"]
            by_id={str(r["etabs_object"]):r for r in rows}
            if len(by_id)!=len(rows) or set(by_id)!=set(beams):
                raise ValueError("OpenSees source-beam IDs fail original native ETABS crosswalk")
            # Native exports may use metres or millimetres. Legacy test
            # fixtures with blank units preserve the historical mm convention;
            # reject unknown nonblank source units.
            unit_rows=wb["Frame Assigns - End Len Offsets"].iter_rows(
                min_row=2,max_row=3,values_only=True)
            headers=list(next(unit_rows)); units=list(next(unit_rows))
            offset_scale={}
            for field in ("Offset I","Offset J"):
                unit=units[headers.index(field)]
                if unit not in (None,"","mm","m"):
                    raise ValueError("Unsupported native beam offset unit: "+str(unit))
                offset_scale[field]=1.0 if unit=="m" else 0.001
            for key in beams:
                # Validate original beam length as well as both offsets.
                # An unrelated EDB can reuse IDs but use different geometry.
                length_native=float(beams[key]["Length"])
                length_open=float(by_id[key]["full_length_m"])
                if abs(length_native-length_open)>0.001:
                    raise ValueError("Original beam length disagrees for "+key)
                a=offset_by_id[key];b=by_id[key]
                for native_field,field in (("Offset I","end_i_m"),
                                           ("Offset J","end_j_m")):
                    if abs(float(a[native_field])*offset_scale[native_field]-float(b[field]))>0.001:
                        raise ValueError("Beam end offset disagrees for "+key+" "+native_field)
            gross=float(beam["gross_beam_weight_kN"])
            potential=float(beam["potential_offset_reduction_kN"])
            clear=gross-potential
            delta=clear-weights["BEAM"]
            result.update(opensees_gross_beam_kN=gross,
                opensees_beam_clear_weight_candidate_kN=clear,
                opensees_excess_beam_gross_minus_etabs_kN=gross-weights["BEAM"],
                clear_candidate_minus_etabs_kN=delta,
                beam_offset_source_ids_verified=len(beams),
                opensees_beam_crosswalk_status=(
                    "SOURCE_IDS_OFFSETS_AND_TOTAL_MATCH"
                    if abs(delta)<=0.1 else "SOURCE_IDS_AND_OFFSETS_MATCH_TOTAL_DISAGREES"),
                clear_candidate_matches_native_quantity=abs(delta)<=0.1)
    finally:
        wb.close()
    out=Path(output_folder)
    out.mkdir(parents=True,exist_ok=True)
    (out/"ETABS_Native_Assignment_Gravity_Quantity_Audit.json").write_text(
        json.dumps(result,indent=2,allow_nan=False),encoding="utf-8")
    return result


def audit_analysis_edge_constraints(wb, joints, frames, areas, *, tolerance_m=1e-6):
    """Cross-check generated @LC topology against assignment geometry.

    [REF docs/source/components/validation/etabs_assignment_gravity_audit.py.md]
    Repeated generated names are not unique: retain full directed endpoints.
    Geometric weights are not native constraint DOFs or force coefficients.
    """
    import re
    from collections import defaultdict
    baseline = audit_base_wall_edges(wb, tolerance_m=tolerance_m)
    if baseline['status'] != 'SOURCE_GEOMETRY_ONLY_NOT_NATIVE_MPC':
        raise ValueError('Complete native assignment geometry is required')
    point_rows = _unique_rows(joints, 'Element Name')
    original = _unique_rows(_rows(wb, EDGE_TABLES[0]), 'UniqueName')
    scale = _unit_scale(wb, EDGE_TABLES[0], ('X','Y','Z'))
    assignments = _unique_rows(_rows(wb, EDGE_TABLES[7]), 'UniqueName')
    def coordinate(uid):
        if uid not in point_rows or uid not in original:
            raise ValueError('Missing generated edge point identity: '+uid)
        p = tuple(float(point_rows[uid]['Global '+d]) for d in 'XYZ')
        q = tuple(float(original[uid][d])*scale[d] for d in 'XYZ')
        if not all(math.isfinite(v) for v in (*p,*q)) or math.dist(p,q)>tolerance_m:
            raise ValueError('Generated edge point coordinate mismatch: '+uid)
        return p
    shell_index = defaultdict(list)
    for row in areas:
        shell_index[(row['Story'], row['Object Name'], row['Object Label'])].append(row)
    grouped = defaultdict(list)
    seen = set()
    for row in frames:
        name = row['Element Name']
        if not name.startswith('@LC-'):
            continue
        match = re.fullmatch(r'@LC-(\d+)-([1-4])-([123])',name)
        if row['Object Type']!='Shell' or match is None:
            raise ValueError('Unrecognized generated line-constraint record: '+name)
        key = (row['Story'],row['Object Name'],row['Object Label'],match[1],int(match[2]))
        role = int(match[3]); i,j = row['Elm JtI'],row['Elm JtJ']
        signature = (key,role,i,j)
        if i==j or signature in seen:
            raise ValueError('Duplicate or degenerate generated edge record: '+name)
        seen.add(signature)
        grouped[key].append((role,i,j))
    base = {row['point_id']:row for row in baseline['rows']}
    physical = {uid for uid,row in base.items() if row['role']=='PHYSICAL_LOCATION_CANDIDATE'}
    mesh = {uid for uid,row in base.items() if row['role']=='UNIQUE_WALL_EDGE_GEOMETRIC_CANDIDATE'}
    for uid in base:
        if point_rows.get(uid,{}).get('Story')!='Base':
            raise ValueError('Assignment base point absent from analysis base: '+uid)
        coordinate(uid)
    if set(base)!={uid for uid,row in point_rows.items() if row['Story']=='Base'}:
        raise ValueError('Assignment and analysis base identity sets differ')
    results=[]; matched=set(); intermediate=Counter(); max_error=0.; base_count=0
    for key,rows in sorted(grouped.items()):
        story,owner,label,generated,edge=key
        if assignments.get(owner,{}).get('Constraint')!='Yes':
            raise ValueError('Generated parent lacks enabled edge assignment: '+owner)
        parents=[(i,j) for role,i,j in rows if role==3]
        if len(parents)!=1:
            raise ValueError('Expected one generated parent edge: '+str(key))
        i,j=parents[0]
        candidates=[]
        for shell in shell_index.get((story,owner,label),[]):
            corners=[shell['Elm Jt'+str(n)] for n in range(1,5)]
            if len(set(corners))==4 and {i,j}=={corners[edge-1],corners[edge%4]}:
                candidates.append(shell)
        if len(candidates)!=1:
            raise ValueError('Missing or ambiguous parent shell edge: '+str(key))
        first=[(a,b) for role,a,b in rows if role==1]
        second=[(a,b) for role,a,b in rows if role==2]
        mids={b for a,b in first}
        if (not mids or len(first)!=len(mids) or len(second)!=len(mids)
                or any(a!=i for a,b in first) or any(b!=j for a,b in second)
                or mids!={a for a,b in second}):
            raise ValueError('Incomplete or conflicting generated edge endpoint pairs: '+str(key))
        a,b=coordinate(i),coordinate(j); d=tuple(y-x for x,y in zip(a,b)); L2=math.fsum(v*v for v in d)
        if L2<=tolerance_m**2:
            raise ValueError('Degenerate parent edge geometry: '+str(key))
        on_base=i in base and j in base
        if on_base:
            base_count+=1
            if not {i,j}<=physical:
                raise ValueError('Base parent endpoints not physical location candidates')
        group_rows=[]
        for uid in sorted(mids):
            p=coordinate(uid); t=math.fsum((x-y)*v for x,y,v in zip(p,a,d))/L2
            error=math.dist(p,tuple(x+t*v for x,v in zip(a,d)))
            if error>tolerance_m or not 0<t<1:
                raise ValueError('Intermediate point lies outside parent edge: '+uid)
            max_error=max(max_error,error); intermediate[uid]+=1
            if on_base:
                if uid not in mesh or uid in matched:
                    raise ValueError('Base intermediate point is ambiguous or not a mesh candidate: '+uid)
                candidate=base[uid]['edge_candidates'][0]
                if (candidate['wall_object']!=owner or {candidate['endpoint_i'],candidate['endpoint_j']}!={i,j}
                        or not math.isclose(t,candidate['weight_j'] if candidate['endpoint_i']==i else candidate['weight_i'],abs_tol=1e-9)):
                    raise ValueError('Assignment and generated base edge geometry disagree: '+uid)
                matched.add(uid)
            group_rows.append(dict(point_id=uid,weight_i=1-t,weight_j=t,coordinate_residual_m=error))
        results.append(dict(story=story,owner=owner,label=label,generated_parent_id=generated,
                            analysis_shell_element=candidates[0]['Element Name'],edge=edge,
                            endpoint_i=i,endpoint_j=j,base_edge=on_base,intermediate=group_rows))
    return dict(status='SOURCE_EDGE_GEOMETRY_ONLY',engineering_acceptance='NOT_VERIFIED',
                native_mpc_equivalence='NOT_VERIFIED',native_constraint_forces='NOT_VERIFIED',
                source_model_identity='UNVERIFIED',generated_rows=len(seen),parent_edge_groups=len(results),
                parent_shell_objects=len({(r['story'],r['owner']) for r in results}),
                intermediate_occurrences=sum(intermediate.values()),distinct_intermediate_points=len(intermediate),
                max_coordinate_residual_m=max_error,base_edge_groups=base_count,
                physical_location_candidates=len(physical),base_mesh_points_expected=len(mesh),
                base_mesh_points_matched=len(matched),base_mesh_points_unmatched=sorted(mesh-matched),
                unresolved_assignment_base_points=sorted(set(base)-physical-mesh),groups=results,
                limitations=['Geometric interpolation only; no native MPC coefficients or DOFs inferred.',
                             'No constraint forces, solver restraints, stiffness or mass modified.'])

"""Read native ETABS quantity tables without altering source structural inputs.

The table names and column keys differ among ETABS versions. Capture exact
native rows, preserve unknown units/fields and refuse inferred equivalence.
Use from existing gravity_etabs_direct.connect_and_compare only.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path

KEYWORDS=("material list","material quantities","material quantity",
          "concrete quantities","weight and mass","section properties",
          "area object","frame object","load pattern","load assignments",
          "end length offset","end len offset","insertion point",
          "section property assignment","frame assignment","area assignment",
          "shell uniform load set","uniform load set","floor object",
          "wall object","beam object","column object","brace object",
          "self weight option","self weight multiplier","slab property",
          "wall property","section property definitions",
          "load case","case definitions","nonlinear static",
          "p-delta","pdelta","story shears","story drifts",
          "story displacements","joint displacements",
          "diaphragm displacements","base reactions",
          "story forces","diaphragm center","modal participating mass")


# Catalog families are discovery hints, not proof of table semantics.
# Do not substitute object connectivity for native analytical connectivity.
EVIDENCE_FAMILIES={
    "beam_end_offsets":("end length offset","end len offset","material list","self weight option"),
    "wall_stiffness":("area property modifiers","area assign","shell assign","wall property","area section property"),
    "analytical_mesh":("element connectivity","analysis model","analytical model","analysis element","auto mesh","automesh"),
    "mesh_edge_constraints":("edge constraint","joint constraint","point constraint","constraint definition","constraint assignment","constraint force","joint assign"),
    "physical_supports":("joint reaction","joint restraint","point restraint","base reaction"),
    "rigid_end_zones":("end length offset","end len offset","insertion point","frame release","frame assign"),
    "outrigger_belt_transfer":("element joint force","element forces","frame forces","pier forces","spandrel forces","group assign","group definition"),
    "foundation_section_cuts":("section cut","sectioncut","element joint force","joint reaction"),
}


def evidence_families(table):
    """[REF docs/source/components/validation/etabs_native_quantity_tables.py.md]

    Match native catalog names/keys, allowing CSI naming variations."""
    name=(table["name"]+" "+table["key"]).casefold().replace("-"," ").replace("_"," ")
    name=" ".join(name.split())
    return [family for family,terms in EVIDENCE_FAMILIES.items()
            if any(term in name for term in terms)]


def _tuple_success(raw, minimum, label):
    if not isinstance(raw,(tuple,list)) or len(raw)<minimum or raw[-1] not in (0,None):
        raise RuntimeError(f"{label}: unexpected CSI return contract/status {repr(raw)[:250]}")
    return raw


def _table_catalog(sap):
    raw=_tuple_success(sap.DatabaseTables.GetAvailableTables(),4,"GetAvailableTables")
    # CSI API contract: NumberTables, TableKey[], TableName[], ImportType[], ret.
    n=int(raw[0])
    keys=list(raw[1])
    names=list(raw[2])
    if n<0 or len(keys)!=n or len(names)!=n:
        raise ValueError("ETABS native table catalog length mismatch")
    return [{"key":str(keys[i]),"name":str(names[i])} for i in range(n)]


def _get_native_table(sap,key):
    """Normalize CSI comtypes' actual OUT-parameter tuple, as seen in ETABS v23.

    Signature INPUTS: TableKey, FieldKeyList, GroupName, TableVersion,
                      FieldsKeysIncluded, NumberRecords, TableData.
    Actual comtypes RETURNS on this installation:
        (FieldKeyList_or_GroupName, TableVersion,
         FieldsKeysIncluded, NumberRecords, TableData, retcode)
    This is SIX items, not the eight synthetic inputs+outputs assumed by V01.
    Never index result[4] for field names: result[4] is flattened data.
    """
    raw=sap.DatabaseTables.GetTableForDisplayArray(
        str(key),[],"",0,[],0,[])
    if not isinstance(raw,(list,tuple)):
        raise RuntimeError("GetTableForDisplayArray "+str(key)+
                           ": CSI returned non-tuple "+repr(type(raw)))
    if len(raw)==6:
        # Verified directly against user ETABS v23 log 2026-11-09 22:10:47.
        version,header,number,data,code=raw[1],raw[2],raw[3],raw[4],raw[5]
    elif len(raw)==8:
        # Some wrappers retain supplied arguments in the output tuple.
        version,header,number,data,code=raw[3],raw[4],raw[5],raw[6],raw[7]
    else:
        raise RuntimeError("GetTableForDisplayArray "+str(key)+
                           ": unsupported tuple length "+str(len(raw))+
                           " (expected six or eight)")
    if code not in (0,None):
        raise RuntimeError("GetTableForDisplayArray "+str(key)+
                           ": CSI retcode="+repr(code))
    try:
        fields=[str(x) for x in header]
        count=int(number)
        flat=list(data)
    except (TypeError,ValueError) as exc:
        raise ValueError("Invalid CSI fields/count/data for "+str(key)) from exc
    if count<0 or (not fields and count):
        raise ValueError("Invalid ETABS table header for "+str(key))
    if len(flat)!=count*len(fields):
        raise ValueError("Native ETABS table flattened length mismatch: "+
                         str(key)+" | nrows="+str(count)+
                         " | ncols="+str(len(fields))+
                         " | flat="+str(len(flat)))
    return fields,[flat[i*len(fields):(i+1)*len(fields)] for i in range(count)]


def export_native_quantity_tables(sap,output_dir,*,log=None,gravity_combo=None):
    """[REF docs/source/components/validation/etabs_native_quantity_tables.py.md]

    Pin and restore native database display selection when requested.

    The existing EQ/PDelta adapter owns CSI selection snapshot/restore.
    If the API does not expose the combo selection, do not pretend a
    case-scoped extraction was performed.
    """
    if gravity_combo is None:
        return _export_tables(sap,output_dir,log=log,selection=None)
    from components.validation.etabs_eq_pdelta_native_extract import (
        _db_display_snapshot,_db_restore)
    before=_db_display_snapshot(sap)
    if not before["combos_available"]:
        raise RuntimeError("Native database combination display selection unavailable")
    db=sap.DatabaseTables
    try:
        for method,values in ((db.SetLoadCasesSelectedForDisplay,[]),
                              (db.SetLoadCombinationsSelectedForDisplay,[gravity_combo])):
            code=method(values)
            if isinstance(code,(tuple,list)):
                code=code[-1]
            if code not in (0,None):
                raise RuntimeError("Native database gravity selection failed: "+str(code))
        selected=_db_display_snapshot(sap)
        if selected["cases"] or selected["combos"]!=[gravity_combo]:
            raise RuntimeError("Native database display selection differs from requested gravity combination")
        return _export_tables(sap,output_dir,log=log,selection=selected)
    finally:
        _db_restore(sap,before)


def extract_analytical_mesh(sap, *, log=None):
    """[REF docs/source/components/validation/etabs_native_quantity_tables.py.md]

    Read generated analysis elements, NOT PointObj/FrameObj/AreaObj topology.
    Caller has an analyzed ETABS model and verified kN-m-C present units.
    CSI public API returns named constraints, not necessarily the solver's
    internally condensed edge equations. No fixity or MPC is synthesized.
    """
    import math
    def get(raw, n, label):
        if (not isinstance(raw,(list,tuple)) or len(raw)!=n+1
                or raw[-1]!=0):
            raise ValueError(label+": unexpected native return "+repr(raw)[:200])
        return raw[:-1]
    def names(api,label):
        count,values=get(api.GetNameList(),2,label+".GetNameList")
        vals=[str(v) for v in (values or [])]
        if int(count)!=len(vals) or len(set(vals))!=len(vals) or any(not n for n in vals):
            raise ValueError(label+": invalid analytical names")
        return vals
    if int(sap.GetPresentUnits())!=6:
        raise ValueError("Analytical mesh extraction requires verified kN-m-C units")
    point_api=sap.PointElm
    points={}; errors=[]
    def capture(row,key,fn):
        try:
            row[key]=fn()
        except Exception as exc:
            row[key]=None
            errors.append(dict(kind=row["kind"],id=row["id"],field=key,
                               error=type(exc).__name__+": "+str(exc)))
    def point_xyz(n):
        vals=list(map(float,get(point_api.GetCoordCartesian(n),3,"PointElm.GetCoordCartesian")))
        if not all(math.isfinite(v) for v in vals):
            raise ValueError("Nonfinite analytical coordinates")
        return vals
    def restraint(n):
        flags,=get(point_api.GetRestraint(n),1,"PointElm.GetRestraint")
        if len(flags)!=6 or any(x not in (0,1,False,True) for x in flags):
            raise ValueError("Expected six analytical restraint flags")
        return [bool(x) for x in flags]
    def constraints(n):
        count,point_names,labels=get(point_api.GetConstraint(n),3,"PointElm.GetConstraint")
        point_names=list(point_names or []); labels=list(labels or [])
        if int(count)!=len(point_names) or len(labels)!=len(point_names):
            raise ValueError("Analytical constraint array length mismatch")
        if any(str(p)!=n for p in point_names) or any(not str(c) for c in labels):
            raise ValueError("Unexpected analytical constraint point or name")
        return [str(c) for c in labels]
    def point_object(n):
        obj,kind=get(point_api.GetObj(n),2,"PointElm.GetObj")
        return dict(name=str(obj),object_type=int(kind))
    def axes(n):
        raw,=get(point_api.GetTransformationMatrix(n),1,"PointElm.GetTransformationMatrix")
        vals=list(map(float,raw))
        if len(vals)!=9 or not all(math.isfinite(v) for v in vals):
            raise ValueError("Invalid analytical point transformation matrix")
        return vals

    for i,n in enumerate(names(point_api,"PointElm"),1):
        row=dict(kind="POINT_ELM",id=n)
        for key,fn in (("xyz_m",point_xyz),("restraints_local",restraint),
                       ("constraint_names",constraints),("source_object",point_object),
                       ("transformation_matrix_raw",axes)):
            capture(row,key,lambda fn=fn:fn(n))
        points[n]=row
        if log and i%1000==0:
            log("ETABS_ANALYTICAL_MESH_PROGRESS","Read analytical point elements",count=i)
    if not points:
        raise ValueError("No generated analytical point elements; analyze source first")

    def area_nodes(api,n):
        count,raw=get(api.GetPoints(n),2,"AreaElm.GetPoints")
        ns=list(map(str,raw or []))
        if int(count)!=len(ns) or len(ns) not in (3,4):
            raise ValueError("Unsupported analytical area connectivity")
        return ns
    def line_nodes(api,n):
        return list(map(str,get(api.GetPoints(n),2,"LineElm.GetPoints")))
    def checked_nodes(ns):
        if len(set(ns))!=len(ns) or any(n not in points for n in ns):
            raise ValueError("Missing or duplicate analytical endpoint")
        return ns
    def area_parent(api,n):
        obj,=get(api.GetObj(n),1,"AreaElm.GetObj")
        if not str(obj):raise ValueError("Missing analytical area parent")
        return dict(name=str(obj))
    def line_parent(api,n):
        obj,kind,i,j=get(api.GetObj(n),4,"LineElm.GetObj")
        i,j=float(i),float(j)
        if not str(obj) or not all(math.isfinite(x) for x in (i,j)):
            raise ValueError("Invalid analytical line parent")
        return dict(name=str(obj),object_type=int(kind),relative_distances_raw=[i,j])
    elements=[]
    for kind,api,nodes_fn,parent_fn in (
        ("AREA_ELM",sap.AreaElm,area_nodes,area_parent),
        ("LINE_ELM",sap.LineElm,line_nodes,line_parent)):
        for i,n in enumerate(names(api,kind),1):
            row=dict(kind=kind,id=n)
            capture(row,"points",lambda:checked_nodes(nodes_fn(api,n)))
            capture(row,"source_object",lambda:parent_fn(api,n))
            elements.append(row)
            if log and i%1000==0:
                log("ETABS_ANALYTICAL_MESH_PROGRESS","Read "+kind,count=i)
    if not elements:
        raise ValueError("No generated analytical line/area elements")
    groups={}
    for row in points.values():
        for c in row["constraint_names"] or []:
            groups.setdefault(c,[]).append(row["id"])
    base=min((p["xyz_m"][2] for p in points.values() if p["xyz_m"] is not None),default=None)
    base_points=[p["id"] for p in points.values() if p["xyz_m"] is not None and
                 abs(p["xyz_m"][2]-base)<=1e-6] if base is not None else []
    return dict(schema="etabs-analytical-mesh-native-v1",
                status=("PARTIAL_NATIVE_API_EVIDENCE" if errors else
                        "NATIVE_ANALYTICAL_CONNECTIVITY_CAPTURED_NOT_EQUIVALENCE"),
                units="kN,m,C",engineering_acceptance="NOT_VERIFIED",
                points=list(points.values()),elements=elements,
                point_count=len(points),area_element_count=sum(e["kind"]=="AREA_ELM" for e in elements),
                line_element_count=sum(e["kind"]=="LINE_ELM" for e in elements),
                base_elevation_m=base,base_analytical_point_ids=base_points,
                named_constraint_membership=groups,errors=errors,
                internal_mpc_coefficients="NOT_RECOVERED_BY_NAMED_CONSTRAINT_QUERY",
                limitations=["Native point restraints are local-axis assignments, not physical foundation classification.",
                             "Generated point objects may share coordinates; do not merge by XYZ.",
                             "Named constraints do not establish internal automatic shell-edge MPC coefficients.",
                             "Public CSI 2016 signatures require native ETABS v23 COM qualification."])


def _export_tables(sap,output_dir,*,log=None,selection=None):
    """Capture selected native table records, no geometry/weight assumptions.

    This is diagnostic extraction, not a material list solver and does not
    independently prove the ETABS object weight convention.
    
    [REF docs/source/components/validation/etabs_native_quantity_tables.py.md]
    """
    out=Path(output_dir)
    out.mkdir(parents=True,exist_ok=True)
    catalog=_table_catalog(sap)
    (out/"ETABS_NATIVE_ALL_TABLE_NAMES.json").write_text(
        json.dumps(catalog,indent=2),encoding="utf-8")
    status=[]
    used=set()
    for table in catalog:
        name=table["name"].lower()
        key=table["key"].lower()
        families=evidence_families(table)
        if not families and not any(word in name or word in key for word in KEYWORDS):
            continue
        source_key=table["key"]
        if source_key in used:continue
        used.add(source_key)
        entry={"table_key":source_key,"display_name":table["name"],
               "status":"NOT_EXTRACTED","evidence_families":families}
        try:
            fields,records=_get_native_table(sap,source_key)
            # Stable filename from source key hash; never allow path traversal
            # or table-title collision.
            name_safe="etabs_table_"+hashlib.sha256(
                source_key.encode("utf-8")).hexdigest()[:16]+".csv"
            file=out/name_safe
            with file.open("w",encoding="utf-8-sig",newline="") as handle:
                writer=csv.writer(handle)
                writer.writerow(fields)
                writer.writerows(records)
            entry.update(status="EXPORTED_RAW_NOT_NORMALIZED",
                         file=name_safe,fields=fields,records=len(records),
                         sha256=hashlib.sha256(file.read_bytes()).hexdigest())
        except Exception as exc:
            entry.update(status="UNAVAILABLE_OR_API_ERROR",
                         error=type(exc).__name__+": "+str(exc))
        status.append(entry)
        if log:
            log("ETABS_NATIVE_QUANTITY_TABLE",
                source_key,status=entry["status"],
                records=entry.get("records"),error=entry.get("error"))
    coverage={}
    for family in EVIDENCE_FAMILIES:
        entries=[row for row in status if family in row["evidence_families"]]
        nonempty=[row["table_key"] for row in entries
                  if row.get("status")=="EXPORTED_RAW_NOT_NORMALIZED" and row.get("records",0)>0]
        coverage[family]=dict(
            status=("RAW_NONEMPTY_CANDIDATES_REQUIRE_REVIEW" if nonempty else
                    "CATALOG_PRESENT_NO_NONEMPTY_EVIDENCE" if entries else "NO_CATALOG_CANDIDATES"),
            catalog_candidates=[row["table_key"] for row in entries],
            nonempty_tables=nonempty,
            engineering_acceptance="NOT_VERIFIED")
    analytical=dict(status="NOT_REQUESTED_UNSCOPED_EXPORT",engineering_acceptance="NOT_VERIFIED")
    if selection is not None:
        path=out/"ETABS_NATIVE_ANALYTICAL_MESH.json"
        try:
            mesh=extract_analytical_mesh(sap,log=log)
        except Exception as exc:
            mesh=dict(status="NATIVE_ANALYTICAL_MESH_UNAVAILABLE",
                      engineering_acceptance="NOT_VERIFIED",
                      error=type(exc).__name__+": "+str(exc))
        from components.inputs.output_contract import atomic_json
        atomic_json(path,mesh)
        analytical={k:v for k,v in mesh.items() if k not in
                    ("points","elements","named_constraint_membership","base_analytical_point_ids","errors")}
        analytical.update(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                          error_count=len(mesh.get("errors",[])))
        if log:
            log("ETABS_ANALYTICAL_MESH",analytical["status"],
                point_count=mesh.get("point_count"),error_count=analytical["error_count"])
    manifest={
        "schema":"etabs-native-quantity-raw-v1",
        "analytical_mesh_api":analytical,
        "display_selection":selection,
        "display_selection_status":("GRAVITY_COMBO_READBACK_VERIFIED" if selection is not None
                                    else "NOT_PINNED_RAW_TABLES_ONLY"),
        "engineering_evidence_coverage":coverage,
        "status":"RAW_NATIVE_TABLES_NO_AUTOMATIC_SELF_WEIGHT_ACCEPTANCE",
        "units":"As displayed in ETABS at time of extraction; inspect fields",
        "model_identity":"See matching direct ETABS gravity JSON and log",
        "available_table_count":len(catalog),
        "selected_table_count":len(status),
        "table_exports":status,
        "limitations":[
            "Verify the exact native End Length Offsets Self Weight Option field per object; Auto is not a proven clear-span or gross weight policy.",
            "Top-center frame and Top slab insertion locations change physical solid intersections; the current centered-box overlap calculation is not validated for them.",
            "Material List table existence and columns vary by ETABS version.",
            "Frame, shell and slab model-object quantities need per-source ID alignment.",
            "No load was modified, and no ETABS Self Weight Option inferred.",
            "A zero result or missing table is not evidence of zero self weight.",
            "Native EQX/EQY nonlinear-case, stiffness dependency and story result tables may be unavailable unless the relevant cases have finished analysis and are selected for output.",
            "Native response tables may include envelopes, multiple steps, local axes and duplicate story rows; raw records must not be compared until aligned to the same case, step, coordinate and eccentricity.",
            "Original NBC 105 Aw/T1 values must come from the authoritative original workbook, not reconstructed from these raw results.",
        ],
    }
    (out/"ETABS_NATIVE_QUANTITY_MANIFEST.json").write_text(
        json.dumps(manifest,indent=2),encoding="utf-8")
    return manifest

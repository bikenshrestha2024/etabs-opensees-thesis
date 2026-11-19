# -*- coding: utf-8 -*-
"""ETABS-linked NBC105 ESM workbook adapter.

Uses the user's original ETABS integration engine; never changes RS scale factors.
Select the locally installed legacy engine (.py) and the user's original calculator.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import shutil
from datetime import datetime, timezone

def _hash(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()

def _engine(path):
    path=Path(path).resolve()
    if not path.is_file() or path.suffix.lower()!=".py":
        raise FileNotFoundError("Select the original ETABS integrated Python engine (.py)")
    spec=importlib.util.spec_from_file_location("_nbc105_etabs_esm_original",str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load original ETABS calculation engine.")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    names=("start_etabs_and_open","get_stories","read_etabs_walls",
           "update_excel_from_etabs","read_calculator_inputs","calculate_direction",
           "read_conditions","write_results_to_excel","add_model_etabs_summary",
           "choose_condition_for_model","apply_filename_condition_to_excel")
    missing=[name for name in names if not callable(getattr(module,name,None))]
    if missing:
        raise RuntimeError("Selected Python file is not the supplied ETABS engine: "+", ".join(missing))
    return module

def _api_out(result):
    """Split a comtypes ETABS OAPI return into (outputs, return_code).

    [REF CSI ETABS OAPI: by-reference outputs are returned first, the int
    return code last; 0 = success]
    """
    if isinstance(result, (list, tuple)):
        values = list(result)
        return values[:-1], values[-1] if values else -1
    return [], result


def direct_wall_thickness_inventory(sap):
    """Numeric wall thickness per ETABS area property, read through the API.

    [REF CSI ETABS OAPI cAreaObj.GetNameList / GetDesignOrientation (1 = Wall) /
    GetProperty; cPropArea.GetWall (Thickness, present length units)]
    The thickness is the property's numeric Thickness value. Section NAMES
    (e.g. 'Outrigger Wall 250') are never parsed. Call after SetPresentUnits(6)
    (kN-m-C), so thickness is in metres.
    Output: dict(properties={prop: thickness_m}, wall_areas={prop: count},
    unresolved=[...]).
    """
    outputs, code = _api_out(sap.AreaObj.GetNameList())
    if code != 0 or len(outputs) < 2:
        raise RuntimeError('ETABS AreaObj.GetNameList failed: ' + str(code))
    names = list(outputs[1] or [])
    properties, counts, unresolved = {}, {}, []
    for name in names:
        orient, code = _api_out(sap.AreaObj.GetDesignOrientation(name))
        if code != 0 or not orient or int(orient[0]) != 1:
            continue
        prop_out, code = _api_out(sap.AreaObj.GetProperty(name))
        if code != 0 or not prop_out:
            unresolved.append(f'{name}: GetProperty code {code}')
            continue
        prop = str(prop_out[0])
        counts[prop] = counts.get(prop, 0) + 1
        if prop in properties:
            continue
        wall, code = _api_out(sap.PropArea.GetWall(prop))
        thickness = None
        if code == 0 and len(wall) >= 4:
            try:
                thickness = float(wall[3])
            except (TypeError, ValueError):
                thickness = None
        if thickness is None or not math.isfinite(thickness) or thickness <= 0:
            unresolved.append(f'{prop}: PropArea.GetWall code {code}')
            continue
        properties[prop] = thickness
    return dict(properties=properties, wall_areas=counts, unresolved=unresolved,
                source='ETABS OAPI PropArea.GetWall Thickness (numeric; names not parsed)')


def check_excel_wall_thickness(workbook_path, excel_rows, inventory, *, tolerance_mm=0.5):
    """Compare every Excel 'NBC Calculator' G-column thickness with ETABS values.

    [REF NBC105-2025 §5.1.2 (Awi uses the actual wall thickness); CSI OAPI PropArea.GetWall]
    MATCHED when every used row equals some directly read wall thickness
    within ``tolerance_mm``; MISMATCH otherwise; UNAVAILABLE when ETABS gave
    no wall thickness or the cell holds an unevaluated formula.
    """
    from openpyxl import load_workbook
    allowed_mm = {p: 1000. * t for p, t in inventory.get('properties', {}).items()}
    report = dict(status='UNAVAILABLE', tolerance_mm=tolerance_mm, rows=[], mismatches=[],
                  etabs_wall_thickness_mm=allowed_mm, source=inventory.get('source'),
                  unresolved=inventory.get('unresolved', []))
    if not allowed_mm:
        report['reason'] = 'No wall thickness could be read directly from ETABS.'
        return report
    wb = load_workbook(str(workbook_path), data_only=True, read_only=True)
    try:
        ws = wb['NBC Calculator'] if 'NBC Calculator' in wb.sheetnames else None
        if ws is None:
            report['reason'] = "Workbook has no 'NBC Calculator' sheet."
            return report
        unevaluated = False
        for row in sorted({int(r) for r in excel_rows if r}):
            value = ws[f'G{row}'].value
            try:
                t_mm = float(value)
            except (TypeError, ValueError):
                unevaluated = True
                report['rows'].append(dict(row=row, G=value, status='NOT_NUMERIC'))
                continue
            match = [p for p, a in allowed_mm.items() if abs(a - t_mm) <= tolerance_mm]
            report['rows'].append(dict(row=row, excel_thickness_mm=t_mm, etabs_properties=match))
            if not match:
                report['mismatches'].append(
                    f'NBC Calculator!G{row}={t_mm:g} mm not in ETABS wall thicknesses '
                    + ', '.join(f'{p}={a:g} mm' for p, a in allowed_mm.items()))
    finally:
        wb.close()
    if report['mismatches']:
        report['status'] = 'MISMATCH'
    elif report['rows'] and not unevaluated:
        report['status'] = 'MATCHED'
    else:
        report['reason'] = 'Thickness cells are unevaluated formulas or no rows were used.'
    return report


def apply_reviewed_grouped_walls(workbook, policy):
    """Apply the source-verified two-wall interpretation to the generated copy.

    [REF docs/validation/20261118_RAYLEIGH_RETAINED_DOF_CORRECTION.md]
    [REF docs/source/components/equivalent_static/etabs_linked_excel.py.md]
    """
    from openpyxl import load_workbook

    book=load_workbook(workbook)
    try:
        sheet=book["NBC Calculator"]
        height=(float(sheet["B5"].value)-float(sheet["B7"].value or 0))*float(sheet["B6"].value)
        aw=2*0.6*(12-2*2)*(0.2+min(12/height,0.9)**2)
        if not math.isclose(aw,float(policy["X"]),rel_tol=1e-9):
            raise ValueError("Reviewed 12 m wall geometry and linked workbook height/Aw differ")
        # The two remaining template rows keep their subtotal formulas.
        for row, grid in ((24,"B"),(25,"D")):
            for column,value in enumerate(("X",grid,row-23,row-23,12000,12000,600,2000,2300,2),1):
                sheet.cell(row,column).value=value
        for row in (26,27):
            for column in range(1,11):
                sheet.cell(row,column).value=None
            for column in range(11,15):
                sheet.cell(row,column).value=None
        # This copy is specifically the equivalent-static route. Legacy input
        # templates can have the Modal X/Y spectrum selectors preselected.
        sheet["N3"]="Static"
        sheet["R3"]="Static"
        book.save(workbook)
    finally:
        book.close()


def run_etabs_excel(edb,workbook,engine_path,output_dir,log=print,*,wall_policy=None):
    """Populate original calculator from ETABS, read ORIGINAL calculator method.

    Read-only ETABS: no EQ pattern writes, no analysis or EDB save.
    Workbook is never overwritten; provenance and source cells are recorded.
    """
    edb=Path(edb).expanduser().resolve()
    workbook=Path(workbook).expanduser().resolve()
    output_dir=Path(output_dir).expanduser().resolve()
    if not edb.is_file() or edb.suffix.lower()!=".edb":
        raise ValueError("Select an existing ETABS .edb")
    if not workbook.is_file() or workbook.suffix.lower()!=".xlsx":
        raise ValueError("Select the existing original NBC105 Excel calculator .xlsx")
    if output_dir==workbook.parent and workbook.name.endswith("_ETABS_LINKED_ESM.xlsx"):
        raise ValueError("Select a different source Excel workbook; generated reports are not templates.")
    output_dir.mkdir(parents=True,exist_ok=True)
    grouped=wall_policy is not None
    if grouped and (wall_policy.get("method")!="EXPORT_NODE_GEOMETRY_MATCHED_12M_X_WALL_POLICY"
                    or wall_policy.get("source_edb_sha256")!=_hash(edb)):
        raise ValueError("Reviewed 12 m grouping does not match the selected ETABS EDB bytes")
    suffix="_GROUPED_12M_ETABS_LINKED_ESM.xlsx" if grouped else "_ETABS_LINKED_ESM.xlsx"
    target=output_dir/(edb.stem+"_"+datetime.now().strftime("%Y%m%d_%H%M%S_%f")+suffix)
    if target==workbook:
        raise ValueError("Cannot overwrite the source workbook.")
    eng=_engine(engine_path)
    try:
        import comtypes
    except ImportError as exc:
        raise RuntimeError("ETABS OAPI requires comtypes (conda install -c conda-forge comtypes)") from exc
    comtypes.CoInitialize()
    etabs=sap=None
    try:
        etabs,sap=eng.start_etabs_and_open(str(edb),log=log)
        code=sap.SetPresentUnits(6)
        if isinstance(code,int) and code!=0:
            raise RuntimeError("ETABS kN-m-C unit assignment failed: "+str(code))
        stories=eng.get_stories(sap)
        xb,yb,grid=eng.read_etabs_walls(sap,stories,log=log)
        # [REF CSI OAPI PropArea.GetWall] numeric thickness, independent of
        # the engine's section-name handling.
        try:
            thickness_inventory=direct_wall_thickness_inventory(sap)
            for prop,t in sorted(thickness_inventory['properties'].items()):
                log(f"Direct ETABS wall thickness: {prop} = {1000*t:.1f} mm "
                    f"({thickness_inventory['wall_areas'].get(prop,0)} wall areas; PropArea.GetWall)")
        except Exception as exc:
            thickness_inventory={'properties':{},'unresolved':[str(exc)],
                                 'source':'ETABS OAPI PropArea.GetWall (failed)'}
            log('Direct ETABS wall thickness unavailable: '+str(exc))
        if not stories or not xb or not yb:
            raise RuntimeError("ETABS story/wall extraction incomplete; no invented substitute geometry.")
        shutil.copy2(workbook,target)
        wb=eng.load_workbook(str(target))
        try:
            eng.apply_filename_condition_to_excel(wb,str(edb))
            wb.save(str(target))
        finally:
            wb.close()
        eng.update_excel_from_etabs(str(target),stories,xb,yb,grid)
        if grouped:
            apply_reviewed_grouped_walls(target,wall_policy)
        inp=eng.read_calculator_inputs(str(target))
        try:
            x=eng.calculate_direction(inp,"X",inp["x_rows"],inp["x_source"])
            y=eng.calculate_direction(inp,"Y",inp["y_rows"],inp["y_source"])
            condition_x,condition_y=eng.read_conditions(inp["wb"])
        finally:
            inp["wb"].close()
        for axis,r in (("X",x),("Y",y)):
            for k in ("Aw","adopted_T","k"):
                v=float(r[k])
                if not math.isfinite(v) or v<=0:
                    raise RuntimeError(f"{axis} {k} invalid from original Excel method: {v}")
        if grouped and any(not math.isclose(float(res["Aw"]),float(wall_policy[axis]),rel_tol=1e-9)
                           for axis,res in (("X",x),("Y",y))):
            raise ValueError("Recalculated workbook Aw differs from reviewed X/Y grouping")
        eng.write_results_to_excel(str(target),{"X":x,"Y":y},condition_x,condition_y)
        eng.add_model_etabs_summary(str(target),str(edb),eng.choose_condition_for_model(str(edb),None),
                                    stories,grid,xb,yb)
        summary={}
        for axis,r,condition in (("X",x,condition_x),("Y",y,condition_y)):
            summary[axis]={"Aw_m2":float(r["Aw"]),"T1_s":float(r["adopted_T"]),
                           "k":float(r["k"]),
                           "C_elastic":float(r["C"]),
                           "Cd_ultimate":float(r["Cd_uls"]),
                           "Cd_service":float(r["Cd_service"]),
                           "Cd_selected":float(r["Cd_uls"] if condition=="Ultimate" else r["Cd_service"]),
                           "condition":condition,
                           "height_m":float(inp["H"]),"soil_type":inp["soil"],"Z":float(inp["Z"]),
                           "I":float(inp["I"]),"R_mu":float(inp["Rmu"]),
                           "Omega_u":float(inp["Ou"]),"Omega_s":float(inp["Os"]),
                           "spectrum_source":inp[axis.lower()+"_source"],
                           "original_excel_row_contributions":[
                               {"sheet":"NBC Calculator","row":a.get("excel_row"),
                                "source_cells":{"wall_length_mm":"F"+str(a.get("excel_row")),
                                                "wall_thickness_mm":"G"+str(a.get("excel_row")),
                                                "opening_width_mm":"H"+str(a.get("excel_row")),
                                                "opening_count":"J"+str(a.get("excel_row"))},
                                "effective_wall_length_m":a.get("effective_m"),
                                "gross_wall_length_m":a.get("wall_m"),
                                "Aw_contribution_m2":a.get("contribution")} for a in r.get("records",[])]}
            log(f"{axis}: Excel Aw={r['Aw']} m2, adopted T={r['adopted_T']} s")
        thickness_check=check_excel_wall_thickness(
            target,[a.get("excel_row") for r in (x,y) for a in r.get("records",[])],
            thickness_inventory)
        log("Excel vs direct ETABS wall thickness: "+thickness_check["status"]
            +("" if not thickness_check["mismatches"] else " | "+"; ".join(thickness_check["mismatches"][:3])))
        audit={"status":("THICKNESS_MISMATCH_DO_NOT_USE" if thickness_check["status"]=="MISMATCH"
                         else "RESEARCH COMPARISON ONLY; NOT NBC DESIGN ACCEPTANCE"),
               "direct_thickness_check":thickness_check,
               "original_method":"Supplied ETABS-integrated Excel calculator",
               "source_edb":str(edb),"source_edb_sha256":_hash(edb),
               "source_excel":str(workbook),"source_excel_sha256":_hash(workbook),
               "source_engine":str(Path(engine_path).resolve()),"source_engine_sha256":_hash(engine_path),
               "output_excel":str(target),"output_excel_sha256":_hash(target),
               "timestamp_utc":datetime.now(timezone.utc).isoformat(),
               "etabs_read_only":True,"response_spectrum_scale_factors_changed":False,
               "stories":len(stories),"X_walls":len(x["records"]),"Y_walls":len(y["records"]),
               "wall_basis":wall_policy["method"] if grouped else "ORIGINAL_EXCEL_WALL_ROWS",
               "assembled_model_sha256":wall_policy.get("assembled_model_sha256") if grouped else None,
               "coefficients":summary}
        audit_path=target.with_suffix(".provenance.json")
        audit_path.write_text(json.dumps(audit,indent=2,default=str),encoding="utf-8")
        return target,audit_path,summary
    finally:
        # This module does not save or modify the source EDB.
        if etabs is not None:
            try: eng.close_etabs(etabs,sap)
            except Exception as exc: log("ETABS shutdown warning: "+str(exc))
        comtypes.CoUninitialize()
def publish_route_comparison(output, export_dir, verify_result, *, scripts=None):
    """Compare linked coefficients to verified, completed direct solver cases.

    [REF docs/source/components/equivalent_static/etabs_linked_excel.py.md]
    """
    from components.inputs.output_contract import atomic_json
    from components.inputs.project_workbooks import _source_edb_path
    from openpyxl import Workbook
    from components.gravity.workbook_publishing import publish_workbook

    output=Path(output)
    if scripts is None:
        batches=list((output/"ESM_Runner_Status").glob("*/CASE_STATUS.json"))
        if not batches:
            raise ValueError("waiting for completed OpenSees Direct cases")
        batch=max(batches,key=lambda p:p.stat().st_mtime_ns)
        records=json.loads(batch.read_text(encoding="utf-8-sig"))
        if not records or any(row["status"]!="SUCCESS" or row["return_code"]!=0 for row in records):
            raise ValueError("latest OpenSees Direct batch is incomplete")
        scripts=[Path(row.get("runner_path") or output/row["case"]) for row in records]
    audited=[]
    for runner in map(Path,scripts):
        evidence=verify_result(runner,export_dir)
        path=runner.parent/f"NBC105_ESM_Calculation_{evidence['case']}_V111.json"
        response=runner.parent/f"NBC105_ESM_OpenSees_Response_META_{evidence['case']}.json"
        if path.stat().st_mtime_ns>response.stat().st_mtime_ns:
            raise ValueError(f"{evidence['case']}: calculation changed after the saved solver response")
        audited.append((evidence,json.loads(path.read_text(encoding="utf-8-sig"))))
    if not audited:
        raise ValueError("waiting for completed OpenSees Direct cases")
    edb=_source_edb_path(export_dir)
    if not edb or not Path(edb).is_file():
        raise ValueError("source ETABS EDB is unavailable for the identity check")
    edb_hash=_hash(edb)
    linked={}
    for file in sorted((output/"ETABS_Linked_ESM").glob("*_GROUPED_12M_ETABS_LINKED_ESM.provenance.json"),
                       key=lambda p:p.stat().st_mtime_ns,reverse=True):
        try:
            audit=json.loads(file.read_text(encoding="utf-8-sig"))
            conditions={audit["coefficients"][a]["condition"] for a in ("X","Y")}
            state={"Ultimate":"ULS","Service":"SLS","Serviceability":"SLS"}.get(next(iter(conditions))) if len(conditions)==1 else None
            if state and state not in linked and audit["source_edb_sha256"]==edb_hash and audit["direct_thickness_check"]["status"]=="MATCHED":
                if _hash(audit["output_excel"])==audit["output_excel_sha256"]:
                    linked[state]=(file,audit)
        except (OSError,ValueError,KeyError,TypeError):
            continue
    rows=[]
    pending=[]
    for evidence,direct in audited:
        case,state,axis=(evidence[k] for k in ("case","state","axis"))
        if state not in linked:
            pending.append(f"{case}: reviewed ETABS-linked {state} workbook missing")
            continue
        path,audit=linked[state]
        ref=audit["coefficients"][axis]
        aw=float(direct["period_selection"]["empirical_Aw_"+axis+"_m2"])
        pairs=(("height_m","height_m"),("Z","zoning_factor_Z"),("I","importance_factor_I"),
               ("R_mu","ductility_factor_R_mu"),("Omega_u","overstrength_factor_Omega_u"),
               ("Omega_s","overstrength_factor_Omega_s"))
        if (audit["assembled_model_sha256"]!=evidence["model_sha256"]
                or not math.isclose(ref["Aw_m2"],aw,rel_tol=1e-9)
                or ref["spectrum_source"]!="Static" or ref["soil_type"]!=direct["soil_type"]
                or any(not math.isclose(float(ref[a]),float(direct[b]),rel_tol=1e-9) for a,b in pairs)):
            pending.append(f"{case}: source model, Aw or analysis inputs differ")
            continue
        for label,a,b in (("Aw_m2",ref["Aw_m2"],aw),("T1_s",ref["T1_s"],direct["period_s"]),
                          ("k",ref["k"],direct["period_exponent_k"]),
                          ("Cd",ref["Cd_selected"],direct["design_coefficient_Cd"])):
            rows.append(dict(case=case,quantity=label,etabs_linked=a,opensees_direct=b,
                             direct_minus_linked=b-a,linked_provenance=str(path)))
    if not rows:
        raise ValueError("; ".join(pending))
    folder=output/"ESM_Route_Comparison"
    status="PARTIAL_CALCULATION_COMPARISON" if pending else "COMPLETE_CALCULATION_COMPARISON"
    data=dict(status=status,scope="NBC calculation inputs and coefficients; native ETABS response requires mapped solver results",
              source_edb_sha256=edb_hash,rows=rows,pending=pending)
    workbook=Workbook()
    sheet=workbook.active
    sheet.title="ESM route comparison"
    sheet.append(list(rows[0]))
    for row in rows:
        sheet.append(list(row.values()))
    sheet.freeze_panes="B2"
    sheet.auto_filter.ref=sheet.dimensions
    for col,width in zip("ABCDEF",(23,18,20,20,24,80)):
        sheet.column_dimensions[col].width=width
    notes=workbook.create_sheet("Status")
    for value in (status,data["scope"],*pending):
        notes.append([value])
    notes.column_dimensions["A"].width=110
    folder.mkdir(parents=True,exist_ok=True)
    token=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    result=folder/f"ETABS_Linked_vs_OpenSees_Direct_ESM_{token}.xlsx"
    publish_workbook(workbook,result,temp_prefix=".esm_")
    atomic_json(result.with_suffix(".json"),data)
    atomic_json(folder/"LATEST_ESM_Route_Comparison.json",
                {"status":status,"workbook":str(result),"report":str(result.with_suffix(".json"))})
    return f"{status}: {result}"

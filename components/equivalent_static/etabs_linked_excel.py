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

def run_etabs_excel(edb,workbook,engine_path,output_dir,log=print):
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
    target=output_dir/(edb.stem+"_"+datetime.now().strftime("%Y%m%d_%H%M%S_%f")+"_ETABS_LINKED_ESM.xlsx")
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
        eng.write_results_to_excel(str(target),{"X":x,"Y":y},condition_x,condition_y)
        eng.add_model_etabs_summary(str(target),str(edb),eng.choose_condition_for_model(str(edb),None),
                                    stories,grid,xb,yb)
        summary={}
        for axis,r,condition in (("X",x,condition_x),("Y",y,condition_y)):
            summary[axis]={"Aw_m2":float(r["Aw"]),"T1_s":float(r["adopted_T"]),
                           "k":float(r["k"]),"C":float(r["Cd_uls"] if condition=="Ultimate" else r["Cd_service"]),
                           "condition":condition,
                           "original_excel_row_contributions":[
                               {"sheet":"NBC Calculator","row":a.get("excel_row"),
                                "Aw_contribution_m2":a.get("contribution")} for a in r.get("records",[])]}
            log(f"{axis}: Excel Aw={r['Aw']} m2, adopted T={r['adopted_T']} s")
        audit={"status":"RESEARCH COMPARISON ONLY; NOT NBC DESIGN ACCEPTANCE",
               "original_method":"Supplied ETABS-integrated Excel calculator",
               "source_edb":str(edb),"source_edb_sha256":_hash(edb),
               "source_excel":str(workbook),"source_excel_sha256":_hash(workbook),
               "source_engine":str(Path(engine_path).resolve()),"source_engine_sha256":_hash(engine_path),
               "output_excel":str(target),"output_excel_sha256":_hash(target),
               "timestamp_utc":datetime.now(timezone.utc).isoformat(),
               "etabs_read_only":True,"response_spectrum_scale_factors_changed":False,
               "stories":len(stories),"X_walls":len(xb),"Y_walls":len(yb),
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

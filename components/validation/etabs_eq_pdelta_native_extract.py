"""Read-only native ETABS earthquake case and result evidence.

No analysis is started. Existing result-output selection is restored.
Select each exact native case independently; do not combine response steps
or confuse a nonlinear initial-state response with its dependent linear EQ.
"""
from __future__ import annotations
from pathlib import Path
import csv
import hashlib
import json
import re

from components.validation.gravity_etabs_direct import (
    _names,_snapshot,_restore,_select,_base)
from components.validation.etabs_native_quantity_tables import (
    _table_catalog,_get_native_table)

CASE_HINTS=(
    "EQX","EQY","EQX+ P Delta Initial","EQY+ P Delta Initial",
    "EQX+ P-Delta","EQY+ P-Delta")
OUTPUT_TERMS=(
    "story shear","story drift","story displacement","joint displacement",
    "diaphragm displacement","base reaction","diaphragm center",
    "load case definition","static nonlinear","p-delta","pdelta",
    "static load case","case - static","story forces")

def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _find_actual(names):
    # EXACT native case names are retained. Similar spelling is reported
    # as a candidate, not substituted or assumed equivalent.
    return [name for name in names if (
        re.search(r"(?i)\bEQ[XY]\b",name)
        or re.search(r"(?i)^EQ[XY][+\-]",name))]

def _db_display_snapshot(sap):
    """Snapshot DatabaseTables output selection; Results.Setup is separate."""
    db=sap.DatabaseTables
    raw=db.GetLoadCasesSelectedForDisplay()
    if not isinstance(raw,(list,tuple)) or len(raw)<3 or raw[-1] not in (0,None):
        raise RuntimeError("CSI DatabaseTables case selector mismatch: "+repr(raw)[:250])
    n=int(raw[0]);cases=list(raw[1])
    if len(cases)!=n:raise RuntimeError("DatabaseTables case count mismatch")
    getcombos=getattr(db,"GetLoadCombinationsSelectedForDisplay",None)
    combos=[]
    if getcombos is not None:
        other=getcombos()
        if not isinstance(other,(list,tuple)) or len(other)<3 or other[-1] not in (0,None):
            raise RuntimeError("CSI DatabaseTables combo selector mismatch")
        combos=list(other[1])
        if len(combos)!=int(other[0]):raise RuntimeError("DatabaseTables combo count mismatch")
    return dict(cases=cases,combos=combos,combos_available=getcombos is not None)


def _db_select_case(sap,case):
    db=sap.DatabaseTables
    result=db.SetLoadCasesSelectedForDisplay([case])
    if isinstance(result,(list,tuple)):result=result[-1]
    if result not in (0,None):raise RuntimeError("Set database case selector failed: "+str(result))
    if hasattr(db,"SetLoadCombinationsSelectedForDisplay"):
        code=db.SetLoadCombinationsSelectedForDisplay([])
        if isinstance(code,(list,tuple)):code=code[-1]
        if code not in (0,None):raise RuntimeError("Clear database combos failed")


def _db_restore(sap,snapshot):
    if snapshot is None:return
    db=sap.DatabaseTables
    result=db.SetLoadCasesSelectedForDisplay(snapshot["cases"])
    if isinstance(result,(list,tuple)):result=result[-1]
    if result not in (0,None):raise RuntimeError("Restore database case selections failed")
    if snapshot["combos_available"]:
        code=db.SetLoadCombinationsSelectedForDisplay(snapshot["combos"])
        if isinstance(code,(list,tuple)):code=code[-1]
        if code not in (0,None):raise RuntimeError("Restore database combos failed")


def export_eq_pdelta_native_evidence(sap,out_dir,*,log=None,max_rows=1000000):
    """Query existing ETABS saved case responses and display tables.

    ETABS DatabaseTables availability and headers vary by version.
    Missing results and table/API failures are explicit evidence.
    """
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    before=_snapshot(sap)
    db_before=None
    db_selection_status="NOT_CHECKED"
    try:
        db_before=_db_display_snapshot(sap)
        db_selection_status="NATIVE_TABLE_DISPLAY_SNAPSHOT"
    except Exception as selection_err:
        db_selection_status="UNAVAILABLE: "+type(selection_err).__name__+": "+str(selection_err)
    events=[]
    log=log or (lambda *_args,**_kwargs:None)
    try:
        case_names=_names(sap.LoadCases,"LoadCases")
        selected=_find_actual(case_names)
        catalog=_table_catalog(sap)
        tables=[item for item in catalog
                if any(term in (item["key"]+" "+item["name"]).lower()
                       for term in OUTPUT_TERMS)]
        manifest=dict(schema="etabs-eqx-eqy-pdelta-native-v1",
                      exact_native_cases=case_names,
                      selected_eq_case_names=selected,
                      selected_case_count=len(selected),
                      table_display_selection_status=db_selection_status,
                      table_catalog=catalog,events=events,
                      status="SOURCE_EVIDENCE_NOT_STRUCTURAL_VALIDATION",
                      disclaimer="Only existing saved results; no ETABS model, load case or solver changes.")
        for case in selected:
            table_case_selected=False
            if db_before is not None:
                try:
                    _db_select_case(sap,case)
                    table_case_selected=True
                except Exception as filter_exc:
                    events.append(dict(case=case,type="TABLE_DISPLAY_SELECTION",
                        status="BLOCKED",error=str(filter_exc)))
            try:
                _select(sap,case)
                all_base=_base(sap,case)
                if not all_base:
                    raise ValueError("No saved base reaction results")
                # Some nonlinear cases have multiple load steps. Preserve all
                # available, do not silently choose a value from an envelope.
                path=out/("base_"+hashlib.sha256(case.encode()).hexdigest()[:16]+".csv")
                with path.open("w",encoding="utf-8-sig",newline="") as f:
                    writer=csv.DictWriter(f,fieldnames=list(all_base[0]))
                    writer.writeheader();writer.writerows(all_base)
                events.append(dict(case=case,type="BASE_REACTIONS",
                                   status="EXPORTED_ALL_STEPS",count=len(all_base),
                                   path=path.name,sha256=_sha(path)))
            except Exception as exc:
                events.append(dict(case=case,type="BASE_REACTIONS",
                                   status="MISSING_OR_API_ERROR",error=str(exc)))
            for row in tables:
                key=row["key"]
                try:
                    fields,records=_get_native_table(sap,key)
                    normalized=[str(x).replace(" ","").replace("_","").lower()
                                for x in fields]
                    idx=next((i for i,value in enumerate(normalized)
                              if value in ("outputcase","loadcase","case")),None)
                    response_table=any(term in key.lower() for term in (
                        "story shear","story forces","story drift",
                        "displacement","base reaction"))
                    if response_table and idx is None:
                        raise ValueError("Missing exact output-case column: "+key)
                    if response_table and not table_case_selected:
                        raise ValueError("Native DatabaseTables case selection unverified")
                    if idx is not None:
                        records=[v for v in records if str(v[idx])==case]
                    if len(records)>max_rows:
                        raise ValueError(f"{len(records)} rows exceed explicit {max_rows} audit limit")
                    filename="case_"+hashlib.sha256(
                        (case+"\n"+key).encode()).hexdigest()[:20]+".csv"
                    path=out/filename
                    with path.open("w",encoding="utf-8-sig",newline="") as f:
                        writer=csv.writer(f);writer.writerow(fields);writer.writerows(records)
                    events.append(dict(case=case,type="NATIVE_TABLE",table_key=key,
                                       fields=fields,records=len(records),
                                       file=filename,sha256=_sha(path),
                                       native_case_column=fields[idx] if idx is not None else None,
                                       display_selection_verified=table_case_selected,
                                       status="EXPORTED_RAW_NOT_NORMALIZED"))
                except Exception as exc:
                    events.append(dict(case=case,type="NATIVE_TABLE",table_key=key,
                                       status="UNAVAILABLE_OR_API_ERROR",
                                       error=type(exc).__name__+": "+str(exc)))
            log("ETABS_EQ_CASE_AUDIT",case,
                tables_exported=sum(item["case"]==case and
                    item["status"]=="EXPORTED_RAW_NOT_NORMALIZED"
                    for item in events))
        if not selected:
            manifest["warning"]="No native ETABS EQX/EQY cases found. Do not infer case names from load PATTERN names."
        manifest["failed_case_or_table_queries"]=sum(
            event["status"] in ("UNAVAILABLE_OR_API_ERROR","MISSING_OR_API_ERROR")
            for event in events)
        manifest["notes"]=[
            "EQX+ P Delta Initial is nonlinear PDelta; signed full initial gravity and 1.5 EQX is not the same as EQX+ P-Delta.",
            "EQX+ P-Delta linear static uses stiffness of initial case but excludes loads in initial case; compare only matching incremental signed response.",
            "Story shears and displacements are native unnormalized records; verify step, axes, eccentricity and diaphragm reference.",
            "±5% accidental eccentricity is a separate branch; negative initial EQ direction also requires documented screening.",
            "Preserve original NBC105 RS Scaling Excel adopted Aw and T1 values; no period/area substitution.",
        ]
        (out/"ETABS_EQ_PDELTA_NATIVE_INDEX.json").write_text(
            json.dumps(manifest,indent=2,default=str),encoding="utf-8")
        return manifest
    finally:
        try:
            _db_restore(sap,db_before)
        finally:
            _restore(sap,before)

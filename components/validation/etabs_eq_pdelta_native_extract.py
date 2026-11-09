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

def export_eq_pdelta_native_evidence(sap,out_dir,*,log=None,max_rows=1000000):
    """Query existing ETABS saved case responses and display tables.

    ETABS DatabaseTables availability and headers vary by version.
    Missing results and table/API failures are explicit evidence.
    """
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    before=_snapshot(sap)
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
                      table_catalog=catalog,events=events,
                      status="SOURCE_EVIDENCE_NOT_STRUCTURAL_VALIDATION",
                      disclaimer="Only existing saved results; no ETABS model, load case or solver changes.")
        for case in selected:
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
        _restore(sap,before)

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
          "area object","frame object","load pattern","load assignments")


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
    # Standard CSI OAPI signature: Key, FieldKeyList, GroupName,
    # TableVersion, FieldsKeysIncluded, NumberRecords, TableData, ret.
    raw=_tuple_success(
        sap.DatabaseTables.GetTableForDisplayArray(str(key),[],"",0,[],0,[]),
        8,"GetTableForDisplayArray "+str(key))
    fields=[str(x) for x in raw[4]]
    count=int(raw[5])
    flat=list(raw[6])
    if count<0 or not fields and count:
        raise ValueError("Invalid ETABS table header for "+str(key))
    if len(flat)!=count*len(fields):
        raise ValueError("Native ETABS table flattened length mismatch: "+str(key))
    return fields,[flat[i*len(fields):(i+1)*len(fields)] for i in range(count)]


def export_native_quantity_tables(sap,output_dir,*,log=None):
    """Capture selected native table records, no geometry/weight assumptions.

    This is diagnostic extraction, not a material list solver and does not
    independently prove the ETABS object weight convention.
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
        if not any(word in name or word in key for word in KEYWORDS):
            continue
        source_key=table["key"]
        if source_key in used:continue
        used.add(source_key)
        entry={"table_key":source_key,"display_name":table["name"],
               "status":"NOT_EXTRACTED"}
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
    manifest={
        "schema":"etabs-native-quantity-raw-v1",
        "status":"RAW_NATIVE_TABLES_NO_AUTOMATIC_SELF_WEIGHT_ACCEPTANCE",
        "units":"As displayed in ETABS at time of extraction; inspect fields",
        "model_identity":"See matching direct ETABS gravity JSON and log",
        "available_table_count":len(catalog),
        "selected_table_count":len(status),
        "table_exports":status,
        "limitations":[
            "Material List table existence and columns vary by ETABS version.",
            "Frame, shell and slab model-object quantities need per-source ID alignment.",
            "No load was modified, and no ETABS Self Weight Option inferred.",
            "A zero result or missing table is not evidence of zero self weight.",
        ],
    }
    (out/"ETABS_NATIVE_QUANTITY_MANIFEST.json").write_text(
        json.dumps(manifest,indent=2),encoding="utf-8")
    return manifest

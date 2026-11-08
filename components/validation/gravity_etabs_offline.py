"""Offline ETABS full-table gravity evidence vs two OpenSees wall support runs.

Consumes the already completed ETABS Joint Reactions worksheet (or CSV),
without launching COM or rerunning any ETABS case. ETABS point Unique Name
matches the source ETABS point name in OpenSees_Element_Connectivity.json.
A match by Label alone is prohibited because display labels can be reused.

[REF docs/review/GRAVITY_ETABS_COMPARISON.md] Native evidence precedence.
"""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path

CASE="1. DL + LL"
FIELDS=("etabs_unique_name","etabs_label","opensees_node_tag",
        "x_m","y_m","z_m","etabs_FZ_kN","opensees_source_Rz_kN",
        "opensees_continuous_Rz_kN","delta_source_minus_etabs_kN",
        "delta_continuous_minus_etabs_kN","status")

def _iter_joint_rows(path):
    source=Path(path)
    if not source.is_file():
        raise FileNotFoundError("Original ETABS full-table export is missing: "+str(source))
    suffix=source.suffix.lower()
    if suffix==".csv":
        with source.open("r",encoding="utf-8-sig",newline="") as stream:
            yield from csv.reader(stream)
    elif suffix in (".xlsx",".xlsm"):
        from openpyxl import load_workbook
        # read_only streams only selected sheet row XML. A 500MB workbook can
        # still take substantial time and memory to resolve shared strings.
        wb=load_workbook(source,data_only=True,read_only=True)
        try:
            matches=[n for n in wb.sheetnames if n.strip().lower()=="joint reactions"]
            if len(matches)!=1:
                raise ValueError("ETABS workbook requires exactly one 'Joint Reactions' worksheet; found "+str(matches))
            ws=wb[matches[0]]
            for row in ws.iter_rows(values_only=True):
                yield row
        finally:
            wb.close()
    else:
        raise ValueError("Use original ETABS .xlsx/.xlsm or extracted Joint Reactions .csv")

def _str(value):
    return "" if value is None else str(value).strip()

def _number(value,label):
    try: n=float(value)
    except (ValueError,TypeError) as exc:raise ValueError(label+" must be numeric; got "+repr(value)) from exc
    if not math.isfinite(n):raise ValueError(label+" must be finite")
    return n

def read_etabs_joint_reactions(export,case=CASE):
    """Read complete, exact DL+LL Base joint reactions (not visible Excel filters).

    [REF docs/review/GRAVITY_ETABS_COMPARISON.md] ETABS completed table evidence.
    """
    header=None
    seen={}
    accepted=0
    for row in _iter_joint_rows(export):
        parts=[_str(x) for x in row]
        if header is None:
            lookup={key.strip().lower():i for i,key in enumerate(parts)}
            required=("story","label","unique name","output case","fz")
            if all(k in lookup for k in required):
                header=lookup
            continue
        def cell(name):
            i=header[name]
            return row[i] if i<len(row) else None
        if _str(cell("output case"))!=case or _str(cell("story")).lower()!="base":
            continue
        name=_str(cell("unique name"))
        if not name:raise ValueError("ETABS Joint Reactions Base row lacks Unique Name")
        fz=_number(cell("fz"),"ETABS FZ for "+name)
        if name in seen:
            raise ValueError("Multiple Base results for ETABS unique point "+name+
                             " in exact combination "+case+"; review time/step and table export")
        seen[name]={"etabs_unique_name":name,"etabs_label":_str(cell("label")),
                    "etabs_FZ_kN":fz}
        accepted+=1
    if header is None:
        raise ValueError("Could not locate ETABS Joint Reactions header: Story / Label / Unique Name / Output Case / FZ")
    if not accepted:raise ValueError("No ETABS Base Joint Reactions for exact "+case)
    return seen

def compare_etabs_export(etabs_export,topology_json,source_gravity_json,
                         continuous_gravity_json=None,case=CASE):
    """Match by *verified source mapping*, not identical solver node numbers.

    [REF components/validation/gravity_node_comparison.py] Source ID provenance.
    """
    etabs=read_etabs_joint_reactions(etabs_export,case)
    topology=json.loads(Path(topology_json).read_text(encoding="utf-8-sig"))
    source=json.loads(Path(source_gravity_json).read_text(encoding="utf-8-sig"))
    continuous=(json.loads(Path(continuous_gravity_json).read_text(encoding="utf-8-sig"))
                if continuous_gravity_json is not None else None)
    if not source.get("ok") or source.get("wall_support_strategy")!="ETABS_SOURCE_SUPPORTS":
        raise ValueError("OpenSees source-support run is not a verified completed ETABS_SOURCE_SUPPORTS case")
    if source.get("gravity_profile")!="GRAVITY_1.0D_1.0L":
        raise ValueError("Source-support OpenSees gravity profile is not full 1D+1L")
    if continuous is not None:
        if not continuous.get("ok") or continuous.get("wall_support_strategy")!="CONTINUOUS_WALL_BASE_FIXED":
            raise ValueError("Continuous OpenSees gravity strategy missing/invalid")
        if continuous.get("gravity_profile")!="GRAVITY_1.0D_1.0L":
            raise ValueError("Continuous gravity profile differs from full gravity")
    mapped={}
    collisions={}
    for entry in topology.get("node_map",[]):
        key=_str(entry.get("etabs_point_name"))
        tag=_str(entry.get("opensees_node_tag"))
        if key in mapped and mapped[key]!=tag:collisions.setdefault(key,set()).update((mapped[key],tag))
        elif key:mapped[key]=tag
    if collisions:
        raise ValueError("Ambiguous ETABS point map IDs: "+str({k:sorted(v) for k,v in collisions.items()}))
    osr={_str(r["node_tag"]):_number(r["rz_kN"],"OpenSees Rz") for r in source["reactions"]}
    ctr={_str(r["node_tag"]):_number(r["rz_kN"],"Continuous Rz") for r in continuous["reactions"]} if continuous else {}
    coords={_str(n["tag"]):n for n in source.get("nodes",[])}
    rows=[]
    for unique,item in etabs.items():
        tag=mapped.get(unique)
        xyz=coords.get(tag,{}) if tag else {}
        rz=osr.get(tag)
        cr=ctr.get(tag) if continuous else None
        status=("UNMAPPED_ETABS_UNIQUE_NAME" if not tag else
                "NO_OPENSEES_REACTION_AT_MAPPED_NODE" if rz is None else
                "MATCHED_ETABS_SOURCE_SUPPORT")
        rows.append(dict(**item,opensees_node_tag=tag,x_m=xyz.get("x_m"),
            y_m=xyz.get("y_m"),z_m=xyz.get("z_m"),
            opensees_source_Rz_kN=rz,opensees_continuous_Rz_kN=cr,
            delta_source_minus_etabs_kN=rz-item["etabs_FZ_kN"] if rz is not None else None,
            delta_continuous_minus_etabs_kN=cr-item["etabs_FZ_kN"] if cr is not None else None,
            status=status))
    rows.sort(key=lambda v:(v["delta_source_minus_etabs_kN"] is None,
                -abs(v["delta_source_minus_etabs_kN"] or 0)))
    nmatched=sum(x["status"]=="MATCHED_ETABS_SOURCE_SUPPORT" for x in rows)
    etabs_total=sum(x["etabs_FZ_kN"] for x in rows)
    os_total=_number(source["report"]["support_vertical_reaction_kN"],"OpenSees total Rz")
    applied=_number(source["report"]["applied_vertical_load_kN"],"OpenSees applied gravity")
    return dict(schema="etabs-export-offline-gravity-v1",
        interpretation="Exact ETABS Base Joint Reactions versus OpenSees, matched by source ETABS unique point name",
        case=case,etabs_export=str(etabs_export),source_gravity_json=str(source_gravity_json),
        continuous_gravity_json=str(continuous_gravity_json) if continuous else None,
        reference_source="ETABS_FINISHED_FULL_TABLE_EXPORT_NOT_LIVE_COM",
        etabs_joint_records=len(rows),matched_source_nodes=nmatched,
        unmapped_or_missing_reactions=len(rows)-nmatched,
        sum_etabs_base_joint_FZ_kN=etabs_total,
        opensees_source_total_reaction_kN=os_total,
        opensees_source_applied_kN=applied,
        difference_opensees_minus_etabs_kN=os_total-etabs_total,
        difference_percent=100*(os_total-etabs_total)/abs(etabs_total) if etabs_total else None,
        matched_ETABS_FZ_kN=sum(x["etabs_FZ_kN"] for x in rows if x["opensees_source_Rz_kN"] is not None),
        matched_OpenSees_Rz_kN=sum(x["opensees_source_Rz_kN"] for x in rows if x["opensees_source_Rz_kN"] is not None),
        constraints=("Source EDB/model table identity and physical point mapping must be verified",
            "This audit does not equate internal ETABS analysis-mesh reactions with original point labels",
            "Global gravity weight discrepancy requires load and self-weight reconciliation"),
        rows=rows)

def export_offline_comparison(report,folder):
    """Persist the complete original ETABS point comparison.

    [REF docs/review/GRAVITY_ETABS_COMPARISON.md] Full audit evidence.
    """
    out=Path(folder);out.mkdir(parents=True,exist_ok=True)
    (out/"ETABS_Offline_Gravity_Comparison.json").write_text(
        json.dumps(report,indent=2,allow_nan=False),encoding="utf8")
    with (out/"ETABS_Offline_Joint_Reaction_Differences.csv").open(
        "w",encoding="utf-8-sig",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=FIELDS,extrasaction="ignore")
        writer.writeheader();writer.writerows(report["rows"])
    from openpyxl import Workbook
    wb=Workbook();ws=wb.active;ws.title="Summary"
    for key,value in report.items():
        if isinstance(value,(int,float,str)) and value is not None:ws.append([key,value])
    sh=wb.create_sheet("All 76 ETABS joints");sh.append(list(FIELDS))
    for row in report["rows"]:sh.append([row.get(k) for k in FIELDS])
    sh.freeze_panes="A2";sh.auto_filter.ref=sh.dimensions
    wb.save(out/"ETABS_Offline_Gravity_Comparison.xlsx")
    return out

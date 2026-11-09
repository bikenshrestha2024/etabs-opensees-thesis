"""Physical self-weight is independent of ETABS cracked-section stiffness.

ETABS weight and mass have THEIR OWN modifier slots. Only a verified
unity weight modifier can be treated as unchanged physical weight.
Source: docs/source/components/model/physical_weight_modifiers.py.md
[REF docs/source/components/model/physical_weight_modifiers.py.md]
"""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path

FRAME_LABELS=("A","As2","As3","J","I22","I33","mass","weight")
AREA_LABELS=("f11","f22","f12","m11","m22","m12","v13","v23","mass","weight")


def decode_api_modifiers(raw, count, label):
    """Parse CSI COM GetModifiers array with return code 0, fail if unknown.

    [REF docs/source/components/model/physical_weight_modifiers.py.md]
    """
    if not isinstance(raw,(list,tuple)) or not raw or raw[-1]!=0:
        raise ValueError(label+": ETABS GetModifiers did not succeed")
    arrays=[v for v in raw[:-1] if isinstance(v,(tuple,list)) and len(v)==count]
    if len(arrays)!=1:
        raise ValueError(label+": no unique "+str(count)+"-component modifier vector")
    values=[float(x) for x in arrays[0]]
    if not all(math.isfinite(x) and x>0 for x in values):
        raise ValueError(label+": nonfinite/nonpositive modifier")
    return dict(zip(FRAME_LABELS if count==8 else AREA_LABELS,values))


def extract_native_weight_modifiers(sap,frame_rows):
    """Read native ETABS frame and area object + section modifier evidence.

    No model writes. Read-only GetModifiers cannot change native EDB.
    [REF docs/source/components/model/physical_weight_modifiers.py.md]
    """
    records=[]
    errors=[]
    cache={}
    def query(kind,scope,name,prop=None):
        key=(kind,scope,name)
        if key in cache:
            return cache[key]
        count=8 if kind=="frame" else 10
        provider=(
            sap.FrameObj if kind=="frame" and scope=="object" else
            sap.PropFrame if kind=="frame" else
            sap.AreaObj if scope=="object" else sap.PropArea)
        try:
            values=decode_api_modifiers(provider.GetModifiers(str(name)),count,
                f"{kind} {scope} {name}")
            cache[key]=values
        except Exception as error:
            cache[key]=None
            errors.append(f"{kind}/{scope}/{name}: {error}")
        return cache[key]
    for row in frame_rows:
        obj=str(row["etabs_object"])
        prop=str(row.get("assigned_section") or "").strip()
        if not prop:continue
        o=query("frame","object",obj)
        p=query("frame","section",prop)
        records.append(dict(kind="frame",object=obj,section=prop,
                            object_modifiers=o,section_modifiers=p))
    # The area list comes from the original native ETABS model, including
    # walls and slabs, not from drawing coordinates or section-name guesses.
    try:
        raw=list(sap.AreaObj.GetNameList())
        if not raw or raw[-1]!=0:raise ValueError("GetNameList did not succeed")
        names=next((v for v in raw[:-1] if isinstance(v,(list,tuple))
                    and all(isinstance(x,str) for x in v)),None)
        if names is None:raise ValueError("Missing native area object names")
        for obj in names:
            try:
                property_raw=list(sap.AreaObj.GetProperty(str(obj)))
                if not property_raw or property_raw[-1]!=0:
                    raise ValueError("AreaObj.GetProperty failed")
                prop=next((str(x) for x in property_raw[:-1]
                    if isinstance(x,str) and x.strip()),None)
                if not prop:
                    raise ValueError("Missing assigned area section property")
                o=query("area","object",obj)
                p=query("area","section",prop)
                records.append(dict(kind="area",object=str(obj),section=prop,
                                    object_modifiers=o,section_modifiers=p))
            except Exception as e:
                errors.append(f"area/{obj}: {e}")
    except Exception as e:
        errors.append("AreaObj.GetNameList: "+str(e))
    return dict(schema="etabs-native-independent-modifiers-v1",
                records=records,errors=errors,complete=not errors,
                source="native ETABS GetModifiers, no write API")


def review_physical_weight_modifiers(native,patterns,output_dir):
    """Verify weight unity without replacing geometric section properties.

    [REF docs/source/components/model/physical_weight_modifiers.py.md]
    """
    rows=[]
    status="NATIVE_WEIGHT_MODIFIERS_VERIFIED"
    issues=[]
    if not isinstance(native,dict) or not native.get("records"):
        status="NATIVE_WEIGHT_MODIFIERS_NOT_EXTRACTED"
        issues.append("A fresh original ETABS API modifier export is required")
        native=dict(records=[],errors=["metadata absent"],complete=False)
    for record in native["records"]:
        obj=record["object"]
        kind=record["kind"]
        for scope in ("object","section"):
            v=record.get(scope+"_modifiers")
            if not isinstance(v,dict):
                issues.append(f"{kind} {obj} {scope}: modifier array unverified")
                continue
            mass=float(v["mass"])
            weight=float(v["weight"])
            if abs(weight-1)>1e-9:
                issues.append(f"{kind} {obj} {scope}: native ETABS WEIGHT modifier={weight} not unity")
            if abs(mass-1)>1e-9:
                issues.append(f"{kind} {obj} {scope}: native ETABS MASS modifier={mass}; reconcile separate seismic mass")
            stiff_keys=FRAME_LABELS[:6] if kind=="frame" else AREA_LABELS[:8]
            rows.append(dict(kind=kind,object=obj,section=record["section"],
                modifier_level=scope,stiffness_modifier_values=
                    json.dumps({k:v[k] for k in stiff_keys},sort_keys=True),
                mass_modifier=mass,weight_modifier=weight,
                physical_weight_policy="DO_NOT_APPLY_STIFFNESS_MODIFIERS"))
    pattern_rows=[]
    total_coefficient=0.
    for rec in patterns or []:
        pat=str(rec.get("pattern",""))
        if not pat:raise ValueError("Empty native self-weight load pattern")
        mult=float(rec["multiplier"])
        if not math.isfinite(mult):raise ValueError("Nonfinite self-weight multiplier")
        total_coefficient+=mult
        pattern_rows.append(dict(pattern=pat,self_weight_multiplier=mult))
    if not pattern_rows:
        issues.append("Missing native ETABS load-pattern self-weight multiplier evidence")
    elif abs(total_coefficient-1)>1e-9:
        issues.append(f"Full unfactored 1D+1L self-weight allocation is {total_coefficient}, expected 1.0")
    if native.get("errors") or not native.get("complete"):
        issues.extend(native.get("errors") or ["Native modifier evidence incomplete"])
    nonunit_weight=[x for x in issues if "WEIGHT modifier=" in x]
    if nonunit_weight:
        # Do not knowingly calculate wrong physical weight.
        raise ValueError("NONUNITY NATIVE ETABS WEIGHT MODIFIER; "
                         "do not silently force physical weight=100%: "+
                         " | ".join(nonunit_weight[:8]))
    if issues:
        status="NATIVE_WEIGHT_OR_MASS_EVIDENCE_INCOMPLETE"
    report=dict(schema="gravity-physical-stiffness-mass-separation-v1",
        status=status,mode="READ_ONLY_GRAVITY_ACCOUNTING",
        physical_weight_source="source material gamma times original geometric member volume",
        stiffness_policy="independent elastic ULS/SLS section analysis modifiers",
        mass_policy="independent NBC105 seismic mass factors, not a reduction of physical gravity",
        full_gravity_dead_weight_coefficient=total_coefficient,
        native_records_count=len(native["records"]),
        native_extraction_complete=bool(native.get("complete")),
        evidence_issues=issues,modifiers=rows,patterns=pattern_rows,
        physical_self_weight_not_scaled_by_cracked_section=True,
        source_weight_modifier_verified=(status=="NATIVE_WEIGHT_MODIFIERS_VERIFIED"))
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/"Gravity_Physical_Weight_Modifier_Audit.json").write_text(
        json.dumps(report,indent=2),encoding="utf-8")
    with (out/"Gravity_Physical_Weight_Modifier_Audit.csv").open(
         "w",newline="",encoding="utf-8-sig") as file:
        cols=["kind","object","section","modifier_level","stiffness_modifier_values",
              "mass_modifier","weight_modifier","physical_weight_policy"]
        w=csv.DictWriter(file,fieldnames=cols)
        w.writeheader();w.writerows(rows)
    from openpyxl import Workbook
    wb=Workbook();ws=wb.active;ws.title="Native object and section"
    fields=["kind","object","section","modifier_level","mass_modifier",
            "weight_modifier","stiffness_modifier_values"]
    ws.append(fields)
    for entry in rows:ws.append([entry[k] for k in fields])
    status_sheet=wb.create_sheet("Verification")
    for name,value in report.items():
        if not isinstance(value,(list,dict)):
            status_sheet.append([name,value])
    for issue in issues:status_sheet.append(["EVIDENCE GAP",issue])
    pats=wb.create_sheet("Self weight patterns")
    pats.append(["ETABS pattern","Physical self weight allocation"])
    for rec in pattern_rows:pats.append([rec["pattern"],rec["self_weight_multiplier"]])
    for sheet in wb:
        sheet.freeze_panes="A2"
        sheet.column_dimensions["A"].width=36
        sheet.column_dimensions["B"].width=48
        if sheet.max_row>1:sheet.auto_filter.ref=sheet.dimensions
    wb.save(out/"Gravity_Physical_Weight_Modifier_Audit.xlsx")
    return report

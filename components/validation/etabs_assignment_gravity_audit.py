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


def audit_native_assignment_workbook(workbook_path, output_folder,
                                     beam_audit_path=None):
    """Record material weights, section lists, source-ID/offset consistency.

    DO NOT interpret 'Auto' as a user-verified beam self-weight rule.
    Source workbook and output are local; do not publish workbook bytes.
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
        if beam_audit_path is not None:
            beam=json.loads(Path(beam_audit_path).read_text(encoding="utf-8-sig"))
            if beam.get("schema")!="beam-self-weight-end-offset-v1":
                raise ValueError("Incompatible OpenSees beam audit schema")
            rows=beam["rows"]
            by_id={str(r["etabs_object"]):r for r in rows}
            if len(by_id)!=len(rows) or set(by_id)!=set(beams):
                raise ValueError("OpenSees source-beam IDs fail original native ETABS crosswalk")
            for key in beams:
                a=offset_by_id[key];b=by_id[key]
                for native_field,field in (("Offset I","end_i_m"),
                                           ("Offset J","end_j_m")):
                    if abs(float(a[native_field])/1000-float(b[field]))>0.001:
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

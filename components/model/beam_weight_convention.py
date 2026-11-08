"""Independent, source-traceable beam self-weight clear-length audit.

This module only adjusts applied beam self-weight loads when explicitly
confirmed from native ETABS load/offset evidence; it does NOT use
rigid-zone-factor as a substitute for the ETABS Self Weight Option.
OpenSees frame stiffness, non-self-weight line loads and shell loads are
unchanged.

[REF docs/source/components/model/beam_weight_convention.py.md]
"""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path

GROSS="GROSS_SECTION_LENGTH"
CLEAR="ETABS_BEAM_CLEAR_LENGTH"


def build_beam_weight_audit(segments, frame_metadata, *, policy=GROSS,
                            etabs_clear_weight_confirmed=False):
    """Return source-beam audit plus indexed clear span for each original object.

    [REF CSI ETABS FrameObj.GetEndLengthOffset; ETABS Material List by Object Type]
    Never infer the ETABS Auto self-weight selection just from offsets.
    Activation requires comparing native ETABS beam weight and source
    beam geometry; a zero-offset beam still receives normal full weight.
    """
    if policy not in (GROSS,CLEAR):
        raise ValueError("Unknown ETABS beam weight policy "+str(policy))
    if policy==CLEAR and etabs_clear_weight_confirmed is not True:
        raise ValueError("Clear beam weight requires explicit verification against "
                         "native ETABS beam weight and Self Weight Option")
    rows=[]
    intervals={}
    for obj,children in sorted(segments.items()):
        if not children:continue
        category=str(children[0]["category"]).upper()
        if category!="BEAM":continue
        length=float(children[-1]["end"])
        if not math.isfinite(length) or length<=0:
            raise ValueError("Invalid source beam length "+str(obj))
        area=float(children[0]["properties"]["A"])
        unit_weight=float(children[0]["properties"]["weight"])
        if not all(math.isfinite(x) and x>0 for x in (area,unit_weight)):
            raise ValueError("Invalid beam section area/weight "+str(obj))
        record=frame_metadata.get(str(obj),{}).get("GetEndLengthOffset")
        valid=(isinstance(record,(tuple,list)) and len(record)==5
               and record[-1] in (0,None))
        if valid:
            auto,li,lj,rigid=record[:4]
            li=float(li);lj=float(lj);rigid=float(rigid)
            valid=(all(math.isfinite(x) for x in (li,lj,rigid))
                   and li>=0 and lj>=0 and li+lj<=length+1e-8
                   and 0<=rigid<=1)
        if policy==CLEAR and not valid:
            raise ValueError("Missing/invalid ETABS end offset record for beam "+str(obj))
        if valid:
            clear_start=min(length,li)
            clear_end=max(clear_start,length-lj)
            clear_length=max(0.,clear_end-clear_start)
        else:
            clear_start=0.;clear_end=length;clear_length=length
        gross=area*length*unit_weight
        potential=(length-clear_length)*area*unit_weight if valid else None
        selected_length=clear_length if policy==CLEAR else length
        intervals[str(obj)]=(clear_start,clear_end) if policy==CLEAR else (0.,length)
        rows.append(dict(etabs_object=str(obj),category="BEAM",
             full_length_m=length,end_i_m=li if valid else None,
             end_j_m=lj if valid else None,
             etabs_offset_auto=bool(auto) if valid else None,
             rigid_zone_factor=rigid if valid else None,
             clear_length_m=clear_length if valid else None,
             frame_area_m2=area,unit_weight_kN_m3=unit_weight,
             gross_weight_kN=gross,
             potential_offset_weight_kN=potential,
             selected_weight_kN=area*selected_length*unit_weight,
             selected_policy=policy,
             evidence_state=("SOURCE_OFFSET_VERIFIED_NUMERIC_ONLY" if valid
                             else "SOURCE_OFFSET_UNAVAILABLE")))
    gross_total=sum(r["gross_weight_kN"] for r in rows)
    applied_total=sum(r["selected_weight_kN"] for r in rows)
    return dict(schema="beam-self-weight-end-offset-v1",
       policy=policy,etabs_clear_weight_confirmed=bool(etabs_clear_weight_confirmed),
       status=("ETABS_CLEAR_WEIGHT_SOURCE_CONFIRMED_BY_USER" if policy==CLEAR
               else "AUDIT_ONLY_GROSS_WEIGHT_APPLIED"),
       beam_count=len(rows),
       gross_beam_weight_kN=gross_total,
       selected_beam_weight_kN=applied_total,
       potential_offset_reduction_kN=gross_total-applied_total if policy==CLEAR else
                                     sum(r["potential_offset_weight_kN"] or 0. for r in rows),
       unresolved_offset_count=sum(r["end_i_m"] is None for r in rows),
       constraints=[
         "Only source BEAM self-weight is shortened; columns/walls/slabs/SHS braces retain source weight",
         "Original frame stiffness and non-self-weight frame loads are unchanged",
         "Avoid double subtraction: do not combine with VERIFIED_SINGLE_OWNER volume correction",
         "Rounding and physical insertion-point geometry may still affect local reaction distribution",
         "Seismic mass uses the same assembled corrected source gravity vectors"
       ],rows=rows),intervals


def export_beam_weight_audit(folder,audit):
    """Write per-beam and aggregate comparison including source object IDs.

    [REF docs/source/components/model/beam_weight_convention.py.md]
    """
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    (folder/"ETABS_OpenSees_Beam_Weight_Reconciliation.json").write_text(
        json.dumps(audit,indent=2,allow_nan=False),encoding="utf8")
    with (folder/"ETABS_OpenSees_Beam_Weight_Reconciliation.csv").open(
          "w",newline="",encoding="utf-8-sig") as f:
        if audit["rows"]:
            w=csv.DictWriter(f,fieldnames=list(audit["rows"][0]))
            w.writeheader();w.writerows(audit["rows"])
    return folder

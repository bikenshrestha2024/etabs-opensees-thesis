"""Compare assumed joint counts with geometric RCC-overlap ledger (AUDIT ONLY).

Does not alter gravity loads, physical mass, support nodes, or stiffness.
[REF docs/source/components/gravity/joint_overlap_review.py.md]
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import csv
import json
import math

USER_HYPOTHESIS=dict(
    candidate_points_per_level=32,
    opening_corner_exclusions=8,
    central_wall_exclusions=2,
    outer_core_exclusions=4,
    separately_claimed_wall_joint_count=14,
    column_joint_width_m=1.1,
    column_joint_depth_m=1.1,
    wall_joint_width_m=.6,
    wall_joint_depth_m=.6,
    vertical_joint_depth_m=.8,
    repeated_levels=25,
    unit_weight_kN_m3=25.,
)


def review_joint_overlap(ledger, output_dir, *, hypothesis=None,
                         beam_offset_candidate_kN=None,
                         observed_global_gap_kN=None):
    """Report overlap by intersecting solid type, not assumed node count.

    [REF docs/source/components/gravity/joint_overlap_review.py.md]
    """
    if not isinstance(ledger,dict) or ledger.get("schema")!="joint-volume-ownership-v1":
        raise ValueError("Actual RCC geometric ownership ledger is required")
    hypo=dict(USER_HYPOTHESIS)
    if hypothesis:
        for k in hypothesis:
            if k not in hypo:raise ValueError("Unknown hypothesis dimension "+k)
        hypo.update(hypothesis)
    for k,v in hypo.items():
        n=float(v)
        if not math.isfinite(n) or n<0:
            raise ValueError("Nonfinite or negative assumption "+k)
    total=int(hypo["candidate_points_per_level"])
    excluded=sum(int(hypo[k]) for k in ("opening_corner_exclusions",
        "central_wall_exclusions","outer_core_exclusions"))
    remaining=total-excluded
    claimed=int(hypo["separately_claimed_wall_joint_count"])
    if remaining<0:raise ValueError("Excluded junction count exceeds candidate count")
    if any(int(hypo[k])!=hypo[k] for k in ("candidate_points_per_level",
        "opening_corner_exclusions","central_wall_exclusions",
        "outer_core_exclusions","separately_claimed_wall_joint_count","repeated_levels")):
        raise ValueError("Joint counts and storeys must be whole numbers")
    levels=int(hypo["repeated_levels"])
    unit=hypo["unit_weight_kN_m3"]
    cz=hypo["vertical_joint_depth_m"]
    per_column=hypo["column_joint_width_m"]*hypo["column_joint_depth_m"]*cz*unit
    per_wall=hypo["wall_joint_width_m"]*hypo["wall_joint_depth_m"]*cz*unit
    hypotheses=[
        dict(label="User arithmetic: 18 candidate column plus 14 wall",
             column_count_per_level=remaining,wall_count_per_level=claimed,
             assumed_overlap_weight_kN=levels*(remaining*per_column+claimed*per_wall),
             caveat="Counts may not be disjoint or correspond to actual modeled junctions"),
        dict(label="Alternative partition: 14 column plus 18 wall",
             column_count_per_level=claimed,wall_count_per_level=remaining,
             assumed_overlap_weight_kN=levels*(claimed*per_column+remaining*per_wall),
             caveat="Sensitivity only; not a physical union or an ETABS weight rule"),
        dict(label="14 wall joints only",
             column_count_per_level=0,wall_count_per_level=claimed,
             assumed_overlap_weight_kN=levels*claimed*per_wall,
             caveat="User's second equation, without any column joints"),
    ]
    rows=ledger.get("rows")
    if not isinstance(rows,list):raise ValueError("Missing per-solid geometric ledger")
    group=defaultdict(lambda:dict(items=0,gross_kN=0.,removed_kN=0.,net_kN=0.))
    by_overlap=defaultdict(float)
    by_source=[]
    for row in rows:
        cls=str(row.get("category","")).upper()
        if cls not in {"COLUMN","BEAM","SHEAR WALL","FLOOR"}:
            raise ValueError("Unexpected source solid category "+cls)
        gross=float(row["gross_weight_kN"])
        removed=float(row["removed_weight_kN"])
        net=float(row["net_weight_kN"])
        if not all(math.isfinite(x) and x>=-1e-6 for x in (gross,removed,net)):
            raise ValueError("Nonfinite or negative overlap source weight "+str(row.get("object")))
        if abs(gross-removed-net)>max(.01,gross*1e-8):
            raise ValueError("Invalid conservation of individual RCC solid weight")
        item=group[cls]
        item["items"]+=1
        item["gross_kN"]+=gross
        item["removed_kN"]+=removed
        item["net_kN"]+=net
        for owner in ("COLUMN","SHEAR WALL","FLOOR","BEAM"):
            amount=float(row.get("overlap_with_"+owner+"_m3",0.))
            if amount>0:
                label=cls+"_OVERLAPS_"+owner
                by_overlap[label]+=amount*float(row["unit_weight_kN_m3"])
        by_source.append({
            "source_kind":row["kind"],"etabs_object":row["object"],
            "category":cls,"gross_kN":gross,
            "potential_overlap_kN":removed,"retained_weight_kN":net,
            "ratio_retained":float(row["retained_ratio"]),
            "comment":"GEOMETRY AUDIT, not automatically deducted"})
    actual=sum(x["removed_kN"] for x in group.values())
    declared=float(ledger["potentially_duplicated_RCC_weight_kN"])
    if abs(actual-declared)>max(.01,abs(declared)*1e-8):
        raise ValueError("Ledger total overlap does not match individual solids")
    if abs(sum(by_overlap.values())-declared)>max(.01,abs(declared)*1e-8):
        raise ValueError("Overlap ownership categories do not sum to physical deduction")
    extra={}
    for label,val in (("beam_offset_candidate_kN",beam_offset_candidate_kN),
                      ("observed_global_gap_kN",observed_global_gap_kN)):
        if val is not None:
            v=float(val)
            if not math.isfinite(v):raise ValueError(label+" is nonfinite")
            extra[label]=v
    report=dict(
        schema="joint-overlap-types-review-v1",
        actual_ledger_policy=ledger["policy"],
        geometric_source_verified=bool(ledger.get("geometry_verified",False)),
        actual_ledger_global_overlap_kN=actual,
        actual_group_totals=dict(sorted(group.items())),
        owner_relationship_overlap_kN=dict(sorted(by_overlap.items())),
        all_source_solid_count=len(rows),
        hypothesis=hypo,
        arithmetic_check=dict(
            subtraction_result_32_minus_8_minus_2_minus_4=remaining,
            separately_claimed_wall_joints=claimed,
            assumed_column_joint_kN_each=per_column,
            assumed_wall_joint_kN_each=per_wall),
        alternative_joint_estimates=hypotheses,
        optional_comparison=extra,
        recommendation=("Do not deduct hypotheses from gravity: actual intersection "
            "union from validated source solids is needed. Beam end-offset "
            "candidate and joint union corrections MUST NOT be added."),
        interpretation="AUDIT ONLY, not an ETABS mass/weight convention match",
        limitations=[
            "Only supported axis-aligned centered boxes are represented; object insertion, eccentricity, rotations and irregular solids may invalidate physical union.",
            "A floor node or an opening-edge node is not itself a weight volume; classify modeled solids rather than point names.",
            "Physical slab-beam-column-wall overlaps and ETABS frame self-weight options are distinct source-model accounting questions.",
            "All 25 floors may have different member dimensions. Constant junction counts/depths are hypotheses, not deductions.",
            "Changing foundation support count cannot change the independently applied physical building gravity."
        ])
    out=Path(output_dir)
    out.mkdir(parents=True,exist_ok=True)
    (out/"Gravity_Joint_Type_Overlap_Review.json").write_text(
        json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    with (out/"Gravity_Joint_Type_Overlap_Solids.csv").open(
        "w",newline="",encoding="utf-8-sig") as f:
        writer=csv.DictWriter(f,fieldnames=list(by_source[0]) if by_source else
            ["source_kind","etabs_object","category","gross_kN","potential_overlap_kN","retained_weight_kN","ratio_retained","comment"])
        writer.writeheader();writer.writerows(by_source)
    with (out/"Gravity_Joint_Type_Overlap_Review.csv").open(
        "w",newline="",encoding="utf-8-sig") as f:
        writer=csv.writer(f)
        writer.writerow(["category","count","gross_kN","potential_overlap_kN","net_kN"])
        for category,v in sorted(group.items()):
            writer.writerow([category,v["items"],v["gross_kN"],v["removed_kN"],v["net_kN"]])
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font,PatternFill
    except ImportError:
        raise RuntimeError("openpyxl required for review workbook; CSV and JSON already saved")
    wb=Workbook()
    summary=wb.active
    summary.title="Component overlap"
    summary.append(["Element category","Object or cell count","Gross weight kN",
                    "Potential overlap kN","Retained weight kN"])
    for category,v in sorted(group.items()):
        summary.append([category,v["items"],v["gross_kN"],v["removed_kN"],v["net_kN"]])
    pairs=wb.create_sheet("Physical overlap ownership")
    pairs.append(["Physical intersection type","Potential overlap weight kN"])
    for k,v in sorted(by_overlap.items()):pairs.append([k,v])
    est=wb.create_sheet("Count arithmetic hypotheses")
    est.append(["Hypothesis","Column per level","Wall per level",
                "Assumed weight kN","Status"])
    for h in hypotheses:
        est.append([h["label"],h["column_count_per_level"],
                    h["wall_count_per_level"],h["assumed_overlap_weight_kN"],
                    "HYPOTHESIS ONLY, NOT APPLIED"])
    detail=wb.create_sheet("Actual model solids")
    keys=list(by_source[0]) if by_source else []
    if keys:
        detail.append(keys)
        for item in by_source:detail.append([item[k] for k in keys])
    flags=wb.create_sheet("Engineering gates")
    for k,v in [("Actual union potential",actual),
                ("Geometry verified",ledger.get("geometry_verified")),
                ("32-8-2-4",remaining),
                ("Separately claimed wall count",claimed),
                ("Original ETABS Self Weight Option","NOT VERIFIED BY THIS MODULE"),
                ("Double deduction","PROHIBITED"),
                ("Source-volume representation","AXIS-ALIGNED BOX ASSUMPTION"),
                ("ETABS base reaction equivalence","NOT VALIDATED")]:
        flags.append([k,v])
    for sheet in wb:
        sheet.freeze_panes="A2"
        sheet.column_dimensions["A"].width=46
        sheet.column_dimensions["B"].width=32
        if sheet.max_row>1:sheet.auto_filter.ref=sheet.dimensions
        for cell in sheet[1]:
            cell.font=Font(color="FFFFFF",bold=True)
            cell.fill=PatternFill("solid",fgColor="183B56")
    wb.save(out/"Gravity_Joint_Type_Overlap_Review.xlsx")
    return report

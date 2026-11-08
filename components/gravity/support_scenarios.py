"""Compare full-gravity results for two independently run wall-base restraint policies.

Both models MUST share the same applied load profile, geometry and units.
This is a *boundary-condition sensitivity study*, not automatic verification
of foundation design or equality with the ETABS analysis mesh.
"""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path

SOURCE="ETABS_SOURCE_SUPPORTS"
CONTINUOUS="CONTINUOUS_WALL_BASE_FIXED"
PROFILES=(SOURCE,CONTINUOUS)
DISPLAY_NAMES={
    SOURCE:"ETABS Reaction Validation",
    CONTINUOUS:"ETABS Node Position / Continuous",
}

def compare_wall_support_gravity(source_result, continuous_result):
    """Compare two real completed gravity solver results and matching node tags.

    [REF components/model/assembly.py _gravity_wall_support_strategy]
    [REF docs/review/GRAVITY_ETABS_COMPARISON.md]
    """
    results={SOURCE:source_result,CONTINUOUS:continuous_result}
    for mode,payload in results.items():
        if not payload.get("ok"):
            raise ValueError(mode+" did not complete gravity analysis")
        if payload.get("wall_support_strategy")!=mode:
            raise ValueError(mode+" has missing/wrong support strategy provenance")
        if payload.get("gravity_profile")!="GRAVITY_1.0D_1.0L":
            raise ValueError(mode+" is not full 1.0D+1.0L gravity")
    def scalar(row,key):
        value=float(row[key])
        if not math.isfinite(value):raise ValueError("Nonfinite "+key)
        return value
    a=source_result["report"];b=continuous_result["report"]
    wa=scalar(a,"applied_vertical_load_kN");wb=scalar(b,"applied_vertical_load_kN")
    if abs(wa-wb)>max(0.01,wa*1e-7):
        raise ValueError("Two gravity cases have different applied vertical loads")
    summary=[]
    for mode,payload in results.items():
        rep=payload["report"]
        summary.append(dict(strategy=mode,display_name=DISPLAY_NAMES[mode],
            applied_kN=scalar(rep,"applied_vertical_load_kN"),
            reaction_kN=scalar(rep,"support_vertical_reaction_kN"),
            equilibrium_error_percent=scalar(rep,"equilibrium_error_percent"),
            maximum_downward_Uz_m=scalar(rep,"max_downward_vertical_displacement_m"),
            support_count=len(payload["reactions"]),
            additional_wall_base_nodes=len(payload.get("added_wall_support_tags",[]))))
    source_by={str(r["node_tag"]):r for r in source_result["reactions"]}
    continuous_by={str(r["node_tag"]):r for r in continuous_result["reactions"]}
    coords={str(n["tag"]):n for n in continuous_result["nodes"]}
    rows=[]
    for tag in sorted(set(source_by)|set(continuous_by),key=lambda v:int(v)):
        aa=source_by.get(tag);bb=continuous_by.get(tag);c=coords.get(tag,{})
        ra=scalar(aa,"rz_kN") if aa else None
        rb=scalar(bb,"rz_kN") if bb else None
        rows.append(dict(node_tag=tag,x_m=c.get("x_m"),y_m=c.get("y_m"),
            z_m=c.get("z_m"),source_only_Rz_kN=ra,
            continuous_Rz_kN=rb,
            delta_kN=rb-ra if ra is not None and rb is not None else None,
            status="COMMON_REACTION" if ra is not None and rb is not None else
                ("CONTINUOUS_ONLY" if bb else "SOURCE_ONLY_ONLY")))
    return dict(
        schema="gravity-wall-base-strategy-v1",
        status="SENSITIVITY_NOT_ETABS_VALIDATION_OR_FOUNDATION_DESIGN",
        strategy_display_names=dict(DISPLAY_NAMES),
        same_full_gravity_applied_kN=wa,
        summary=summary,per_node=rows,
        reaction_total_difference_kN=summary[1]["reaction_kN"]-summary[0]["reaction_kN"],
        max_Uz_difference_m=summary[1]["maximum_downward_Uz_m"]-summary[0]["maximum_downward_Uz_m"],
        explanation=[
            "Only restraints differ; shell and frame loads and seismic mass are unchanged",
            "The continuous-base run is a prescribed fixed-boundary sensitivity case, not a raft/soil spring model",
            "Individual reactions at newly fixed nodes have no one-to-one ETABS equivalent",
            "ETABS comparison requires native wall auto-mesh edge restraint/constraint verification"
        ])

def export_wall_support_comparison(report,output):
    """Write source data, comparison workbook and concise machine-readable JSON.

    [REF components/gravity/gui_and_reports.py GravityAnalysisGUI.run_both_wall_supports]
    """
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    (out/"Gravity_Wall_Base_Strategy_Comparison.json").write_text(
        json.dumps(report,indent=2,allow_nan=False),encoding="utf8")
    fields=["node_tag","x_m","y_m","z_m","source_only_Rz_kN",
            "continuous_Rz_kN","delta_kN","status"]
    with (out/"Gravity_Wall_Base_Nodal_Reaction_Differences.csv").open(
        "w",newline="",encoding="utf-8-sig") as stream:
        w=csv.DictWriter(stream,fieldnames=fields);w.writeheader();w.writerows(report["per_node"])
    from openpyxl import Workbook
    wb=Workbook();ws=wb.active;ws.title="Summary"
    ws.append(["Two gravity wall-base strategies","Sensitivity analysis only"])
    ws.append(["Applied gravity (kN)",report["same_full_gravity_applied_kN"]])
    ws.append(["Reaction difference (kN)",report["reaction_total_difference_kN"]])
    ws.append(["Max downward UZ difference (m)",report["max_Uz_difference_m"]])
    sm=wb.create_sheet("Strategy cases")
    cols=list(report["summary"][0]);sm.append(cols)
    for item in report["summary"]:sm.append([item[k] for k in cols])
    nd=wb.create_sheet("Support reaction differences")
    nd.append(fields)
    for row in report["per_node"]:nd.append([row.get(k) for k in fields])
    nd.freeze_panes="A2";nd.auto_filter.ref=nd.dimensions
    wb.save(out/"Gravity_Wall_Base_Strategy_Comparison.xlsx")
    return out

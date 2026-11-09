"""Independent saved-response comparison for ETABS and OpenSees ESM/PDelta.

Only physically comparable RAW (unamplified) signed response columns accepted.
CSV schema: story_name,elevation_m,story_shear_kN,displacement_m,drift_ratio
Rows are aligned by unique story_name AND matching elevation.
All ETABS data are separate source evidence; source case definitions must pass
check_etabs_case_contract BEFORE any comparison is labelled comparable.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path

FIELDS=("story_shear_kN","displacement_m","drift_ratio")
ABS_SCREEN={"story_shear_kN":1.0,"displacement_m":1e-5,"drift_ratio":1e-6}
REL_SCREEN_PERCENT=5.0

def _hash(path):
    digest=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):digest.update(block)
    return digest.hexdigest()

def _read_rows(path):
    p=Path(path).resolve()
    if not p.is_file():raise FileNotFoundError(p)
    rows={}
    with p.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        missing={"story_name","elevation_m",*FIELDS}-set(reader.fieldnames or ())
        if missing:raise ValueError(f"{p.name}: missing {sorted(missing)}")
        for r in reader:
            name=str(r["story_name"]).strip()
            if not name or name in rows:raise ValueError("Empty/duplicate story ID: "+name)
            row={}
            for k in ("elevation_m",*FIELDS):
                value=float(r[k])
                if not math.isfinite(value):raise ValueError(f"{name}: invalid {k}")
                row[k]=value
            rows[name]=row
    if not rows:raise ValueError("Empty story response table")
    return rows

def compare_saved_case(*,etabs_csv,opensees_csv,output_dir,axis,
                        etabs_case,opensees_case,contract_issues=(),
                        metadata=None):
    """Never invent a PASS when source case physics or data are unverified."""
    axis=str(axis).upper()
    if axis not in ("X","Y"):raise ValueError("Axis must be X or Y")
    details=dict(metadata or {})
    required=("source_model_sha256","units","support_strategy","response_scope",
              "eccentricity_branch","gravity_preload","pdelta_stiffness_source",
              "load_pattern_factors","limit_state")
    blockers=list(contract_issues)
    blockers += ["MISSING_METADATA:"+k for k in required
                 if k not in details or details[k] in (None,"")]
    if details.get("response_scope")!="RAW_SIGNED_ANALYSIS":
        blockers.append("RESPONSE_MUST_BE_RAW_NOT_DESIGN_AMPLIFIED")
    if details.get("units")!="kN_m":
        blockers.append("RESULT_UNITS_MUST_BE_kN_m")
    if details.get("model_equivalence_verified") is not True:
        blockers.append("SOURCE_MODEL_EQUIVALENCE_NOT_VERIFIED")
    if details.get("force_case_equivalence_verified") is not True:
        blockers.append("LATERAL_FORCE_CASE_EQUIVALENCE_NOT_VERIFIED")
    if details.get("preload_equivalence_verified") is not True:
        blockers.append("PRELOAD_AND_STIFFNESS_EQUIVALENCE_NOT_VERIFIED")
    if details.get("coordinate_system")!="GLOBAL_XY":
        blockers.append("COORDINATE_AXES_NOT_CONFIRMED")
    a=_read_rows(etabs_csv)
    b=_read_rows(opensees_csv)
    if set(a)!=set(b):
        blockers.append("STORY_ID_SET_MISMATCH")
    common=sorted(set(a)&set(b),key=lambda n:a[n]["elevation_m"])
    results=[]
    for story in common:
        x,y=a[story],b[story]
        if abs(x["elevation_m"]-y["elevation_m"])>1e-4:
            blockers.append("STORY_HEIGHT_MISMATCH:"+story)
            continue
        for key in FIELDS:
            ref,calc=x[key],y[key]
            delta=calc-ref
            diff_pct=None if abs(ref)<ABS_SCREEN[key] else 100*delta/abs(ref)
            screened=(abs(delta)<=ABS_SCREEN[key] or
                      (diff_pct is not None and abs(diff_pct)<=REL_SCREEN_PERCENT))
            results.append(dict(axis=axis,etabs_case=etabs_case,
                opensees_case=opensees_case,story_name=story,
                elevation_m=x["elevation_m"],metric=key,
                etabs_value=ref,opensees_value=calc,
                signed_difference=delta,absolute_difference=abs(delta),
                signed_percent_difference=diff_pct,
                screen_within_5_percent=screened,
                screening_not_code_acceptance=True))
    if not common:blockers.append("NO_COMMON_STORIES")
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    csv_path=out/("EQ_Comparison_"+axis+".csv")
    columns=list(results[0]) if results else [
        "axis","etabs_case","opensees_case","story_name","elevation_m",
        "metric","etabs_value","opensees_value","signed_difference",
        "absolute_difference","signed_percent_difference",
        "screen_within_5_percent","screening_not_code_acceptance"]
    with csv_path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(results)
    report=dict(schema="etabs-opensees-static-earthquake-comparison-v1",
        axis=axis,etabs_case=etabs_case,opensees_case=opensees_case,
        etabs_source=dict(path=str(Path(etabs_csv).resolve()),sha256=_hash(etabs_csv)),
        opensees_source=dict(path=str(Path(opensees_csv).resolve()),sha256=_hash(opensees_csv)),
        metadata=details,blockers=sorted(set(blockers)),
        checked_rows=len(results),scanned_failures=sum(
            not row["screen_within_5_percent"] for row in results),
        status=("COMPATIBLE_NUMERIC_SCREEN_ONLY"
                if not blockers else "BLOCKED_NOT_COMPARABLE"),
        note="5% diagnostic screen is not a structural or seismic code acceptance criterion. "
             "Only signed raw static responses at the same elevations and identical "
             "load/eccentricity branches can be compared.")
    (out/("EQ_Comparison_"+axis+".json")).write_text(
        json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    try:
        from openpyxl import Workbook
        wb=Workbook(); ws=wb.active; ws.title="Comparison"
        ws.append(columns)
        for row in results:ws.append([row[k] for k in columns])
        note=wb.create_sheet("Gates")
        note.append(["Status",report["status"]])
        for blocker in report["blockers"]:note.append(["Blocker",blocker])
        note.append(["Note",report["note"]])
        for sh in wb:
            sh.freeze_panes="A2"
            sh.column_dimensions["A"].width=35
        wb.save(out/("EQ_Comparison_"+axis+".xlsx"))
    except ImportError:pass
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(1,3,figsize=(15,6),constrained_layout=True)
        titles={"story_shear_kN":"Story shear (kN)","displacement_m":"Raw displacement (m)",
                "drift_ratio":"Raw interstory drift ratio"}
        for j,key in enumerate(FIELDS):
            values=[r for r in results if r["metric"]==key]
            ax[j].plot([r["etabs_value"] for r in values],
                       [r["elevation_m"] for r in values],"o-",label="ETABS")
            ax[j].plot([r["opensees_value"] for r in values],
                       [r["elevation_m"] for r in values],"x--",label="OpenSees")
            ax[j].set(xlabel=titles[key],ylabel="Elevation (m)")
            ax[j].grid(alpha=0.3);ax[j].legend()
        fig.suptitle(f"{axis}: {etabs_case} versus {opensees_case} | {report['status']}")
        fig.savefig(out/("EQ_Comparison_"+axis+".png"),dpi=150)
        plt.close(fig)
    except ImportError:pass
    return report

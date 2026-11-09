"""Run a complete offline 4-case EQX/EQY comparison matrix from a JSON index.

Index layout:
{"cases":[{"axis":"X","role":"dependent_positive","etabs_case":...,
"opensees_case":...,"native_case_definition":{...},
"initial_source_case":"EQX+ P Delta Initial",
"etabs_story_csv":"...","opensees_story_csv":"...",
"comparison_metadata":{...}}, ...]}
The script NEVER launches ETABS or OpenSees; no inferred input data.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from components.validation.eq_pdelta_case_contract import check_etabs_case_contract
from components.validation.eq_pdelta_comparison import compare_saved_case

def execute_matrix(config_path,out_dir):
    source=Path(config_path).resolve()
    cfg=json.loads(source.read_text(encoding="utf-8-sig"))
    if not isinstance(cfg,dict) or not isinstance(cfg.get("cases"),list):
        raise ValueError("Index requires list 'cases'")
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    rows=[]
    used=set()
    for entry in cfg["cases"]:
        axis=str(entry.get("axis","")).upper()
        role=entry.get("role")
        key=(axis,role)
        if key in used:raise ValueError("Duplicate earthquake case axis and role: "+str(key))
        used.add(key)
        issues=check_etabs_case_contract(
            entry.get("native_case_definition"),axis=axis,role=role,
            initial_case=entry.get("initial_source_case"))
        # Cases that cannot be compared still get a gate report; these are
        # not zero-valued measurements or implicit success.
        raw_files=(entry.get("etabs_story_csv"),entry.get("opensees_story_csv"))
        if any(not p or not Path(p).is_file() for p in raw_files):
            rows.append(dict(axis=axis,role=role,
                status="BLOCKED_MISSING_SAVED_RESPONSE",
                blockers=issues+["MISSING_ETABS_OR_OPENSEES_STORY_CSV"],
                etabs_case=entry.get("etabs_case"),
                opensees_case=entry.get("opensees_case")))
            continue
        result=compare_saved_case(
            etabs_csv=raw_files[0],opensees_csv=raw_files[1],
            output_dir=out/f"{axis}_{role}",axis=axis,
            etabs_case=str(entry.get("etabs_case","")),
            opensees_case=str(entry.get("opensees_case","")),
            contract_issues=issues,
            metadata=entry.get("comparison_metadata") or {})
        rows.append(dict(axis=axis,role=role,
                         status=result["status"],blockers=result["blockers"],
                         checked_rows=result["checked_rows"],
                         screen_failures=result["scanned_failures"],
                         etabs_case=entry.get("etabs_case"),
                         opensees_case=entry.get("opensees_case")))
    required={(axis,role) for axis in ("X","Y")
                        for role in ("plain","dependent_positive")}
    missing=sorted(required-used)
    result=dict(schema="eqx-eqy-pdelta-static-four-case-matrix-v1",
                index_source=str(source),
                matrix=rows,missing_required_cases=missing,
                overall="REVIEW_ONLY_NOT_CODE_ACCEPTANCE",
                caution="Raw signed response comparisons are gated by source identity, "
                        "PDelta stiffness case, eccentricity, selected step and drift definition. "
                        "Unmatched cases are not filled with zero.")
    (out/"EQ_PDelta_4Case_Matrix.json").write_text(
        json.dumps(result,indent=2,allow_nan=False),encoding="utf-8")
    try:
        from openpyxl import Workbook
        wb=Workbook();ws=wb.active;ws.title="Case matrix"
        ws.append(["Axis","Role","ETABS case","OpenSees case","Status",
                   "Blockers","Compared rows","Screen failures"])
        for r in rows:
            ws.append([r.get("axis"),r.get("role"),r.get("etabs_case"),
                       r.get("opensees_case"),r["status"],"; ".join(r["blockers"]),
                       r.get("checked_rows"),r.get("screen_failures")])
        ws.append(["MISSING REQUIRED","; ".join(map(str,missing))])
        ws.freeze_panes="A2"
        ws.column_dimensions["A"].width=26
        ws.column_dimensions["B"].width=26
        ws.column_dimensions["C"].width=30
        ws.column_dimensions["D"].width=30
        ws.column_dimensions["E"].width=40
        ws.column_dimensions["F"].width=85
        wb.save(out/"EQ_PDelta_4Case_Matrix.xlsx")
    except ImportError:pass
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("matrix_json")
    parser.add_argument("--out",default="EQ_PDelta_Comparison")
    args=parser.parse_args()
    report=execute_matrix(args.matrix_json,args.out)
    for row in report["matrix"]:
        print(row["axis"],row["role"],row["status"],row["blockers"])
    print("MISSING:",report["missing_required_cases"])

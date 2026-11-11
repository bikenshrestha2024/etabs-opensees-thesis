"""Read-only original Excel versus continuous-pier Aw reconciliation.

Never substitutes continuous-pier Aw for the approved original workbook method.
A same-EDB source hash is required. Numerical differences alone do not identify
which physical wall is responsible when the wall IDs are not shared.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

from components.inputs.aw_sources import (
    latest_linked_reference, linked_reference_from_audit, edb_identity,
)


def reconcile(export_dir, state, *, audit_path=None):
    """[REF docs/source/components/equivalent_static/aw_reconciliation.py.md] Source contract and engineering limitations in linked guide."""
    from components.inputs.project_workbooks import _source_edb_path
    from components.inputs.opensees_nbc_sync import _source_snapshot
    current_edb = _source_edb_path(export_dir)
    if not current_edb:
        raise ValueError("Current export has no source ETABS EDB identity")
    if audit_path is None:
        ref, reason = latest_linked_reference(export_dir, state)
        if ref is None:
            raise ValueError("No same-EDB original Excel calculation: " + reason)
        audit_path = ref["provenance_json"]
    audit_file = Path(audit_path)
    audit = json.loads(audit_file.read_text(encoding="utf-8-sig"))
    identity = edb_identity(current_edb, audit)
    if identity not in ("SAME_EDB_PATH", "BYTE_IDENTICAL_EDB"):
        raise ValueError("Excel and selected EDB are not proven identical; " + identity)
    ref = linked_reference_from_audit(audit, audit_file, state=state, current_edb=current_edb)
    snapshot = _source_snapshot(export_dir, state)
    axes = {}
    for axis in ("X", "Y"):
        record = audit["coefficients"][axis]
        excel_aw = float(record["Aw_m2"])
        snapshot_aw = snapshot["aw_candidate_m2"].get(axis)
        snap = snapshot["opening_reduction_audit"]["axes"][axis]
        continuous = float(snapshot_aw) if snapshot_aw is not None else None
        rows = record.get("original_excel_row_contributions", [])
        contributions = [float(r["Aw_contribution_m2"]) for r in rows
                         if r.get("Aw_contribution_m2") is not None]
        if len(contributions) != len(rows):
            raise ValueError(axis + " original Excel wall contributions are incomplete")
        if not math.isclose(math.fsum(contributions), excel_aw, rel_tol=1e-7, abs_tol=1e-8):
            raise ValueError(axis + " workbook wall contributions do not reconstruct Aw")
        axes[axis] = {
            "original_excel_aw_m2": excel_aw,
            "original_workbook_adopted_period_s": float(record["T1_s"]),
            "continuous_pier_diagnostic_m2": continuous,
            "gross_projected_diagnostic_m2": snap["gross_projected_Aw_m2"],
            "excel_minus_continuous_m2": (excel_aw - continuous if continuous is not None else None),
            "excel_rows": rows,
            "gross_segments": snap.get("gross_segments", []),
            "continuous_segments": snap.get("continuous_segments", []),
            "opening_evidence": snapshot["aw_evidence"][axis],
            "wall_by_wall_match_status": "NOT_PAIRED_WITH_COMMON_ETABS_WALL_IDS",
            "status": "NUMERICAL_RESEARCH_RECONCILIATION_NOT_CODE_ACCEPTANCE"
        }
    return {
        "state": state,
        "edb_identity": identity,
        "source_edb": str(current_edb),
        "original_source_sha256": audit.get("source_edb_sha256"),
        "original_workbook_sha256": audit.get("source_excel_sha256"),
        "original_excel_audit": str(audit_file),
        "assembled_model_sha256": snapshot["assembled_model_sha256"],
        "axes": axes,
        "caution": ("The NBC first-storey Aw index, gross geometric projection, and "
                    "through-height continuous-pier diagnostic are different measures. "
                    "Without a shared verified object-to-pier/opening map, individual "
                    "contribution differences cannot be assigned to a specific wall.")
    }


def export_reconciliation(export_dir, state, output_dir, *, audit_path=None):
    """[REF docs/source/components/equivalent_static/aw_reconciliation.py.md] Source contract and engineering limitations in linked guide."""
    report = reconcile(export_dir, state, audit_path=audit_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "NBC105_Aw_Reconciliation.json").write_text(
        json.dumps(report, indent=2, default=str, allow_nan=False), encoding="utf-8")
    from openpyxl import Workbook
    wb = Workbook()
    summary = wb.active
    summary.title = "Aw comparison"
    summary.append(["Axis", "Original Excel Aw (m2)", "Continuous diagnostic (m2)",
                    "Gross projection (m2)", "Excel minus continuous (m2)",
                    "Excel adopted period (s)", "Interpretation"])
    for axis in ("X", "Y"):
        r = report["axes"][axis]
        summary.append([axis, r["original_excel_aw_m2"],
                        r["continuous_pier_diagnostic_m2"],
                        r["gross_projected_diagnostic_m2"],
                        r["excel_minus_continuous_m2"],
                        r["original_workbook_adopted_period_s"],
                        r["wall_by_wall_match_status"]])
    excel_sheet = wb.create_sheet("EXCEL_ORIGINAL")
    excel_sheet.append(["Axis", "Excel row", "Length (m)", "Effective length (m)",
                        "Aw contribution (m2)", "Source cell references"])
    for axis, r in report["axes"].items():
        for item in r["excel_rows"]:
            excel_sheet.append([axis, item.get("row"),
                                item.get("gross_wall_length_m"),
                                item.get("effective_wall_length_m"),
                                item.get("Aw_contribution_m2"),
                                json.dumps(item.get("source_cells", {}))])
    for key, label in (("gross_segments", "GROSS_GEOMETRY"),
                       ("continuous_segments", "CONTINUOUS_PIER")):
        ws = wb.create_sheet(label)
        ws.append(["Axis", "Source segmentation JSON - NOT matched to Excel object IDs"])
        for axis, r in report["axes"].items():
            for item in r[key]:
                ws.append([axis, json.dumps(item, default=str)])
    origin = wb.create_sheet("SOURCE_PROVENANCE")
    for key in ("state", "edb_identity", "source_edb", "original_source_sha256",
                "original_workbook_sha256", "original_excel_audit",
                "assembled_model_sha256", "caution"):
        origin.append([key, report.get(key)])
    for ws in wb:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
    wb.save(out / "NBC105_Aw_Reconciliation.xlsx")
    return report, out

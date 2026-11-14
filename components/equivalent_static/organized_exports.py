"""Copy-only combined export for NBC 105 ESM. Never reclassify diagnostic loads as code acceptance.

Keep legacy solver outputs at their original paths: generated runner scripts may
refer to them. This module creates an independent review snapshot with explicit
ETABS-linked and OpenSees-direct namespaces, provenance, source hashes and ZIP.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

_CASE = re.compile(r"(ULS|SLS)_[XY][+-]_E[+-0]", re.IGNORECASE)
_STATE = re.compile(r"(ULS|SLS)", re.IGNORECASE)
_MODULES = {
    "etabs": "ETABS_Linked_Equivalent_Static",
    "opensees": "OpenSees_Direct_Equivalent_Static",
}
_CATEGORIES = {
    ".json": "JSON", ".xlsx": "Excel", ".xls": "Excel",
    ".csv": "CSV", ".pdf": "PDF", ".png": "Plots",
    ".jpg": "Plots", ".jpeg": "Plots", ".py": "Scripts",
    ".log": "Logs", ".txt": "Logs",
}
_DIRECT_PREFIXES = (
    "NBC105_ESM_", "OpenSees_NBC105_ESM_", "ESM_Source_Diagnostics",
    "NBC105_Rayleigh_",
)


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_files(root):
    """Yield ESM files only; ignore gravity, other analysis and previous snapshots."""
    for source in sorted(root.iterdir()):
        if source.is_file() and source.name.startswith(_DIRECT_PREFIXES):
            if source.suffix.lower() in _CATEGORIES and not source.name.endswith(".processing.json"):
                yield "opensees", source
    for subfolder, role in (("ETABS_Linked_ESM", "etabs"),
                            ("ESM_Runner_Status", "opensees")):
        folder = root / subfolder
        if folder.is_dir():
            for source in sorted(folder.rglob("*")):
                if source.is_file() and not source.is_symlink():
                    if source.suffix.lower() in _CATEGORIES and not source.name.endswith(".processing.json"):
                        yield role, source


def _case_info(path):
    match = _CASE.search(path.name)
    if match:
        return match.group(0).upper().replace("+", "plus").replace("-", "minus"), match.group(1).upper()
    match = _STATE.search(path.name)
    return "GENERAL", match.group(1).upper() if match else "UNSPECIFIED"


def _data_rows(input_root):
    cases, stories = [], []
    for file in sorted(input_root.glob("NBC105_ESM_Calculation_*.json")):
        try:
            document = json.loads(file.read_text(encoding="utf-8-sig"))
            if not isinstance(document, dict):
                raise ValueError("calculation JSON must contain an object")
            case = str(document.get("response_case") or document.get("direction_case") or file.stem)
            row = {
                "Case": case,
                "State": document.get("limit_state"),
                "Period T1 (s)": document.get("period_s"),
                "Aw-X (m2)": (document.get("period_selection") or {}).get("empirical_Aw_X_m2")
                    if isinstance(document.get("period_selection") or {}, dict) else None,
                "Aw-Y (m2)": (document.get("period_selection") or {}).get("empirical_Aw_Y_m2")
                    if isinstance(document.get("period_selection") or {}, dict) else None,
                "Z": document.get("zoning_factor_Z"),
                "Soil": document.get("soil_type"),
                "Site verification": document.get("site_subsoil_status"),
                "Ch(T1)": document.get("spectral_shape_Ch"),
                "C elastic": document.get("elastic_spectrum_C_k"),
                "Cd design": document.get("design_coefficient_Cd"),
                "W (kN)": document.get("total_seismic_weight_kN"),
                "V (kN)": document.get("base_shear_kN"),
                "k": document.get("period_exponent_k"),
                "Sum Fi (kN)": document.get("total_floor_force_kN"),
                "ESM eligible": bool(document.get("code_eligible", False)),
                "Eligibility reason": document.get("esm_eligibility"),
                "ETABS parity": "NOT VERIFIED — independent source comparison required",
                "Source": file.name,
            }
            cases.append(row)
            for floor in document.get("stories", []):
                if not isinstance(floor, dict):
                    continue
                stories.append({
                    "Case": case, "State": document.get("limit_state"),
                    "Story": floor.get("story_name"),
                    "Index": floor.get("story_number"),
                    "h (m)": floor.get("height_m"),
                    "Wi (kN)": floor.get("seismic_weight_kN"),
                    "Wi*h^k": (
                        float(floor["seismic_weight_kN"]) *
                        float(floor["height_m"]) ** float(document["period_exponent_k"])
                        if all(k in floor for k in ("seismic_weight_kN", "height_m"))
                        and "period_exponent_k" in document else None
                    ),
                    "Fi (kN)": floor.get("lateral_force_kN"),
                    "Master node": floor.get("master_node_tag"),
                    "Source": file.name,
                })
        except (OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
            cases.append({"Case": file.stem, "ETABS parity": "INVALID SOURCE",
                          "Eligibility reason": str(exc), "Source": file.name})
    return cases, stories


def _combined_workbook(target, cases, stories, manifest):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    wb = Workbook()
    cover = wb.active
    cover.title = "Read Me"
    for row in (
        ("NBC 105:2025 ESM consolidated review", "Comparative evidence only"),
        ("Output type", "Copy-only combined calculation and source index"),
        ("Structural response", "Not inferred from the applied-force cases"),
        ("ULS high-rise eligibility", "Per-case: inspect eligibility flag; do NOT assert code acceptance"),
        ("Site classification", "Vs30 and geotechnical evidence must be independently verified"),
        ("ETABS source match", "Same EDB SHA + verified case-story mapping required"),
        ("Stop/cancel", "Cancelled/failed solver cases must not be reported as validated"),
        ("Engineering review", "REVIEW_MAIN/02_ESM: model-specific acceptance remains open"),
    ):
        cover.append(row)
    for name, rows in (("Case Summary", cases), ("Storey Forces", stories), ("Source Manifest", manifest)):
        sheet = wb.create_sheet(name)
        if not rows:
            sheet.append(["No matching saved data; no results inferred"])
            continue
        headings = list(dict.fromkeys(key for row in rows for key in row))
        sheet.append(headings)
        for row in rows:
            sheet.append([str(row.get(key)) if isinstance(row.get(key), (dict, list))
                          else row.get(key) for key in headings])
    gate = wb.create_sheet("Validation Gates")
    for row in (
        ("Gate", "State", "Reason"),
        ("Source model SHA / EDB identity", "REQUIRES REVIEW", "Match workbook, OpenSees source and native ETABS EDB"),
        ("Wall Aw opening/grouping", "REQUIRES REVIEW", "Do not equate 12m grouped geometry with legacy 6m wall input"),
        ("Seismic mass / gravity overlap", "REQUIRES REVIEW", "Validate original load factors and isolated load paths"),
        ("ULS ESM method eligibility", "COMPARISON ONLY FOR HIGH-RISE", "NBC §3.2.1 limitations"),
        ("Site Vs30", "REQUIRES GEOTECHNICAL EVIDENCE", "NBC §4.1.3.1"),
        ("Solved response", "NOT INFERRED", "Applied floor force is not recovered story shear"),
        ("Native ETABS comparison", "NOT VERIFIED", "Separate source-identical response evidence required"),
    ):
        gate.append(row)
    for sheet in wb:
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="203A5F")
        for column in sheet.columns:
            first = column[0]
            max_width = max((len(str(c.value)) if c.value is not None else 0
                             for c in column), default=12)
            sheet.column_dimensions[first.column_letter].width = min(72, max(15, max_width + 2))
        for row in sheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=False)
    wb.save(target)


def _latest_batch_status(root):
    """Read one newest ESM solver batch. Never equate calculation files with solved cases."""
    directory = root / "ESM_Runner_Status"
    candidates = sorted(directory.glob("*/CASE_STATUS.json")) if directory.is_dir() else []
    if not candidates:
        return {"status": "NOT_RUN", "completed": 0, "records": [], "status_file": None}
    path = max(candidates, key=lambda p: (p.stat().st_mtime_ns, str(p)))
    try:
        records = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(records, list):
            raise ValueError("CASE_STATUS must be a list")
        for item in records:
            if not isinstance(item, dict) or not isinstance(item.get("case"), str):
                raise ValueError("CASE_STATUS contains invalid case row")
        expected = {file.name for file in root.glob(
            "OpenSees_NBC105_ESM_Load_And_Static_Analysis_*.py")}
        recorded = [item["case"] for item in records]
        unique_recorded = set(recorded)
        # Do not certify completion on count alone: duplicates or an unrelated
        # older run can otherwise hide a missing X/Y eccentricity case.
        successes = {
            item["case"] for item in records
            if item["case"] in expected
            and item.get("status") == "SUCCESS"
            and item.get("return_code") == 0
        }
        duplicates = sorted({name for name in recorded if recorded.count(name) > 1})
        missing = sorted(expected - successes)
        unexpected = sorted(unique_recorded - expected)
        complete = (
            bool(expected) and not duplicates and not missing
            and not unexpected and len(records) == len(expected)
        )
        state = "COMPLETE_SOLVER_ONLY" if complete else "PARTIAL_OR_FAILED"
        return {"status": state, "completed": len(successes),
                "record_count": len(records), "expected_scripts": len(expected),
                "missing_cases": missing, "duplicate_cases": duplicates,
                "unexpected_cases": unexpected, "records": records,
                "status_file": str(path), "status_sha256": _sha256(path)}
    except (OSError, ValueError, TypeError) as exc:
        return {"status": "INVALID_CASE_STATUS", "completed": 0, "records": [],
                "status_file": str(path), "error": str(exc)}


def build_combined_esm_export(output_root):
    """[REF docs/source/components/equivalent_static/organized_exports.py.md]
    Return copy-only artifact paths. Never edit input EDB, XLSX, model or case.
    """
    root = Path(output_root).expanduser().resolve(strict=True)
    selected = list(_source_files(root))
    if not selected:
        raise ValueError("No ESM source output files found. Calculate and export a case first.")
    datetime_token = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    # Keep the original per-case scripts/results readable; publish immutable review
    # evidence under the selected ETABS export\u2019s 03_ESM subtree.
    from components.inputs.output_layout import review_snapshots_for
    snapshot = review_snapshots_for(root, "ESM") / datetime_token
    snapshot.mkdir(parents=True, exist_ok=False)
    manifest = []
    for module, source in selected:
        case, state = _case_info(source)
        destination_dir = snapshot / _MODULES[module] / state / case / _CATEGORIES[source.suffix.lower()]
        destination_dir.mkdir(parents=True, exist_ok=True)
        target = destination_dir / source.name
        if target.exists():
            # Two saved runs can have a duplicate name; retain both and explain provenance.
            target = destination_dir / (source.stem + "_" + _sha256(source)[:12] + source.suffix)
        shutil.copy2(source, target)
        manifest.append({
            "source_path": str(source), "snapshot_path": str(target.relative_to(snapshot)),
            "sha256": _sha256(source), "bytes": source.stat().st_size,
            "module": _MODULES[module], "state": state, "case": case,
        })
    cases, stories = _data_rows(root)
    batch = _latest_batch_status(root)
    if not cases:
        raise ValueError("ESM artifacts were found, but no calculation JSON is available; "
                         "an engineering combined result cannot be generated.")
    workbook = snapshot / "ESM_Combined_Inspection.xlsx"
    _combined_workbook(workbook, cases, stories, manifest)
    # Report state must be visible directly inside the workbook, not only JSON.
    from openpyxl import load_workbook
    wb = load_workbook(workbook)
    status_sheet = wb.create_sheet("Solver Batch Status")
    status_sheet.append(("Item", "Value"))
    for key in ("status", "completed", "record_count", "expected_scripts", "status_file", "error"):
        if key in batch:
            status_sheet.append((key, str(batch[key])))
    for key in ("missing_cases", "duplicate_cases", "unexpected_cases", "status_sha256"):
        if key in batch:
            status_sheet.append((key, ", ".join(batch[key]) if isinstance(batch[key], list) else str(batch[key])))
    status_sheet.append(())
    status_sheet.append(("Case", "Execution status", "Exit code", "Elapsed (s)"))
    for item in batch.get("records", []):
        status_sheet.append((item.get("case"), item.get("status"),
                             item.get("return_code"), item.get("elapsed_s")))
    status_sheet.append(("Note", "This workbook can contain calculated ESM forces before all solver cases finish."))
    status_sheet.append(("Engineering status", "NOT NATIVE ETABS VERIFIED; ULS high-rise ESM comparison only"))
    from openpyxl.styles import Alignment, Font, PatternFill
    status_sheet.freeze_panes = "B2"
    status_sheet.column_dimensions["A"].width = 70
    status_sheet.column_dimensions["B"].width = 36
    status_sheet.column_dimensions["C"].width = 18
    status_sheet.column_dimensions["D"].width = 22
    for column in status_sheet[1]:
        column.font = Font(bold=True, color="FFFFFF")
        column.fill = PatternFill("solid", fgColor="203A5F")
    for row in status_sheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=False)
    wb.save(workbook)
    overview = {
        "schema": "ESM_ORGANIZED_V1", "source_root": str(root),
        "created_utc": datetime.now(timezone.utc).isoformat(), "files": manifest,
        "case_count": len(cases), "story_rows": len(stories),
        "solver_batch": batch,
        "snapshot_status": ("COMPLETE_SOLVER_ONLY" if batch["status"] == "COMPLETE_SOLVER_ONLY"
                            else "PARTIAL_OR_UNVERIFIED"),
        "acceptance": "COMPARISON_ONLY_NOT_NATIVE_ETABS_OR_NBC_CERTIFICATION",
        "original_outputs_modified": False,
        "combined_workbook": workbook.name,
    }
    manifest_file = snapshot / "ESM_Export_Manifest.json"
    manifest_file.write_text(json.dumps(overview, indent=2, ensure_ascii=False), encoding="utf-8")
    archive = snapshot.parent / ("ESM_Combined_Inspection_" + datetime_token + ".zip")
    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=6) as zipped:
        for file in sorted(snapshot.rglob("*")):
            if file.is_file():
                zipped.write(file, arcname=file.relative_to(snapshot))
    latest = snapshot.parent / "LATEST_ESM_COMBINED_EXPORT.txt"
    latest.write_text(str(archive) + "\n" + str(workbook) + "\n" +
                      str(manifest_file) + "\n", encoding="utf-8")
    return {
        "zip": str(archive), "workbook": str(workbook),
        "manifest": str(manifest_file), "folder": str(snapshot),
        "source_count": len(manifest), "cases": len(cases),
        "solver_batch_status": batch["status"],
    }

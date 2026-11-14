"""Read-only structural audit of ETABS export and analysis-stage organization.

Engineering scope: file navigation, reproducible evidence inventory and SHA checks
for existing categorized copies. Does not infer solver convergence or NBC acceptance.
No source EDB or workbook is read, edited, moved, uploaded, or deleted.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from components.inputs.export_mirror import EXTS, PRIVATE_NAMES, classification, _digest
from components.inputs.output_layout import STAGE_FOLDERS, export_root_for

STAGE_NAMES = set(STAGE_FOLDERS.values())
IGNORED_SOURCE_SUFFIXES = (".processing.json", ".processing.log", ".tmp", ".partial")
STAGE_HINTS = {
    "02_GRAVITY": ("gravity", "support", "reaction", "joint_overlap"),
    "03_ESM": ("esm", "equivalent_static"),
    "04_MODAL": ("modal", "eigen"),
    "05_MRSM": ("mrsm", "response_spectrum", "cqc"),
    "06_LINEAR_TIME_HISTORY": ("linear_time_history", "linear_th", "ltha"),
    "07_NONLINEAR_TIME_HISTORY": ("nonlinear_time_history", "nonlinear_th", "nltha"),
}


def audit_export_structure(export_dir, *, verify_copies=True):
    """[REF docs/source/components/inputs/folder_audit.py.md]\n    Check stage ownership, uncategorized export files and stale mirror copies.

    Reads directory metadata and hashes only *existing categorized mirror copies*
    if verify_copies is true. Source paths are recorded as local diagnostic data:
    do not commit a report generated against a confidential project export.
    """
    root = export_root_for(export_dir)
    if not root.is_dir():
        raise NotADirectoryError(root)
    mirror = root / STAGE_FOLDERS["ETABS_EXPORT"]
    root_files = []
    missing_mirrors = []
    conflicting_mirrors = []
    excluded_sidecars = []
    source_evidence = []
    legacy_analysis = root / "OpenSees_Analysis_Results"
    for p in sorted(root.iterdir(), key=lambda x: x.name.casefold()):
        if not p.is_file() or p.is_symlink():
            continue
        name_lower = p.name.casefold()
        if name_lower.endswith(IGNORED_SOURCE_SUFFIXES):
            excluded_sidecars.append(p.name)
            continue
        root_files.append(p.name)
        if p.suffix.casefold() not in EXTS or name_lower in PRIVATE_NAMES:
            continue
        category = classification(p.name)
        expected = mirror / category / p.name
        source_evidence.append({"file": p.name, "category": category,
                                "mirror": expected.relative_to(root).as_posix()})
        if not expected.is_file():
            missing_mirrors.append(p.name)
        elif verify_copies and _digest(p) != _digest(expected):
            conflicting_mirrors.append({"source": p.name,
                                        "copy": expected.relative_to(root).as_posix()})
    stage_details = {}
    for key, stage_name in STAGE_FOLDERS.items():
        stage = root / stage_name
        stage_details[key] = {
            "path": stage_name,
            "exists": stage.is_dir(),
            "subfolders": sorted(p.name for p in stage.iterdir()
                                 if p.is_dir() and not p.is_symlink()) if stage.is_dir() else [],
            "loose_files": sorted(p.name for p in stage.iterdir()
                                  if p.is_file() and not p.is_symlink()) if stage.is_dir() else [],
            "engineering_status": "NOT_CHECKED_BY_FOLDER_AUDIT",
        }
    legacy_cases = []
    if legacy_analysis.is_dir():
        legacy_cases = sorted(p.name for p in legacy_analysis.iterdir()
                              if p.is_dir() and not p.is_symlink())
    unexpected_folders = sorted(p.name for p in root.iterdir()
                                if p.is_dir() and not p.is_symlink()
                                and p.name not in STAGE_NAMES
                                and p.name != "OpenSees_Analysis_Results")
    findings = []
    if missing_mirrors:
        findings.append({"id": "EXPORT_MIRROR_INCOMPLETE",
                         "severity": "ORGANIZATION",
                         "count": len(missing_mirrors),
                         "action": "Run 09_ORGANIZE_ETABS_EXPORT.py to make SHA-verified copies. Do not move active source files."})
    if conflicting_mirrors:
        findings.append({"id": "EXPORT_MIRROR_HASH_MISMATCH",
                         "severity": "BLOCKED",
                         "count": len(conflicting_mirrors),
                         "action": "Compare original and existing categorized files; do not silently overwrite."})
    if legacy_cases:
        findings.append({"id": "LEGACY_ANALYSIS_ROOT_PRESENT",
                         "severity": "COMPATIBILITY",
                         "count": len(legacy_cases),
                         "action": "Keep historical runs readable. Migrate each producer and reader together; do not bulk move results."})
    if root_files:
        findings.append({"id": "FLAT_SOURCE_FILES_RETAINED",
                         "severity": "COMPATIBILITY",
                         "count": len(root_files),
                         "action": "Active export readers still depend on flat paths; categorized mirrors do not replace them."})
    return {
        "schema": "THESIS_FOLDER_AUDIT_V1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "selected_export": str(root),
        "status": "FOLDER_NAVIGATION_AND_COPY_CHECK_ONLY_NOT_ENGINEERING_VALIDATION",
        "files_in_export_root": root_files,
        "excluded_processing_sidecars": excluded_sidecars,
        "eligible_source_artifacts": source_evidence,
        "missing_categorized_copies": missing_mirrors,
        "conflicting_categorized_copies": conflicting_mirrors,
        "legacy_analysis_case_folders": legacy_cases,
        "unexpected_top_level_folders": unexpected_folders,
        "stages": stage_details,
        "findings": findings,
    }


def write_folder_audit(export_dir, *, verify_copies=True):
    """[REF docs/source/components/inputs/folder_audit.py.md]\n    Write one local immutable-ish dated audit under 01_ETABS_EXPORT/00_MANIFEST.

    Only an audit output is created. Existing audit files aren't overwritten.
    """
    root = export_root_for(export_dir)
    report = audit_export_structure(root, verify_copies=verify_copies)
    folder = root / "01_ETABS_EXPORT" / "00_MANIFEST" / "FOLDER_AUDITS"
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    json_path = folder / ("Folder_Audit_" + stamp + ".json")
    md_path = folder / ("Folder_Audit_" + stamp + ".md")
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8", errors="strict")
    lines = [
        "# ETABS → OpenSees export folder audit",
        "", "Status: **File structure only — not structural validation**",
        "", "## Source and compatibility",
        f"- Export root: `{root}`",
        f"- Flat root files: {len(report['files_in_export_root'])}",
        f"- Missing categorized copies: {len(report['missing_categorized_copies'])}",
        f"- Mirror hash conflicts: {len(report['conflicting_categorized_copies'])}",
        f"- Processing sidecars excluded: {len(report['excluded_processing_sidecars'])}",
        f"- Legacy analysis case directories: {len(report['legacy_analysis_case_folders'])}",
        "", "## Canonical stages", "",
        "| Stage | Directory present | Subfolders | Loose files |",
        "|---|---|---:|---:|",
    ]
    for key, info in report["stages"].items():
        lines.append(f"| {key} | {info['exists']} | {len(info['subfolders'])} | {len(info['loose_files'])} |")
    lines.extend(["", "## Findings", ""])
    lines.extend(f"- **{finding['id']}** ({finding['severity']}): {finding['action']}"
                 for finding in report["findings"])
    lines.extend(["", "No findings does not imply acceptable ETABS/OpenSees equivalence.",
                  "See sibling JSON for exact filenames, SHA mismatch locations and stage inventory."])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path

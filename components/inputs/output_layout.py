"""Canonical stage paths for copy-only evidence snapshots.

This module never changes source models or moves live analysis files.  Existing
OpenSees_Analysis_Results paths stay valid until a separate writer/reader
migration passes all native engineering and compatibility checks.

REF docs/source/components/inputs/output_layout.py.md
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import os
import tempfile

STAGE_FOLDERS = {
    "ETABS_EXPORT": "01_ETABS_EXPORT",
    "GRAVITY": "02_GRAVITY",
    "ESM": "03_ESM",
    "MODAL": "04_MODAL",
    "MRSM": "05_MRSM",
    "LTHA": "06_LINEAR_TIME_HISTORY",
    "NLTHA": "07_NONLINEAR_TIME_HISTORY",
}
# Auxiliary directories are first-class destinations, but they are not
# analysis stages; keep their existing names without renaming archived runs.
AUXILIARY_FOLDERS = {
    "MODEL": "02_MODEL",
    "ETABS_COMPARISONS": "08_ETABS_COMPARISONS",
    "SOFTWARE_DIAGNOSTICS": "09_SOFTWARE_DIAGNOSTICS",
    "UPLOAD_PACKAGES": "90_UPLOAD_PACKAGES",
}
# Legacy path names are readable aliases; never create them as new canonical stages.
LEGACY_STAGE_ALIASES = {
    "06_LINEAR_TH": "LTHA",
    "07_NONLINEAR_TH": "NLTHA",
}
ALL_STAGE_FOLDERS = {**STAGE_FOLDERS, **AUXILIARY_FOLDERS}
_LEGACY_ROOT = "opensees_analysis_results"


def export_root_for(source_path):
    """[REF docs/source/components/inputs/output_layout.py.md]\n    Infer existing ETABS export root from a legacy model/results path.

    Accepts a selected export root itself or a path nested beneath either
    OpenSees_Analysis_Results or a known stage folder. No directories are
    created and no solver/source files are modified.
    """
    source = Path(source_path).expanduser().resolve()
    chain = (source, *source.parents)
    for location in chain:
        if location.name.casefold() == _LEGACY_ROOT:
            return location.parent
    for location in chain:
        if location.name.casefold() in {
            value.casefold() for value in (*ALL_STAGE_FOLDERS.values(), *LEGACY_STAGE_ALIASES)
        }:
            return location.parent
    return source



def canonical_stage_folder(stage):
    """[REF docs/source/components/inputs/output_layout.py.md]
    Resolve canonical key/name or supported legacy alias without creating dirs.
    """
    key = str(stage).strip().upper()
    if key in ALL_STAGE_FOLDERS:
        return ALL_STAGE_FOLDERS[key]
    if key in LEGACY_STAGE_ALIASES:
        return STAGE_FOLDERS[LEGACY_STAGE_ALIASES[key]]
    for value in ALL_STAGE_FOLDERS.values():
        if value.casefold() == key.casefold():
            return value
    raise ValueError("Unknown canonical output stage: " + str(stage))


def result_roots(source_path, *, stages=None, include_legacy=True):
    """[REF docs/source/components/inputs/output_layout.py.md]
    Read-only, de-duplicated roots for native result discovery.

    Only actual directories are returned. Never synthesize a result or mix
    case content with unrelated source EDBs; callers must validate identities.
    """
    source = Path(source_path).expanduser().resolve()
    root = export_root_for(source)
    keys = tuple(stages) if stages is not None else (
        "GRAVITY", "ESM", "MODAL", "MRSM", "LTHA", "NLTHA")
    candidates = []
    if include_legacy:
        candidates.append(root / "OpenSees_Analysis_Results")
    for key in keys:
        canonical = root / canonical_stage_folder(key)
        candidates.append(canonical)
        if str(key).upper() == "LTHA":
            candidates.append(root / "06_LINEAR_TH")
        elif str(key).upper() == "NLTHA":
            candidates.append(root / "07_NONLINEAR_TH")
    # A specific user-selected case that is outside the above trees is valid,
    # but don't re-scan it when its parent is already in the roots.
    if source != root and source.is_dir():
        candidates.append(source)
    found = []
    seen = set()
    for candidate in candidates:
        if not candidate.is_dir() or candidate.is_symlink():
            continue
        resolved = candidate.resolve()
        if any(parent in seen for parent in resolved.parents):
            continue
        # Discard an already selected child when a parent is added later.
        found = [p for p in found if resolved not in p.parents]
        seen = {p for p in seen if resolved not in p.parents}
        if resolved not in seen:
            found.append(resolved)
            seen.add(resolved)
    return tuple(found)


def review_snapshots_for(source_path, stage):
    """[REF docs/source/components/inputs/output_layout.py.md]\n    Return the single canonical copy-only review parent for a known stage."""
    key = str(stage).upper()
    if key not in STAGE_FOLDERS:
        raise ValueError("Unknown thesis analysis stage: " + str(stage))
    return export_root_for(source_path) / STAGE_FOLDERS[key] / "REVIEW_SNAPSHOTS"


def canonical_gravity_run_root(selected_output):
    """[REF docs/source/components/inputs/output_layout.py.md]
    Redirect a *new* gravity write away from legacy all-stage results.

    Only paths under a named `OpenSees_Analysis_Results` are remapped.
    Already canonical or explicitly user-selected external paths are preserved.
    This does NOT relocate existing results or edit their embedded links.
    """
    selected = Path(selected_output).expanduser().resolve()
    chain = (selected, *selected.parents)
    legacy = next((p for p in chain
                   if p.name.casefold() == _LEGACY_ROOT), None)
    if legacy is None:
        return selected
    relative = selected.relative_to(legacy)
    case_name = relative.parts[0] if relative.parts else "GENERAL"
    # Preserve model/state scope without nesting arbitrary legacy subfolders.
    if case_name in (".", "..") or not case_name:
        raise ValueError("Invalid gravity case folder")
    return legacy.parent / STAGE_FOLDERS["GRAVITY"] / "RUNS" / case_name


def write_stage_index(export_dir):
    """[REF docs/source/components/inputs/output_layout.py.md]\n    Atomically publish a navigation index; never infer engineering pass.

    Does not create stage folders, read large solver outputs, or publish the
    contents of private EDB/XLSX files. Explicitly separates folder presence
    from executed/validated analysis state.
    """
    root = Path(export_dir).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(root)
    stages = []
    for name, folder in STAGE_FOLDERS.items():
        location = root / folder
        snapshot_root = location / "REVIEW_SNAPSHOTS"
        snapshots = (sorted(p.name for p in snapshot_root.iterdir()
                            if p.is_dir() and not p.is_symlink())
                     if snapshot_root.is_dir() else [])
        latest = snapshot_root / "LATEST_ORGANIZED_RESULT.txt"
        if name == "ESM":
            latest_esm = snapshot_root / "LATEST_ESM_COMBINED_EXPORT.txt"
            if latest_esm.is_file():
                latest = latest_esm
        stages.append({
            "stage": name, "folder": folder,
            "present": location.is_dir(),
            "review_snapshot_count": len(snapshots),
            "latest_review_folder": (
                (Path(folder) / "REVIEW_SNAPSHOTS" / snapshots[-1]).as_posix()
                if snapshots else None
            ),
            "latest_pointer": (
                (Path(folder) / "REVIEW_SNAPSHOTS" / latest.name).as_posix()
                if latest.is_file() else None
            ),
            "engineering_status": "NOT_ASSESSED_BY_FILE_INDEX",
        })
    manifest = {
        "schema": "THESIS_STAGE_INDEX_V1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "FILE_NAVIGATION_ONLY_NOT_SOLVER_OR_CODE_VALIDATION",
        "legacy_analysis_results_present": (
            root / "OpenSees_Analysis_Results").is_dir(),
        "stages": stages,
    }
    destination = root / "01_ETABS_EXPORT" / "00_MANIFEST"
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / "analysis_stage_index.json"
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=destination,
        suffix=".partial", delete=False
    ) as handle:
        temp = Path(handle.name)
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    try:
        os.replace(temp, output)
    finally:
        temp.unlink(missing_ok=True)
    return output

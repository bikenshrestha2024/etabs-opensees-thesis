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
_LEGACY_ROOT = "opensees_analysis_results"


def export_root_for(source_path):
    """Infer existing ETABS export root from a legacy model/results path.

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
            value.casefold() for value in STAGE_FOLDERS.values()
        }:
            return location.parent
    return source


def review_snapshots_for(source_path, stage):
    """Return the single canonical copy-only review parent for a known stage."""
    key = str(stage).upper()
    if key not in STAGE_FOLDERS:
        raise ValueError("Unknown thesis analysis stage: " + str(stage))
    return export_root_for(source_path) / STAGE_FOLDERS[key] / "REVIEW_SNAPSHOTS"


def write_stage_index(export_dir):
    """Atomically publish a navigation index; never infer engineering pass.

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

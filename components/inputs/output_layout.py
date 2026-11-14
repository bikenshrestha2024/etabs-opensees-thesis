"""Canonical stage paths for copy-only evidence snapshots.

This module never changes source models or moves live analysis files.  Existing
OpenSees_Analysis_Results paths stay valid until a separate writer/reader
migration passes all native engineering and compatibility checks.

REF docs/source/components/inputs/output_layout.py.md
"""
from __future__ import annotations

from pathlib import Path

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

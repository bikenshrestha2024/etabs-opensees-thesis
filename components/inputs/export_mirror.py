"""Organize a legacy flat ETABS export without breaking current flat-path readers.

READS ONLY files in the selected export root and COPIES them to an audit
mirror. Never moves, deletes, edits or renames the original source evidence.
REF docs/source/components/inputs/export_mirror.py.md
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from hashlib import sha256
import json
import os
import shutil
import tempfile

EXTS = {".json", ".csv", ".xlsx", ".xlsm", ".html", ".py", ".txt"}
PRIVATE_NAMES = {"project_sources.private.json", "gravity_evidence_manifest.json"}


def _digest(path):
    """Stream SHA256 without loading large model JSON into RAM."""
    h = sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classification(name):
    """Classification for generated ETABS export artifacts only.

    [REF docs/source/components/inputs/export_mirror.py.md]
    """
    s = name.lower()
    if "log" in s or "diagnostic" in s:
        return "07_LOGS"
    if "visual" in s or "3d" in s or "floor_plan" in s or s.endswith(".html"):
        return "04_VISUALIZATION"
    if "mapping" in s or "lookup" in s or "node_map" in s or "connectivity" in s:
        return "02_MAPPING"
    if "load" in s or "mass" in s or "gravity" in s:
        return "03_LOADS"
    if "review" in s or "error" in s or "issue" in s:
        return "09_REVIEW"
    if "audit" in s or "reconciliation" in s:
        return "05_AUDITS"
    if "config" in s or "parameter" in s:
        return "06_CONFIG"
    if s.endswith(".py"):
        return "08_PROCESSING"
    return "01_SOURCE"


def export_mirror(export_dir):
    """Create safe categorized copies with content-addressed manifest.

    [REF docs/source/components/inputs/export_mirror.py.md]
    Existing destination with different bytes fails closed. Does not follow
    symlinks or recurse. Export model and source EDB are never modified.
    """
    root = Path(export_dir).resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    target = root / "01_ETABS_EXPORT"
    target.mkdir(exist_ok=True)
    entries = []
    for original in sorted(root.iterdir()):
        if not original.is_file() or original.is_symlink():
            continue
        # Export-side .processing.json files are transient sidecar status,
        # not model source. Do not fill the canonical folders with these.
        # Casefold private names for reliable Windows classification.
        lowered = original.name.casefold()
        if (original.suffix.lower() not in EXTS
                or lowered in PRIVATE_NAMES
                or lowered.endswith((".processing.json", ".processing.log",
                                     ".partial", ".tmp"))):
            continue
        relative = Path(classification(original.name)) / original.name
        dest = target / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        original_hash = _digest(original)
        if dest.is_file():
            if _digest(dest) != original_hash:
                raise ValueError("Existing categorized copy differs; review manually: "+str(dest))
        else:
            with tempfile.NamedTemporaryFile(dir=dest.parent,suffix=".partial",
                                             delete=False) as temp:
                part = Path(temp.name)
            try:
                shutil.copy2(original, part)
                if _digest(part) != original_hash:
                    raise IOError("Copy did not preserve source bytes: "+original.name)
                os.replace(part, dest)
            finally:
                part.unlink(missing_ok=True)
        entries.append({"original": str(original), "categorized": str(dest),
                        "category": relative.parent.name, "sha256": original_hash,
                        "size_bytes": original.stat().st_size})
    manifest = {"schema": 1, "status": "MIRRORED_LEGACY_PATHS_PRESERVED",
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "selected_export": str(root), "files": entries}
    folder = target / "00_MANIFEST"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "export_mirror_manifest.json"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=folder,
                                     suffix=".partial",delete=False) as out:
        json.dump(manifest,out,indent=2)
        part = Path(out.name)
    os.replace(part, path)
    return path

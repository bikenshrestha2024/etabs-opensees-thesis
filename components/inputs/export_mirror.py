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
LIVE_CONVERSION_LOG = "etabs_opensees_conversion_log.txt"


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


def export_mirror(export_dir, *, exclude_live_conversion_log=False):
    """Create categorized copies after a fail-closed, whole-batch preflight.

    [REF docs/source/components/inputs/export_mirror.py.md]
    The preflight detects source/destination conflicts before copying ANY new
    files. Source files and existing mirror copies are never overwritten.
    This is not a filesystem transaction: an unexpected I/O error during the
    copy phase can still leave copies; a manifest is published only on success.
    """
    supplied = Path(export_dir).expanduser()
    if supplied.is_symlink():
        raise ValueError("Refusing symlinked selected export root")
    root = supplied.resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    target = root / "01_ETABS_EXPORT"
    manifest_dir = target / "00_MANIFEST"
    manifest_path = manifest_dir / "export_mirror_manifest.json"
    if any(path.is_symlink() for path in (target, manifest_dir, manifest_path)):
        raise ValueError("Refusing categorized export symlink")
    # A complete source/destination plan is necessary: failing halfway through
    # the copy phase creates a misleading partially refreshed mirror.
    plan = []
    excluded_live_logs = []
    for original in sorted(root.iterdir()):
        if not original.is_file() or original.is_symlink():
            continue
        lowered = original.name.casefold()
        if exclude_live_conversion_log and lowered == LIVE_CONVERSION_LOG:
            excluded_live_logs.append(str(original))
            continue
        if (original.suffix.lower() not in EXTS
                or lowered in PRIVATE_NAMES
                or lowered.endswith((".processing.json", ".processing.log",
                                     ".partial", ".tmp"))):
            continue
        relative = Path(classification(original.name)) / original.name
        dest = target / relative
        if dest.parent.is_symlink() or dest.is_symlink():
            raise ValueError("Refusing categorized destination symlink: " + str(dest))
        if dest.exists() and not dest.is_file():
            raise ValueError("Categorized destination is not a regular file: " + str(dest))
        original_hash = _digest(original)
        if dest.exists() and _digest(dest) != original_hash:
            raise ValueError("Existing categorized copy differs; review manually: " + str(dest))
        plan.append((original, dest, relative, original_hash, original.stat().st_size))

    # No directory is created before preflight completes successfully.
    entries = []
    for original, dest, relative, original_hash, size in plan:
        if dest.parent.is_symlink() or dest.is_symlink():
            raise ValueError("Refusing categorized destination symlink: " + str(dest))
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_file():
            if _digest(dest) != original_hash:
                raise ValueError("Existing categorized copy changed during mirroring: " + str(dest))
        else:
            with tempfile.NamedTemporaryFile(dir=dest.parent, suffix=".partial",
                                             delete=False) as temp:
                part = Path(temp.name)
            try:
                shutil.copy2(original, part)
                if _digest(part) != original_hash:
                    raise IOError("Source changed during copy; review manually: " + original.name)
                # Publish without replacing a path another producer just created.
                try:
                    if os.name == "nt":
                        os.rename(part, dest)
                    else:
                        os.link(part, dest)
                except FileExistsError as exc:
                    raise ValueError("Destination created during copy: " + str(dest)) from exc
            finally:
                part.unlink(missing_ok=True)
        entries.append({"original": str(original), "categorized": str(dest),
                        "category": relative.parent.name, "sha256": original_hash,
                        "size_bytes": size})

    manifest = {"schema": 1, "status": "MIRRORED_LEGACY_PATHS_PRESERVED",
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "selected_export": str(root), "files": entries,
                "excluded_live_logs": excluded_live_logs}
    if manifest_dir.is_symlink() or manifest_path.is_symlink():
        raise ValueError("Refusing mirror manifest destination symlink")
    manifest_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                     dir=manifest_dir, suffix=".partial",
                                     delete=False) as out:
        part = Path(out.name)
        try:
            json.dump(manifest, out, indent=2)
            out.flush()
            os.fsync(out.fileno())
        except BaseException:
            # Windows cannot remove a NamedTemporaryFile while open. The
            # enclosing context closes it before the cleanup below.
            raise
    try:
        if manifest_path.is_symlink():
            raise ValueError("Refusing mirror manifest destination symlink")
        os.replace(part, manifest_path)
    finally:
        part.unlink(missing_ok=True)
    return manifest_path

"""Canonical, case-local ownership of review ZIP files across all thesis modules.

Only ZIP destinations move. Native solver results and review snapshot manifests
retain their existing locations. This is a local file-management contract,
NOT an engineering acceptance, native solver or user-upload action.
"""
from __future__ import annotations

from pathlib import Path


def review_zip_directory(selected):
    """Resolve the nearest source-owned case's `07_EXPORT_ZIP` folder.

    For canonical case runs, accept any nested 02_RESULTS/06_REVIEW/... path
    and locate the exact run ancestor (verified by its CASE_MANIFEST.json).
    A legacy results root without a canonical manifest receives its own local
    `07_EXPORT_ZIP` subfolder; never redirect outside the selected tree or
    silently reuse an unrelated case's ZIP folder. Does not create anything.
    """
    raw=Path(selected).expanduser()
    if any(part.is_symlink() for part in (raw,*raw.parents)):
        raise ValueError("Refusing symlinked ZIP export path: "+str(raw))
    root=raw.parent if raw.is_file() else raw
    for ancestor in (root,*root.parents):
        if ancestor.name=="07_EXPORT_ZIP" and ancestor.is_dir():
            return ancestor
        candidate=ancestor/"07_EXPORT_ZIP"
        manifest=ancestor/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
        if candidate.is_dir() and manifest.is_file():
            if candidate.is_symlink() or manifest.is_symlink():
                raise ValueError("Refusing linked case ZIP folder/manifest")
            return candidate
    # Existing pre-manifest run folders may already have all seven case
    # sections; preserve their exact case-local destination.
    for ancestor in (root,*root.parents):
        candidate=ancestor/"07_EXPORT_ZIP"
        if candidate.is_dir() and (ancestor/"02_RESULTS").is_dir():
            if candidate.is_symlink():
                raise ValueError("Refusing linked case ZIP folder")
            return candidate
    return root/"07_EXPORT_ZIP"


def ensure_review_zip_directory(selected):
    """Create the selected case ZIP directory, refusing linked destinations."""
    target=review_zip_directory(selected)
    if any(part.is_symlink() for part in (target,*target.parents)):
        raise ValueError("Refusing redirected ZIP destination: "+str(target))
    target.mkdir(parents=True,exist_ok=True)
    if target.is_symlink():
        raise ValueError("Refusing redirected ZIP destination")
    return target

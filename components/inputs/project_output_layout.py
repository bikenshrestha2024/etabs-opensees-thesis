"""Non-destructive per-project output layout and source provenance.

Model conversion uses the original ETABS EDB. This module only creates
local directories/indices, never modifies EDB, Excel or solver artifacts.
[REF docs/source/components/inputs/project_output_layout.py.md]
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

MODULES = (
    "01_ETABS_EXPORT", "02_GRAVITY", "03_ESM", "04_MODAL", "05_MRSM",
    "06_LINEAR_TH", "07_NONLINEAR_TH", "08_ETABS_COMPARISONS",
    "09_SOFTWARE_DIAGNOSTICS", "90_UPLOAD_PACKAGES",
)


def sha256_file(path):
    """[REF docs/source/components/inputs/project_output_layout.py.md] File byte digest only."""
    h = hashlib.sha256()
    with Path(path).open("rb") as reader:
        for block in iter(lambda: reader.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def create_project_layout(source_edb, selected_output_root, *,
                          create_analysis_directories=True):
    """[REF docs/source/components/inputs/project_output_layout.py.md]
    Create stable subfolders beneath the exact user-selected output root.

    Source SHA changes are a blocker: a directory once bound to an EDB cannot
    silently be rebound to a different EDB. An existing legacy result tree is
    left untouched. Caller owns Windows UI and any ETABS OAPI lifecycle.
    """
    source = Path(source_edb).expanduser().resolve(strict=True)
    if source.suffix.lower() != ".edb":
        raise ValueError("The authoritative physical source must be a .EDB file.")
    if not source.is_file():
        raise FileNotFoundError(str(source))
    root = Path(selected_output_root).expanduser().resolve()
    if root == source or root in source.parents:
        raise ValueError("Output root must not be an ancestor of the source EDB.")
    root.mkdir(parents=True, exist_ok=True)
    sha = sha256_file(source)
    manifest_dir = root / "00_SOURCE_MANIFEST"
    manifest_dir.mkdir(exist_ok=True)
    manifest = manifest_dir / "PROJECT_CONTEXT.json"
    if manifest.exists():
        previous = json.loads(manifest.read_text(encoding="utf-8-sig"))
        if previous.get("source_edb_sha256") != sha:
            raise ValueError(
                "Selected output root belongs to a DIFFERENT EDB SHA256. "
                "Choose another output root; existing results were not modified.")
    layout = {name: str(root / name) for name in MODULES}
    layout["REVIEW_MAIN"] = str(root / "REVIEW_MAIN")
    if create_analysis_directories:
        for folder in layout.values():
            Path(folder).mkdir(parents=True, exist_ok=True)
    # Preserve first recorded start time on repeated runs of the same source.
    created = (previous.get("created_utc") if manifest.exists() else None)
    document = {
        "schema": "etabs-opensees-project-context-v1",
        "source_edb": str(source),
        "source_edb_sha256": sha,
        "output_root": str(root),
        "created_utc": created or datetime.now(timezone.utc).isoformat(),
        "refreshed_utc": datetime.now(timezone.utc).isoformat(),
        "status": "SOURCE_IDENTIFIED_NOT_ENGINEERING_VERIFIED",
        "modules": layout,
        "legacy_output": str(root / "OpenSees_Analysis_Results"),
        "note": "Legacy outputs remain at existing locations until all readers are migrated."
    }
    temp = manifest.with_suffix(".tmp")
    temp.write_text(json.dumps(document, indent=2), encoding="utf-8")
    temp.replace(manifest)
    return document


def case_folder(layout, module, case_id, *, limit_state=None):
    """[REF docs/source/components/inputs/project_output_layout.py.md]
    Resolve a case folder under its canonical module without traversal."""
    from re import fullmatch
    name = str(module).strip()
    if name not in MODULES:
        raise ValueError("Unknown output module: " + name)
    parts = [str(limit_state)] if limit_state else []
    parts.append(str(case_id))
    if not all(fullmatch(r"[A-Za-z0-9_.-]+", p or "") and
               p not in (".", "..") for p in parts):
        raise ValueError("Case names must not contain separators or '..'.")
    base = Path(layout["modules"][name]).resolve()
    destination = base.joinpath(*parts).resolve()
    if base not in destination.parents:
        raise ValueError("Case output escaped selected project folder.")
    destination.mkdir(parents=True, exist_ok=False)
    return destination

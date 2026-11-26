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

from components.inputs.output_layout import ALL_STAGE_FOLDERS, LEGACY_STAGE_ALIASES, canonical_stage_folder, export_root_for

# Single registry. Historical 06_LINEAR_TH / 07_NONLINEAR_TH are readable
# aliases but must not be created as competing new stage directories.
MODULES = tuple(ALL_STAGE_FOLDERS.values())


def sha256_file(path):
    """[REF docs/source/components/inputs/project_output_layout.py.md] File byte digest only."""
    h = hashlib.sha256()
    with Path(path).open("rb") as reader:
        for block in iter(lambda: reader.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def require_import_root(selected_output_root):
    """Validate import destination without creating files or modifying rebuilds.

    [REF docs/source/components/inputs/project_output_layout.py.md]
    """
    if not str(selected_output_root).strip():
        raise ValueError("Select an explicit ETABS export root.")
    candidate=Path(selected_output_root).expanduser()
    if any(part.is_symlink() for part in (candidate,*candidate.parents)):
        raise ValueError("Refusing linked ETABS export root.")
    root=candidate.resolve()
    if export_root_for(root)!=root or (root/"CLEAR_BEAM_REBUILD_STATUS.json").exists():
        raise ValueError("Import requires the original project export root, not a stage/run/rebuilt model folder. Select a new export root for a new import.")
    return root


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
    root = require_import_root(selected_output_root)
    if root == source or root in source.parents:
        raise ValueError("Output root must not be an ancestor of the source EDB.")
    sha = sha256_file(source)
    manifest_dir = root / "00_SOURCE_MANIFEST"
    manifest = manifest_dir / "PROJECT_CONTEXT.json"
    # Validate existing output destinations before any directory or manifest
    # is created. A linked manifest dir would otherwise write outside the
    # user-selected export case, and a linked stage would scatter its results.
    if manifest_dir.is_symlink() or manifest.is_symlink():
        raise ValueError("Refusing linked project manifest destination")
    previous = None
    if manifest.exists():
        try:
            previous = json.loads(manifest.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError, TypeError) as exc:
            raise ValueError("Unreadable existing project source manifest") from exc
        if not isinstance(previous, dict):
            raise ValueError("Existing project source manifest must be a JSON object")
        if previous.get("source_edb_sha256") != sha:
            raise ValueError(
                "Selected output root belongs to a DIFFERENT EDB SHA256. "
                "Choose another output root; existing results were not modified.")
    layout = {name: str(root / name) for name in MODULES}
    layout["REVIEW_MAIN"] = str(root / "REVIEW_MAIN")
    if create_analysis_directories:
        for folder in layout.values():
            if Path(folder).is_symlink():
                raise ValueError("Refusing linked project output stage: " + folder)
    root.mkdir(parents=True, exist_ok=True)
    manifest_dir.mkdir(exist_ok=True)
    if create_analysis_directories:
        for folder in layout.values():
            Path(folder).mkdir(parents=True, exist_ok=True)
    # Preserve first recorded start time on repeated runs of the same source.
    created = previous.get("created_utc") if previous is not None else None
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
    # Unique same-directory temporary file and atomic replacement. Reusing a
    # fixed .tmp name risks clobbering an unrelated interrupted writer.
    from components.inputs.output_contract import atomic_json
    atomic_json(manifest, document)
    return document


def case_folder(layout, module, case_id, *, limit_state=None):
    """[REF docs/source/components/inputs/project_output_layout.py.md]
    Resolve a case folder under its canonical module without traversal."""
    from components.inputs.output_contract import safe_component
    name = str(module).strip()
    # Existing callers that supply legacy names now write to the canonical
    # stage rather than creating a second, differently named directory.
    try:
        canonical = canonical_stage_folder(name)
    except ValueError as exc:
        raise ValueError("Unknown output module: " + name) from exc
    parts = [safe_component(limit_state)] if limit_state is not None else []
    parts.append(safe_component(case_id))
    stage_path = Path(layout["modules"][canonical])
    if stage_path.is_symlink():
        raise ValueError("Refusing linked case stage")
    current = stage_path
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Refusing linked case output component")
    base = stage_path.resolve()
    destination = current.resolve()
    if base not in destination.parents:
        raise ValueError("Case output escaped selected project folder.")
    destination.mkdir(parents=True, exist_ok=False)
    return destination

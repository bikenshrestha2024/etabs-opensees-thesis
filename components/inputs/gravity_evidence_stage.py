"""Local, source-preserving staging of explicit ETABS gravity evidence workbooks.

Never accept an LFS pointer as spreadsheet evidence. This stages *both* files
chosen by the engineer, preserving their bytes; it never uploads them to Git.
REF docs/source/components/inputs/gravity_evidence_stage.py.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import os
import shutil
import tempfile

ROLES = ("etabs_assignment", "etabs_full_table")
VALID_EXTENSIONS = {".xlsx", ".xlsm"}
LFS_PREFIX = b"version https://git-lfs.github.com/spec/v1"


def file_sha256(path):
    """SHA256 of the exact bytes. [REF docs/source/components/inputs/gravity_evidence_stage.py.md]"""
    h = sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _validate_excel(path):
    """Validate the ZIP container without changing Excel formulas or layout."""
    from zipfile import ZipFile, BadZipFile
    path = Path(path)
    if path.suffix.lower() not in VALID_EXTENSIONS or not path.is_file():
        raise ValueError("Provide a real .xlsx/.xlsm ETABS workbook for each role")
    with path.open("rb") as stream:
        if stream.read(len(LFS_PREFIX)) == LFS_PREFIX:
            raise ValueError(f"Git LFS pointer is not a workbook: {path}")
    try:
        with ZipFile(path) as archive:
            names = set(archive.namelist())
            if "[Content_Types].xml" not in names or "xl/workbook.xml" not in names:
                raise ValueError(f"Invalid Excel OOXML workbook: {path}")
            if archive.testzip() is not None:
                raise ValueError(f"Workbook ZIP CRC failed: {path}")
    except BadZipFile as exc:
        raise ValueError(f"Not a valid Excel OOXML archive: {path}") from exc
    return path.resolve()


def manifest_path(export_dir):
    """Private export-scoped manifest location. [REF docs/source/components/inputs/gravity_evidence_stage.py.md]"""
    return Path(export_dir) / "01_ETABS_EXPORT" / "10_PRIVATE_ETABS_WORKBOOKS" / "gravity_evidence_manifest.json"


def stage_gravity_workbooks(export_dir, *, assignment, full_table, source_edb=None):
    """Stage read-only copies and atomic SHA manifest for an explicit ULS model.

    [REF docs/source/components/inputs/gravity_evidence_stage.py.md]

    Workbook structure is checked, but full ETABS scientific equivalence is
    NOT implied. Caller must independently confirm model, load case, and
    expected native ETABS tables. A staged workbook may not equal its source
    EDB or contain solved joint reactions; separate gates remain mandatory.
    """
    folder = Path(export_dir).resolve()
    if not folder.is_dir():
        raise FileNotFoundError(folder)
    selected = {"etabs_assignment": _validate_excel(assignment),
                "etabs_full_table": _validate_excel(full_table)}
    destination = manifest_path(folder).parent
    destination.mkdir(parents=True, exist_ok=True)
    prepared = {}
    for role, source in selected.items():
        target = destination / (role + source.suffix.lower())
        if source != target.resolve():
            # Copy into temporary filename first to avoid partial accepted files.
            with tempfile.NamedTemporaryFile(dir=destination, prefix=role+"_",
                                             suffix=".partial", delete=False) as tmp:
                partial = Path(tmp.name)
            try:
                shutil.copyfile(source, partial)
                if file_sha256(partial) != file_sha256(source):
                    raise IOError("Source/staged workbook hash mismatch: "+role)
                os.replace(partial, target)
            finally:
                partial.unlink(missing_ok=True)
        prepared[role] = {"path": str(target), "sha256": file_sha256(target),
                          "source_name": source.name, "bytes": target.stat().st_size}
    edb = Path(source_edb).resolve() if source_edb else None
    doc = {"schema": 1,
           "status": "STAGED_NOT_ETABS_VALIDATED",
           "created_utc": datetime.now(timezone.utc).isoformat(),
           "export_dir": str(folder),
           "source_edb": str(edb) if edb else None,
           "source_edb_sha256": file_sha256(edb) if edb and edb.is_file() else None,
           "workbooks": prepared,
           "validation_needed": ["ETABS model identity", "native assignment sheet presence",
                                 "matching ULS load case and joint reactions",
                                 "source versus OpenSees gravity parity"]}
    path = manifest_path(folder)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination,
                                     suffix=".partial", delete=False) as tmp:
        json.dump(doc, tmp, indent=2)
        temp = Path(tmp.name)
    os.replace(temp, path)
    return path


def staged_gravity_workbooks(export_dir):
    """Return matching staged files or reject stale/altered evidence, never guess.

    [REF docs/source/components/inputs/gravity_evidence_stage.py.md]
    """
    path = manifest_path(export_dir)
    if not path.is_file():
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    if Path(doc.get("export_dir", "")).resolve() != Path(export_dir).resolve():
        raise ValueError("Staged workbook manifest belongs to another export")
    if doc.get("source_edb_sha256"):
        edb = Path(doc["source_edb"])
        if not edb.is_file() or file_sha256(edb) != doc["source_edb_sha256"]:
            raise ValueError("Source EDB hash changed since workbook staging")
    result = {}
    for role in ROLES:
        record = doc["workbooks"][role]
        candidate = _validate_excel(record["path"])
        if file_sha256(candidate) != record["sha256"]:
            raise ValueError("Staged ETABS workbook changed: "+role)
        result[role] = str(candidate)
    return result

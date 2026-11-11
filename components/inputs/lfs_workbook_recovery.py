"""Git LFS workbook recovery for the Windows ETABS conversion workflow.

Attempts local Git LFS only in an actual repository checkout. A downloaded
GitHub ZIP has no Git metadata, so the UI instead offers to locate the original
workbook. Original source files and Git-tracked registries are never modified.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path


LFS_MAGIC = b"version https://git-lfs.github.com/spec/v1"


def is_lfs_pointer(path):
    path = Path(path)
    if not path.is_file():
        return False
    with path.open("rb") as handle:
        return handle.read(len(LFS_MAGIC)) == LFS_MAGIC


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda:handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _checkout(path):
    """Only ascend from the input; never pull from an unrelated Git checkout."""
    for parent in Path(path).resolve().parents:
        if (parent / ".git").exists():
            return parent
    return None


def recover_lfs_pointer(path, *, expected_sha256, timeout_seconds=180, log=None):
    """Try git lfs pull in place, verify bytes, report nonfatal failure.

    No direct arbitrary download URLs or manual credential prompts.
    A failed/absent Git LFS process leaves the pointer in place.
    """
    target = Path(path).resolve()
    if not is_lfs_pointer(target):
        if target.is_file() and digest(target) == expected_sha256:
            return True, "VALID_EXISTING_WORKBOOK"
        return False, "MISSING_OR_HASH_MISMATCH"
    root = _checkout(target)
    if root is None:
        return False, "ARCHIVE_WITHOUT_GIT_METADATA"
    git = shutil.which("git")
    if not git:
        return False, "GIT_NOT_INSTALLED"
    relative = target.relative_to(root).as_posix()
    try:
        version = subprocess.run([git,"-C",str(root),"lfs","version"],
                                 capture_output=True,text=True,
                                 timeout=15,check=False)
        if version.returncode:
            return False, "GIT_LFS_NOT_INSTALLED"
        if log:
            log("[LFS] Recovering source workbook from checked-out repository: "+relative)
        result = subprocess.run(
            [git,"-C",str(root),"lfs","pull","--include="+relative,"--exclude="],
            capture_output=True,text=True,timeout=timeout_seconds,check=False)
        if result.returncode:
            if log:
                log("[LFS] Git LFS pull failed (exit "+str(result.returncode)+")")
            return False, "GIT_LFS_PULL_FAILED"
        if is_lfs_pointer(target):
            return False, "GIT_LFS_POINTER_REMAINS"
        if not target.is_file() or digest(target) != expected_sha256:
            return False, "RECOVERED_CONTENT_HASH_MISMATCH"
        return True, "RECOVERED_AND_SHA256_VERIFIED"
    except (OSError,subprocess.TimeoutExpired,ValueError) as exc:
        if log:
            log("[LFS] Automatic recovery unavailable: "+type(exc).__name__)
        return False, "GIT_LFS_RECOVERY_UNAVAILABLE"


def _registered_source(runtime_root, edb, role):
    """Pick only SHA-bound sources matching the selected physical EDB."""
    root = Path(runtime_root).resolve()
    edb_hash = digest(edb)
    locations = [root / "project_sources.private.json",
                 root / "excel" / "SOURCE_REGISTRY.json"]
    for registry in locations:
        if not registry.is_file():
            continue
        data = json.loads(registry.read_text(encoding="utf-8-sig"))
        if data.get("source_edb_sha256") != edb_hash:
            continue
        entry = (data.get("sources") or {}).get(role)
        if not entry:
            continue
        path = Path(entry["path"])
        if not path.is_absolute():
            path = registry.parent / path
        return path, str(entry["sha256"]), registry, edb_hash
    return None


def ensure_gui_workbooks(runtime_root, export_dir, edb, *, parent, log=None):
    """Recover (or browse for) only registered LFS-pointer source workbooks.

    The dialog is triggered only after automatic Git LFS fails; exact source
    SHA256 and EDB identity are mandatory. Overrides are written solely to a
    private file in the selected export directory, never to tracked JSON.
    """
    from tkinter import filedialog, messagebox
    runtime_root = Path(runtime_root).resolve()
    export_dir = Path(export_dir).resolve()
    edb = Path(edb).resolve()
    if not edb.is_file():
        raise FileNotFoundError("Selected ETABS source EDB does not exist: "+str(edb))
    for role in ("etabs_full_table","etabs_assignment","nbc_calculator","slab_load_path"):
        found = _registered_source(runtime_root, edb, role)
        if found is None:
            continue
        path, expected, registry, edb_hash = found
        if path.is_file() and not is_lfs_pointer(path):
            if digest(path) == expected:
                continue
            raise ValueError("Registered "+role+" workbook has changed; source SHA256 mismatch: "+str(path))
        if not is_lfs_pointer(path):
            raise FileNotFoundError("Registered "+role+" workbook missing: "+str(path))
        recovered,status = recover_lfs_pointer(path,expected_sha256=expected,log=log)
        if recovered:
            if log: log("[LFS] "+role+": "+status)
            continue
        if log: log("[LFS] "+role+": "+status+"; requesting original workbook")
        messagebox.showwarning(
            "Original ETABS Excel workbook required",
            "The repository contains only a Git LFS pointer, not the actual workbook.\n\n"
            "Automatic recovery status: "+status+"\n\n"
            "Select the ORIGINAL Excel workbook for "+role+".\n"
            "Its SHA256 must match the approved project registry.\n"
            "The original file will be used read-only, without copying or overwriting it.",
            parent=parent)
        candidate = filedialog.askopenfilename(
            parent=parent,title="Select original workbook — "+path.name,
            filetypes=[("Excel workbooks","*.xlsx"),("All files","*.*")])
        if not candidate:
            raise FileNotFoundError("Original workbook not selected for "+role+
                ". Conversion was stopped without substituting an unverified file.")
        candidate = Path(candidate).resolve()
        if is_lfs_pointer(candidate) or not candidate.is_file() or digest(candidate) != expected:
            raise ValueError("Selected workbook does not match registered SHA256 for "+role+
                             "; conversion stopped. Choose the original unmodified file.")
        # The local override is private and bound to the selected actual EDB.
        private = export_dir / "project_sources.private.json"
        if private.exists():
            data = json.loads(private.read_text(encoding="utf-8-sig"))
            if data.get("source_edb_sha256") != edb_hash:
                raise ValueError("Existing private source registry belongs to another EDB: "+str(private))
        else:
            data = {"source_edb_sha256":edb_hash,"sources":{}}
        data.setdefault("sources",{})[role] = {
            "path":str(candidate),"sha256":expected}
        export_dir.mkdir(parents=True,exist_ok=True)
        private.write_text(json.dumps(data,indent=2),encoding="utf-8")
        if log:
            log("[LFS] Source-verified "+role+" selected in private registry (original unchanged).")

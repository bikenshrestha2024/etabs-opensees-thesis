"""Repair an ETABS export output layout without breaking historical readers.

Default mode is read-only. --apply creates hash-verified categorized copies:
  - loose root files -> existing 01_ETABS_EXPORT mirror
  - historical ESM runs -> 03_ESM/REVIEW_SNAPSHOTS/HISTORICAL_<case>
It NEVER moves/deletes the originals, alters solver JSON, changes supports,
or silently treats a mirrored folder as an analyzed/approved case.

python tools/repair_project_output_layout.py "D:\\PROJECT\\EXPORT_CASE"
python tools/repair_project_output_layout.py "D:\\PROJECT\\EXPORT_CASE" --apply
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from components.inputs.export_mirror import export_mirror
from components.inputs.output_layout import export_root_for

_ELIGIBLE = ("nbc105_esm_", "nbc105_rayleigh_", "esm_runner_status",
             "etabs_linked_esm", "nbc105_input_sync", "nbc105_input_provenance")
_SKIP = (".partial", ".tmp", ".processing.json", ".processing.log")
_MAX_DEPTH = 5


def _sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _safe_path(path, root):
    p = Path(path)
    if any(parent.is_symlink() for parent in (p, *p.parents) if parent == root or root in parent.parents):
        raise ValueError("Refusing symlinked source or destination: " + str(p))
    if root != p and root not in p.parents:
        raise ValueError("Path escaped selected export: " + str(p))
    return p


def plan_migration(export_root):
    """Read-only snapshot plan with content hashes and bounded traversal."""
    supplied = Path(export_root).expanduser()
    if supplied.is_symlink():
        raise ValueError("Selected root must not be a symlink")
    root = export_root_for(supplied)
    if not root.is_dir():
        raise NotADirectoryError(root)
    root = root.resolve()
    if root.is_symlink():
        raise ValueError("Refusing symlinked export root")
    legacy = root / "OpenSees_Analysis_Results"
    stage = root / "03_ESM" / "REVIEW_SNAPSHOTS"
    _safe_path(stage, root)
    records = []
    skipped = []
    if legacy.is_symlink():
        raise ValueError("Refusing linked historical results directory")
    if legacy.is_dir():
        for case in sorted(legacy.iterdir(), key=lambda p: p.name.casefold()):
            if case.is_symlink():
                skipped.append({"path": str(case.relative_to(root)), "reason": "LINKED_CASE"})
                continue
            if not case.is_dir():
                continue
            source_case = case.name
            if source_case in ("", ".", "..") or "/" in source_case or "\\" in source_case:
                raise ValueError("Invalid historical case name")
            for base, dirs, files in os.walk(case, followlinks=False):
                base_path = Path(base)
                depth = len(base_path.relative_to(case).parts)
                if depth > _MAX_DEPTH:
                    dirs.clear()
                    continue
                dirs[:] = sorted(d for d in dirs
                    if not (base_path/d).is_symlink() and
                    not d.casefold().endswith(_SKIP))
                for name in sorted(files):
                    file = base_path / name
                    rel = file.relative_to(case)
                    if file.is_symlink() or name.casefold().endswith(_SKIP):
                        continue
                    if not any(part.casefold().startswith(_ELIGIBLE)
                               for part in rel.parts):
                        continue
                    _safe_path(file,root)
                    dest = stage / ("HISTORICAL_" + source_case) / rel
                    _safe_path(dest,root)
                    if dest.is_symlink() or dest.parent.is_symlink():
                        raise ValueError("Refusing linked ESM mirror target")
                    digest = _sha(file)
                    if dest.exists() and (not dest.is_file() or _sha(dest) != digest):
                        raise ValueError("Historical ESM mirror collision: " + str(dest))
                    records.append({"source": file, "dest": dest,
                                    "sha256": digest, "size_bytes": file.stat().st_size})
    root_loose = []
    for file in sorted(root.iterdir(), key=lambda p:p.name.casefold()):
        if file.is_file() and not file.is_symlink():
            root_loose.append(file.name)
    return root, records, root_loose, skipped


def _copy_verified(source, dest, expected_sha):
    if dest.exists():
        if _sha(dest) != expected_sha:
            raise ValueError("Mirror collision: " + str(dest))
        return "EXISTING_IDENTICAL"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=dest.parent, suffix=".partial",
                                     delete=False) as temp:
        tmp = Path(temp.name)
    try:
        shutil.copy2(source, tmp)
        if _sha(tmp) != expected_sha or _sha(source) != expected_sha:
            raise ValueError("Source changed during ESM mirror copy")
        # Exclusive creation; never overwrite a solver or another writer.
        if os.name == "nt":
            os.rename(tmp, dest)
        else:
            os.link(tmp, dest)
    finally:
        tmp.unlink(missing_ok=True)
    return "COPIED_IDENTICAL"


def repair_layout(export_dir, *, apply=False):
    root, records, loose, skipped = plan_migration(export_dir)
    report = {
        "schema": "ETABS_EXPORT_ESM_LAYOUT_REPAIR_V1",
        "status": "APPLIED_SAFE_COPIES_NO_SOURCE_MOVE" if apply else "DRY_RUN_NO_CHANGES",
        "export_root": str(root), "loose_root_file_count": len(loose),
        "loose_root_filenames": loose,
        "historical_esm_mirror_files": len(records), "skipped": skipped,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "items": [{
            "source": str(item["source"].relative_to(root)),
            "mirror": str(item["dest"].relative_to(root)),
            "sha256": item["sha256"],"size_bytes":item["size_bytes"]}
            for item in records],
        "notice":"Historical artifacts are copied, never moved; original consumers"
                 " remain valid. Review root duplicates separately before deletion."
    }
    if apply:
        # A flat root file can be regenerated AFTER the earlier 01_ETABS_EXPORT
        # source mirror was created. Never overwrite that older, immutable
        # proof of an earlier model conversion; retain BOTH SHA identities.
        from components.inputs.export_mirror import EXTS, PRIVATE_NAMES, classification
        staged_root=[]
        changed_root=[]
        for f in sorted(root.iterdir(),key=lambda p:p.name.casefold()):
            if not f.is_file() or f.is_symlink():
                continue
            lower=f.name.casefold()
            if f.suffix.lower() not in EXTS or lower in PRIVATE_NAMES or lower.endswith(_SKIP):
                continue
            dest=root/"01_ETABS_EXPORT"/classification(f.name)/f.name
            _safe_path(dest,root)
            if dest.is_symlink() or (dest.exists() and not dest.is_file()):
                raise ValueError("Unsafe categorized root mirror: "+str(dest))
            source_sha=_sha(f)
            if dest.is_file() and _sha(dest)!=source_sha:
                # Versioned review copy, not a silent overwrite of 01_ETABS_EXPORT.
                revision=(root/"01_ETABS_EXPORT"/"09_REVIEW"/"ROOT_SOURCE_REVISIONS"/
                          (source_sha+f.suffix.lower()))
                _safe_path(revision,root)
                if revision.is_symlink() or (
                        revision.exists() and (not revision.is_file()
                        or _sha(revision)!=source_sha)):
                    raise ValueError("Conflicting root source revision: "+str(revision))
                changed_root.append({"source":str(f.relative_to(root)),
                    "stale_mirror":str(dest.relative_to(root)),
                    "current_sha256":source_sha,
                    "historical_sha256":_sha(dest),
                    "immutable_revision":str(revision.relative_to(root))})
                staged_root.append((f,revision,source_sha))
            else:
                staged_root.append((f,dest,source_sha))
        report["root_mirror_conflicts"]=changed_root
        report["root_mirror_status"]=(
            "STALE_PRIMARY_COPIES_PRESERVED_REVISION_SNAPSHOTS_CREATED"
            if changed_root else "SOURCE_MIRRORS_CURRENT")
        for source,dest,digest in staged_root:
            _safe_path(dest,root)
            _copy_verified(source,dest,digest)
        report["root_mirror_manifest"]=str(
            (root/"03_ESM"/"REVIEW_SNAPSHOTS"/"LAYOUT_REPAIR_MANIFEST.json").relative_to(root))
        if changed_root:
            report["status"]="APPLIED_COPIES_WITH_STALE_PRIMARY_MIRROR_REVIEW_REQUIRED"
        for item in records:
            _safe_path(item["dest"],root)
            _safe_path(item["source"],root)
            item_status=_copy_verified(item["source"],item["dest"],item["sha256"])
            for record in report["items"]:
                if record["mirror"] == str(item["dest"].relative_to(root)):
                    record["copy_status"]=item_status
                    break
        dest=root/"03_ESM"/"REVIEW_SNAPSHOTS"/"LAYOUT_REPAIR_MANIFEST.json"
        _safe_path(dest,root)
        dest.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=dest.parent,mode="w",
                                         encoding="utf-8",suffix=".partial",
                                         delete=False) as f:
            partial=Path(f.name)
            json.dump(report,f,indent=2)
        try:
            os.replace(partial,dest)
        finally:
            partial.unlink(missing_ok=True)
    return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export_root")
    parser.add_argument("--apply",action="store_true",
                        help="Create verified copies only; do not delete/move sources")
    args=parser.parse_args(argv)
    result=repair_layout(args.export_root,apply=args.apply)
    # Do not print every confidential filename in a large project by default.
    print(json.dumps({key:result[key] for key in (
        "status","loose_root_file_count","historical_esm_mirror_files",
        "root_mirror_manifest","notice") if key in result},indent=2))
    return result


if __name__=="__main__":
    main()

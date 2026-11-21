"""[REF docs/source/tools/audit_gravity_workspace.py.md]
Read-only inventory of source-model gravity outputs and exact duplicate bytes.

No solver, move, delete, network request, or hidden replacement occurs. The
report can be saved explicitly within 02_GRAVITY/06_REVIEW for local triage.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path

from components.inputs.output_layout import export_root_for
from components.gravity.output_ownership import section


def _digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as inp:
        for block in iter(lambda:inp.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()


def inspect(export_dir, *, limit_files=20000):
    """[REF docs/source/tools/audit_gravity_workspace.py.md]
    Compare exact content digests, not timestamps, names, or structural values.
    """
    root=export_root_for(export_dir)
    gravity=root/"02_GRAVITY"
    legacy=root/"OpenSees_Analysis_Results"
    sources=[("CANONICAL_GRAVITY",gravity),("HISTORICAL_SHARED",legacy)]
    records=[]
    skipped=[]
    count=0
    for family,source in sources:
        if not source.is_dir():
            continue
        if source.is_symlink():
            raise ValueError("Refusing symlinked gravity inventory root")
        for current,dirs,names in os.walk(source,followlinks=False):
            current=Path(current)
            dirs[:]=sorted(d for d in dirs
                if not (current/d).is_symlink()
                and d not in (".git","__pycache__",".pytest_cache"))
            for name in sorted(names):
                path=current/name
                if path.is_symlink():
                    skipped.append({"path":str(path),"reason":"SYMLINK"})
                    continue
                if not path.is_file():
                    continue
                if not (family=="CANONICAL_GRAVITY" or
                        name.casefold().startswith(("gravity_","primary_32_","etabs_nonzero_",
                            "latest_gravity_","case_summary","evidence_manifest"))):
                    continue
                count+=1
                if count>limit_files:
                    raise ValueError("Inventory limit exceeded; select a smaller source export")
                try:
                    size=path.stat().st_size
                    digest=_digest(path)
                    if path.stat().st_size!=size:
                        raise IOError("size changed while hashing")
                except OSError as exc:
                    skipped.append({"path":str(path),"reason":type(exc).__name__})
                    continue
                rel=path.relative_to(root).as_posix()
                # Categories describe evidence provenance, not correctness.
                if "/REVIEW_SNAPSHOTS/" in "/"+rel or "/ZIP_Exports/" in "/"+rel:
                    role="DERIVED_REVIEW_COPY_OR_ARCHIVE"
                elif rel.startswith("02_GRAVITY/00_INDEXES/"):
                    role="INDEX_POINTER"
                elif rel.startswith("02_GRAVITY/RUNS/"):
                    role="CANONICAL_ACTIVE_OR_RETAINED_CASE"
                elif rel.startswith("OpenSees_Analysis_Results/"):
                    role="HISTORICAL_SHARED_OUTPUT"
                else:
                    role="UNCLASSIFIED_RETAINED_GRAVITY"
                records.append({"path":rel,"bytes":size,"sha256":digest,"role":role})
    byhash=defaultdict(list)
    for item in records:
        byhash[(item["bytes"],item["sha256"])].append(item["path"])
    duplicates=[{"bytes_per_copy":size,"sha256":digest,
                 "copies":len(paths),"paths":paths,
                 "potential_redundant_bytes":size*(len(paths)-1)}
                for (size,digest),paths in byhash.items() if len(paths)>1]
    duplicates.sort(key=lambda item:(-item["potential_redundant_bytes"],item["sha256"]))
    return {
        "schema":"GRAVITY_WORKSPACE_CONTENT_AUDIT_V1",
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "assessment":"HASHED_FILE_INVENTORY_ONLY_NOT_ENGINEERING_EQUIVALENCE",
        "source_export_root":str(root),
        "file_count":len(records),
        "exact_duplicate_groups":len(duplicates),
        "potential_redundant_bytes":sum(d["potential_redundant_bytes"] for d in duplicates),
        "inventory":records,"duplicate_groups":duplicates,"skipped":skipped,
        "safe_next_action":"Review case and model fingerprint before any deletion. "+
            "Shared/derived snapshots can be legitimate audit evidence.",
    }


def save_report(report,export_dir):
    """[REF docs/source/tools/audit_gravity_workspace.py.md]
    Save one explicitly requested local audit; never change inspected sources.
    """
    root=export_root_for(export_dir)
    dest=section(root/"02_GRAVITY","REVIEWS",create=True)/"GRAVITY_WORKSPACE_AUDIT"
    if dest.is_symlink():
        raise ValueError("Refusing linked review output")
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    folder=dest/stamp
    folder.mkdir(parents=True,exist_ok=False)
    path=folder/"EXACT_DUPLICATE_REVIEW.json"
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",
                    encoding="utf-8")
    (folder/"README_FIRST.txt").write_text(
        "READ ONLY duplicate byte scan; no source files moved/deleted.\n"
        "Different case paths may contain identical bytes legitimately.\n"
        "Source model SHA, structural boundary conditions and comparison manifests\n"
        "must be reviewed before accepting any apparent duplicate.\n",
        encoding="utf-8")
    return folder


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export_root",type=Path,
                        help="ETABS export root (contains 02_GRAVITY)")
    parser.add_argument("--max-files",type=int,default=20000)
    parser.add_argument("--write",action="store_true",
                        help="Explicitly save a local diagnostic report; never relocate/delete")
    args=parser.parse_args(argv)
    if args.max_files<1:
        parser.error("--max-files must be positive")
    report=inspect(args.export_root,limit_files=args.max_files)
    summary={key:report[key] for key in ("assessment","file_count",
                "exact_duplicate_groups","potential_redundant_bytes","skipped")}
    print(json.dumps(summary,indent=2))
    if args.write:
        print("Local report:",save_report(report,args.export_root))
    return 0


if __name__=="__main__":
    raise SystemExit(main())

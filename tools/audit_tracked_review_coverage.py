"""Read-only complete Git-index file coverage inventory (NOT semantic review).

Every tracked file is NOT_REVIEWED_CURRENT_HEAD until its exact-current-blob
source lines are independently reviewed and the review ledger is signed.
No source content or private project output is copied. Optional local
structured reports are written only to an explicitly selected export case.

Usage:
 python tools/audit_tracked_review_coverage.py --repo .
 python tools/audit_tracked_review_coverage.py --repo . --export "<LOCAL_EXPORT>"
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _git(root, *args):
    completed = subprocess.run(
        ["git", "-C", str(root), *args], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return completed.stdout


def _category(name):
    parts = Path(name).parts
    if not parts:
        return "UNCLASSIFIED"
    if parts[0] in ("archive", "Archived", "Saved_Projects") or (
            any(p.casefold().startswith(("archive", "saved_project_", "recovered_"))
                for p in parts)):
        return "HISTORICAL_OR_ARCHIVE"
    if name.endswith(".py") and (len(parts) == 1 or parts[0] in (
            "components", "tools")):
        return "ACTIVE_PYTHON_SOURCE"
    if name.endswith(".py") and parts[0] == "tests":
        return "PYTHON_TEST"
    if parts[0] == ".github":
        return "CI_OR_GITHUB_CONFIG"
    if parts[0] in ("docs", "REVIEW_MAIN", "engineering", "LITERATURE",
                    "KNOWLEDGE_BASE"):
        return "DOCUMENTATION_OR_REVIEW"
    return "OTHER_TRACKED_FILE"


def inventory(repo):
    """Enumerate every Git-index file, without assuming any source was reviewed."""
    root=Path(repo).resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(root)
    head=_git(root,"rev-parse","HEAD").decode("ascii").strip()
    # Git index hashes are Git blob IDs, never raw-file SHA256 evidence.
    index=_git(root,"ls-files","--stage","-z")
    rows=[]
    for raw in index.split(b"\0"):
        if not raw:
            continue
        try:
            meta,path=raw.split(b"\t",1)
            mode,blob,stage=meta.decode("ascii").split(" ")
            name=path.decode("utf-8","surrogateescape").replace("\\","/")
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValueError("Malformed Git-index row") from exc
        if stage!="0":
            raise ValueError("Unmerged index entry prevents clean coverage baseline")
        category=_category(name)
        rows.append(dict(path=name,git_blob_sha=blob,git_mode=mode,
                         category=category,
                         review_status="NOT_REVIEWED_CURRENT_HEAD",
                         exact_lines_inspected="",
                         inspector="",source_sha_verified=False,
                         native_solver_verified=False))
    paths=[r["path"] for r in rows]
    if len(paths)!=len(set(paths)):
        raise ValueError("Duplicate tracked path in source coverage inventory")
    # An uncommitted tracked modification invalidates a current-HEAD
    # assertion, but must never be overwritten by this read-only inventory.
    changed=_git(root,"status","--porcelain","--untracked-files=no")
    status="HEAD_CLEAN_TRACKED_FILES" if not changed else "TRACKED_WORKTREE_DIFFERS_FROM_HEAD"
    return dict(
        schema="THESIS_GIT_REVIEW_COVERAGE_BASELINE_V1",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        git_head=head,source_index_status=status,
        scope="ALL_TRACKED_FILES_IN_GIT_INDEX_NOT_ALL_FILES_ON_DISK",
        acceptance="FILE_INVENTORY_ONLY_NO_SEMANTIC_OR_NATIVE_ENGINEERING_REVIEW",
        tracked_count=len(rows),
        reviewed_current_head_count=0,
        review_not_completed_count=len(rows),
        counts_by_category=dict(sorted(Counter(x["category"] for x in rows).items())),
        entries=sorted(rows,key=lambda x:x["path"]),
        next_step=("Inspect current blob source and log exact lines/functions, "
                   "units, side effects, callers, readers, code citations and "
                   "test/native evidence before changing review_status."))


def save_local(report, export_root, repo):
    """Publish a fresh private-local JSON/CSV/README under diagnostics only."""
    from components.inputs.output_layout import export_root_for
    root=export_root_for(export_root)
    repository=Path(repo).resolve(strict=True)
    if root==repository or repository in root.parents:
        raise ValueError("Review outputs must be outside the public source checkout")
    if not root.is_dir():
        raise NotADirectoryError(root)
    ancestor=root
    for part in ("09_SOFTWARE_DIAGNOSTICS","REVIEW_REGISTERS","RUNS"):
        ancestor=ancestor/part
        if ancestor.is_symlink():
            raise ValueError("Refusing linked review-register output destination")
    run=ancestor/(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
                   +"_"+uuid4().hex[:8])
    run.mkdir(parents=True,exist_ok=False)
    for folder in ("JSON","CSV","REPORT"):
        (run/folder).mkdir()
    from components.inputs.output_contract import atomic_json
    atomic_json(run/"JSON"/"Tracked_Review_Coverage.json",report)
    fields=("path","git_blob_sha","git_mode","category","review_status",
            "exact_lines_inspected","inspector","source_sha_verified",
            "native_solver_verified")
    with (run/"CSV"/"Tracked_Review_Coverage.csv").open(
            "x",encoding="utf-8-sig",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n")
        writer.writeheader()
        for row in report["entries"]:
            writer.writerow({k:row[k] for k in fields})
    (run/"REPORT"/"READ_FIRST.md").write_text(
        "# Frozen tracked-file inventory; no source review performed\n\n"
        f"Git HEAD: {report['git_head']}\n"
        f"Tracked files: {report['tracked_count']}\n"
        f"Worktree: {report['source_index_status']}\n\n"
        "Every file is NOT_REVIEWED_CURRENT_HEAD. Do not rename that to "
        "REVIEWED using a syntax scan, missing-guide check or passing CI. "
        "The Git blob ID is not the SHA256 of an ETABS model/record. "
        "Keep this locally with private project case evidence.\n",
        encoding="utf-8")
    return run


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",default=str(_ROOT))
    parser.add_argument("--export",help="Optional selected local export for JSON/CSV/README")
    args=parser.parse_args(argv)
    report=inventory(args.repo)
    print(json.dumps({key:report[key] for key in (
        "git_head","source_index_status","tracked_count",
        "reviewed_current_head_count","counts_by_category","acceptance")},
        indent=2))
    if args.export:
        print("Local review coverage:",save_local(report,args.export,args.repo))
    return 0


if __name__=="__main__":
    raise SystemExit(main())

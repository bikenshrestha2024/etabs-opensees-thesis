"""Verify a frozen, per-file review ledger against the exact Git revision.

Does NOT convert a Git inventory into a source/engineering review. SHA values
are Git BLOB IDs, not raw-file SHA256. Requires git, stdlib Python only.
Usage:
    python tools/validate_review_ledger.py
"""
from __future__ import annotations
import csv
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT/"docs"/"review"/"ledger"/"REVIEW_LEDGER_BASELINE_20261104.csv"
BASE = "66c5c971ea297dc9d7fb0499b871a6204297913d"
ALLOWED = {"NOT_REVIEWED", "PARTIAL_SEMANTIC_REVIEW", "REVIEWED_SOURCE_FULL"}
FIELDS = ("baseline_commit","file_path","git_blob_sha","size_bytes",
          "inventory_kind","inspection_scope","inspected_lines_or_functions",
          "review_status","finding_or_risk","verification_evidence",
          "native_model_status","remaining_action")


def is_scoped_python(path):
    return path.endswith(".py") and (
        path.startswith(("components/", "tests/", "tools/"))
        or "/" not in path
    )


def github_tree_snapshot(commit=BASE, cwd=ROOT):
    """Git baseline tree, including root launchers and compatibility aliases."""
    p = subprocess.run(["git", "ls-tree", "-r", "-l", commit],
                       cwd=cwd, check=True, capture_output=True, text=True)
    result = {}
    for line in p.stdout.splitlines():
        meta, path = line.split("\t", 1)
        mode, objtype, sha, size = meta.split()
        if objtype == "blob" and is_scoped_python(path):
            result[path] = (sha, int(size))
    return result


def validate_ledger(path=LEDGER, *, tree=None, baseline=BASE):
    with Path(path).open(encoding="utf-8", newline="") as stream:
        rd=csv.DictReader(stream)
        if rd.fieldnames != list(FIELDS):
            raise ValueError("Ledger columns/schema changed")
        rows=list(rd)
    if not rows:
        raise ValueError("Empty review ledger")
    paths=set()
    for number,row in enumerate(rows,2):
        file=row["file_path"]
        if not is_scoped_python(file) or file in paths:
            raise ValueError(f"Missing scope or duplicate file at CSV row {number}: {file}")
        paths.add(file)
        if row["baseline_commit"]!=baseline:
            raise ValueError("Mixed baseline commits at "+file)
        if not re.fullmatch(r"[0-9a-f]{40}",row["git_blob_sha"]):
            raise ValueError("Not a real Git blob identifier: "+file)
        if row["review_status"] not in ALLOWED:
            raise ValueError("Unknown review status for "+file)
        if row["review_status"]=="NOT_REVIEWED":
            if row["inspected_lines_or_functions"]!="NOT_INSPECTED":
                raise ValueError("Unreviewed file given inspected lines: "+file)
            if row["finding_or_risk"]!="NOT_EVALUATED":
                raise ValueError("Unreviewed file given invented findings: "+file)
        else:
            if not row["inspected_lines_or_functions"].strip() or (
                    row["inspection_scope"]!="DIRECT_GITHUB_SOURCE_REVIEW"):
                raise ValueError("Reviewed file missing actual inspection evidence: "+file)
        if row["native_model_status"] not in ("NOT_RUN","PASS","FAIL","NOT_EVALUATED",
                                               "REQUIRES_PROJECT_EVIDENCE"):
            raise ValueError("Unknown native test status: "+file)
    if tree is None:
        tree=github_tree_snapshot(baseline)
    missing=set(tree)-paths
    unexpected=paths-set(tree)
    if missing or unexpected:
        raise ValueError("Frozen baseline coverage differs: missing=%r extra=%r" %
                         (sorted(missing)[:12],sorted(unexpected)[:12]))
    for row in rows:
        file=row["file_path"]
        blob,size=tree[file]
        if blob!=row["git_blob_sha"] or size!=int(row["size_bytes"]):
            raise ValueError("Blob or size differs from baseline: "+file)
    return dict(baseline=baseline, files=len(rows),
                actually_inspected=sum(r["review_status"]!="NOT_REVIEWED" for r in rows),
                not_reviewed=sum(r["review_status"]=="NOT_REVIEWED" for r in rows))


def main():
    print(validate_ledger())


if __name__=="__main__":
    main()

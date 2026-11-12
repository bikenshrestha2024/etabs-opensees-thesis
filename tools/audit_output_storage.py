"""Read-only output storage audit for the ETABS-to-OpenSees thesis.

[REF docs/source/tools/audit_output_storage.py.md]
Python 3.12, standard library only. Does not delete, rewrite, rename or
deduplicate original solver evidence. Use --root with the chosen project
output root. If no --root is supplied, choose a folder via tkinter.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def _sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_output(root, *, max_large=50, hash_duplicates=True):
    """Inventory actual bytes and content-identical files without mutation.

    A file's location and basename have no effect on the SHA identity.
    Two distinct solver runs often differ only slightly; those files are
    NOT duplicates and must never be deleted based on name alone.
    Symlinked files/directories are intentionally not followed.
    """
    root = Path(root).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(str(root))
    entries = []
    errors = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if not (Path(dirpath) / d).is_symlink()]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.is_symlink():
                continue
            try:
                stat = path.stat()
                rel = path.relative_to(root)
                entries.append({
                    "relative_path": str(rel).replace("\\", "/"),
                    "bytes": stat.st_size,
                    "extension": path.suffix.lower() or "(none)",
                    "module_folder": rel.parts[0] if len(rel.parts) > 1
                                     else "(root)",
                })
            except OSError as exc:
                errors.append({"path": str(path), "error": str(exc)})
    by_module = defaultdict(lambda: {"bytes": 0, "count": 0})
    by_type = defaultdict(lambda: {"bytes": 0, "count": 0})
    by_size = defaultdict(list)
    for item in entries:
        by_module[item["module_folder"]]["bytes"] += item["bytes"]
        by_module[item["module_folder"]]["count"] += 1
        by_type[item["extension"]]["bytes"] += item["bytes"]
        by_type[item["extension"]]["count"] += 1
        # Zero-byte files are allowed but should not produce vast false duplicate reports.
        if item["bytes"]:
            by_size[item["bytes"]].append(item)
    duplicates = []
    if hash_duplicates:
        for size, candidates in by_size.items():
            if len(candidates) < 2:
                continue
            groups = defaultdict(list)
            for item in candidates:
                try:
                    groups[_sha256(root / item["relative_path"])].append(item)
                except OSError as exc:
                    errors.append({"path": item["relative_path"], "error": str(exc)})
            for digest, group in groups.items():
                if len(group) > 1:
                    duplicates.append({
                        "sha256": digest, "bytes_per_file": size,
                        "repeat_count": len(group),
                        "redundant_bytes": (len(group) - 1) * size,
                        "paths": [x["relative_path"] for x in group],
                        "review_only": True,
                    })
    result = {
        "schema": "etabs-opensees-output-size-audit-v1",
        "status": "DISK_FOOTPRINT_ONLY_NOT_ENGINEERING_EQUIVALENCE",
        "source_root": str(root),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "total_files": len(entries),
        "total_bytes": sum(x["bytes"] for x in entries),
        "module_folders": dict(sorted(by_module.items(),
                                      key=lambda pair: -pair[1]["bytes"])),
        "extensions": dict(sorted(by_type.items(),
                                  key=lambda pair: -pair[1]["bytes"])),
        "largest_files": sorted(entries, key=lambda x: -x["bytes"])[:max_large],
        "exact_duplicate_groups": sorted(duplicates,
                                         key=lambda x: -x["redundant_bytes"]),
        "exact_duplicate_redundant_bytes": sum(
            g["redundant_bytes"] for g in duplicates),
        "scan_errors": errors,
        "hash_duplicates": bool(hash_duplicates),
        "action": "REPORT_ONLY_NO_DELETION",
    }
    return result


def write_report(report, destination):
    """Write only to a fresh dedicated review directory; never alter source runs."""
    out = Path(destination).expanduser().resolve()
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("Report destination already contains files: " + str(out))
    out.mkdir(parents=True, exist_ok=True)
    (out / "DISK_AUDIT.json").write_text(json.dumps(report, indent=2),
                                         encoding="utf-8")
    with (out / "LARGEST_FILES.csv").open("w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(fp, fieldnames=(
            "relative_path", "bytes", "extension", "module_folder"))
        writer.writeheader()
        writer.writerows(report["largest_files"])
    with (out / "EXACT_DUPLICATES.csv").open("w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.writer(fp)
        writer.writerow(("sha256", "bytes_per_file", "repeat_count",
                         "redundant_bytes", "relative_path"))
        for group in report["exact_duplicate_groups"]:
            for path in group["paths"]:
                writer.writerow((group["sha256"], group["bytes_per_file"],
                                 group["repeat_count"], group["redundant_bytes"], path))
    mib = 1024 ** 2
    lines = [
        "# Disk footprint — read-only evidence inventory",
        "",
        "**This is not permission to delete raw engineering results.**",
        "",
        "Root: `" + report["source_root"] + "`",
        "",
        "Total: **{:.2f} MiB** in {} files.".format(
            report["total_bytes"] / mib, report["total_files"]),
        "",
        "Exact duplicate footprint (review candidates only): **{:.2f} MiB**.".format(
            report["exact_duplicate_redundant_bytes"] / mib),
        "",
        "## Top-level folder sizes",
        "",
        "| Folder | Size (MiB) | Files |",
        "|---|---:|---:|",
    ]
    for name, info in report["module_folders"].items():
        lines.append("| `{}` | {:.2f} | {} |".format(
            name.replace("|", "/"), info["bytes"] / mib, info["count"]))
    lines.extend([
        "",
        "## Engineering storage rules",
        "",
        "Source model JSON, original ETABS EDB and verified Excel calculations, "
        "native logs, stage results and SHA evidence must remain immutable.",
        "Repeated derived PNG/PDF/ZIP packages may be copied rather than linked. "
        "Use exact SHA matching and provenance mapping before proposing cleanup.",
        "A matching basename or similar size does not establish duplication. "
        "This program NEVER deletes, overwrites, moves or hardlinks files.",
        "",
        "## Outstanding",
        "",
        "Classify the largest files as raw or derived, verify active case readers, "
        "preserve a sole authoritative result for each source/case, then review "
        "potential archival actions manually. Native ETABS/OpenSees physics "
        "equivalence is not assessed by disk size.",
    ])
    (out / "READ_FIRST.md").write_text("\n".join(lines) + "\n",
                                       encoding="utf-8")
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Existing project output root")
    parser.add_argument("--out", help="New report folder (outside the audited root preferred)")
    parser.add_argument("--no-hash", action="store_true",
                        help="Fast size-only inventory; no duplicate SHA checks")
    args = parser.parse_args(argv)
    root = args.root
    if not root:
        from tkinter import Tk, filedialog
        top = Tk()
        top.withdraw()
        try:
            root = filedialog.askdirectory(title="Select original project output root")
        finally:
            top.destroy()
    if not root:
        raise SystemExit("No output directory selected; nothing modified.")
    report = scan_output(root, hash_duplicates=not args.no_hash)
    # A new sibling report directory avoids making the audit part of its
    # own source tree, preserving a stable measured byte total.
    dest = Path(args.out) if args.out else (
        Path(root).resolve().parent /
        ("Disk_Audit_" + datetime.now().strftime("%Y%m%d_%H%M%S")))
    result = write_report(report, dest)
    print("DISK AUDIT (NO FILES REMOVED):", result)
    print("Total bytes:", report["total_bytes"],
          "| identical-file candidates:", report["exact_duplicate_redundant_bytes"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

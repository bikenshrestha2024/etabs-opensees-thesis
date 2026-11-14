#!/usr/bin/env python3
"""[REF LITERATURE/UPLOAD_INVENTORY_20261114.md]
Private, offline SHA256 inventory of uploaded scientific PDFs.

No PDF is uploaded, changed, deleted or copied. The audit JSON must remain in
a private local project folder: it includes filenames and local path metadata.
Only standard-library Python 3.12 is required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def hash_file(path: Path) -> str:
    """[REF LITERATURE/UPLOAD_INVENTORY_20261114.md] SHA256 full bytes."""
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def inventory(source_folder: Path):
    """[REF LITERATURE/UPLOAD_INVENTORY_20261114.md] Read-only PDF audit."""
    root = source_folder.resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(root)
    records = []
    for candidate in sorted(root.rglob("*"), key=lambda p: p.as_posix().casefold()):
        if candidate.is_symlink() or not candidate.is_file() or candidate.suffix.casefold() != ".pdf":
            continue
        content_length = candidate.stat().st_size
        records.append({
            "relative_filename": candidate.relative_to(root).as_posix(),
            "byte_size": content_length,
            "sha256": hash_file(candidate),
            "is_pdf_signature": candidate.open("rb").read(5) == b"%PDF-",
            "status": "HASHED_NOT_BIBLIOGRAPHICALLY_VALIDATED",
        })
    hashes = defaultdict(list)
    for row in records:
        hashes[row["sha256"]].append(row["relative_filename"])
    return {
        "schema": "THESIS_PRIVATE_PDF_SHA256_AUDIT_V1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_folder": str(root),
        "file_count": len(records),
        "duplicate_sha256_groups": [
            {"sha256": k, "filenames": v}
            for k, v in sorted(hashes.items()) if len(v) > 1
        ],
        "files": records,
        "note": "Equal SHA256 proves byte identity. Unequal SHA256 does not prove different publications/editions. Review metadata and pages before deduplicating.",
    }


def save_private_json(report, target: Path):
    """[REF LITERATURE/UPLOAD_INVENTORY_20261114.md] Atomic local write."""
    target = target.expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=target.parent, suffix=".tmp", delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(report, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        os.replace(temporary, target)
    finally:
        if "temporary" in locals():
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf_folder", type=Path, help="Private folder containing original uploaded PDFs")
    parser.add_argument("--output", required=True, type=Path,
                        help="Private output JSON path, outside PUBLIC GitHub")
    args = parser.parse_args()
    report = inventory(args.pdf_folder)
    save_private_json(report, args.output)
    print("PDF_COUNT=" + str(report["file_count"]))
    print("DUPLICATE_SHA256_GROUPS=" + str(len(report["duplicate_sha256_groups"])))
    print("PRIVATE_MANIFEST=" + str(args.output.resolve()))


if __name__ == "__main__":
    main()

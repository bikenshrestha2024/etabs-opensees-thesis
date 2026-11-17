"""Atomic XLSX evidence publisher for on-demand gravity and mesh exports.

[REF docs/source/components/gravity/workbook_publishing.py.md]
No ETABS access, finite-element calculations or source workbook modification.
"""
from __future__ import annotations

import hashlib
import os
import tempfile
import zipfile
from pathlib import Path


def publish_workbook(workbook, destination, *, temp_prefix=".gravity_") -> str:
    """Save and hash a large XLSX without corrupting an existing destination.

    Returns SHA256 of exactly the newly published XLSX bytes. Saves in an
    exclusive temporary file under the destination directory, verifies that
    the ZIP central directory contains minimum workbook parts, streams its
    SHA256 using 1-MiB blocks, and atomically replaces the destination.
    Failed serialization, ZIP validation or hashing preserves any old file.
    This verifies the XLSX container, not formulas or engineering acceptance.
    """
    target=Path(destination)
    if target.suffix.casefold()!=".xlsx":
        raise ValueError("XLSX destination requires .xlsx suffix")
    for part in (target,*target.parents):
        if part.is_symlink():
            raise ValueError("Refusing linked XLSX output destination")
    target.parent.mkdir(parents=True,exist_ok=True)
    for part in (target,*target.parents):
        if part.is_symlink():
            raise ValueError("Refusing linked XLSX output destination")
    fd,name=tempfile.mkstemp(prefix=temp_prefix,suffix=".xlsx",dir=target.parent)
    os.close(fd)
    staged=Path(name)
    try:
        workbook.save(staged)
        try:
            with zipfile.ZipFile(staged) as archive:
                paths=set(archive.namelist())
                if not {"[Content_Types].xml","xl/workbook.xml"}.issubset(paths):
                    raise ValueError("invalid XLSX: missing workbook ZIP parts")
        except zipfile.BadZipFile as exc:
            raise ValueError("invalid XLSX: serialization did not produce a ZIP") from exc
        sha=hashlib.sha256()
        with staged.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024*1024),b""):
                sha.update(chunk)
        for part in (target,*target.parents):
            if part.is_symlink():
                raise ValueError("Refusing linked XLSX output destination")
        os.replace(staged,target)
        return sha.hexdigest()
    finally:
        staged.unlink(missing_ok=True)

"""Publish a small, explicitly selected, checksum-verified local review ZIP.

An archive is an evidence transport, NEVER ETABS/OpenSees equivalence or
engineering approval. Source models are not changed and nothing is uploaded.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

from components.inputs.review_zip_paths import ensure_review_zip_directory


_PACKAGE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*\.zip$")
_CATEGORY_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
_BLOCKED_SUFFIXES = {'.zip', '.7z', '.rar', '.edb', '.pem', '.key', '.p12', '.env'}


def _refuse_linked_path(path: Path) -> None:
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError(f"Refusing symlinked evidence path: {path}")


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def publish_case_evidence_zip(source_run, *, filename, files, category=None,
                              status='REVIEW_EVIDENCE_NOT_ENGINEERING_ACCEPTANCE') -> Path:
    """Create an atomic archive with an SHA256 manifest and no implicit file crawl.

    files is an iterable of (archive_relative_path, absolute_source_path).
    Only explicitly selected files are included; duplicate or unsafe archive
    paths and symlinks fail closed. Do not package sensitive source files unless
    the user has explicitly selected the local evidence package for review.
    """
    root = Path(source_run).expanduser()
    _refuse_linked_path(root)
    if not root.is_dir():
        raise NotADirectoryError(f"Evidence source folder is absent: {root}")
    if not isinstance(filename, str) or not _PACKAGE_NAME.fullmatch(filename):
        raise ValueError('ZIP filename must be a single safe .zip filename')
    if category is not None and (not isinstance(category, str)
                                 or not _CATEGORY_NAME.fullmatch(category)):
        raise ValueError('ZIP category must be a single safe folder name')
    selected = list(files)
    if not selected:
        raise ValueError('Refusing an empty evidence ZIP')
    seen = {'EVIDENCE_MANIFEST.json'}
    entries = []
    for name, src in selected:
        if not isinstance(name, str) or '\\' in name:
            raise ValueError(f"Unsafe ZIP archive path: {name!r}")
        archive_name = PurePosixPath(name)
        if (archive_name.is_absolute() or not name.strip() or
                any(part in ('', '.', '..') for part in name.split('/')) or
                archive_name.as_posix() in seen):
            raise ValueError(f"Unsafe/duplicate ZIP archive path: {name!r}")
        seen.add(archive_name.as_posix())
        path = Path(src).expanduser()
        _refuse_linked_path(path)
        if not path.is_file():
            raise FileNotFoundError(f"Missing ZIP evidence file: {path}")
        if path.suffix.lower() in _BLOCKED_SUFFIXES:
            raise ValueError(f"Prohibited ZIP source file type: {path.name}")
        entries.append({'archive_path': archive_name.as_posix(),
                        'path': path, 'bytes': path.stat().st_size,
                        'sha256': _sha256(path)})
    destination = ensure_review_zip_directory(root)
    if category:
        destination /= category
    _refuse_linked_path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / filename
    _refuse_linked_path(target)
    temporary = target.with_name(target.name + '.tmp-' + uuid4().hex)
    manifest = {
        'schema': 'thesis-evidence-zip-v1',
        'status': str(status),
        'engineering_acceptance': 'NOT_VERIFIED',
        'source_upload': 'NONE_LOCAL_ONLY',
        'file_count': len(entries),
        'files': [{k: e[k] for k in ('archive_path', 'bytes', 'sha256')}
                  for e in entries],
    }
    try:
        with ZipFile(temporary, 'w', compression=ZIP_DEFLATED,
                     compresslevel=6, allowZip64=True) as archive:
            for entry in entries:
                if (_sha256(entry['path']) != entry['sha256'] or
                        entry['path'].stat().st_size != entry['bytes']):
                    raise IOError(f"Evidence changed before ZIP: {entry['archive_path']}")
                archive.write(entry['path'], arcname=entry['archive_path'])
            archive.writestr('EVIDENCE_MANIFEST.json', json.dumps(manifest, indent=2))
        with ZipFile(temporary) as verified:
            corrupt = verified.testzip()
            if corrupt:
                raise IOError(f"ZIP integrity failure: {corrupt}")
            if len(verified.namelist()) != len(entries) + 1:
                raise IOError('ZIP file count does not match source manifest')
            for entry in entries:
                digest = hashlib.sha256()
                with verified.open(entry['archive_path']) as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                        digest.update(chunk)
                if digest.hexdigest() != entry['sha256']:
                    raise IOError(f"Source changed while packaging: {entry['archive_path']}")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return target

# -*- coding: utf-8 -*-
"""Local, privacy-conscious review exports and Tk text scrolling.

No network calls. Original solver outputs remain untouched. ZIP files are
review evidence, not engineering acceptance; input earthquake files outside
the run directory are NOT copied automatically.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from datetime import datetime
from zipfile import ZIP_DEFLATED, ZipFile


def attach_text_scrollbar(parent, text):
    """Pack a Text widget and its vertical/horizontal scrollbar in a shared frame.

    text must have parent as its Tk master. The GUI/event loop owns all widgets.
    """
    from tkinter import ttk
    text.configure(wrap="none")
    yscroll = ttk.Scrollbar(parent, orient="vertical", command=text.yview)
    xscroll = ttk.Scrollbar(parent, orient="horizontal", command=text.xview)
    text.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    text.grid(row=0, column=0, sticky="nsew")
    yscroll.grid(row=0, column=1, sticky="ns")
    xscroll.grid(row=1, column=0, sticky="ew")
    return yscroll, xscroll


def export_review_zip(output_dir, analysis, *, max_file_bytes=512 * 1024 * 1024):
    """Archive existing local run evidence, not source models or external records.

    Snapshot path: <output_dir>/Review_ZIPs/<analysis>_<timestamp>.zip.
    Excludes symbolic links, existing archives, hidden files, generated ZIPs,
    and unusually large files. Manifest records exclusions, file SHA256 and
    explicit diagnostic/non-acceptance status. No original file is moved.
    """
    root = Path(output_dir).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(root)
    analysis = {"linear": "Linear_Time_History", "nonlinear": "Nonlinear_Time_History"}[analysis]
    target_dir = root / "Review_ZIPs"
    target_dir.mkdir(exist_ok=True)
    dest = target_dir / (analysis + "_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".zip")
    manifest = {
        "schema": "history-review-evidence-v1", "analysis": analysis,
        "status": "REVIEW_EVIDENCE_NOT_ENGINEERING_ACCEPTANCE",
        "source_directory": str(root),
        "warning": "May contain local paths, coordinates and engineering data. Review before sharing publicly. Ground motions outside source directory are not included.",
        "files": [], "excluded": [],
    }
    try:
        with ZipFile(dest, "w", compression=ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
            for path in sorted(root.rglob("*")):
                if path.is_symlink() or not path.is_file():
                    continue
                relative = path.relative_to(root)
                rel = relative.as_posix()
                if relative.parts[0] == "Review_ZIPs" or any(part.startswith(".") for part in relative.parts):
                    continue
                if path.suffix.lower() in {".zip", ".rar", ".7z", ".edb", ".p12", ".pem", ".key", ".env"}:
                    manifest["excluded"].append({"file": rel, "reason": "archive/model/credential file excluded"})
                    continue
                size = path.stat().st_size
                if size > max_file_bytes:
                    manifest["excluded"].append({"file": rel, "reason": "size limit", "bytes": size})
                    continue
                digest = hashlib.sha256()
                with path.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
                archive.write(path, arcname=rel)
                manifest["files"].append({"path": rel, "bytes": size, "sha256": digest.hexdigest()})
            archive.writestr("REVIEW_EVIDENCE_MANIFEST.json", json.dumps(manifest, indent=2))
    except Exception:
        dest.unlink(missing_ok=True)
        raise
    return dest, manifest


def export_review_zip_dialog(parent, output_dir, analysis):
    """User-triggered local export with privacy confirmation and clear errors."""
    from tkinter import messagebox
    if not messagebox.askyesno(
        "Export local review evidence",
        "Create a ZIP from the selected analysis output folder? It may contain "
        "model paths, project details and structural results. Inspect the ZIP "
        "before sharing. This does NOT establish NBC compliance.",
        parent=parent,
    ):
        return None
    try:
        dest, manifest = export_review_zip(output_dir, analysis)
    except (OSError, ValueError, KeyError) as exc:
        messagebox.showerror("Review ZIP export failed", str(exc), parent=parent)
        return None
    messagebox.showinfo(
        "Review ZIP exported",
        f"{dest}\nIncluded: {len(manifest['files'])} files; "
        f"excluded: {len(manifest['excluded'])}. Original results unchanged.",
        parent=parent,
    )
    return dest

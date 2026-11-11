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
    [REF components/ui/history_results.py] GUI scroll interaction convention.
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


def choose_history_run_folder(folder, analysis):
    """Choose newest run containing a matching config, log or summary.

    Do not automatically archive unrelated Gravity/ESM/MRSM folders merely
    because the GUI stores a common analysis-results root.
    [REF docs/review/20261111_HISTORY_GUI_SECURITY_AND_PHYSICS.md] Review-only source isolation.
    """
    root = Path(folder).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(root)
    module = {"linear": "Linear", "nonlinear": "Nonlinear"}[analysis]
    candidates = [
        p for p in root.rglob("*")
        if p.is_file() and not p.is_symlink()
        and "Review_ZIPs" not in p.parts
        and module + "_Time_History_" in p.name
        and (p.name.endswith(".log") or p.name.endswith(".json"))
        and any(token in p.name for token in ("RunConfig", "Run_V", "Summary"))
    ]
    if not candidates:
        raise FileNotFoundError(
            "No matching " + module + " Time History run found below " + str(root)
            + ". Run or select the correct analysis output first.")
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0].parent


def _category(path):
    suffix = path.suffix.lower()
    name = path.name.lower()
    if suffix == ".log" or "error" in name or "timing" in name:
        return "Logs"
    if any(token in name for token in ("runconfig", "input_record", "source_provenance")):
        return "Inputs"
    if suffix in {".png", ".jpg", ".jpeg", ".svg"}:
        return "Plots"
    if suffix == ".pdf":
        return "Reports"
    if suffix in {".csv", ".xlsx", ".xls", ".tsv"}:
        return "Tables"
    return "Analysis"


def export_review_zip(output_dir, analysis, *, max_file_bytes=512 * 1024 * 1024):
    """Archive existing local run evidence, not source models or external records.

    Snapshot path: <output_dir>/Review_ZIPs/<analysis>_<timestamp>.zip.
    Excludes symbolic links, existing archives, hidden files, generated ZIPs,
    and unusually large files. Manifest records exclusions, file SHA256 and
    explicit diagnostic/non-acceptance status. No original file is moved.
    [REF engineering/rules/PROVENANCE.md] Immutable source evidence and hashes.
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
                arcname = analysis + "/" + _category(path) + "/" + rel
                archive.write(path, arcname=arcname)
                manifest["files"].append({"path": rel, "archive_path": arcname,
                                           "bytes": size, "sha256": digest.hexdigest()})
            archive.writestr("REVIEW_EVIDENCE_MANIFEST.json", json.dumps(manifest, indent=2))
    except Exception:
        dest.unlink(missing_ok=True)
        raise
    return dest, manifest


def export_review_zip_dialog(parent, output_dir, analysis):
    """User-triggered local export with privacy confirmation and clear errors.

    [REF engineering/rules/CORE_RULES.md] Keep source data private and unmodified.
    """
    from tkinter import messagebox
    try:
        selected_run = choose_history_run_folder(output_dir, analysis)
    except (OSError, ValueError, KeyError) as exc:
        messagebox.showerror("Review ZIP requires a matching history run", str(exc), parent=parent)
        return None
    if not messagebox.askyesno(
        "Export local review evidence",
        "Export this analysis run only?\\n\\n" + str(selected_run)
        + "\\n\\nIt may contain local model paths and project details. "
          "Inspect the ZIP before sharing. This does NOT establish NBC compliance.",
        parent=parent,
    ):
        return None
    try:
        dest, manifest = export_review_zip(selected_run, analysis)
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

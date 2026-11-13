"""Read a bounded, repository-tracked citation document in a scrollable GUI.

The previous launcher attempted os.startfile on a nonexistent markdown file
beside components/ui/application.py, raising an exception on Windows.

[REF docs/00_RESEARCH_REFERENCES.md]
"""
from __future__ import annotations
from pathlib import Path

MAX_REFERENCE_BYTES = 2_000_000
DEFAULT_REFERENCE = "docs/02_MODEL_NBC_REFERENCE_AND_VALIDATION.md"


def resolve_reference_document(repo_root: Path | None = None,
                               relative_path: str = DEFAULT_REFERENCE) -> Path:
    """Find the shipped citation document; fail with a readable error.

    [REF docs/02_MODEL_NBC_REFERENCE_AND_VALIDATION.md]
    """
    root = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]
    target = (root / relative_path).resolve()
    if not target.is_relative_to(root):
        raise ValueError("Reference path must stay within this repository")
    if not target.is_file():
        raise FileNotFoundError(
            f"Reference document missing: {target}. Update this repository; "
            "the original citation button pointed to a nonexistent file.")
    if target.stat().st_size > MAX_REFERENCE_BYTES:
        raise ValueError("Reference document is too large for the text viewer; use a smaller indexed chapter.")
    return target


def open_reference_viewer(parent=None, repo_root: Path | None = None) -> None:
    """Show the full citation notes with vertical/horizontal scrolling.

    No browser, PDF reader or external shell association is required.
    [REF docs/02_MODEL_NBC_REFERENCE_AND_VALIDATION.md]
    """
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    try:
        path = resolve_reference_document(repo_root)
        document = path.read_text(encoding="utf-8-sig")
    except (OSError, ValueError, UnicodeError) as exc:
        messagebox.showerror("NBC citation document", str(exc), parent=parent)
        return
    win = tk.Toplevel(parent) if parent else tk.Tk()
    win.title("NBC 105:2025 — Source references and Model verification")
    win.geometry("1080x740")
    win.minsize(680, 430)
    outer = ttk.Frame(win, padding=10)
    outer.pack(fill="both", expand=True)
    ttk.Label(outer, text=str(path), anchor="w").pack(fill="x")
    body = ttk.Frame(outer)
    body.pack(fill="both", expand=True, pady=7)
    yscroll = ttk.Scrollbar(body, orient="vertical")
    xscroll = ttk.Scrollbar(body, orient="horizontal")
    view = tk.Text(body, wrap="none", height=30, font=("Consolas", 10),
                   yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    yscroll.config(command=view.yview)
    xscroll.config(command=view.xview)
    yscroll.pack(side="right", fill="y")
    xscroll.pack(side="bottom", fill="x")
    view.pack(side="left", fill="both", expand=True)
    view.insert("1.0", document)
    view.config(state="disabled")
    bar = ttk.Frame(outer)
    bar.pack(fill="x")
    ttk.Button(bar, text="Copy document", command=lambda: (win.clipboard_clear(),
               win.clipboard_append(document))).pack(side="left")
    ttk.Button(bar, text="Save a copy", command=lambda: _save_copy(
               filedialog, messagebox, win, document)).pack(side="left", padx=6)
    ttk.Button(bar, text="Close", command=win.destroy).pack(side="right")


def _save_copy(filedialog, messagebox, win, document):
    location = filedialog.asksaveasfilename(parent=win, defaultextension=".md",
        filetypes=[("Markdown", "*.md"), ("Text", "*.txt")],
        initialfile="NBC105_Model_References.md")
    if not location:
        return
    try:
        Path(location).write_text(document, encoding="utf-8")
    except OSError as exc:
        messagebox.showerror("Save citation document", str(exc), parent=win)

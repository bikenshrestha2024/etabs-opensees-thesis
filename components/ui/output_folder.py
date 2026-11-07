"""One shared 'Open output folder' action for every analysis window.

[REF docs/review/00_CANONICAL_RUN_ORDER_AND_NAMING.md (one isolated output folder per analysis)]

Previously each GUI called ``os.startfile`` inline (Windows-only, raising an
unexplained error when the folder did not exist yet), and several analysis
windows (MRSM, linear and nonlinear time history, irregularity review,
literature demo) had no button at all.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def resolve_folder(value):
    """Return an existing folder Path from a str/Path/StringVar/callable, or None.

    [REF components/inputs/project_workbooks.py analysis_output_folder] A file
    path resolves to its parent folder; a missing folder is NOT created here
    (opening a folder must never create analysis output silently).
    """
    if callable(value) and not hasattr(value, 'get'):
        value = value()
    if hasattr(value, 'get'):
        value = value.get()
    text = str(value or '').strip()
    if not text:
        return None
    path = Path(text).expanduser()
    if path.is_file():
        path = path.parent
    return path if path.is_dir() else None


def open_folder(value, *, parent=None, title='Open output folder'):
    """Open the folder in the system file browser; explain if it is missing.

    [REF Python os.startfile (Windows); xdg-open / open (Linux, macOS)]
    Returns the opened Path or None.
    """
    path = resolve_folder(value)
    if path is None:
        raw = value.get() if hasattr(value, 'get') else (value() if callable(value) else value)
        try:
            from tkinter import messagebox
            messagebox.showinfo(title, 'The output folder does not exist yet:\n'
                                + str(raw or '(not set)')
                                + '\n\nRun the analysis first or choose another folder.',
                                parent=parent)
        except Exception:
            pass
        return None
    if sys.platform.startswith('win'):
        os.startfile(str(path))  # noqa: S606 - user-requested folder view
    else:
        subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', str(path)])
    return path


def add_open_output_button(parent, value, *, text='Open output folder', window=None, **pack):
    """Create and pack a ttk button that opens ``value`` (StringVar/str/callable).

    [REF components/ui/output_folder.py open_folder]
    """
    from tkinter import ttk
    button = ttk.Button(parent, text=text,
                        command=lambda: open_folder(value, parent=window or parent))
    button.pack(**({'side': 'left', 'padx': 4} | pack))
    return button


def offer_open_folder(value, message, *, parent=None, title='Analysis finished'):
    """Completion dialog that also offers to open the result folder.

    [REF components/ui/output_folder.py open_folder] Returns True if opened.
    """
    from tkinter import messagebox
    if resolve_folder(value) is None:
        messagebox.showinfo(title, message, parent=parent)
        return False
    if messagebox.askyesno(title, message + '\n\nOpen the output folder now?', parent=parent):
        return open_folder(value, parent=parent) is not None
    return False

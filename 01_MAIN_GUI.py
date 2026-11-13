"""01 — Main ETABS → OpenSeesPy GUI.

Short, numbered user entry point for Windows / Spyder.
Uses the existing fresh-process startup with logging; no solver code changes.
[REF docs/programs/01_MAIN_GUI.md]
"""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().with_name("01.py")),
        run_name="__main__",
    )

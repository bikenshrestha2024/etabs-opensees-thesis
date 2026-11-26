"""Compatibility entry for saved shortcuts to the main workbench."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().with_name("01_WORKFLOW_START.py")),
        run_name="__main__",
    )

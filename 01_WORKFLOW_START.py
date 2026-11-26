"""Compatibility entry for the canonical 01.py launcher."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().with_name("01.py")),run_name="__main__")

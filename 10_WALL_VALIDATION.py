"""Legacy compatibility alias: run 07_WALL_VALIDATION.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("07_WALL_VALIDATION.py")),run_name=__name__)
globals().update(_namespace)

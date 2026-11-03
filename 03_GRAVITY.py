"""Legacy compatibility alias: run 10_GRAVITY.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("10_GRAVITY.py")),run_name=__name__)
globals().update(_namespace)

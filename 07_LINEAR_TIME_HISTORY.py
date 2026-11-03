"""Legacy compatibility alias: run 14_LINEAR_TIME_HISTORY.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("14_LINEAR_TIME_HISTORY.py")),run_name=__name__)
globals().update(_namespace)

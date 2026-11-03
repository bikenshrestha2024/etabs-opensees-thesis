"""Legacy compatibility alias: run 18_NONLINEAR_PERFORMANCE.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("18_NONLINEAR_PERFORMANCE.py")),run_name=__name__)
globals().update(_namespace)

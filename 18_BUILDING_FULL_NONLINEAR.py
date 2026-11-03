"""Legacy compatibility alias: run 17_BUILDING_FULL_NONLINEAR.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("17_BUILDING_FULL_NONLINEAR.py")),run_name=__name__)
globals().update(_namespace)

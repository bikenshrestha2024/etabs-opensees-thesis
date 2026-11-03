"""Legacy compatibility alias: run 15_BUILDING_NONLINEAR_TRIAL.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("15_BUILDING_NONLINEAR_TRIAL.py")),run_name=__name__)
globals().update(_namespace)

"""Legacy compatibility alias: run 16_NONLINEAR_REVIEWED_MODEL.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("16_NONLINEAR_REVIEWED_MODEL.py")),run_name=__name__)
globals().update(_namespace)

"""Legacy compatibility alias: run 03_MATERIAL_PARAMETER_SETUP.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("03_MATERIAL_PARAMETER_SETUP.py")),run_name=__name__)
globals().update(_namespace)

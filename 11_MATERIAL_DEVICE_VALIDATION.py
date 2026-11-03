"""Legacy compatibility alias: run 06_MATERIAL_DEVICE_VALIDATION.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("06_MATERIAL_DEVICE_VALIDATION.py")),run_name=__name__)
globals().update(_namespace)

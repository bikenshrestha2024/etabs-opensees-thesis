"""Legacy compatibility alias: run 05_STEEL02_CALIBRATION.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("05_STEEL02_CALIBRATION.py")),run_name=__name__)
globals().update(_namespace)

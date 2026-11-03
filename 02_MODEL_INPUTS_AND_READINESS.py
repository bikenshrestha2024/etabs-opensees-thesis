"""Legacy compatibility alias: run 02_INPUT_READINESS.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("02_INPUT_READINESS.py")),run_name=__name__)
globals().update(_namespace)

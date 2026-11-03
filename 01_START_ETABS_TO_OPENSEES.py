"""Legacy compatibility alias: run 01_WORKFLOW_START.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("01_WORKFLOW_START.py")),run_name=__name__)
globals().update(_namespace)

"""Legacy compatibility alias: run 20_TRACE_FAILED_ELEMENT.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("20_TRACE_FAILED_ELEMENT.py")),run_name=__name__)
globals().update(_namespace)

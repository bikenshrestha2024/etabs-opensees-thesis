"""Legacy compatibility alias: run 08_COMPONENT_RESULTS.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("08_COMPONENT_RESULTS.py")),run_name=__name__)
globals().update(_namespace)

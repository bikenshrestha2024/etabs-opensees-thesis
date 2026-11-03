"""Legacy compatibility alias: run 09_LITERATURE_COMPONENT_DEMO.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("09_LITERATURE_COMPONENT_DEMO.py")),run_name=__name__)
globals().update(_namespace)

"""Legacy compatibility alias: run 13_RESPONSE_SPECTRUM.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("13_RESPONSE_SPECTRUM.py")),run_name=__name__)
globals().update(_namespace)

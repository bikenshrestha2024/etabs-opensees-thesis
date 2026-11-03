"""Legacy compatibility alias: run 04_LITERATURE_MATERIAL_PROFILES.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("04_LITERATURE_MATERIAL_PROFILES.py")),run_name=__name__)
globals().update(_namespace)

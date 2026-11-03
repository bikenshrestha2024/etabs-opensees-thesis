"""Legacy compatibility alias: run 11_MODAL_ULS_SLS.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("11_MODAL_ULS_SLS.py")),run_name=__name__)
globals().update(_namespace)

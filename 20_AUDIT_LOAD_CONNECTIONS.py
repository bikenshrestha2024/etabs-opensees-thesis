"""Legacy compatibility alias: run 19_AUDIT_LOAD_CONNECTIONS.py instead."""
from pathlib import Path
import runpy
_namespace=runpy.run_path(str(Path(__file__).resolve().with_name("19_AUDIT_LOAD_CONNECTIONS.py")),run_name=__name__)
globals().update(_namespace)

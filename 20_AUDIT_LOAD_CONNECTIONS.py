"""Legacy compatibility alias: run 19_AUDIT_LOAD_CONNECTIONS.py instead."""
from pathlib import Path
import runpy
_target = Path(__file__).resolve().with_name("19_AUDIT_LOAD_CONNECTIONS.py")
if __name__ == "__main__":
    runpy.run_path(str(_target))["main"]()
else:
    globals().update(runpy.run_path(str(_target), run_name=__name__))

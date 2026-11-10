"""Main numbered launcher. Run from Spyder or `python 01.py`."""
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parent
if __name__ == '__main__':
    sys.path.insert(0, str(ROOT))
    runpy.run_path(str(ROOT / 'RUN_ETABS_TO_OPENSEES.py'), run_name='__main__')

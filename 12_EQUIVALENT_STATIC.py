from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parent


if __name__ == '__main__':
    sys.path.insert(0, str(ROOT))
    runpy.run_path(str(ROOT / 'OpenSees_Earthquake_Analysis_NBC105_V111.py'), run_name='__main__')

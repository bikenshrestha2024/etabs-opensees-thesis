from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parent


if __name__ == '__main__':
    sys.path.insert(0, str(ROOT))
    runpy.run_path(str(ROOT / 'OpenSees_Gravity_GUI_V110.py'), run_name='__main__')

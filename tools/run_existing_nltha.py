"""One-command direct nonlinear time-history analysis of an EXISTING OpenSees model.

Run from the repo checkout:
  python tools/run_existing_nltha.py --model-folder "..." --x-path "..." \\
      --y-path "..." --output-dir "..." --event Kobe --variant-id M4

Native OpenSeesPy/XARA must be present in the chosen Python interpreter.
No source EDB or confidential model data is pushed to GitHub by this file.
"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from components.nonlinear_time_history.direct_existing_model import main

if __name__=="__main__":
    main()

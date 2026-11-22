"""38 — Directly launch one existing Soil-C M0–M6 NLTHA case in OpenSeesPy.

Example: python 38_EXECUTE_SOIL_C_NLTHA.py --config "D:/Thesis/RunMatrix/configs/M0/ULS/Kobe.json" --allow-research-diagnostic --run

Without --run, this is a read-only input preflight.
The Stage 36 research configs cannot become thesis-accepted runs by flag alone.
"""
from components.nonlinear_time_history.soil_c_case_execution import main

if __name__ == "__main__":
    raise SystemExit(main())

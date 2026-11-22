"""Stage 38: canonical alias for the ONLY existing-model NLTHA runner.

The implementation lives in components/nonlinear_time_history/direct_existing_model.py
and uses the shared building_exploratory native solver. No separate physics
or model defaults are created by this launcher.
[REF docs/programs/38_DIRECT_EXISTING_MODEL_NLTHA.md]
"""
from components.nonlinear_time_history.direct_existing_model import main

if __name__ == "__main__":
    main()

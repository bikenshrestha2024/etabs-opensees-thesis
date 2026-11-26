# 15 — Short nonlinear diagnostic trial

**Current launcher:** [`15_BUILDING_NONLINEAR_TRIAL.py`](../../15_BUILDING_NONLINEAR_TRIAL.py)  
**Previous launcher:** [`08_BUILDING_NONLINEAR_TRIAL.py`](../../08_BUILDING_NONLINEAR_TRIAL.py) (compatibility alias)

## Goal
Open the exploratory nonlinear history GUI for an assembled export. Set a positive trial duration before starting a short run. The GUI starts with a duration of zero, which requests the full record. The [triage program](21_NLTHA_TRIAGE.md) can prepare controlled ZERO/X/Y/XY short probes.

## Input checklist
Confirm the current export folder, validated geometry and section mapping, gravity and mass data, analysis units, selected material cards, and output destination as applicable to this subprogram. Do not mix old saved V156 exports with source modules from the new checkout.

## Execution
In Spyder open `15_BUILDING_NONLINEAR_TRIAL.py` and run. Alternatively from the repository root invoke `python 15_BUILDING_NONLINEAR_TRIAL.py`. If the script requires arguments (particularly the two diagnostic scripts), inspect the Python source usage and supply an appropriate export or failed-run folder.

## Validation and results
Review the program's actual run logs, input assumptions, generated files and solver status before interpreting engineering output. Material examples and smoke tests are not experimental calibration, and an incomplete nonlinear earthquake history must not be ranked. The building transient first-step failure remains unresolved.

[Complete run order](00_PROGRAM_INDEX.md) · [Modeling basis](../../Research_Components/02_MODELLING_BASIS.md)

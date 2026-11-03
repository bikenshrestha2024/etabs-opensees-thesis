# 10 — Gravity equilibrium and reactions

**Current launcher:** [`10_GRAVITY.py`](../../10_GRAVITY.py)  
**Previous launcher:** [`03_GRAVITY.py`](../../03_GRAVITY.py) (compatibility alias)

## Goal
Gravity equilibrium and reactions. Run from the complete repository with a compatible Windows Python/OpenSeesPy environment. This entry point retains the original launcher's numerical implementation unchanged.

## Input checklist
Confirm the current export folder, validated geometry and section mapping, gravity and mass data, analysis units, selected material cards, and output destination as applicable to this subprogram. Do not mix old saved V156 exports with source modules from the new checkout.

## Execution
In Spyder open `10_GRAVITY.py` and run. Alternatively from the repository root invoke `python 10_GRAVITY.py`. If the script requires arguments (particularly the two diagnostic scripts), inspect the Python source usage and supply an appropriate export or failed-run folder.

## Validation and results
Review the program's actual run logs, input assumptions, generated files and solver status before interpreting engineering output. Material examples and smoke tests are not experimental calibration, and an incomplete nonlinear earthquake history must not be ranked. The building transient first-step failure remains unresolved.

[Complete run order](00_PROGRAM_INDEX.md) · [Modeling basis](../../Research_Components/02_MODELLING_BASIS.md)

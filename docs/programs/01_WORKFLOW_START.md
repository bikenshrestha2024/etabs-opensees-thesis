# 01 — Main ETABS-to-OpenSees GUI

The canonical entry is [`01_WORKFLOW_START.py`](../../01_WORKFLOW_START.py). [`01.py`](../../01.py), [`01_MAIN_GUI.py`](../../01_MAIN_GUI.py), and [`01_START_ETABS_TO_OPENSEES.py`](../../01_START_ETABS_TO_OPENSEES.py) open the same workbench when run directly.

## Goal
Main ETABS-to-OpenSees GUI. Run from the complete repository with a compatible Windows Python/OpenSeesPy environment. This entry point retains the original launcher's numerical implementation unchanged.

## Input checklist
Confirm the current export folder, validated geometry and section mapping, gravity and mass data, analysis units, selected material cards, and output destination as applicable to this subprogram. Do not mix old saved V156 exports with source modules from the new checkout.

## Execution
In Spyder open `01_WORKFLOW_START.py` and run it. From the repository root, use `python 01.py`. The launcher guide describes startup logging and the Windows smoke check. [Launcher guide](01_MAIN_GUI.md)

## Validation and results
Review the program's actual run logs, input assumptions, generated files and solver status before interpreting engineering output. Material examples and smoke tests are not experimental calibration, and an incomplete nonlinear earthquake history must not be ranked. The building transient first-step failure remains unresolved.

[Complete run order](00_PROGRAM_INDEX.md) · [Modeling basis](../../Research_Components/02_MODELLING_BASIS.md)

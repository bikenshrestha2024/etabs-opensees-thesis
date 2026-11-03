# runner_and_gui.py — source module guide

**Code:** [`components/nonlinear_time_history/runner_and_gui.py`](../../../components/nonlinear_time_history/runner_and_gui.py)  
**Baseline blob:** `40e4ea93ec8f3c9a1778a9bfd639de9dcc802236`  
**Role:** Nonlinear time-history and research calibration  
**Review priority:** P0; documentation is NOT a native solver test.

## Responsibilities
This file is part of the nonlinear_time_history subsystem. Verify actual callable functions and imported dependencies in the linked source before refactoring. Do not infer an API solely from the module name.

## Engineering input checks
Check accepted versus failed steps, constitutive calibration and full-record case status. Record input file SHA256, SI base-unit system (kN–m–s for OpenSees), material/reference grade, source ETABS export and expected model configuration.

## Output and failure checks
Record full output path, model/record/orientation/ULS-SLS identifiers, solver version, accepted analysis duration, complete logs, nonfinite response checks and independent benchmark comparisons. Distinguish nominal inputs from calibrated experiment values.

## Source and validation references
R01 R02 R03 R04 R12 R13. The IDs are registered in [00_RESEARCH_REFERENCES.md](../../00_RESEARCH_REFERENCES.md). These are relevant research directions and not proof that the file's numerical model is validated.

## Done criteria
Document required parameters and default units in implementation docstrings, add deterministic tests and explicit errors, then perform applicable OpenSeesPy benchmark, gravity/modal or complete NLTHA regression. A smoke test must not imply experimental or design approval.

[Source index](../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../00_THESIS_ACCEPTANCE_GATES.md)

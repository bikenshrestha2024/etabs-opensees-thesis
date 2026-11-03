# gui_and_reports.py — source module guide

**Code:** [`components/gravity/gui_and_reports.py`](../../../components/gravity/gui_and_reports.py)  
**Baseline blob:** `05de2fb0d5a91641fb4ea9ddb5ef7e0edb45d4b3`  
**Role:** Gravity equilibrium and load paths  
**Review priority:** P1; documentation is NOT a native solver test.

## Responsibilities
This file is part of the gravity subsystem. Verify actual callable functions and imported dependencies in the linked source before refactoring. Do not infer an API solely from the module name.

## Engineering input checks
Compare applied forces/reactions, source DL/LL patterns, diaphragm constraints and units. Record input file SHA256, SI base-unit system (kN–m–s for OpenSees), material/reference grade, source ETABS export and expected model configuration.

## Output and failure checks
Record full output path, model/record/orientation/ULS-SLS identifiers, solver version, accepted analysis duration, complete logs, nonfinite response checks and independent benchmark comparisons. Distinguish nominal inputs from calibrated experiment values.

## Source and validation references
Refer only to applicable source in register. The IDs are registered in [00_RESEARCH_REFERENCES.md](../../00_RESEARCH_REFERENCES.md). These are relevant research directions and not proof that the file's numerical model is validated.

## Done criteria
Document required parameters and default units in implementation docstrings, add deterministic tests and explicit errors, then perform applicable OpenSeesPy benchmark, gravity/modal or complete NLTHA regression. A smoke test must not imply experimental or design approval.

[Source index](../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../00_THESIS_ACCEPTANCE_GATES.md)

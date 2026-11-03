# legacy_solver_stack.py — source module guide

**Code:** [`components/shared/legacy_solver_stack.py`](../../../components/shared/legacy_solver_stack.py)  
**Baseline blob:** `43e3cd43ef19bb5c108ac2608934cd427dabbbea`  
**Role:** Solver and response utilities  
**Review priority:** P1; documentation is NOT a native solver test.

## Responsibilities
This file is part of the shared subsystem. Verify actual callable functions and imported dependencies in the linked source before refactoring. Do not infer an API solely from the module name.

## Engineering input checks
Check deterministic finite-value guards, exceptions, resource management and recorded solver metadata. Record input file SHA256, SI base-unit system (kN–m–s for OpenSees), material/reference grade, source ETABS export and expected model configuration.

## Output and failure checks
Record full output path, model/record/orientation/ULS-SLS identifiers, solver version, accepted analysis duration, complete logs, nonfinite response checks and independent benchmark comparisons. Distinguish nominal inputs from calibrated experiment values.

## Source and validation references
Refer only to applicable source in register. The IDs are registered in [00_RESEARCH_REFERENCES.md](../../00_RESEARCH_REFERENCES.md). These are relevant research directions and not proof that the file's numerical model is validated.

## Done criteria
Document required parameters and default units in implementation docstrings, add deterministic tests and explicit errors, then perform applicable OpenSeesPy benchmark, gravity/modal or complete NLTHA regression. A smoke test must not imply experimental or design approval.

[Source index](../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../00_THESIS_ACCEPTANCE_GATES.md)

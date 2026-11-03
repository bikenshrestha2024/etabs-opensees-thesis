# nonlinear_preflight.py — source module guide

**Code:** [`components/model/nonlinear_preflight.py`](../../../components/model/nonlinear_preflight.py)  
**Baseline blob:** `f85fb118d4faccc49669a4d0598a0e1aeabf3f81`  
**Role:** ETABS model assembly and source reconciliation  
**Review priority:** P1; documentation is NOT a native solver test.

## Responsibilities
This file is part of the model subsystem. Verify actual callable functions and imported dependencies in the linked source before refactoring. Do not infer an API solely from the module name.

## Engineering input checks
Check 3D nodes/elements, 6 DOFs, source material, shell orientation, rebar, loads and gravity. Record input file SHA256, SI base-unit system (kN–m–s for OpenSees), material/reference grade, source ETABS export and expected model configuration.

## Output and failure checks
Record full output path, model/record/orientation/ULS-SLS identifiers, solver version, accepted analysis duration, complete logs, nonfinite response checks and independent benchmark comparisons. Distinguish nominal inputs from calibrated experiment values.

## Source and validation references
Refer only to applicable source in register. The IDs are registered in [00_RESEARCH_REFERENCES.md](../../00_RESEARCH_REFERENCES.md). These are relevant research directions and not proof that the file's numerical model is validated.

## Done criteria
Document required parameters and default units in implementation docstrings, add deterministic tests and explicit errors, then perform applicable OpenSeesPy benchmark, gravity/modal or complete NLTHA regression. A smoke test must not imply experimental or design approval.

[Source index](../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../00_THESIS_ACCEPTANCE_GATES.md)

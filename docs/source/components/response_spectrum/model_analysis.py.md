# model_analysis.py — source module guide

**Code:** [`components/response_spectrum/model_analysis.py`](../../../components/response_spectrum/model_analysis.py)  
**Baseline blob:** `03da0dd6173126200f166bfaf2d7023a25bd556f`  
**Role:** NBC105 modal response-spectrum analysis  
**Review priority:** P1; documentation is NOT a native solver test.

## Responsibilities
This file is part of the response_spectrum subsystem. Verify actual callable functions and imported dependencies in the linked source before refactoring. Do not infer an API solely from the module name.

## Engineering input checks
Check effective modal mass, base-shear scaling, response combination and offsets. Record input file SHA256, SI base-unit system (kN–m–s for OpenSees), material/reference grade, source ETABS export and expected model configuration.

## Output and failure checks
Record full output path, model/record/orientation/ULS-SLS identifiers, solver version, accepted analysis duration, complete logs, nonfinite response checks and independent benchmark comparisons. Distinguish nominal inputs from calibrated experiment values.

## Source and validation references
R10. The IDs are registered in [00_RESEARCH_REFERENCES.md](../../00_RESEARCH_REFERENCES.md). These are relevant research directions and not proof that the file's numerical model is validated.

## Done criteria
Document required parameters and default units in implementation docstrings, add deterministic tests and explicit errors, then perform applicable OpenSeesPy benchmark, gravity/modal or complete NLTHA regression. A smoke test must not imply experimental or design approval.

[Source index](../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../00_THESIS_ACCEPTANCE_GATES.md)

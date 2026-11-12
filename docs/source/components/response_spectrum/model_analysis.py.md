# model_analysis.py — source documentation

**Python source:** [components/response_spectrum/model_analysis.py](../../../../components/response_spectrum/model_analysis.py)
**Git baseline content SHA:** 03da0dd6173126200f166bfaf2d7023a25bd556f
**Subsystem:** Modal response spectrum and NBC scaling
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the response_spectrum implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-12 visible run and export workflow

The existing per-case `CaseLedger` remains authoritative. A top-level status field and indeterminate bar now report **READY / RUNNING / EXPORTING / EXPORTED / COMPLETED / FAILED / REVIEW REQUIRED** and on reopen show the stored `MRSM_Batch_Status_V151.json` completion count. Each stage status is written through the Tk UI thread. Numerical completion is not NBC design acceptance. Preserve model source state, six-case X/Y E0/Eplus/Eminus output, 76-source-supported production baseline pending original six-DOF restraint review, and full selected-model hash in ZIP.

# building_exploratory.py — Research full-building nonlinear runner

**Python source:** [components/nonlinear_time_history/building_exploratory.py](../../../../components/nonlinear_time_history/building_exploratory.py)
**Current Git blob SHA:** 7c7141c691ac44906b60837b4b2d95876f6121a7
**Review status:** Source content was inspected for these specific behaviors. Physical/numerical validation not executed.

## What this file currently implements
Copies source export to isolated_model, reads paired PEER histories, creates ULS/SLS cases and fresh XY/YX models, performs gravity preload and initial modal analysis, applies UniformExcitation, records accepted transient histories and separate failure evidence.

## Explicit assumptions and known deficiencies
Materials are explicitly research assumptions. It supports ZERO, X, Y, XY first-step diagnostics, optional Rayleigh overrides and UmfPack/SparseGeneral. A completed 0.005 s trial must be distinguished from full record; post-failure element localForce can be contaminated. Status COMPLETED_EXPLORATORY_RECORD is not accepted by the separate performance assessor as COMPLETED_FULL_RECORD.

## Required thesis engineering changes
Require identical model and record hash for each orientation; record first accepted state, dt sensitivity, solver retry changes, complete earthquake duration and finite response. Verify wall/beam/column plastic states and device outputs. Fix X-only AREA:354/482 diagnostics before M0-M6 ranking.

## Cited scientific context
R01, R02, R03, R10, R12, R13.
References are indexed in [the research source register](../../../00_RESEARCH_REFERENCES.md). Paper citations establish appropriate model context, not code validation.

## Required regression output
Unit/metadata tests, isolated material or wall benchmarks, complete solver log, model+record hashes, type-safe status, full-record duration and independent ETABS/experiment comparison. Avoid marking a case verified if any gate remains unresolved.

[Source module index](../../00_SOURCE_GUIDE_INDEX.md) · [G00–G10 acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md)


## Accepted-state early failure and source provenance (2026-11-04)

During every accepted nonlinear step, `capture` validates each recorded numeric channel with `verify_numeric_accepted_row` before appending response rows. The full-duration history gate then checks timestamps, schema stability, provenance and completeness. A malformed/nonfinite row now stops a diagnostic immediately instead of being stored as a valid nonlinear result. The 0.005s X-only wall failure remains an independent native-model issue.

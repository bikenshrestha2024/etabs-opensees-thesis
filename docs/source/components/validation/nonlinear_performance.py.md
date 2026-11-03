# nonlinear_performance.py — Performance criteria and full-suite acceptance checks

**Python source:** [components/validation/nonlinear_performance.py](../../../../components/validation/nonlinear_performance.py)
**Current Git blob SHA:** 090fb77953dbcadf717e2663338df2a4522c498f
**Review status:** Source content was inspected for these specific behaviors. Physical/numerical validation not executed.

## What this file currently implements
Defines NBC-based edge drift templates, demands keyed by ground-motion pair/orientation and expected model SHA, reviewer-controlled member/device acceptance limits and suite aggregation.

## Explicit assumptions and known deficiencies
Requires status COMPLETED_FULL_RECORD; exploratory runner produces COMPLETED_EXPLORATORY_RECORD. This is a deliberate evidence-tier mismatch requiring a reviewed evidence-promotion workflow, not a string replacement. The supplied NBC105:2025 code places drift values in clause 5.5.3 while 9.3.3.1 references 5.6.

## Required thesis engineering changes
Keep thresholds, hazard level, positive limiting strength/deformation, acceptance class and citation transparent. Test exact-7-record behavior separately before deciding code interpretation. Reject incomplete histories, missing pair orientations and sources with mismatching SHA/units.

## Cited scientific context
R10; compare ASCE41/LATBSDC member criteria only when actual project acceptance basis is selected.
References are indexed in [the research source register](../../../00_RESEARCH_REFERENCES.md). Paper citations establish appropriate model context, not code validation.

## Required regression output
Unit/metadata tests, isolated material or wall benchmarks, complete solver log, model+record hashes, type-safe status, full-record duration and independent ETABS/experiment comparison. Avoid marking a case verified if any gate remains unresolved.

[Source module index](../../00_SOURCE_GUIDE_INDEX.md) · [G00–G10 acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md)

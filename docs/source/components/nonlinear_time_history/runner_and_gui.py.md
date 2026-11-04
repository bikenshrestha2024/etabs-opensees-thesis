# runner_and_gui.py — Production-oriented paired nonlinear history workflow

**Python source:** [components/nonlinear_time_history/runner_and_gui.py](../../../../components/nonlinear_time_history/runner_and_gui.py)
**Current Git blob SHA:** 514247faae41e5fe70b53441a4bb3c0954f47b30
**Review status:** Source content was inspected for these specific behaviors. Physical/numerical validation not executed.

## What this file currently implements
Contains a separate, execution-off-by-default nonlinear case runner, input-record audit, readiness gate, adaptive nonlinear interval stepping, per-case output and GUI orchestration.

## Explicit assumptions and known deficiencies
Unlike exploratory runner, this route requests reviewed nonlinear material and model readiness. It must not be silently replaced with the exploratory model simply because the latter starts or fails differently.

## Required thesis engineering changes
Align typed case status and output schema with performance assessor; validate earthquake pair orientation and scale factors, energy/damping handling, exception capture, subprocess cancellation and output completion. Provide a research-run manifest with model, record and solver hashes.

## Cited scientific context
R01, R02, R05, R10 and documented OpenSees integration algorithms.
References are indexed in [the research source register](../../../00_RESEARCH_REFERENCES.md). Paper citations establish appropriate model context, not code validation.

## Required regression output
Unit/metadata tests, isolated material or wall benchmarks, complete solver log, model+record hashes, type-safe status, full-record duration and independent ETABS/experiment comparison. Avoid marking a case verified if any gate remains unresolved.

[Source module index](../../00_SOURCE_GUIDE_INDEX.md) · [G00–G10 acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md)


## Nonfinite accepted-step safety (2026-11-04)

`record_accepted` calls `full_record_gate.verify_numeric_accepted_row` before `HistoryStream.append`. This guards against generating a supposedly successful history with `NaN`, infinite or missing numeric response channels even when OpenSees returns 0. This is a **recorder** check, not proof that every constitutive integration point is finite or calibrated. CI covers the utility and compiles this module; native transient is still required.

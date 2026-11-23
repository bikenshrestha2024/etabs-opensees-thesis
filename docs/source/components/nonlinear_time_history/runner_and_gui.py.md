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


## 2026-11-22: original RC assessment reference / accepted-step wall safeguards

Original upstream reference: `nirajkyadav/Framework_for_Seismic_Assessment_of_RC_Buildings`, MIT; see the dated `REVIEW_MAIN/04_NONLINEAR/FORK_RC_ASSESSMENT_20261117/SOURCE_REVIEW.md` adoption/exclusion table. This module is the active shared nonlinear interval owner; the exploratory runner imports the same function through its existing compatibility launcher.

`_advance_nonlinear_interval` now obtains solver time before each algorithm attempt, checks the actual successful increment via `verify_committed_transient_increment`, and updates `accepted_steps`, `minimum_accepted_dt_s`, `first_accepted_step` and `last_accepted_time_s` **after** the callback verifies and records finite responses. Failed algorithms preserve the source first-failure evidence and may fall back only if the rejected time state has **not** advanced. The algorithm sequence and Newmark values, gravity/P-Delta source, 32 physical supports, 44 shell-mesh transfer points, NBC mass, damping, scaled input motions and adaptive subdivision depth are unchanged.

When `diagnostic_first_step_wall=true`, `record_accepted` saves the first focused element/node snapshot and chronology report before writing any accepted history row. `require_accepted_focused_step` rejects nonfinite wall responses or missing requested solver tags, rather than recording an apparent success. For diagnostic-only watched tag `110280`, use a **matching live** `OpenSees_Complete_Element_Map_V118.json`; a historical X-wall tag is not assumed valid across versions.

This is a headless software regression and an **incomplete physical verification**. Require native zero, X, Y, XY, YX first-step controls, independent wall material and coupling-beam patch tests, and full-duration XY/YX runs before claiming solved M0–M6 or NBC §9.3 compliance.

## 2026-11-23 — builder-change readiness selection safety

The NLTHA GUI now synchronizes the readiness selection when the selected nonlinear builder changes. It verifies the candidate V134 draft or legacy V116 manifest against the new model path and script SHA, clears the former model's selected file if neither matches and logs the selected source. An unchanged builder does not disturb a manually chosen readiness file. The source-bound readiness gate remains fail-closed; human review flags and the original source model are not changed. Headless synthetic coverage: `tests/test_readiness_model_selection_20261123.py`.

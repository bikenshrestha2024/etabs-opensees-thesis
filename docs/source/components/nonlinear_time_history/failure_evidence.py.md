# failure_evidence.py — source documentation

**Python source:** [components/nonlinear_time_history/failure_evidence.py](../../../../components/nonlinear_time_history/failure_evidence.py)
**Git baseline content SHA:** 18d17aed1b307d8fa50085772cc961236bf0d61a
**Subsystem:** Nonlinear transient model and research constitutive laws
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the nonlinear_time_history implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R01 R02 R03 R04 R05 R06. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)

## V26 — preserve catastrophic first-step evidence (2026-11-15)

`snapshot_selected_state()` and `snapshot_failed_step()` now record nonfinite solver clocks without putting non-JSON numeric `NaN` or `Infinity` into the report. The legacy `time_s`/`analysis_time_s` remains a finite numeric when available and is `null` when nonfinite; the new `time_status`/`analysis_time_status` explicitly says `NONFINITE_NAN` or `NONFINITE_INFINITY`. A failed step's nonfinite clock therefore does **not** erase the diagnostic. The source and failure report JSON is written using the existing atomic run-output writer, avoiding partial replacement of the saved failure state.

A malformed, absent, symlinked, or duplicate-conflicting `element_map_path` now produces `element_map_status=INVALID_SOURCE_MAPPING` and a nonempty `element_map_error` while leaving the observed nonfinite element response captured. Such a report has no trusted source area mapping and **must not** infer the initiating wall/material failure. The accepted committed-state snapshot still must be captured **before** attempting a failed nonlinear step, preferably in a separate artifact; this code cannot reconstruct it afterward. `maximum_findings`/`max_values` bounds reject invalid or unreasonably large settings. Failed post-step data remain potentially contaminated.

Tests: `tests/verify_failure_evidence.py`; added to NLTHA Python quality workflow invocation. The test uses synthetic FakeOps and is not a reproduced 25-storey E-SFI solver failure.

**Native engineering reproduction remains open:** original affected element tag (historically 110280), exact source mesh SHA and wall/quad mapping, P-Delta/gravity preload state, ConcreteCM/SteelMPF/FSAM parameters, actual first accepted step/time and log traceback, isolated zero/X/Y/XY tests, connected-bay interface actions, and independent material calibration. Do not treat this recording fix as proof of root-cause resolution.

## Recovery guard scope
The shared nonlinear interval recovery caller sets `scan_all=True` even when `suspect_tags` is supplied. Selected live tags are queried first for evidence, but all live element tags and nodal displacement responses are screened before retry. Missing focused tags are reported. Standalone focused snapshots retain their narrower semantics. Unsupported/error responses are not proof of finite material states; this is a bounded numerical screen, not native constitutive validation.

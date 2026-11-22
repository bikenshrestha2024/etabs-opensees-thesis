# full_record_gate.py — implementation guide

**Source:** [components/nonlinear_time_history/full_record_gate.py](../../../../components/nonlinear_time_history/full_record_gate.py)
**Source blob SHA:** 32594f1c60b01be293008172ab63ad7e2d6800d2
**Workstream:** 05 full record evidence.

## Input contract and failure gate

Use the module's exact function docstrings and the corresponding stage guide under docs/programs. All data are kN-m-s model units unless source quantities explicitly say mm, MPa or g. Nonfinite, missing, mismatched or unapproved inputs must block the relevant analysis rather than be interpreted as zero.

## Provenance and cited method

NBC 105:2025 is governing seismic basis (DUDBC). Wall model formulation: Kolozvari et al. (2023), https://doi.org/10.1016/j.engstruct.2023.116700. Research device context: Korkmaz & Kircil (2026), https://doi.org/10.3390/buildings16040711. Only cite the relevant physical domain: these papers do not validate this specific building.

## Verification

Unit test: tests/verify_full_record_gate.py. This is a solver-free input/response behavior check. A successful test cannot establish true nonlinear wall convergence, experimental calibration, structural performance or device approval. Native OpenSeesPy and source ETABS comparisons must still be run.

[Guide index](../../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../00_THESIS_ACCEPTANCE_GATES.md)


## Accepted-state falsifiability improvement (2026-11-04)

`verify_numeric_accepted_row` now raises on nonfinite/missing or textual response channels **before** either NLTHA runner writes an accepted row to CSV. `verify_accepted_history` rejects inconsistent channel schemas across time samples. A solver's successful return code does not certify finite responses. `compare_time_step_results` requires genuine 64-character input fingerprints and accepted-step evidence before comparing response metrics; full-duration source hashes and smaller fine time steps are necessary but not experimental validation.

[Error register](../../../review/02_SOFTWARE_ERROR_REMEDIATION.md).


## 2026-11-22: positive solver return is not sufficient for clock acceptance

`verify_committed_transient_increment(start_time_s, end_time_s, requested_dt_s)` is a **pure, solver-free** time-increment contract, called by the existing shared nonlinear transient recovery after `ops.analyze(1, dt)==0` and before any accepted recorder callback. All inputs are seconds, finite and `dt > 0`. It requires strictly increasing native time and a matching increment with tight bounded roundoff tolerance. A false `rc=0`, stagnant clock, overshoot, NaN/Inf or wrong requested substep fails the analysis without fabricating a completed history. Returned `CLOCK_MATCHED_NOT_PHYSICS_VALIDATED` is a bookkeeping observation only, not an RC wall convergence result.

Both production `runner_and_gui.py` and exploratory `building_exploratory.py` invoke this same step contract through the shared `_advance_nonlinear_interval`. First accepted and minimum `dt` diagnostics are updated only after the application callback succeeds. A rejected step that advances the native clock aborts instead of reusing a potentially corrupted trial state; the failure-snapshot path is unchanged. Regression: `tests/test_nltha_step_clock_contract_20261122.py`. Relevant methodological contrast: the external Niraj Yadav RC assessment repository uses a similar Newton fallback workflow but hardcoded retry intervals are not carried into the thesis.

# V24 — full-duration nonlinear M0–M6 evidence gate
**Date:** 2026-11-15
**Initial main SHA:** `68f9b5a959965d4b761a525781a0e694b77d2623`
**Classification:** partial semantic review and executable regression; **NOT FULL-DURATION NATIVE NLTHA**

## Confirmed inconsistency

V23 improved `tools/audit_soil_c_case_completion.py` to require explicit durations, valid SHA-256 strings and accepted states for the 224-case Soil-C record matrix. However `components/nonlinear_time_history/variant_comparison.py::compare_completed_cases` still accepted a completion-status string/boolean *without measured duration*, and accepted any nonempty record hash, causing two physically different acceptance paths for the same M0–M6 summaries. A string `"true"` was also treated as a completed boolean. The matrix scanner could coerce fractional/text state counts via `int(...)`.

## Corrective changes

- M0–M6 manifest requires 64 hexadecimal character model-export SHA-256; input orientation case requires 64 hexadecimal ground-motion SHA-256.
- Each `completion_gate` must have literal JSON `true` for completion, `FULL_DURATION_NUMERIC_SCREEN` and `accepted_channels_finite=true`, finite positive source/requested/achieved duration in seconds matching within `1e-7` s and at least two accepted states recorded as a literal integer (not string, float or boolean).
- Negative/nonfinite/non-numeric response metrics are rejected with a controlled error before pooling.
- The separate 224-case inspector now refuses fractional, text or boolean `accepted_states` without `int()` truncation.
- Regression tests added/updated in `tests/verify_variant_comparison.py` and `tests/verify_soil_c_case_completion.py`.
- A prior guide incorrectly said 14 orientations for 8 pairs; corrected to **16 XY/YX orientation histories per limit state, variant and 8-event suite**.

These checks verify the **metadata contract**; an analyst must still independently hash actual paired waveform/model bytes and confirm the raw accepted-history trace has all of the finite states claimed in metadata. A full-duration numerical screen does not calibrate E-SFI wall materials, FVD constitutive behavior, outrigger connections or prove seismic code compliance.

## Native acceptance workflow and output folder

Use the existing `tools/run_native_wall_probes.py` separate zero/X/Y/XY research probes and source SHA checks to investigate the first-step X-wall element-110280 localForce symptom at ~0.005 s, without changing materials/supports merely to obtain convergence. After independently verified geometry, wall orientation, gravity preload, material state, source EDB reinforcement and base restraints, run the full 7 variants × 2 ULS/SLS states × 8 paired Soil C records × XY/YX = **224 orientation cases**.

Persist fresh cases under:
```text
<LOCAL_EXPORT>/07_NONLINEAR_TIME_HISTORY/RUNS/<STATE>/<VARIANT_EVENT_ORIENTATION>/<UTC_RUN>/
  00_INPUT_SOURCE/    CASE_MANIFEST.json, raw-record hashes, model/material/device source
  01_LOGS/            solver, failures, state count, convergence/iterations
  02_RESULTS/         complete accepted trace, response metrics, device forces
  03_EXCEL/           summary tables
  04_FIGURES/         roof/shear/drift/torsion histories
  05_COMPARISONS/     M0–M6 and time-step sensitivity
  06_REVIEW/          failure audit and explicit human acceptance
  07_EXPORT_ZIP/      reproducible review bundle with manifest
```
This is the canonical **target contract**; existing legacy writers/readers are not all migrated, so no historical output is renamed or destroyed by this review.

**Acceptance:** `SYNTHETIC_COMPLETION_GATES_CORRECTED_NATIVE_224_CASE_ANALYSES_UNVERIFIED`.

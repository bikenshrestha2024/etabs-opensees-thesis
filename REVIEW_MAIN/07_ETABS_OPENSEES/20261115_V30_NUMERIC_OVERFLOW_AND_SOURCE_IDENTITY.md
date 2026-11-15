# V30 — finite inputs, overflowing engineering results, and source byte identity

Date: 2026-11-15. Base main SHA: `32bfc5956b6c358d32c3d1cfb87ccb63fe30fdae`.
Status: `SOFTWARE_NUMERIC_INTEGRITY_HARDENED_NATIVE_ETABS_EQUIVALENCE_OPEN`.

## Inspected active functions and defects

1. `components/validation/design_checks.py::combine_actions()` validated six signed first-order basis components as finite, then formed weighted superpositions without validating the **calculated six components**. A coefficient multiplying a finite very large input can overflow to Inf and leak into `Combined_actions.csv` or JSON. V30 now produces a case/member/station `NOT EVALUATED` issue for nonfinite combined actions; no valid combined record is fabricated.
2. `evaluate_checks()` validated demand and limit separately but did not check the computed `utilization=demand/limit`. Finite operands can produce Inf, and the rejected value itself must never remain in the generated report (JSON with allow_nan=False fails). V30 checks the ratio, resets invalid utilization to null, and records `NOT EVALUATED` with an explicit numerical reason.
3. `scan_drift()` had a parallel issue in saved CSV and MRSM JSON drift ratio derivation, where finite 1e308 drift ratios divided by 0.025/0.006 can overflow. V30 rejects the affected entire input file from review plots and records a nonfinite calculation issue.
4. `run()` previously hashed the authoritative serialized model using one file read but parsed it using a separate file read. The source could change between reads, creating a misattributed model fingerprint. V30 hashes and parses **the same immutable Python byte string**; invalid top-level JSON types fail before report generation.
5. `run()::input_rows()` previously followed linked V135 editable criteria CSV sources. V30 rejects linked canonical or historical criteria input files rather than silently adopting external changes as authoritative project checks.

## Engineering bounds

No adopted NBC 105:2025 combination factors, drift limits, source model geometry, support restraints, stiffness, ETABS Excel Aw/T1, ground motion, reinforcement or nonlinear material parameters were changed. This correction concerns error detection and trustworthy recorded numerics, not changing seismic design equations. `NOT EVALUATED` for a numeric overflow must not be mistaken for a passing result.

## Reproduction and tests

`tests/test_v135_drift_source_completion_v13.py` adds synthetic regression scenarios:
- finite demand 1e308 and finite limit 1e-308 resulting in invalid utilization;
- finite six-component basis superposed with factor 2 resulting in overflow;
- finite but extreme CSV and MRSM drift ratios yielding nonfinite computed utilization and exclusion from accepted rows;
- symlinked user-editable criteria source is refused with original target bytes unchanged.

Existing V29 writer/output-index/XLSX and source fingerprint tests remain in the same suite. All tests are synthetic Python/filesystem tests, **not** ETABS, OpenSees/XARA, actual NBC capacity or nonlinear source-model verification.

## Structured evidence location

`REVIEW_MAIN/07_ETABS_OPENSEES/`: this engineering/numerical review.
`docs/review/ledger/`: inspected source blob identities and line ranges.
`engineering/agent_edits/`: source-editor attribution.
Local case outputs stay under `<SELECTED_EXPORT>/09_SOFTWARE_DIAGNOSTICS/DESIGN_CHECKS_V135` with `Design_Check_Output_Index_V135.json`, report JSON, Excel, log and per-table CSV; do not treat a stale CSV whose index reports `NO_CURRENT_ROWS_PRIOR_CSV_NOT_REPLACED` as current result evidence.

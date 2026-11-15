# V29 — Derived report output migration and seven-gate audit

Date: 2026-11-15. Main baseline: `9bc2aa1a9bede8dc8932d6b12ea0660e9b20043e`.
Scope is targeted semantic inspection of selected active modules and callers, not all **3,002 Git-tracked baseline blobs**.

## Verified code-level findings and corrections

1. `saved_case_identity.py`: linked response and ESM sidecar paths, malformed explicit model SHA, and linked serialized model fingerprint are now separately flagged/excluded rather than silently treated as source matches.
2. `design_checks.py::write_rows()`: replaced direct derived V135 CSV writes with the existing `components.inputs.output_contract.write_table` staged writer. Invalid nonfinite numeric rows no longer truncate an existing report. Filenames and CSV columns remain those previously emitted; empty-row no-write behavior remains for compatibility (a still-open stale-output migration risk).
3. `design_checks.py::run()`: replaces `Design_Check_Report_V135.xlsx` only after the newly generated workbook is successfully saved as a same-directory staged XLSX and passes linked-output checks. Workbook content/formatting is unchanged, and staged files are cleaned.
4. `design_checks.py::templates()`: validates the output chain to prevent criteria templates being written via linked diagnostics directories or linked direct files. Exclusive creation protects concurrently created input criteria from truncation; historical user-edited criteria remain intact.
5. `design_checks.py::run()`: rejects a linked `OpenSees_Complete_Model_Data_V118.json` source file before reporting any canonical source match.

Regressions: `tests/test_saved_case_identity_v142.py`, `tests/test_post_v8_missing_coverage_v9.py`, and `tests/test_v135_drift_source_completion_v13.py`. A prior CI run correctly failed on an obsolete historical fixture that expected malformed SHA to be reported merely `NOT_VERIFIED`. The fixture was updated to require exclusion, with absent SHA separately remaining `NOT_VERIFIED`. A passed CI source revision must be recorded from GitHub Actions; never call it native ETABS/OpenSees validation.

## Seven requirements — status

| Requirement | Contribution in V29 | Gate |
|---|---|---|
| Complete semantic inspection | Reviewed specific reader/writer functions and regression consumers; exact Git blobs recorded | **OPEN** |
| Legacy writer/reader migration | One additional derived CSV producer and V135 XLSX writer migrated safely | **OPEN**, other producers/consumers unconverted |
| Native Windows GUI regression | No interactive desktop test; headless Windows verification remains separate | **OPEN** |
| X-wall first-step instability | No constitutive/numerical parameters changed | **OPEN** |
| 32/76/97 physical support equivalence | No physical restraints changed | **OPEN** |
| ETABS–OpenSees numerical equivalence | Source evidence checks hardened | **OPEN** |
| Full-duration NLTHA sensitivity | No real native full-duration 224 run matrix executed | **OPEN** |

## Folder ownership and output organization

- `REVIEW_MAIN/07_ETABS_OPENSEES`: saved case provenance and numerical equivalence evidence.
- `REVIEW_MAIN/08_SOFTWARE_SECURITY`: cross-module output migration and seven-gate status.
- `docs/review/ledger`: exact source content blob and inspected line intervals.
- `engineering/agent_edits`: actual editor and touched paths.
- Private ETABS export remains the **only canonical ownership root** for stage outputs: `02_GRAVITY,03_ESM,04_MODAL,05_MRSM,06_LINEAR_TIME_HISTORY,07_NONLINEAR_TIME_HISTORY,08_ETABS_COMPARISONS,09_SOFTWARE_DIAGNOSTICS,90_UPLOAD_PACKAGES`; history and model source files stay unchanged.
- New case staging: `<STAGE>/RUNS/<STATE>/<CASE>/<RUN_ID>/{00_INPUT_SOURCE,01_LOGS,02_RESULTS,03_EXCEL,04_FIGURES,05_COMPARISONS,06_REVIEW,07_EXPORT_ZIP}` and `CASE_MANIFEST.json`.

## Remaining high-priority observed migration risks

- V135 continues to preserve existing CSV output when a stage has zero rows; a previously generated CSV could remain stale. A per-run immutable publisher and reader transition with explicit `NO_CURRENT_ROWS` status is required before changing this behavior.
- The V135 text log and some legacy producers are not yet using staged writes; multiple related output files are not one atomic transaction.
- The result-identity gate does not independently verify raw payload content, structural response or physical numerical equivalence.
- Symlink path checks are normal filesystem guards, not an OS-level TOCTOU race-proof security boundary.

## Post-review V29 output-index amendment (current revision)

The V135 output generator now writes `Design_Check_Output_Index_V135.json` in its existing `09_SOFTWARE_DIAGNOSTICS/DESIGN_CHECKS_V135` report directory. Every table receives a `current_row_count` and a precise `CURRENT_DERIVED_TABLE` or `NO_CURRENT_ROWS_PRIOR_CSV_NOT_REPLACED` status. This avoids silently presenting an old same-name CSV as a fresh result, without deleting historical data or breaking readers. The index carries the exact selected serialized model SHA and explicit `DERIVED_SOFTWARE_REPORT_NOT_ENGINEERING_ACCEPTANCE` scope; it is **not** a case completion certificate.

The generated `Design_Check_V135.log` is also now published through same-directory staged atomic replacement, with temp cleanup. The first log implementation incorrectly used an escaped newline literal and failed CI; it was fixed with normal `\n` escapes and retested. The report remains a **multi-file nontransactional** collection; a successful index cannot by itself prove all related outputs were created in one atomic snapshot. Regressions: `tests/test_v135_drift_source_completion_v13.py`; no original source file was changed.

Recommended user upload package: generated `Design_Check_Output_Index_V135.json`, `Design_Check_Report_V135.json`, `Design_Check_Report_V135.xlsx`, `Design_Check_V135.log` and only the CSV files whose index status is `CURRENT_DERIVED_TABLE`; do not include stale CSVs as current analysis evidence.

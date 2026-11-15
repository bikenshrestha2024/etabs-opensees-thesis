# design_checks.py — source documentation

**Python source:** [components/validation/design_checks.py](../../../../components/validation/design_checks.py)
**Git baseline content SHA:** 4b274bf66f7fa1b04457f1ce61d2f6983a3def22
**Subsystem:** Code criteria, benchmark comparison and experimental evidence
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the validation implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R01 R04 R05 R10 R12 R13. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)

## V28 — completion and drift result evidence gates (2026-11-15)

`saved_drift_solver_status()` no longer trusts an isolated `solver_status` string from arbitrary JSON. It resolves a saved response to the closest canonical run and calls `inspect_case_manifest` for full folder, stage, state, case, run-ID, units, subfolder and source-hash grammar checks. Invalid canonical metadata yields `INVALID_RUN_MANIFEST` and numerical drift-limit PASS remains `NOT EVALUATED`; a valid `COMPLETED_SOLVER_ONLY` is a *software completion assertion*, not ETABS equivalence or seismic compliance. Missing historical manifest remains `NO_RUN_COMPLETION_MANIFEST`.

`scan_drift()` reads each CSV and MRSM JSON as a single all-or-nothing unit before appending saved result rows. A later NaN/Inf, missing state/field, malformed case or corrupted JSON rejects *all rows from that file* and records an issue; symlinked saved CSV/JSON source files are refused. Neither a partially parsed CSV nor an early case of a malformed MRSM result may silently contribute a PASS to the design-check table.

Regressions: `tests/test_v135_drift_source_completion_v13.py` (full canonical vs malformed manifest, mixed valid/invalid CSV/MRSM, and case/stage/run mismatch). CI path filtering now includes this test file for push changes.

## V29 — atomic derived report publishing and source protection (2026-11-15)

The existing `write_rows(path, rows)` preserves its data columns and no-op for genuinely empty rows but now publishes nonempty derived V135 CSV reports via shared `components.inputs.output_contract.write_table()`. Nonfinite source values or IO errors will not truncate the prior completed CSV. This does **not** mean that an empty current table removes/refreshes a historical CSV: stale same-name reports remain an open compatibility migration issue.

`run()` stages the V135 generated XLSX in a uniquely named file in the same report directory, validates the output destination against preexisting symlinks and atomically replaces the prior workbook only after `openpyxl` successfully saves it. Source model `OpenSees_Complete_Model_Data_V118.json` is refused when its direct path is linked. `templates()` also refuses linked destinations, and uses exclusive file creation for otherwise missing criteria templates rather than potentially truncating a concurrently created user-edited input.

The V135 multi-file CSV, XLSX, JSON and text-log set is **not one atomic transaction**. The workbook and derived CSV changes do not edit original Excel Aw/T1, ETABS EDB or historical imported source criteria. Tests: `tests/test_v135_drift_source_completion_v13.py`; verified non-native GitHub quality/compilation is **not** a model qualification or physical drift benchmark.

## V29 update — V135 current-output index and atomic diagnostic log

`run()` now writes `Design_Check_Output_Index_V135.json` with a model SHA, generation timestamp, each table's current row count, and `CURRENT_DERIVED_TABLE` versus `NO_CURRENT_ROWS_PRIOR_CSV_NOT_REPLACED` classifications. The previous legacy empty-row no-write behavior is preserved, but an old report must no longer be interpreted as belonging to the latest refresh when the index says no current rows. The output index is data provenance, **not** a real ETABS/OpenSees simulation result.

`Design_Check_V135.log` now uses a unique same-directory staged text file and atomic final replacement. This prevents a partially written log from truncating the prior completed log. The current workbook, JSON, CSV and log remain separately published rather than an atomic multi-file transaction. Regression: `tests/test_v135_drift_source_completion_v13.py`.

## V30 — finite *calculated* quantities and exact source bytes (2026-11-15)

`combine_actions()` now checks all **derived** signed action components after superposition, in addition to the existing finite-basis checks. A finite extreme source value multiplied by a finite combination factor can overflow to `inf`; such an action is omitted from `Combined actions` and recorded as `NOT EVALUATED` in the missing-basis/issues table, without inventing a finite force. `evaluate_checks()` now checks the calculated demand/limit ratio itself, clearing an overflowed utilization to `null` before JSON/CSV publication and marking the criterion `NOT EVALUATED`. Both saved CSV and MRSM JSON branches of `scan_drift()` similarly reject the **whole affected source file** when a derived drift utilization is nonfinite, even when raw ratio input fields are individually finite.

`run()` now hashes and parses the exact same bytes from `OpenSees_Complete_Model_Data_V118.json`, instead of separately reading it twice; top-level serialized model must be a JSON object. Its editable input criteria reader refuses a symbolic-linked canonical or legacy criteria CSV before treating it as the user's numerical design evidence.

Regressions: `tests/test_v135_drift_source_completion_v13.py`; evidence covers synthetic large finite values causing float overflow and linked original criteria preservation. These tests do not change accepted NBC 105:2025 factors or physical model parameters. Numerical overflow is not structural failure evidence, and a matching hash is not an ETABS/OpenSees native model acceptance result.


## 2026-11-15 — immutable current-run V135 CSV bundle

The derived V135 report writes all nine current tables into a uniquely named `09_SOFTWARE_DIAGNOSTICS/DESIGN_CHECKS_V135/RUNS/<run-id>/TABLES/` folder. **Zero-row results now have a header-only current CSV**, so an old same-name flat file cannot be mistaken for data from this run if the consumer follows the stable `Design_Check_Output_Index_V135.json` fields `current_run_manifest` and `tables[...].current_csv`. Legacy flat CSVs are still preserved for older readers and prior evidence, and the original V135 JSON/Excel/index paths and report status are not changed. Each new run owns its manifest and exact model SHA; a run whose outputs have not been fully written is not pointed to by the stable index. The regression test is `tests/test_v135_drift_source_completion_v13.py`. Do not call a combination `PASS` on the basis of a current CSV or a saved gravity response: approved signed elastic component actions and actual design criteria are needed.

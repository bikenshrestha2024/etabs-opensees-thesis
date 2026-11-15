# V24 — Seven-gate audit progress and source coverage boundary
**Date:** 2026-11-15
**Baseline head:** `68f9b5a959965d4b761a525781a0e694b77d2623`
**Scope:** explicitly inspected: repository engineering rules and active review register, recursive Git main tree and CI results, `components/validation/etabs_equivalence_report.py::evaluate`, `components/nonlinear_time_history/variant_comparison.py::validate_variant_manifest/compare_completed_cases`, `tools/audit_soil_c_case_completion.py::inspect_case`, and their unit tests and guides. Code inspection does **not** mean every other tracked file was reviewed.

## Seven workstreams

| Workstream | V24 progress | Actual status |
|---|---|---|
| Every file semantic review | Surveyed 2,982 tracked Git blobs at baseline, inspected **named functions only** and updated source guides; frozen per-file review remains authoritative | **OPEN** — semantic source/line-level inspection for all current files incomplete |
| Legacy writer/reader migration | Target stage hierarchy unchanged and documented; V22/V23 audits remain read-only | **OPEN** — full producers/readers/GUI/ZIP compatibility migration not performed |
| Native Windows GUI | Previous Windows 3.12 headless regression passed; not an interactive Tk/Spyder/OAPI run | **OPEN** — real GUI interaction untested |
| X-wall instability | Preserved native wall probe and qualification gates, did not suppress failed step | **OPEN** — first ~0.005 s source failure root cause not established |
| 32/76/97 supports | Existing evidence gates retained; none reinterpreted or mass fixed | **OPEN** — independently validated native support/DOF and six-component reaction comparison absent |
| ETABS–OpenSees numeric equivalence | Reject nonfinite/malformed OpenSees evidence, arithmetic overflow and malformed tolerance policy | **OPEN** — actual native source-by-source comparisons not run |
| Full-duration nonlinear sensitivity | M0–M6 completion gate now aligned to 224-case scanner; false truthy/malformed duration evidence blocked | **OPEN** — full calibrated native histories absent |

## Standard folders and review process

One selected local ETABS export case is the root. Within it use canonical stage folders `01_ETABS_EXPORT`, `02_MODEL`, `02_GRAVITY`, `03_ESM`, `04_MODAL`, `05_MRSM`, `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY`, `08_ETABS_COMPARISONS`, `09_SOFTWARE_DIAGNOSTICS`, `90_UPLOAD_PACKAGES` and `REVIEW_MAIN`. New migrated runs share `RUNS/STATE/CASE/RUN_ID` with eight `00_INPUT_SOURCE` through `07_EXPORT_ZIP` subdirectories. Do **not** claim every historical producer conforms. Keep `OpenSees_Analysis_Results` readable until old GUI readers and writers are migrated and individually regression tested.

Do not publish native original EDB, source workbook, private ground motions or local absolute-path reports into this public GitHub repository. Source code CI must be reported separately from independent native ETABS/OpenSees and project-calibrated NLTHA evidence. Avoid source modification to force a passing gate.

## Files changed (V24)

`components/validation/etabs_equivalence_report.py`, `tests/verify_etabs_direct_equivalence.py`, `components/nonlinear_time_history/variant_comparison.py`, `tests/verify_variant_comparison.py`, `tools/audit_soil_c_case_completion.py`, `tests/verify_soil_c_case_completion.py`, related `docs/source` guides and these dated review files. New workflows and source-register tests created in V23 are retained; this round does not falsely re-certify their original revision.

**Overall:** `TARGETED_SOURCE_DEFECTS_FIXED_AND_COMMITTED_NATIVE_ENGINEERING_GATES_OPEN`.

## V24 supplementary reader-migration and output validation (2026-11-15)

Additional targeted semantic inspection: `components/validation/case_review.py::collect` (lines 5–137 at current Git blob `825f651f5e1e9b8ebafab741bf48634ac79e8bd8`). Old code crashed an entire saved-result review when encountering invalid gravity profile JSON or malformed floor-edge CSV, and could emit NaN/Inf deformation responses. It now reports per-file `INVALID_GRAVITY_PROFILE`, `INVALID_FLOOR_EDGE_DRIFT` or `INVALID_DEFORMATION_RESULT`; rejects linked saved inputs; removes all partial rows from a damaged CSV while leaving other files untouched. Existing model-source identity filtering and `NO_SAVED_LATERAL_DEFLECTION` truthfulness remain active. Regression: `tests/test_case_review_canonical_output.py`, pass in GitHub `NLTHA Python quality checks` for commit `9ce5e3998a689d0dbe525bbebc00e2158d45ffc1`, run <https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43672387392>.

The existing `09_SOFTWARE_DIAGNOSTICS/CASE_REVIEW_V142` writer location remains deliberately compatible with old GUI readers. This is **one consumer hardening step** and does not constitute the full legacy writer/reader migration, numerical model matching or interactive Windows GUI validation. The semantic source line/blobs are appended to `docs/review/ledger/REVIEW_LEDGER_V24_20261115_TARGETED.csv`.

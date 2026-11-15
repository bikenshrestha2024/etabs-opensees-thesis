# case_review.py — source documentation

**Python source:** [components/validation/case_review.py](../../../../components/validation/case_review.py)
**Git baseline content SHA:** 9c79bfab9314cb33c03e42eb4a9ead3af78fba1c
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

## V24 saved-result reader fault isolation (2026-11-15)

`collect()` is a **read-only** consumer of both canonical stage result roots and archived `OpenSees_Analysis_Results`. Previously it could stop the entire review on malformed gravity-profile JSON or floor-edge displacement CSV, and it could admit nonfinite (NaN/Inf) deformation data to plotted evidence. Its new file-specific error statuses are `INVALID_GRAVITY_PROFILE`, `INVALID_FLOOR_EDGE_DRIFT`, `INVALID_DEFORMATION_RESULT`, plus `LINKED_*_REFUSED` for linked input files. A partly-read invalid floor-edge CSV contributes **no** deflection rows: valid rows from a broken CSV cannot be silently treated as a complete result. Other files may still be reviewed. The pre-existing `identity_screen()` remains responsible for excluding demonstrated model-SHA conflicts; missing SHA is still `NOT_VERIFIED`, not proof of ETABS/OpenSees compatibility. Regression: `tests/test_case_review_canonical_output.py`.

**Output path compatibility:** the `export()` review workbook still publishes the historical `09_SOFTWARE_DIAGNOSTICS/CASE_REVIEW_V142` folder expected by existing GUI consumers. Do not mass-move it without a writer+reader compatibility test. Its numerical plots are review-only and do not assert native solver completion or model equivalence.

## V24 legacy-compatible report publisher hardening

`export()` explicitly refuses symlinked `09_SOFTWARE_DIAGNOSTICS` or `CASE_REVIEW_V142` output directories, writes the XLSX to a unique same-folder temporary workbook and atomically replaces the previous workbook only after a successful save. The existing JSON artifact already uses `atomic_json()`. The user-visible filenames `All_Case_Review_V142.xlsx` and `All_Case_Review_V142.json` remain exactly where the GUI expects them, so no historical reader is silently broken. Test: `tests/test_case_review_canonical_output.py`. The pair of Excel/JSON files is not a single transactional bundle; callers should inspect both timestamps and identity for full reproducibility.

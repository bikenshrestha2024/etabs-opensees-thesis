# Uniform analysis-output contract — ETABS ↔ OpenSeesPy

**Source:** `components/inputs/output_contract.py`; central resolver `components/inputs/output_layout.py`. This is filesystem provenance and software UI policy, **not** NBC 105:2025 structural certification.

## Canonical stage ownership

All new stage tools should call `canonical_stage_folder(stage)` / `create_case_run(...)` instead of constructing stage names locally:

| Stage key | Folder |
|---|---|
| ETABS_EXPORT | `01_ETABS_EXPORT` |
| GRAVITY | `02_GRAVITY` |
| ESM | `03_ESM` |
| MODAL | `04_MODAL` |
| MRSM | `05_MRSM` |
| LTHA | `06_LINEAR_TIME_HISTORY` |
| NLTHA | `07_NONLINEAR_TIME_HISTORY` |

Auxiliary destinations remain distinct: `02_MODEL` (MESH_04/08/16 model assembly), `08_ETABS_COMPARISONS`, `09_SOFTWARE_DIAGNOSTICS`, `90_UPLOAD_PACKAGES`. The old `06_LINEAR_TH` and `07_NONLINEAR_TH` directories are **readable aliases**, never new production stage directories. `OpenSees_Analysis_Results` is retained for historical runs. No existing file has been moved.

## One consistent new case run

```text
<export>/<STAGE>/RUNS/<STATE>/<CASE_ID>/<UTC_TIMESTAMP_RANDOM>/
├── 00_INPUT_SOURCE/
│   └── CASE_MANIFEST.json
├── 01_LOGS/
├── 02_RESULTS/
├── 03_EXCEL/
├── 04_FIGURES/
├── 05_COMPARISONS/
├── 06_REVIEW/
└── 07_EXPORT_ZIP/
```

This layout is **available as a shared API**, not automatically applied to all historic/active stage runners. Each stage's writer+reader must be connected and Windows-tested before switching its production path. Never use folder existence alone as run-completion evidence.

## API contract

- `create_case_run(export_dir, stage, case_id, state='AS_CONFIGURED', model_sha256=None, source_edb_sha256=None, units='kN-m-s')` creates a **new** unique run only. Validates safe path components and the literal kN–m–s engineering unit basis. Hash fields are explicit, not inferred.
- `record_case_status(run_dir, 'RUNNING'|'COMPLETED_SOLVER_ONLY'|'FAILED'|'INTERRUPTED'|'INCOMPLETE')` updates the manifest without making any design-acceptance assertion. `VERIFIED_ETABS_EQUIVALENCE` cannot be set without a separate engineering-review field and is not self-certifying.
- `style_workbook(workbook)` applies common navy headers, white bold text, alternating row shading, fixed 30-point header height, freeze/filter and bounded column widths to a new generated Excel workbook, without modifying cell values. Applied to V142 review Excel; other module workbooks require individually verified integration.
- `atomic_json(path, data)` writes UTF-8, sorted keys, indentation 2, no NaN/Inf and an atomic replace. Use only for **new derived outputs** and explicit state updates, never original source datasets.
- `write_table(path, rows, columns=...)` writes deterministic header order, CSV comma-delimited, UTF-8, stable \n line endings, atomic replacement. Authors are responsible for units in headers, numerical/force signs and complete case identification.
- `result_roots(path, stages=(...), include_legacy=True)` returns only existing canonical/historical results roots, deduplicates parent-child paths and never makes analysis files.
- `create_project_layout()` now obtains canonical stage folders from that same registry. Legacy stage strings passed to `case_folder()` are resolved to canonical destinations. Existing historical folders retain their prior names.

## Output formatting expectations for GUIs/ZIP publishers

Every future figure/report should share:
- consistent title `<STATE> | <METHOD> | <CASE_ID> | <MODEL_ID>`, units on **every** ordinate/abscissa, explicit global/local axes and sign convention;
- a common statuses vocabulary: missing, running, solver-only completed, failed, incomplete, source-equivalence unverified, reviewed/accepted;
- input evidence: source EDB SHA, assembled model SHA, loads, mass and unit conventions, support choice, stiffness state, record/direction and orientation, numerical solver settings, duration/step and convergence;
- CSV/Excel sorted by natural story elevation then element/native ID, numeric cells for physical quantities, metadata and actual source references in independent tabs;
- ZIPs grouped into `00_INPUT_SOURCE`, `01_LOGS`, `02_RESULTS`, `03_EXCEL`, `04_FIGURES`, `05_COMPARISONS`, `06_REVIEW`; a manifest of source SHA and files, with failed/missing evidence explicit. Exclude ETABS original EDB, source calculations and confidential project datasets unless user expressly approves.

**Engineering safeguards:** the 32/76/97-node support cases are distinct; do not change physical restraints to repair a report path. The project-adopted IS 16700:2023 slab stiffness remains 0.25 Ig ULS / 0.35 Ig SLS, without forcing OpenSees shell parameter values; actual section commands must be audited. Do not label a zero-length/blank drift graph as a valid zero response. Native ETABS/OpenSees and NLTHA calibration remain separate validation gates.

## Migration acceptance

1. Locate each writer, GUI field, auto-open, PDF/Excel exporter, ZIP publisher and reader, then change them together in one stage-specific PR.
2. Run `tests/test_unified_output_contract.py`, existing folder tests, `tests/test_project_output_layout_v171.py`, and a native Windows smoke case.
3. Verify that old results still open, new exact stage outputs are discovered once, source hash/case is preserved, output status is truthful and no original model/workbook was modified.
4. Record stage-specific acceptance or blocker under `REVIEW_MAIN`. **Do not mass-migrate numerical output names or rename solver native IDs.**

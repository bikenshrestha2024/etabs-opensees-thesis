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

- `create_case_run(export_dir, stage, case_id, state='AS_CONFIGURED', model_sha256=None, source_edb_sha256=None, units='kN-m-s')` creates a **new** unique run only. Validates safe path components and the explicitly supplied kN–m–s or kN–mm–s model basis. The history modules use the model's declared length basis; result output units (e.g., exported metres) must still be verified separately. Hash fields are explicit, not inferred.
- `prepare_history_run(model_script, stage, state, scope, model_length_unit=...)` creates distinct source-script-fingerprinted LTHA/NLTHA runs in the matching stage and stores the units (`m` or `mm`) explicitly. The script SHA is **not** an assembled model SHA, and a truncated transient never becomes a full-record PASS.
- `inspect_case_manifest(run_dir, expected_stage=...)` reads a case without modification and verifies source/state identity, declared model units, standard subfolders, recorded SHA syntax and status vocabulary. It also requires that the canonical stage recorded inside the manifest matches the physical containing stage directory, even when `expected_stage` is omitted; a missing, unknown, or alias-only recorded stage is not a valid canonical manifest. Any discrepancy is listed as an issue, **not silently repaired**.
- `record_case_status(run_dir, 'RUNNING'|'COMPLETED_SOLVER_ONLY'|'FAILED'|'INTERRUPTED'|'INCOMPLETE')` updates the manifest without making any design-acceptance assertion. `VERIFIED_ETABS_EQUIVALENCE` cannot be set without a separate engineering-review field and is not self-certifying.
- `style_workbook(workbook)` applies common navy headers, white bold text, alternating row shading, fixed 30-point header height, freeze/filter and bounded column widths to a new generated Excel workbook, without modifying cell values. Applied to V142 review Excel; other module workbooks require individually verified integration.
- `atomic_json(path, data)` writes UTF-8, sorted keys, indentation 2, no NaN/Inf and an atomic replace. Use only for **new derived outputs** and explicit state updates, never original source datasets.
- `write_table(path, rows, columns=...)` writes deterministic nonblank string headers, CSV comma-delimited, UTF-8, stable \n line endings, atomic replacement. Real floating scalars (including NumPy float32/float64 when available) and `Decimal` NaN/Infinity values are rejected before publication; a rejected file leaves no partial CSV. Authors remain responsible for units, signs, complete case identification and validating numeric values that arrive as strings or other third-party scalar types.
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

## Common local project-wide stage inventory

`python tools/audit_stage_output_migration.py "<selected export case>" --write` now publishes two **new** time-stamped diagnostics under `09_SOFTWARE_DIAGNOSTICS/MIGRATION_AUDITS`:

- `Live_Stage_Output_Audit_<UTC>.json` — uniform seven-stage and auxiliary directory inventory, case manifest statuses, source/units evidence, invalid folder contract counts and pending native checks.
- `Live_Stage_Output_Audit_<UTC>.xlsx` — five consistently styled tabs: Stage summary, Case registry, Missing or inconsistent, Auxiliary folders and Read first. The workbook contains navigation metadata and review flags rather than confidential EDB contents or numerical design approval.

Without `--write`, the audit is read-only and prints summary status. It does not rearrange or delete files. Existing original EDB/Excel outputs remain unchanged, and users should **not commit local audit files** with absolute project paths.

## Migration acceptance

1. Locate each writer, GUI field, auto-open, PDF/Excel exporter, ZIP publisher and reader, then change them together in one stage-specific PR.
2. Run `tests/test_unified_output_contract.py`, existing folder tests, `tests/test_project_output_layout_v171.py`, and a native Windows smoke case.
3. Verify that old results still open, new exact stage outputs are discovered once, source hash/case is preserved, output status is truthful and no original model/workbook was modified.
4. Record stage-specific acceptance or blocker under `REVIEW_MAIN`. **Do not mass-migrate numerical output names or rename solver native IDs.**

## V22 migration inventory: missing runs and linked diagnostics

The read-only stage audit now reports `MISSING_CASE_MANIFEST` when a canonical `RUNS/<state>/<case>/<run-id>` directory exists without `00_INPUT_SOURCE/CASE_MANIFEST.json`. It flags linked intermediate state/case/run paths without descending through them. Each JSON stage entry and workbook Stage summary include `missing_run_manifest_count` and `linked_run_path_count` separately from total manifest count; the detailed Missing or inconsistent sheet gives exact affected paths. The explicit `--write` publisher refuses linked `09_SOFTWARE_DIAGNOSTICS`, `MIGRATION_AUDITS` and `RUNS` destinations before creating its JSON/Excel report. These checks only inventory filesystem evidence; they do **not** infer that a solver ran or migrate old writers. Regression: `tests/test_stage_output_migration_audit.py`.

## V27 — fail-closed identifiers and linked destinations (2026-11-15)

`safe_component()` now rejects missing/boolean run identifiers, instead of converting them into `None`/`True`/`False` literal directory names. `inspect_case_manifest()` now requires exact string identity of `case_id`, `state`, and `run_id`, rejecting surrounding whitespace or missing values even when a stripped value would be syntactically safe. This is a provenance and identity check; it does not change historic case names or move old results.

`atomic_json()` and `write_table()` now check for pre-existing symlinks in the entire target path ancestor chain and at the final file name. The validation runs before creating any directories, after creating the parent, and before `os.replace`; the output remains atomic for ordinary local filesystem writes. As with ordinary `Path.is_symlink()` checks, OS-level concurrent directory swaps/junction semantics are not fully solved; do not treat this as a multi-user adversarial filesystem security boundary. The change preserves the source JSON/CSV content and filenames, and does not write to source EDB/Excel.

Regression: `tests/test_unified_output_contract.py`. This is software validation only, not an ETABS/OpenSees physics acceptance gate.

## V28 — status publication requires matching canonical identity (2026-11-15)

`record_case_status()` now obtains a read-only `inspect_case_manifest(run_dir)` result and **refuses every invalid or misfiled manifest** before changing `solver_status`. A valid schema string alone is insufficient: stage/state/case/run path identity, declared units, SHA syntax, enumerated subfolders and status constraints are checked together. The inspector also reports `LINKED_CASE_MANIFEST_PATH` when the run root, `00_INPUT_SOURCE` directory or manifest file is a direct symlink; it does not rewrite old results. Existing valid new-run transitions remain compatible. This gate does **not** independently verify the ETABS EDB, physical load path, native solver completion or engineering certification.

Regression: `tests/test_unified_output_contract.py` tests mismatched stage/case/run/units, linked source manifest and unchanged original JSON on refusal.


## 2026-11-15 manifest symlink ancestry safeguard

The read-only `inspect_case_manifest` function now checks the **unresolved** run directory and every parent for symlinks before resolving paths. Previously, resolving a run path could hide a symlinked stage or case ancestor, allowing a redirected manifest to appear valid. A detected linked parent returns `LINKED_CASE_MANIFEST_PATH` without reading the redirected manifest. The same check protects `record_case_status`, which depends on the inspection gate. A synthetic local symlink regression test verifies non-mutation. This does not eliminate concurrent filesystem races or validate physical ETABS/OpenSees analysis.


## Linked input-source evidence visibility (2026-11-15)

`tools/audit_stage_output_migration.py` checks every canonical `RUNS/<state>/<case>/<run>/00_INPUT_SOURCE/CASE_MANIFEST.json` location without following links. A symlinked `00_INPUT_SOURCE` directory is inventoried as `SYMLINKED_RUN_INPUT_SOURCE_REFUSED`; a symlinked manifest is reported as `SYMLINKED_RUN_MANIFEST_REFUSED`. Previously the depth walk could silently treat these files as present while the `rglob` step skipped them, producing an inaccurate zero-issue output. Both are excluded from run counts, included in linked-path totals, and do not count as solver evidence. Deterministic filesystem-only tests cover the cases. No user ETABS file or structural result is migrated by this audit.

Manifest inspection reports INVALID_SOLVER_STATUS and returns UNKNOWN for malformed or unrecognized solver status values, including JSON arrays and objects.


## 2026-11-23 — Compact, source-hashed new history case directories

The optional shared `compact_case_id(stage, scope, source_sha256)` produces a
Windows-portable **48-character-or-shorter** identifier using a shortened stage,
a sanitized, truncated human scope, a six-hex full-scope disambiguator and 12
hex characters of the verified source SHA256. It fails for missing/invalid SHA,
unsupported stages or invalid lengths. The full original model script filename,
complete 64-character source SHA, analysis state, units, and acceptance status
remain in `HISTORY_INPUT_PROVENANCE.json` and `CASE_MANIFEST.json`. This
helper is opt-in for later module writer+reader migrations; `prepare_history_run`
now uses it for **new LTHA and NLTHA** runs only. Existing long folders are
never moved or renamed. Filename/12-hex ID alone is not engineering/model
acceptance: downstream readers must check the full manifest and source SHA.
Synthetic tests: `tests/test_history_run_output_contract.py`.


## 2026-11-24 — Source-bound shortening for **new manifested run folders**

The existing `compact_case_id(stage, scope, sha256)` is now recognized for every canonical/auxiliary stage in `ALL_STAGE_FOLDERS`, including MODEL, ETABS_COMPARISONS, SOFTWARE_DIAGNOSTICS and UPLOAD_PACKAGES. No stage directory itself is renamed. When `create_case_run` is given a valid portable human case label **longer than 48 characters** and a complete 64-hex `model_sha256` or `source_edb_sha256`, it produces the established max-48-character stage/scope-token/source-token name. The full original input remains in `00_INPUT_SOURCE/CASE_MANIFEST.json` as `original_case_id`, along with `case_label_mode=COMPACT_SOURCE_BOUND` and `compact_source_basis` (MODEL_SHA256 preferred over SOURCE_EDB_SHA256). No new input files or solver models are read to guess a hash.

Short names and unfingerprinted long labels retain their exact existing paths with `case_label_mode=EXACT` and `original_case_id` equal to their directory case label. Missing source SHA is **not silently replaced by a hash of a filename**. Historical manifests lacking all three new keys remain valid and readable.

`inspect_case_manifest` now recomputes the source-bound compact name from the saved full label, recorded stage and declared source hash. Tampered original labels, changed declared hashes, missing source basis or altered label modes produce `COMPACT_CASE_ID_MISMATCH`; `record_case_status` then refuses status updates. New runs continue to use unique run IDs beneath `RUNS/<STATE>/<CASE_ID>/<RUN_ID>`, and historical result files are not moved or deleted.

This improves path lengths for source-hashed manifested runs across analysis stages. **It does not change legacy ESM calculations written directly by `analysis_output_folder` / `write_outputs`**, which require a separate writer-plus-reader migration under Issue #177. A 12-hex token labels a case; engineering acceptance still requires complete source, support, load, mass, material and result identities. Tests: `tests/test_compact_manifested_runs_20261124.py`, existing output-contract and saved-case suites. Native ETABS/OpenSees evidence was unavailable for this filesystem-only patch.

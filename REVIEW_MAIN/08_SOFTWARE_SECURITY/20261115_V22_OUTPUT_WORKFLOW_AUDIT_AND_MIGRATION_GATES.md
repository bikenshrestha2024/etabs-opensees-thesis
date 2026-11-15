# V22 — Source-output workflow audit, path hardening and migration inventory
**Date:** 2026-11-15
**Repository:** https://github.com/bikenshrestha2024/etabs-opensees-thesis
**Branch:** `main`
**Acceptance:** `SOFTWARE_SOURCE_PATCHES_COMMITTED_NATIVE_ENGINEERING_NOT_VERIFIED`

## Reviewed scope and evidence boundaries

At the start of this round, the GitHub `main` recursive tree contained **2,972 tracked blobs**. This is a repository-wide file listing, **not** a line-by-line semantic review of every blob. The targeted audit examined `AGENTS.md`, current repository CI, output writers and reader inventories, `components/inputs/output_contract.py`, `output_layout.py`, `project_output_layout.py`, `tools/audit_live_output_writers.py`, `tools/audit_stage_output_migration.py`, associated regression tests and source documentation. The existing immutable per-file review ledger remains authoritative for any claim of semantic coverage. No uninspected file has been marked reviewed.

## Confirmed defects and corrective changes

| ID | Severity | Area | Actual defect | Change | Regression |
|---|---|---|---|---|---|
| V22-01 | P1 | Writer AST scan | `Path.open("w")` was missed: the scanner looked only at the second positional argument, suitable for built-in `open(path,"w")` but not `Path.open(mode)`. | Resolve positional mode by API call form; recognize append/binary/keyword modes; surface unknown dynamic modes as `DYNAMIC_MODE_REVIEW_REQUIRED` rather than assume read. | `tests/test_deep_output_inventory_v16.py` |
| V22-02 | P1 | Stage migration inventory | Existing canonical run folders without a manifest were entirely absent from an `rglob("CASE_MANIFEST.json")`-only report. | Inspect exactly `RUNS/<STATE>/<CASE>/<RUN>` to flag `MISSING_CASE_MANIFEST`; flag linked state/case/run directories without following them. | `tests/test_stage_output_migration_audit.py` |
| V22-03 | P1 | Stage overview reporting | Missing manifests and linked run paths were not distinct from generic invalid/unknown contracts. | Add per-stage and summary counts plus Excel Stage summary columns; preserve the existing JSON schema and detailed Missing or inconsistent tab. | Same tests |
| V22-04 | P1 | Project output path safety | `create_project_layout()` allowed linked `00_SOURCE_MANIFEST` or stage directories and fixed-name `PROJECT_CONTEXT.tmp`; existing malformed manifests could raise a non-actionable runtime error. | Validate existing destination links before directory creation; fail closed on invalid manifest; use same-directory atomic JSON replace with unique temp. `case_folder()` rejects linked intermediate components. | `tests/test_project_output_layout_v171.py` |
| V22-05 | P1 | Optional audit export | `audit_stage_output_migration.py --write` accepted symlinked `09_SOFTWARE_DIAGNOSTICS/MIGRATION_AUDITS/RUNS` and could write report paths outside the selected export case. | Reject linked ancestors before creating a timestamped audit run, consistent with the writer inventory exporter. | `tests/test_stage_output_migration_audit.py` |

**Limits:** Link rejection does not eliminate filesystem races, NTFS junction/reparse-point risks, or bugs in remaining stage-specific writers. A file marked by a static scanner is only a **potential** writer, never proof that a code path executed.

## Canonical layout — retain existing files, no blanket move

The user-selected ETABS export case owns all outputs, with seven analysis stages and separate supporting directories:

```text
<SELECTED_EXPORT_CASE>/
├── 00_SOURCE_MANIFEST/
│   └── PROJECT_CONTEXT.json
├── 01_ETABS_EXPORT/
├── 02_MODEL/
├── 02_GRAVITY/
├── 03_ESM/
├── 04_MODAL/
├── 05_MRSM/
├── 06_LINEAR_TIME_HISTORY/
├── 07_NONLINEAR_TIME_HISTORY/
├── 08_ETABS_COMPARISONS/
├── 09_SOFTWARE_DIAGNOSTICS/
│   ├── WRITER_AUDITS/RUNS/<UTC>/JSON,CSV,REPORT/
│   ├── MIGRATION_AUDITS/RUNS/<UTC>/JSON,EXCEL/
│   └── DISK_AUDITS/
├── 90_UPLOAD_PACKAGES/
├── REVIEW_MAIN/
└── OpenSees_Analysis_Results/          # legacy, read-only until migration
```

For each **newly migrated** stage-producing case, standardize on:

```text
<STAGE>/RUNS/<STATE>/<CASE_ID>/<RUN_ID>/
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

**Do not infer existing stage migration from this target layout.** The output-contract API exists; not every production writer/GUI reader uses it yet. Do not rename old run or historical results to make an audit appear clean.

## Upgrade and acceptance workflow

1. **Freeze inputs:** Hash original ETABS EDB, original Excel Aw/T1 workbook, model script and ground-motion records; never upload private files or local paths to this public repository.
2. **Read-only inventory:** Run writer scan and stage migration scan without `--write`; compare candidate writer methods, dynamic file modes, unmanifested cases, linked-path flags, and old result locations.
3. **Stage by stage:** Before touching an output writer, locate its associated old readers, GUI folder defaults, exported Excel/CSV/PDF paths, preview links, ZIP publisher, state selectors, and case model identity. Adopt `create_case_run` for new runs only after compatibility tests.
4. **Publish local evidence:** Generate a timestamped JSON/CSV writer audit and a separate JSON/Excel stage report into the same selected export case's `09_SOFTWARE_DIAGNOSTICS` folder. The migration summary explicitly distinguishes missing manifests and linked folders.
5. **Run offline CI:** Verify all folder/report tests on the exact commit. Do not promote passing syntax/metadata checks to native structural equivalence.
6. **Run Windows/native gate:** ETABS OAPI + OpenSees: GUI open/stop/restart/scroll/export, signed foundation reaction components for independently justified 32/76/97 options, shell-to-beam/wall load paths, ULS/SLS modal and seismic force/drift, and zero/X/Y then full XY/YX nonlinear records with exact source hashes.
7. **Engineering sign-off:** Record reviewer, expected/actual totals and tolerance, signed discrepancies, failed case evidence and explicit acceptance; keep the unresolved X-wall first-step localForce anomaly and physical support-condition selection open until verified against the real model.

### Windows/local reproduction (no native solver invoked by these commands)

```powershell
python -m unittest tests.test_deep_output_inventory_v16 tests.test_stage_output_migration_audit tests.test_project_output_layout_v171 tests.test_unified_output_contract tests.test_output_layout -v
python tools/audit_live_output_writers.py --repo .
python tools/audit_stage_output_migration.py "<SELECTED_EXPORT_CASE>"
python tools/audit_live_output_writers.py --repo . --export "<SELECTED_EXPORT_CASE>" --write
python tools/audit_stage_output_migration.py "<SELECTED_EXPORT_CASE>" --write
```

Keep outputs in the user-selected export root, not GitHub; reports can contain model identity, private absolute paths, or case metadata.

## Outstanding: do not mark complete

- Literal per-file semantic code audit of all tracked code and historical archives: **NOT COMPLETE**.
- Full migration of all stage writers + readers, native Windows GUI testing, and device/material calibration: **NOT COMPLETE**.
- ETABS/OpenSees physical source equivalence, 32/76/97 support interpretation, individual signed foundation reactions, X-wall first-step failure, full-duration bidirectional NLTHA: **NOT VERIFIED**.
- No original EDB, completed Excel, native gravity report or earthquake waveform was changed by the V22 code updates.

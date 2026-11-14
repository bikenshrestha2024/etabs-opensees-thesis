# Production output migration V2 — ETABS/OpenSees thesis

**Date:** 2026-11-14. **Scope:** V135 diagnostics writer, modal audit writer/reader and read-only native-case inventory. **Status:** CODE AND CI TESTED; WINDOWS-NATIVE SOLVER CHECKS STILL REQUIRED.

## What changed (actual running code, not just an architectural proposal)

1. `components/validation/design_checks.py` (V135) creates and opens `09_SOFTWARE_DIAGNOSTICS/DESIGN_CHECKS_V135` instead of creating `OpenSees_Analysis_Results/Design_Checks_V135` for its derived reports. Its seismic drift inventory searches existing `03_ESM`, `05_MRSM`, `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY` and the old analysis-results root, excluding review snapshots as new response runs. **Missing ULS/SLS cases are NOT EVALUATED, never zero or PASS.** Edit-ready canonical criteria win when data rows exist; otherwise a populated legacy source is read-only fallback. Report JSON includes exact source paths. V135 workbook uses the common formatting; the JSON uses the common atomic writer.
2. `components/modal/gui_and_reports.py` (automatic output selection only) now creates each ULS or SLS run under `04_MODAL/RUNS/<STATE>/<SOURCE_CASE>/<UNIQUE_RUN_ID>/`. It keeps `00_INPUT_SOURCE/CASE_MANIFEST.json`, `MODAL_INPUT_PROVENANCE.json`, `01_LOGS/NBC105_Modal_V111_run.log`, `02_RESULTS/NBC105_Modal_V111.json`, copied `03_EXCEL` CSV/XLSX and copied `04_FIGURES` PNG/PDF. The copied views are not solver results. Each run marks `RUNNING`, `FAILED`, `INTERRUPTED` or `COMPLETED_SOLVER_ONLY`; no physical equivalence is inferred. The original model script is never changed. A user explicitly choosing another output directory retains the old custom path.
3. `components/ui/results.py` locates ULS/SLS modal JSONs in both old and canonical stages, excludes snapshots and checks `limit_state`. Missing saved results are labelled missing, not zero; comparison figures are saved into `04_MODAL/REVIEW_SNAPSHOTS`. The viewer selects the newest compatible local result, **not** a verified native model identity.
4. `tools/audit_stage_output_migration.py` inventories all canonical stages and their existing case manifests. It never invokes ETABS or OpenSees and does not touch source input. By default it prints a read-only summary. The `--write` option saves a local JSON audit under `09_SOFTWARE_DIAGNOSTICS/MIGRATION_AUDITS` (do not commit output with private paths).
5. Regression tests `tests/test_design_checks_canonical_v135.py`, `tests/test_modal_canonical_output_v2.py`, `tests/test_stage_output_migration_audit.py` were added to CI. They use synthetic files only; the native solver and Tk GUI are not exercised in GitHub-hosted CI.

## Expected automatic modal folder

```text
<selected ETABS export>/
  04_MODAL/
    00_BATCH_STATUS/Modal_Batch_Status_V151.json
    RUNS/ULS/<source-specific-case>/<unique-run-id>/
      00_INPUT_SOURCE/CASE_MANIFEST.json
      00_INPUT_SOURCE/MODAL_INPUT_PROVENANCE.json
      00_INPUT_SOURCE/_run_nbc105_modal_v111.py
      01_LOGS/NBC105_Modal_V111_run.log
      02_RESULTS/NBC105_Modal_V111.json
      02_RESULTS/<modal-native-reports>
      03_EXCEL/<copies-of-existing-Excel-CSV-reports>
      04_FIGURES/<copies-of-existing-PNG-PDF-reports>
      05_COMPARISONS/
      06_REVIEW/
      07_EXPORT_ZIP/
```

The source **Python script SHA** is not the original EDB SHA nor the assembled model fingerprint; the corresponding provenance fields are explicitly null if unavailable. This remains a native engineering validation gate.

## Windows verification sequence (mandatory before engineering acceptance)

1. `git switch main && git pull --ff-only origin main`; use the real original source export, but protect EDB and original Excel files with a before/after SHA256 inventory.
2. Run `python tools/audit_stage_output_migration.py "D:\\Thesis Opensees\\ETABS 11-14-2026\\3" --write` from the repository checkout. Audit is structural **file-path** evidence only.
3. Open the modal GUI. On the 3rd-storey ULS review case, use automatically selected model and output paths, explicitly confirm source mass/constraints and run ULS. Confirm exactly one fresh unique `04_MODAL` case; the output manifest should be `COMPLETED_SOLVER_ONLY` if the solver exits 0. Compare modes, periods and total modal mass to the identical-source ETABS analysis; do not label mass >=90% as section acceptance.
4. Open saved modal results from the main GUI; verify it finds the new canonical ULS result. SLS must remain explicitly missing until an appropriate source-state SLS model is selected and solved. Verify that old results remain browseable and accidental cross-model selection is not promoted to acceptance.
5. Open V135 design checks. Confirm reports/criteria templates go to `09_SOFTWARE_DIAGNOSTICS/DESIGN_CHECKS_V135`. Verify a saved compatible ULS drift file shows a numeric, source-linked row; missing SLS stays **NOT EVALUATED**, never a blank PASS. When both canonical and legacy criteria are populated, the canonical edited rows take priority, and the original old rows and EDB SHA remain unchanged.
6. Run one modal **cancelled** child process and one intentionally invalid builder case with disposable test inputs, never the original source. Verify `INTERRUPTED` / `FAILED` status and log are recorded without stale success.
7. Re-run the existing 32/76/97 foundation, MESH_04/08/16 vertical-load, pinned brace and wall/FSAM evidence gates separately. These changes did not correct their physical load transfer or nonlinear constitutive laws.

## Still open and should not be represented as completed

- ESM solver, MRSM batch, gravity comparison, LTHA and NLTHA **production writers and their GUI readers** must each migrate and pass a paired native smoke run. A canonical *reader* alone does not make a producer migrated. ESM's multi-case runners and shared response readers still need particular care to avoid processing the wrong ULS/SLS result.
- Fully canonical ZIP export for actual solver outputs, comprehensive workbook styling, canonical static P-Delta preloads and a model-SHA strict cross-run selector remain outstanding. No bulk archive moves/deletes are authorized.
- Numerical ETABS equivalence, effective RC slab bending 0.25/0.35 per project adoption, wall–slab–beam gravity path, pinned braces, material calibration and NLTHA dynamic case gates still require native project evidence.

## Acceptance principles

**Do not modify** original EDB, reference Excel, actual reinforcement, source ground motions, calibrated damper parameters, ETABS-only results, or previously accepted working solver outputs. A generated solver output is evidence of a run, not NBC 105:2025 code compliance. Detailed design decisions remain under their existing `REVIEW_MAIN` and `LITERATURE` sections.

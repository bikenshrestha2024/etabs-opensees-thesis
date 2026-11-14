# Deep source audit V15 — output identity, source preservation, archives and migration

**Date:** 2026-11-14. **Status:** Targeted live-code corrections implemented; Python CI and Windows-native validation must be distinguished. No native ETABS/OpenSees runs, local D-drive source files, or solver output were available through GitHub source inspection.

## Scope and methods

Reviewed actual connected GitHub `main` source, not a screenshot-only inference. Inspected live stage registry and contract, stage migration tool, archive publisher, mirror copier, folder auditor, project output layout, selected gravity/mesh/identity modules and their tests. Reviewed directory inventories for inputs, gravity, model, equivalent-static, modal, MRSM, linear/nonlinear, GUI and validation packages; active repository contains substantially more code than this focused pass could manually validate line by line. Existing `tools/audit_active_repository.py` inventories parsable Python; it cannot prove correct engineering semantics.

### Confirmed code-level defects and V15 changes

| ID | Source | Defect | Correction | Safety |
|---|---|---|---|---|
| O15-01 | `output_layout.export_root_for` | Selected nested `REVIEW_MAIN`/`00_SOURCE_MANIFEST` paths fell through to themselves, opening a new nested export destination | Recognize both as project-root-owned paths | No file moved |
| O15-02 | `output_contract.safe_component` | Windows `COM4...COM9`, `LPT4...LPT9` were accepted | Reject all reserved COM/LPT 1–9 names | Portable run IDs |
| O15-03 | `project_output_layout.case_folder` | Separate regex accepted reserved case/state names that the central run contract rejected | Use central `safe_component` | One policy |
| O15-04 | `organized_results.classify` | Files within canonical gravity/ESM/modal/MRSM stage paths could be classified by misleading file names | Canonical stage owner overrides file-name heuristics | Does not alter old artifacts |
| O15-05 | `organized_results._walk` | Custom destination tree under selected source could be rescanned with old snapshots not covered by hardcoded skip names | Exclude the chosen destination parent and subtree; preserve access to its ancestors | Prevents recursive archive growth |
| O15-06 | `organized_results.publish_organized_results` | Overlapping `gravity_root` and `results_root` could duplicate evidence | Avoid overlapping second scan | Exact native identity still required |
| O15-07 | `organized_results` | Upload ZIP could include an original source workbook/private manifest when the selected source was export root | Exclude known source manifests, classified source stages, and recognizable original workbook names | **Not a complete secrets/privacy scan**; manually approve each ZIP |
| O15-08 | `export_mirror` | Existing symlinked destination could redirect a copy or SHA read outside intended mirror | Refuse stage, category and destination symlinks | Original EDB untouched |
| O15-09 | `folder_audit` | Canonical stage symlink read as a normal directory and could expose unrelated external paths in inventory | Refuse symlinked stage directories and report `BLOCKED` finding | Audit only |
| O15-10 | `audit_stage_output_migration` | A syntactically valid JSON array could crash audit at `.get` | Flag `NONOBJECT_CASE_MANIFEST` and continue | No false certification |
| O15-11 | `audit_stage_output_migration` | Audit `--write` JSON and XLSX created flat files under diagnostics | New run owns `RUNS/<UTC>/JSON/` and `EXCEL/`; old reports preserved | Reader compatibility separately noted |
| O15-12 | `organized_results` | ZIP bundle labels not using shared Windows file-name validator | Use `safe_component` before creating any destination | Prevents invalid archive names |

## Required canonical structure

```text
<EXPORT>/
  00_SOURCE_MANIFEST/
  01_ETABS_EXPORT/
    00_MANIFEST/
    01_SOURCE/
    02_MAPPING/
    03_LOADS/
    04_VISUALIZATION/
    05_AUDITS/
    06_CONFIG/
    07_LOGS/
    08_PROCESSING/
    09_REVIEW/
  02_MODEL/
  02_GRAVITY/
  03_ESM/
  04_MODAL/
  05_MRSM/
  06_LINEAR_TIME_HISTORY/
  07_NONLINEAR_TIME_HISTORY/
  08_ETABS_COMPARISONS/
  09_SOFTWARE_DIAGNOSTICS/
    ANALYSIS_SETTINGS/RUNS/<UTC>/JSON|EXCEL/
    MIGRATION_AUDITS/RUNS/<UTC>/JSON|EXCEL/
    DESIGN_CHECKS_V135/
  90_UPLOAD_PACKAGES/
  REVIEW_MAIN/
  OpenSees_Analysis_Results/    # legacy compatibility, read-only until producers/readers migrate
```

For new fully migrated *solver* producers, `components.inputs.output_contract.RUN_SUBFOLDERS` remains canonical:
`<STAGE>/RUNS/<STATE>/<CASE_ID>/<RUN_ID>/00_INPUT_SOURCE,01_LOGS,02_RESULTS,03_EXCEL,04_FIGURES,05_COMPARISONS,06_REVIEW,07_EXPORT_ZIP`.
Existing audit-only report modules may use `RUNS/<UTC>/JSON|EXCEL` for local diagnostics. Neither scheme implies numerical convergence.

## Open numerical and structural validation

Global equilibrium is **not** proof of individual foundation agreement. Preserve independent 32/76/97 support cases and force components; compare exact corresponding node geometry and physical constraints. ShellMITC4 floor, beam, wall and core load transfer requires 04/08/16 independent models and recovered element/node forces. ULS/SLS project-adopted conventional slab EI, wall cracking stiffness, hinge/release transfer, diaphragm mass/inertia, damping, P-Delta initial states, and nonlinear wall constitutive validation still require native evidence. No numerical output was changed or newly certified by these filesystem fixes.

## Additional caveat: privacy

The organizer now excludes **known** source workbook markers and manifest folders, but arbitrary secrets or private data may appear in model scripts, JSON or logs. Its ZIP is a debugging artifact, **not automatically approved for public GitHub**. Manually review exact manifest contents and perform a secrets scan before sharing. A review ZIP's `source_sha256` is an evidence fingerprint, not an acceptance stamp.

## How to verify locally

```powershell
git switch main
git pull --ff-only origin main
python -m unittest tests.test_organized_results tests.test_unified_output_contract tests.test_project_output_layout_v171 tests.test_stage_output_migration_audit tests.test_folder_audit -v
python -m pytest tests/test_export_mirror.py -q
python tools/audit_stage_output_migration.py "D:\\Thesis Opensees\\ETABS 11-14-2026\\3" --write
python 22_AUDIT_EXPORT_FOLDERS.py "D:\\Thesis Opensees\\ETABS 11-14-2026\\3"
```

Inspect output manifest SHA, run identity, stage, state and source EDB before any automated packaging. Migrate live legacy writer/reader pairs one stage at a time, never bulk-move or rewrite historical evidence.

# Integrated engineering and migration audit — source-controlled findings
**Date:** 2026-11-22  
**Repository branch:** `main`  
**Safety boundary:** static and fixture-based checks are complete where CI confirms PASS; **native engineering and full output migration are NOT certified**.

## Completed work in this audit cycle

1. Identified why the integrated GitHub workflow failed while pytest passed: one obsolete **Git blob SHA** attestation for `components/inputs/project_workbooks.py::read_explicit_excel_calculation`. The previous evidence was retained verbatim in `docs/review/ledger/superseded_semantic_review_attestations_20261122.csv` and removed only from the current attestation register. No fresh review or engineering signoff was fabricated. The static CI gate then passed (GitHub Actions run **44998426880**).
2. The latest integrated static report inspected **3,421 tracked paths** and **682 active Python source/test files** at commit `663c634c`. No explicit local import target was unresolved.
3. Inspected the import graph: **zero eager cycles**, six candidate strongly connected components involving **deferred/conditional imports**. They must be tested for runtime call order, but are not evidence of module-initialization failure. Current review groups:
   - `components/inputs/model_aligned_reference.py`, `components/inputs/project_workbooks.py`, `components/modal/rayleigh.py`
   - `components/inputs/output_contract.py`, `components/inputs/output_layout.py`
   - `components/nonlinear_time_history/material_source_sets.py`, `components/nonlinear_time_history/research_building_materials.py`
   - `components/ui/nbc105_settings_panel.py`, `components/validation/design_checks.py`
   - `components/validation/etabs_eq_pdelta_native_extract.py`, `components/validation/gravity_etabs_direct.py`
   - Eight mutually dependent deferred validation/workbench modules (see CI `02_DEPENDENCIES/import_graph.json` for exact membership)
4. Separated **95 legacy-path string matches** into **82 executable/configuration literals** and **13 documentation/docstring literals**. This is not a count of 82 broken writers: canonical compatibility aliases, audit scanner string constants and legacy *read* paths may be appropriate. Code still needs a per-line producer/consumer audit.
5. `tools/audit_output_writer_reader_pairs.py` now emits **`legacy_reference_line_register.csv`** and **`reader_writer_line_register.csv`**, preserving source file, line, owning module, context and potential read/write operation, as well as its original per-source register. These are source-review candidates, not runtime dependency evidence.
6. Integrated GitHub workflow now runs the full repository static audit, module consistency/shadowing, 13 component catalog checks, current source geometry/Aw reference fixtures and line-level output migration inventory; it packages evidence under `audit/integrated/`.
7. Explicit NBC Excel references no longer qualify as current `SAME_EDB_PATH_REFERENCE` merely because the strings match when the actual EDB is unavailable. Renamed EDB copies require matching file bytes; explicit missing/different files remain research references only. This does **not** establish that an Excel workbook was calculated from a *past revision* of a same-name EDB without an independent recorded source digest.

## Organized CI evidence folders

```text
audit/integrated/
  00_OVERVIEW/integrated_audit.json
  01_TRACKED_FILES/tracked_file_register.csv
  02_DEPENDENCIES/import_graph.json
  03_FINDINGS/consolidated_findings.json
  04_ACCEPTANCE/acceptance_gates.json
  05_OUTPUT_WRITERS/writer_summary.json
  06_SECURITY/secret_scan_summary.json
  07_ARCHIVE_PROVENANCE/exact_blob_duplicates.json
  08_SEMANTIC_REVIEW/function_review_register.csv
  08_SEMANTIC_REVIEW/attestation_validation.json
  09_FACADE_COMPATIBILITY/facade_source_context.csv
  10_MODULE_CONSISTENCY/
  11_COMPONENT_NAVIGATION/catalog.json
  12_MIGRATION_QUEUE/
    all_active_output_pairs.json
    all_active_output_pairs.csv
    legacy_reference_line_register.csv
    reader_writer_line_register.csv
```

## Engineering and migration acceptance (not passed by static CI)

| Requirement | Current acceptance | What is needed |
|---|---|---|
| Full line-by-line independent semantic review | **INCOMPLETE** | Reviewed function/module units with exact current SHA, human-verifiable rationale and regression evidence |
| Remaining duplicate functions | **REVIEW QUEUE** | Inspect and adjudicate each clone group; do not delete historical source or compatibility wrappers automatically |
| Stage-owned output migration | **INCOMPLETE** | On real saved Windows exports verify writer and reader for each Gravity, ESM, Modal, MRSM, LTHA, NLTHA, NBC, 3D, ETABS comparison and ZIP/Excel path |
| Latest 12 m X wall reference | **REQUIRES MODEL VALIDATION** | Source EDB SHA, first-storey 2×12 m wall/opening geometry, full assignment export, current workbook cells/formulas, ULS/SLS |
| 32/76/97 gravity reactions | **UNVERIFIED POINTWISE** | Native source restraint mapping, wall-edge mesh, loads, frame offsets, ETABS/OpenSees per-node vectors; legacy ~3,041 kN / elastic ~768 kN maxima must be reconciled |
| NBC 105 clauses 1–10 Annex A/B | **NOT EXHAUSTIVELY CERTIFIED** | Clause-by-clause input/equation/table/footnote comparison and reviewed native result evidence |
| Nonlinear X-wall first step, M0–M6 | **UNRESOLVED** | Native localForce/material/convergence evidence and full-duration case matrix |
| Windows GUI/Spyder release | **NOT NATIVE-VERIFIED** | Reopen every saved case and rerun on selected conda/OpenSeesPy/ETABS versions |

**Important:** a successful `Integrated tracked-tree, dependency and output review` action now means its **static** gate passed. It is never equivalent to migration completion, ETABS/OpenSees structural validation or an NBC-compliant building design approval.

## Reproduction

From a clean checkout:

```powershell
python -m unittest tests.test_repository_integrated_audit tests.test_deep_output_inventory_v16 tests.test_all_active_output_pair_matrix tests.verify_esm_explicit_excel_method -v
python tools/audit_repository_integrated.py --repo . --output audit/integrated --fail-on-static-blockers
python tools/audit_cross_module_consistency.py --repo . --report-dir audit/integrated/10_MODULE_CONSISTENCY --fail-on-parse --fail-on-shadowed
python tools/audit_component_readmes.py --root . --output audit/integrated/11_COMPONENT_NAVIGATION/catalog.json --check
python tools/audit_output_writer_reader_pairs.py --repo . --report-dir audit/integrated/12_MIGRATION_QUEUE --fail-on-parse
```

On the local, private ETABS export, additionally run the source-specific read-only review:

```powershell
python tools/audit_uniform_output_structure.py --export-root "D:\PATH\TO\EXACT_ETABS_EXPORT"
python tools/audit_stage_output_migration.py "D:\PATH\TO\EXACT_ETABS_EXPORT" --write
python tools/audit_gravity_workspace.py "D:\PATH\TO\EXACT_ETABS_EXPORT" --write
```

The local export inspection is **not performed in GitHub Actions** because the user's Windows-only native EDB, COM environment and entire private solver results are not present there. Do not upload private EDB/XLSX/solver evidence merely to turn a status green.

Tracking: [issue #141](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/141) (all producer/consumer paths), [#142](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/142) (duplicate semantics), [#140](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/140) (gravity pointwise parity).

## 2026-11-22 follow-up: previously omitted relative-import edges

The cross-module and output migration scanners previously missed or under-described `from .` and `from ..` imports. They now share a non-executing Python import resolver with direct tests and integrated CI coverage. This improves the dependency review queue **without completing migration** or validating real runtime call order. See [source-level correction](20261122_RELATIVE_IMPORT_GRAPH_CORRECTION.md). All native engineering and saved-case gates above remain open.

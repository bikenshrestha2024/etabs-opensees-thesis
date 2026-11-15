# V17 canonical case-run output security review — 2026-11-15

**Status:** SOURCE_PATCH_COMMITTED; NATIVE_WINDOWS_REGRESSION_NOT_EXECUTED.
**Scope inspected:** `components/inputs/output_contract.py`, `components/inputs/output_layout.py`, `tests/test_unified_output_contract.py`, V16 audit and existing run-folder migration rules. This is a focused code review, **not** a complete review of every repository file or an ETABS/OpenSees numerical verification.

## Confirmed flaw and correction

**V17-01 — linked ancestors redirect newly created canonical runs.** Before this correction, `create_case_run()` checked the export root, stage alias, case identifier and hashes, but called `parent.mkdir(parents=True, exist_ok=True)` without checking that existing `<case>/<stage>/RUNS/<state>/<case-id>` ancestors were real directories. If a pre-existing ancestor were a directory symlink, Python could create a run and its manifest outside the selected export root, contrary to the single-owning-case contract.

**Patch:** Refuse a symlink at each existing stage, RUNS, state and case-ID ancestor with an explicit `ValueError` before creating new output. This is intentionally scoped to the newly created run hierarchy, not to moving or deleting old results. `export_root_for()` already resolves the explicitly selected source location; this patch does **not** assert that a user-selected root itself is trustworthy or prevent concurrent filesystem replacement races.

**Regression:** `tests/test_unified_output_contract.py::UnifiedOutputContractTests::test_linked_stage_or_case_folder_is_refused_without_external_writes` covers redirects at all four levels and verifies no external run file is created. Test code has been committed; its actual execution on a Windows export drive and the full CI suite still need independent confirmation.

## Separate unresolved inspection findings — NOT CLAIMED FIXED

| ID | Stage | Required verification | Acceptance evidence |
|---|---|---|---|
| V17-02 | ALL / migration | Inventory actual producers and consumers of canonical vs legacy folders; avoid moving live files while old readers remain | Writer/reader mapping, runtime trace, outputs and opening historical runs |
| V17-03 | ALL / security | Audit remaining general-purpose file writers and pointer files against linked-parent, junction, race and external-target risks | Adversarial filesystem tests on Windows and least-privilege execution |
| V17-04 | GRAVITY | Distinguish the 32 physical support locations from the alternative 76/97 node scenarios; reconcile reactions at matched global coordinates, source support DOFs, loads and units | ETABS/OpenSees side-by-side foundation-reaction and slab/wall load path ZIP |
| V17-05 | ESM | Read `Aw X/Y`, X/Y adopted periods from the original completed workbook; do not silently recompute; enforce EDB/workbook SHA identity | Workbook cell provenance, NBC 105:2025 formulas and independently checked period/base-shear sheets |
| V17-06 | MODAL/MRSM | Confirm 40-mode mass participation, torsional mass, diaphragm inertia, numerical CQC, scale and signed ±5% eccentricity cases | Native model-specific modal and MRSM output vs ETABS |
| V17-07 | LTHA/NLTHA | Source-matched complete record duration, units, two horizontal components, orientation swap, signed P-Delta initial state, fresh-domain retries and nonfinite-force isolation | Full-record accepted solver traces and tagged outputs; no partial-run acceptance |
| V17-08 | Nonlinear walls/devices | Resolve X-wall first-step nonfinite local-force response; verify fiber geometry, reinforcing steel, shell/FSAM parameters and damper units | Isolated native element benchmarks and full building regression |
| V17-09 | UI/export ZIP | Check scroll, copy log, process-level cancel, full input/output manifest, path indexing and ZIP publication for each stage | Windows GUI action-by-action checks plus reopen tests |

## Structured outputs retained

```text
<selected-export-case>/
  01_ETABS_EXPORT/{00_MANIFEST,01_SOURCE,02_MAPPING,03_LOADS,04_VISUALIZATION,05_AUDITS,06_CONFIG,07_LOGS,08_PROCESSING,09_REVIEW}/
  02_GRAVITY/RUNS/<state>/<case>/<run-id>/
  03_ESM/RUNS/<state>/<case>/<run-id>/
  04_MODAL/RUNS/<state>/<case>/<run-id>/
  05_MRSM/RUNS/<state>/<case>/<run-id>/
  06_LINEAR_TIME_HISTORY/RUNS/<state>/<case>/<run-id>/
  07_NONLINEAR_TIME_HISTORY/RUNS/<state>/<case>/<run-id>/
  09_SOFTWARE_DIAGNOSTICS/
  90_UPLOAD_PACKAGES/
  REVIEW_MAIN/
```

Each **new** canonical case run uses `00_INPUT_SOURCE,01_LOGS,02_RESULTS,03_EXCEL,04_FIGURES,05_COMPARISONS,06_REVIEW,07_EXPORT_ZIP`. These are actual directories created by `create_case_run`; other production paths require separate writer verification. Do not claim that the existence of these folders proves solver execution or code compliance.

## Reproduce

```powershell
python -m unittest tests.test_unified_output_contract -v
python -m unittest tests.test_deep_output_inventory_v16 tests.test_folder_audit tests.test_output_layout tests.test_stage_output_migration_audit -v
python tools/audit_live_output_writers.py --repo .
```

**Evidence classification:** A source-path safety defect and regression test were added; no native ETABS, OpenSees/XARA, complete time history or physical equivalence test was performed in this review. Preserve all original EDB/XLSX files and historical outputs. Never commit local case paths, model data or private evidence to the public repository.

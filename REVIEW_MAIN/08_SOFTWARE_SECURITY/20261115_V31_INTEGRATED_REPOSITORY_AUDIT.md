# Integrated repository audit — V31 (2026-11-15)

**Scope:** tracked-file metadata and active-source static checks, with an explicitly incomplete engineering review. **Not** a claim of a complete line-by-line semantic review, native ETABS equivalence, or NBC 105:2025 compliance.

## Evidence and baseline

- Repository: `bikenshrestha2024/etabs-opensees-thesis`, branch `main`.
- Starting reviewed HEAD: `e9fdcb0be5270753d745f49a6059013e772499ee`, 3,021 Git-tracked blobs; 173 files at root, 129 root Python scripts (snapshot only; the CI output records actual checkout totals).
- Existing `tools/audit_active_repository.py` covered root + `components/`, `tests/`, `tools/` but **omitted `src/`**. The writer audit `tools/audit_live_output_writers.py` similarly omitted `src/`. Correct both instead of adding another overlapping scanner.
- The active source audit previously decoded files with `errors="replace"`, masking malformed UTF-8. Correct to strict decoding and report `SOURCE_READ_ERROR` rather than treating corrupted content as verified Python.
- Existing regression and governance coverage: `AGENTS.md`, `engineering/rules/CORE_RULES.md`, `ENGINEERING_GATES.md`, `MODULE_BOUNDARIES.md`, `docs/programs/00_PROGRAM_INDEX.md`, static layout, writer scan, source-guide inventory, history security scanner, and the output case-contract tests.
- Historical / frozen bundles and literature documents are **metadata inventoried**, not executed, moved or falsely labeled semantically inspected.

## Single repeatable full-tree assessment

```powershell
python -m unittest -v tests.test_repository_integrated_audit tests.verify_active_repository_audit tests.test_deep_output_inventory_v16
python tools/audit_repository_integrated.py --repo . --output audit/integrated --fail-on-static-blockers
```

The integrated tool calls the existing source, static writer and conservative security audits, and uses `git ls-files` to inventory **every tracked path**. It publishes two untracked local/CI artifacts:

- `audit/integrated/integrated_audit.json` — counts, all tracked file records, source parse/compile errors, missing canonical launchers, import edges, dynamic import candidates, potential cycles, unresolved imports, legacy output path references, categorized findings and gate status.
- `audit/integrated/tracked_file_register.csv` — one row per tracked file, classification and precise review state; `METADATA_INVENTORIED_NOT_SEMANTICALLY_REVIEWED` is never a passing engineering review.

CI: [`.github/workflows/integrated-repository-audit.yml`](../../.github/workflows/integrated-repository-audit.yml) runs on pushes to main, pull requests and manual dispatch. Uploads the report as an Actions artifact; does not upload EDB/XLSX contents or credentials. The secret detector records only the candidate file, line and category, never credential values, and cannot assess prior Git history.

**Static gate:** fail if active-source parse/read errors, missing canonical entry points, or writer scan parse errors. Import cycles / unresolved imports / legacy path markers are review candidates, because reflective imports, optional plugins and compatible readers may be legitimate. Do not auto-delete or auto-rename working code based on a static hint.

## Consolidated defect register and execution gates

| ID | Finding or open obligation | Status / evidence gate |
| --- | --- | --- |
| STATIC-001 | `src/` omitted by two original AST inventories | **CORRECTED IN SOURCE**, new tests; CI results determine acceptance |
| STATIC-002 | UTF-8 replacement could mask an invalid active source file | **CORRECTED IN SOURCE**, malformed-byte regression; CI results determine acceptance |
| ARCH-001 | Missing or cyclic local import edges across active modules | **CHECKED AS CANDIDATES**, requires direct caller tracing before changing imports |
| OUT-001 | Legacy writers/readers still coexist with stage-owned `RUNS/` outputs | **OPEN**: trace every writer and reader per stage; preserve old paths until regression |
| OUT-002 | Old multi-file output publications are not one atomic transaction | **OPEN**: run-owned manifest and completeness/zip proof |
| SEC-001 | Current tracked tree secret candidates | **SCAN ONLY**: human review + Git-history/GitHub alerts still required |
| ENG-P0-001 | 32 primary reaction-support joints versus 76/97 mesh points | **NATIVE EVIDENCE REQUIRED**: ETABS source six-DOF base support/reactions and independent model |
| ENG-P0-002 | Nonfinite X-wall first-step around element 110280 | **NATIVE EVIDENCE REQUIRED**: isolated material, topology, ZERO/X/Y probes, numerical logs |
| ENG-P1-003 | NBC 105 ESM/MRSM, Excel Aw/T1, mass, drift, scale, P-Delta | **NATIVE EVIDENCE REQUIRED**: workbook/EDB SHA and signed case-by-case comparisons |
| ENG-P1-004 | Completed M0–M6 paired motions, nonlinear sensitivity, source-to-record identity | **NATIVE EVIDENCE REQUIRED**: all actual duration and samples, calibration, source hashes |

The reported counts and path lists are generated from **the exact checkout running CI**; this document does not guess whether a detected import or writer is broken in practice.

## Consistent folder and outputs contract

Do not reorganize confidential models by path-only heuristics. Preserve the **selected ETABS export case** as the owning root and canonical stages:

```text
<ETABS_EXPORT_CASE>/
  00_SOURCE_MANIFEST/
  01_ETABS_EXPORT/
  02_MODEL/
  02_GRAVITY/
  03_ESM/
  04_MODAL/
  05_MRSM/
  06_LINEAR_TIME_HISTORY/
  07_NONLINEAR_TIME_HISTORY/
  08_ETABS_COMPARISONS/
  09_SOFTWARE_DIAGNOSTICS/
  90_UPLOAD_PACKAGES/
  REVIEW_MAIN/
```

For newly migrated producing stages, use `<STAGE>/RUNS/<STATE>/<CASE>/<RUN_ID>/00_INPUT_SOURCE`, `01_LOGS`, `02_RESULTS`, `03_EXCEL`, `04_FIGURES`, `05_COMPARISONS`, `06_REVIEW`, `07_EXPORT_ZIP`. Migrate each writer *and* all real GUI/CLI/ZIP/Excel readers together. An existing legacy result must not be silently moved or represented as the latest run. All exports require per-file SHA, source/units/limit-state case provenance, completeness list and explicit `NOT_VERIFIED` acceptance by default.

## Acceptance requirements and boundary

1. **Inventory gate:** every Git-tracked path classified; 0 missing canonical launchers; active parser/compiler errors resolved or explicitly blocking. Historical blobs metadata-only.
2. **Dependency gate:** each unresolved import/cycle candidate assigned confirmed defect, supported optional dependency, or justified false positive. Static edges alone do not prove the runtime boundary.
3. **Output gate:** writer/reader matrix, staged save, sidecar and source hash, log, csv/excel/figure/zip for each actual stage case; tests for missing, corrupt and conflicting files and interrupted runs.
4. **Security gate:** no confirmed keys/private datasets in current public tree; review historical commits and GitHub alerts separately. No live secret values in reports.
5. **Native environment gate:** Windows Python 3.12 + Spyder GUI + ETABS OAPI + OpenSees executable, real case evidence for click, stop, scroll, save and restart.
6. **Engineering gate:** ETABS/OpenSees source identity, gravity/32-76-97 supports, modal, ESM/MRSM and nonlinear isolated/full-record checks with physical quantities and reviewed comparisons.
7. **Research/acceptance gate:** documented NBC 105:2025 code purpose and distinct source-checked, numerically converged, ETABS-matched, experimental and code accepted statuses; no gate is inferred from the preceding one.

**Until the above checks are actually executed and the acceptance evidence is retained, the entire repository must not be described as fully semantically audited or the thesis numerically validated.** This change creates an auditable, repeatable foundation for reviewing it in breadth and depth without one-error-at-a-time guesswork.

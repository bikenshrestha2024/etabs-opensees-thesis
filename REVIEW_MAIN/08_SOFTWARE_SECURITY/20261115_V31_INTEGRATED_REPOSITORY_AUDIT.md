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

- `audit/integrated/00_OVERVIEW/integrated_audit.json` — counts, all tracked file records, source parse/compile errors, missing canonical launchers, import edges, dynamic import candidates, potential cycles, unresolved imports, legacy output path references, categorized findings and gate status.
- `audit/integrated/01_TRACKED_FILES/tracked_file_register.csv` — one row per tracked file, classification and precise review state; `METADATA_INVENTORIED_NOT_SEMANTICALLY_REVIEWED` is never a passing engineering review.

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

## First complete tracked-tree CI result and source follow-up (2026-11-15)

**Verified CI run:** [Integrated tracked-tree audit](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43686569086), `success` for commit `8e9c86115ab7c7778b020af67099c04c131b21b0`; underlying generated ZIP was fetched and the JSON inspected, not inferred from workflow name.

- **3,027** Git-tracked paths inventoried; **530** active Python sources/tests/root scripts AST-scanned/compiled.
- Tracked classification: **129** root launcher/helpers; **401** active sources/tests; **1,145** archive/research snapshots (metadata only); **924** documentation/literature; **174** governance/workflow; **254** other files.
- Writer audit: **334** active root/components/src/tools files visited; **1,017** possible write calls; **96** legacy path literal occurrences; **97** canonical path literal occurrences. A marker occurrence is not an independently proved writer or inconsistency; some markers occur inside the audit tool itself.
- **0** invalid active parse/compile entries, **0** missing canonical entry points, **0** unresolved explicit local module imports. **83** dynamic import calls require manual caller/side-effect review. Static gate `PASS` only.
- **4** cyclic relationships in the inclusive static import graph, listed in the structured artifact; inspecting their actual import statements found reciprocal edges inside functions/GUI callbacks in each group. Only one direction in the ETABS EQ PDelta ↔ gravity pair is at module scope. The follow-up code now separately reports **eager/top-level** import cycles versus any-cycle potential, so these four cannot be misrepresented as confirmed startup failures.
- **7** `src/` source-guide paths missing in the initial run. Added source-grounded guides under `docs/source/src/`; follow-up CI must confirm the new source-guide finding is cleared.
- Static pattern scanning reported no current tracked-tree secret candidates in this run; Git history and credential exposure via binary files remain unverified.

### Focused standalone benchmark defect and coordinated correction

`src/opensees_engine/standalone.py::axial_cantilever_check` previously retrieved the first/next nodes by **list position** even though the neutral data contract determines the element endpoints by stable node tags. Reordering two node records could therefore invalidate the analytical comparison of an otherwise identical cantilever. The new checker resolves node records from the element's `nodes` tags, preserving input-independent physics and unit definitions. Added a solver-free `FakeOps` test with deliberately reversed node ordering in `tests/verify_standalone_neutral_model.py`. No ETABS source, model conversion, full-building solver or engineering load is changed.

Follow-up consolidated regression now includes the neutral schema/standalone test and the ETABS adapter import boundary test in the integrated CI workflow.

### Precise remaining acceptance status

The integrated scan is a **repeatable broad inventory**, not completion of per-function behavior review across 530 Python files. The remaining review work is tracked in [the findings ledger](../../docs/review/ledger/20261115_V31_INTEGRATED_FINDINGS.csv), the structured CI JSON, and `engineering/rules/ENGINEERING_GATES.md`. Do not label function-scoped reciprocal imports, legacy reference strings or untested output writers as confirmed bugs without a targeted reproduction and a native/regression test. Native ETABS, 32/76/97 physical reaction equivalence, X-wall element 110280, full ground-motion durations, NBC/ESM/MRSM scaling and M0–M6 sensitivity remain **NOT_VERIFIED**.

## Verified follow-up CI acceptance (commit `88dc181a3d58dbb4d7ec177d84e0961074dd4c84`)

- [Integrated tracked-tree CI, passed](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43687116810). Its ZIP artifact was downloaded and `integrated_audit.json` inspected.
- Exact checkout: **3,036 tracked paths**; **530 active Python files**; 129 root launchers, 401 active sources/tests, 1,145 archival/research snapshots, 932 documentation/literature, 175 governance/workflows, 254 other tracked files.
- **Static source gate: PASS**; 0 active parse failures; 0 missing canonical launchers; 0 unresolved explicit local imports; 0 `src/` missing guides; 0 current tracked-tree secret pattern candidates.
- Import graph: **253 eager edges** and **254 deferred edges**; **4 potential cycles across the inclusive graph but 0 eager/top-level cycles**. These are deferred import relationships and remain explicitly unverified under actual Windows GUI execution rather than being mislabeled confirmed failures. **83** dynamic-import candidates remain.
- Writer inventory: **334 scanned source files** (root/components/src/tools), **1,017 candidate write calls**, **96** legacy path-literal and **97** canonical-literal occurrences. These numbers are not validated output-producing calls or proven defects.
- The standalone axial tag-order regression and ETABS adapter boundary tests passed within the same integrated CI. [Repository compilation/navigation](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43687116807), [NLTHA Python quality](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43687116800), and [literature provenance](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43687116812) also passed.

**Explicitly not accepted:** complete semantic line-by-line review of all 530 active source files; historic-snapshot semantics; performance profiling of actual 25-storey model; complete writer/reader migration; Windows native GUI and ETABS; 32/76/97 reaction equivalence; first-step wall element 110280; full-duration NLTHA; NBC 105:2025 engineering acceptance. Those gates require actual model records and engineering checks, not CI green checkmarks.


## Review-output subfolder contract

The integrated report publisher now writes a structured, local/read-only audit evidence package rather than two loose files. Its stable folders are `00_OVERVIEW` (full JSON), `01_TRACKED_FILES` (CSV register), `02_DEPENDENCIES` (import graph), `03_FINDINGS` (consolidated open issues), `04_ACCEPTANCE` (separated static and native gates), `05_OUTPUT_WRITERS` (candidate writer counts), and `06_SECURITY` (current-tree redacted summary). A root README explains limitations. The new synthetic test checks each folder and retains the explicit `NOT_VERIFIED` native engineering gate. This audit layout is separate from, and must not displace, the canonical per-case stage output folders under the selected ETABS export.


## Coordinated follow-up — provenance plus standalone engineering benchmark gates (2026-11-15)

**Discovery before edits:** inspected current `main` tracked tree, `AGENTS.md`, `engineering/rules/CORE_RULES.md`, `ENGINEERING_GATES.md`, current V31 integrated source and tests, actual `src/thesis_core/neutral_model.py`, `src/opensees_engine/standalone.py`, standalone caller `tools/run_standalone_benchmark.py`, and unit/adapter tests. GitHub source searches found no other direct callers of the neutral-model API beyond the documented opt-in runner and tests. This remains a focused semantic review of that active subsystem, **not** a claim every active module was manually reviewed.

**Confirmed source defects corrected together (prototype only):**

- The contract previously accepted disconnected extra nodes despite supporting exactly one two-node member. The new fail-closed rule rejects non-two-node input before OpenSees domain setup; no hidden fallback to a multi-member formulation is allowed.
- `True`/`False` previously passed the six-bit fixity test as integers in Python; booleans now fail. Element and connected load-node tags must be actual integers, not booleans or unhashable containers. A nonmapping element/load receives `ValueError`, not an accidental `AttributeError`/`TypeError`. Provenance description must be a nonblank string.
- Six-component reactions were recorded but only three global force equations independently checked. An additional equilibrium gate now evaluates all three global moments about the fixed model origin, including `r × F` lever arms and explicit nodal moments. A fake solver with balanced force but missing reaction moment fails closed. The result adds an explicit `moment_residual_kNm` field, preserving existing `force_residual_kN` and solver status names.

**Tracked-file provenance strengthened:** `tools/audit_repository_integrated.py` now reads exact stage-0 Git-index mode and blob SHA for every tracked path using `git ls-files --stage -z`, records the current checked-out revision (or `UNBORN_HEAD` for synthetic fixtures), and groups byte-identical Git blobs without opening or relocating historical paths. Added `07_ARCHIVE_PROVENANCE/exact_blob_duplicates.json` to organized audit artifacts and `git_mode`/`git_blob_sha` to `01_TRACKED_FILES/tracked_file_register.csv`. These SHA values identify **indexed Git objects**, not unsaved working-tree edits. Matching blob SHA is evidence of exact identity, not approval to delete or rename a working runtime.

**Focused regressions:** `tests/verify_standalone_neutral_model.py` adds disconnected-node refusal before solver calls, bool restraint/tag checks, unhashable connection/load checks, malformed source/load checks, separate force-vs-moment residual tests; `tests/test_repository_integrated_audit.py` verifies staged blob identities, deduplication, CSV columns and the new `07_ARCHIVE_PROVENANCE` output. CI must pass before any static acceptance claim. Real OpenSeesPy, Windows/Spyder GUI, source ETABS EDB, ground motions, 32/76/97 supports and wall element 110280 remain out of scope.

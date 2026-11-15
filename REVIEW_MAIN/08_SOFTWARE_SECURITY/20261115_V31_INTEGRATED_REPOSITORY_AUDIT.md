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


### CI-verified follow-up — coordinated benchmark and Git provenance (commit `78c2c8ddb82c8f9780577749bb8b176a2d31b468`)

- [Integrated source and output audit](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43688867468): **PASS**, including synthetic strict-topology/fixity/load validation, force and moment-balance tests and Git-index duplicate inventory tests. The generated complete ZIP artifact ID is `14151253023`; its JSON/CSV content was independently read after download.
- [Repository compilation and navigation](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43688867387): **PASS**.
- [NLTHA Python quality](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43688867386): **PASS**, **not** full-building nonlinear transient execution.
- [Literature provenance](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43688867398): **PASS**.

**Actual indexed baseline from the CI artifact:** **3,039 tracked files**; **530 active Python files**, clean static parse/compile and zero unresolved explicit local imports; `static_audit=PASS`, native ETABS/OpenSees/NBC acceptance still `NOT_VERIFIED`. `07_ARCHIVE_PROVENANCE/exact_blob_duplicates.json` lists **405** exact-object duplicate groups, of which **384** include at least one historical snapshot. Cross-checking the generated register showed **zero exact-duplicate groups containing two active root/`components/`/`src/`/`tools/` Python modules**. Historical duplicates must not be removed automatically; original old manifests, links, imported names and readers still require ownership review. Git object IDs are source-index provenance, not a confirmation that every historical numerical result is correct.

**Acceptance distinction:** the focused prototype changes and audit artifacts have passed headless software regression. The comprehensive code-by-code inspection of all 530 Python files, actual 25-storey structural modeling, support and load transfer verification, first-step NLTHA investigation, complete M0–M6 motion matrix and Windows Spyder GUI functional evidence remain explicitly **OPEN**.


## V32 coordinated active engineering+inventory follow-up — 2026-11-15

**Repository baseline:** `a9c00c2b5d30e8ad4962b41dea0f094d865eb00b`, 3,040 tracked paths, 530 active Python sources; not a claim that all 530 were semantically reviewed. Read `AGENTS.md`, cross-agent engineering/migration rules, current integrated scanners, source guides, gravity analysis GUI caller `GravityAnalysisGUI.run_both_wall_supports()`, `components/gravity/support_scenarios.py` and the existing mock cases in `tests/verify_gravity_support_scenarios.py` before making changes.

**Confirmed related defects:**

1. `tools/audit_tracked_review_coverage.py::_category` failed to classify `src/` modules as active Python despite V31 integrated scanner recognizing them. It also assigned historical `Verification_V159`, `Worked_Example_V132` and `Research_Components` to generic OTHER. This is a measurable provenance/risk-prioritization inconsistency, not a numerical code flaw.
2. `compare_wall_support_gravity` checked that each saved `support_vertical_reaction_kN` agreed with its own node reaction sum, while allowing both totals to disagree significantly with `applied_vertical_load_kN`. These mismatched-but-internally-consistent reaction records could yield an apparently completed 76/97-support comparison. This is a confirmed software verification weakness, **not** evidence the current native ETABS/OpenSees runs suffer that particular mismatch.
3. Geometry mismatch was checked only among support reaction tags. Shared nonreaction nodes could move between cases while the method still compared reaction deltas as if they belonged to an identical geometric model. The check is expanded to all shared node tags. Legitimately generated additional continuous-base mesh tags remain permitted.
4. The comparison's explanatory sentence claimed "Only restraints differ" although elemental stiffness, mass and applied spatial load distributions were not independently compared. The corrected text explicitly distinguishes intended study design from verified identity. Also corrected the output-only status typo `SOURCE_ONLY_ONLY` → `SOURCE_ONLY` (source-data rows themselves untouched).

**Numerical preflight gate:** each case's summed finite support-node Rz must match reported applied gravity within `max(0.01 kN, 1e-6 × |applied kN|)`, separately from cached reaction sum reconciliation. This is a **local solver force-balance consistency check**; it cannot establish 32/76/97 support equivalence, ETABS native mesh restraints, wall load transfer, correct seismic mass or NBC design acceptance. If this gate fails, no aggregate sensitivity comparison is to be presented. Preserve original raw case JSON/log evidence for triage; never change the model to force equilibrium.

**Regression coverage and CI:** add adversarial cases for reaction total versus applied mismatch, changed nonreaction geometry, source-only label, `src` classification and historic snapshot types. Run the gravity comparator regression inside conda-forge based `repository-integrity.yml` (openpyxl used for Excel output), and coverage regression inside integrated CI. All user EDB/XLSX/ground motions and original case outputs remain untouched.

**Remaining independent gates:** native three-case support/geometry/restraint comparison, original Excel Aw/T1/EDB SHA integration, ESM/MRSM model mass and drifts, 25-storey X-wall first-step NLTHA, complete M0–M6 full-duration sensitivity and Windows Spyder GUI usability. No static Python pass can close these gates.


## V32 final static gate verification — commit `11c7638119c5f09f43c18861afff587dfd207959` (2026-11-15)

The coordinated gravity and tracked-file categorization change was committed as `c994fd68989f0c5a0863d53a8bea56630d8bd9c9`. Its first NLTHA Python-quality run [failed](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43689880952) on a **new test fixture**: the synthetic SOURCE_ONLY test accidentally deleted source reaction node 2, then attempted to assert a result row for that nonexistent node. No native engineering model data or production solver inputs were changed. Commit `11c7638119c5f09f43c18861afff587dfd207959` retains source reactions node 1 = 80 kN and node 2 = 40 kN; the continuous case totals 90+30 = 120 kN, so both maintain 120 kN downward applied gravity. The expected `SOURCE_ONLY` row is now physically and logically present.

**Final six checks (all passed):**

- [Integrated inventory/structured source review](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43690030077) — SUCCESS.
- [Whole-Git tracked coverage inventory](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43689880929) — SUCCESS on the preceding source revision (classifications identical on the corrective fixture-only commit).
- [Repository compilation and navigation, with gravity scenario regressions](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43690030045) — SUCCESS.
- [NLTHA Python quality, including gravity scenario synthetic tests](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43690030098) — SUCCESS.
- [Windows source/output contract smoke](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43690030059) — SUCCESS; not interactive ETABS/Spyder.
- [Literature provenance audit](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43690030055) — SUCCESS.

The [integrated GitHub artifact](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43690030077) was downloaded and its `00_OVERVIEW/integrated_audit.json` inspected: **3,042 Git-tracked paths, 530 active Python files, zero active parser failures, zero explicit unresolved local imports, zero current-tree secret pattern candidates, `static_audit=PASS`**. Four static import-cycle candidate groups remain review-required, and 96 legacy output literal occurrences remain migration candidates, not confirmed failing writers. All original source files and numeric assumptions are untouched.

**Engineering acceptance remains blocked:** the 32/76/97 physical restraint representation, independently sourced ETABS gravity comparisons, slab and wall load paths, nonlinear X-wall first-step element 110280, ESM/MRSM NBC105 design matching, real ground-motion full-duration M0–M6 runs, and native Windows UI operation were not executed during this static test pass. Do not interpret these software-only checks as resolved physical discrepancies.


## 2026-11-15 coordinated mesh-source and disk-output audit review

**Scope:** selected 02_MODEL 4/8/16 ShellMITC4 preparation/staging and read-only diagnostics inventories. Inspected existing consumers `components/gravity/load_path_formulas.py` (referenced launcher), `components/gravity/mesh_cases.py`, `tools/audit_output_storage.py`, their source guides, current tests, source-origin policy, and integrated CI. This is **focused active source semantic inspection**, not line-by-line review of all 530 Python files.

**Confirmed issues:** (1) `stage_case` previously followed symlinked required/optional saved ETABS sources; it created the case run without retaining the original source SHA separately from the mesh-derived output config; (2) `prepared_configs` could write the MESH_04 config before discovering that the MESH_08 destination was an external linked file; (3) disk-usage audits could silently follow a linked root when resolving their input/output path. The corrections refuse redirected path components before output creation and compare source/copy hashes, recording source hashes separately. They preserve all numeric input parameters, originals and legacy paths.

**Verification:** New non-native regressions in `tests/test_model_mesh_case_workflow.py` and `tests/test_output_storage_audit.py` are included in the integrated whole-tree CI workflow. Source, workbook, native solver and GUI acceptance gates remain **NOT_VERIFIED** pending actual local Windows ETABS/OpenSees execution. Never infer gravity or modal agreement from static copy hashes or staged mesh status.


### 2026-11-15 initial integrated CI regression failure and corrective fixture

The first integrated run for commit `7f675504bfed6e1cbad3c4cf7149a8b1f6acdbd5` ([CI run 43691290142](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43691290142)) **failed** in `test_source_and_derived_config_have_separate_digest_evidence`. Cause: the synthetic test compared `original_source_file_sha256` only with the four REQUIRED_SOURCE files, but the fixture deliberately also provided optional `ETABS_Materials.csv`; source staging correctly included it. The test now explicitly verifies the union of required and present optional file source SHA256 records, instead of weakening the implementation by excluding optional input provenance. No production mesh source or physical parameter was changed in this corrective fixture commit. Validation outcome is only PASS after the rerun itself completes successfully.


## 2026-11-15 coordinated forensic ZIP snapshot integrity review

**Verified source scope:** `components/ui/organized_results.py`, its existing 10+ static test fixtures in `tests/test_organized_results.py`, `components/inputs/output_layout.py`, cross-stage existing archive/reader behavior and `docs/source/components/ui/organized_results.py.md`. Three related source defects were identified: (a) empty snapshot directories could be created before discovering no eligible evidence; (b) the actual source-file hash was first measured **after** copying, so source mutation during publication was not checked against an independent initial fingerprint; and (c) redirected selected source/gravity roots and latest-pointer symlinks could be resolved or written without explicit refusal. These are corrected as preflight checks plus a full original-vs-copy-vs-postcopy comparison, retaining legacy paths and all existing archive names/metadata fields. A new integrated CI regression group covers empty input, concurrent source modification and linked source/latest pointer. **Native analysis and confidential payload approval remain OPEN**; this correction must not be mistaken for solver validation or automatic safe-public-upload screening.


### 2026-11-15 confirmed cross-module review acceptance (commits `7f675504`, `8ac9194d`, `c3c67cb1`)

- Mesh staging, original-versus-derived source SHA identity and linked-source/output regression corrections: `7f675504bfed6e1cbad3c4cf7149a8b1f6acdbd5`, with the optional `ETABS_Materials.csv` test fixture corrected in `8ac9194de3a5bc851aac6ce1bf461ec0d9fc7ddb`. [Integrated CI after fixture correction — PASS](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43691409876).
- Forensic snapshot publisher: source prehash, linked-root/latest-pointer refusal, and no empty snapshot directory on missing evidence: `c3c67cb11c40af6abf20ac43d51ac695d234cf2e`. The new source-change-during-copy test checks that no invalid result becomes the latest pointer. [Integrated source/output CI — PASS](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43691792284).
- [Repository compile/navigation — PASS](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43691792273); [NLTHA Python QA — PASS](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43691792298); [literature provenance — PASS](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43691792327). These are source-based checks and do not establish native solver convergence, model identity, 32/76/97 foundation support equivalence, or NBC 105 engineering acceptance.

The unified audit artifact is published by the integrated CI under `00_OVERVIEW`, `01_TRACKED_FILES`, `02_DEPENDENCIES`, `03_FINDINGS`, `04_ACCEPTANCE`, `05_OUTPUT_WRITERS`, `06_SECURITY`, and `07_ARCHIVE_PROVENANCE`. Original solver stage outputs are left in place. No current private ETABS case source is uploaded to the public repository.


## 2026-11-15 semantic coverage expansion and saved gravity-result integrity

**Discovery:** The prior `tools/audit_active_repository.py` inventory compiles active files but captures only top-level functions/classes, while `tools/audit_tracked_review_coverage.py` deliberately records every tracked blob as not reviewed. No per-method/nested-function completeness register existed. New `08_SEMANTIC_REVIEW/function_review_register.csv` contains one module-level unit for each active source plus every AST class, function, async function and nested definition (including functions inside match/conditional branches). Columns: source path, exact Git-index SHA, qualified symbol, start/end source lines, indicative calls and bare exception handlers, explicit review status, reviewer, evidence. **All units remain `NOT_REVIEWED` until supported human/function review**; the program does not turn AST parsing into semantic approval. Acceptance `function_level_semantic_review=INCOMPLETE_NOT_EXECUTED` and `semantic_review_completed_count=0` are deliberately strict. This creates a demonstrable exhaustive *review checklist*, not a claim of completed 530-file semantics.

**Confirmed gravity case defect:** `components/gravity/reaction_case_registry.py::register_case/current_case` previously checked source model SHA and numerical totals while rereading a selected solver result. Two nodal reaction values could be modified by equal and opposite amounts, preserving both totals and case metadata, yet be shown as registered historical evidence. The code now records and rechecks exact solver-result bytes by SHA256 and refuses legacy index entries without this fingerprint until they are explicitly re-registered. New tests exercise a modified but equal-total 32-node reaction distribution and the absence of a registered digest. This is evidence integrity, **not** verification of true native restraint geometry, analytical stiffness or load path.

**Remaining strict gates:** Full function-by-function semantic inspection of all active sources and their runtime callers, numerical ETABS/OpenSees comparison for original 32 support nodes, 76/97 support strategies, ShellMITC4 load transfer, X-wall first-step NLTHA element 110280, whole 25-storey M0–M6 histories, and NBC105:2025 acceptance remain unverified unless separately executed and documented. No source EDB or original Excel workbook is modified.



## 2026-11-15 systematic source snapshot and 59 facade contract triage

A repeatable code-only GitHub Actions artifact from commit `a539ba5c865f41384e0b2ba62234f363f67f2abd` was downloaded, checked byte-for-byte against `REVIEW_MANIFEST.json`, and locally inspected. It contains **532 active Python files and 3 public governance files** without original EDB/XLSX/ground motions/archived runs. In the full public source tree, **59** root Python facades call `exec(compile(...))` to load a `components/` implementation into the facade's global scope. All 59 targets were found in the current source snapshot. This changes the meaning of `__file__` in the implementation, making naive `Path(__file__).parents[2]` module-root computations inconsistent between direct imports and root aliases. Four concrete vulnerable call paths were corrected together: `components/inputs/analysis_autofill.py` (authoritative workbook and modal compatibility lookups), `components/response_spectrum/model_analysis.py` (MRSM project-input root), `components/ui/building_exploratory_gui.py` (isolated one-storey subprocess cwd), and `components/gravity/gui_and_reports.py` (live clear-beam rebuild script location). The `_runtime_repo_root` helper within each affected component reads the actual facade `_component_source` when defined; direct imports continue using their module source location. Root 01–21 launchers, generated model paths, existing readers and numerical inputs remain intact.

The integrated audit now emits `09_FACADE_COMPATIBILITY/facade_source_context.csv`, recording all root exec facades, their mapped implementations, indexed Git blob identities and every implementation location containing `__file__` for future caller-by-caller review. Presence of a facade or source reference is **a static review candidate**, not a proven runtime failure. The new `tests/test_facade_runtime_context.py` verifies direct, facade and exported-runtime path resolution without ETABS/OpenSees or GUI execution. This is a coordinated architectural correction and **not** complete semantic inspection of all 3,900+ functions.


## Follow-up direct-versus-facade root contract review (2026-11-15)

Current public active source snapshot was opened and inspected (532 Python files, three governance Markdown files, exact SHA256 manifest from commit `a539ba5c865f41384e0b2ba62234f363f67f2abd`). Root `exec(compile(...))` compatibility aliases were traced against their actual implementation modules. In addition to the first four confirmed path-context defects, six related function/caller root mismatches have now been corrected together: `components/inputs/project_workbooks.py` (original approved workbook/private registry discovery), `components/model/assembly.py` (direct-call runtime default plus modal input populate), `components/modal/gui_and_reports.py` (generated modal runner's module search root and source workbook), `components/validation/irregularity_review.py` (source workbook and subprocess module root), `components/ui/literature_demo_gui.py` (benchmark input/launcher root), and `components/ui/window_manager.py` (root decision/source review documents). The reviewed code now consistently derives project root from the real implementation `_component_source` when run by a root facade, or the real module `__file__` when imported normally. All project numeric constants, source model/Excel inputs, GUI launcher names and generated standalone scripts remain unchanged.

The linked `tests/test_facade_runtime_context.py` regression now covers **ten concrete implementations**, each in direct-import, root-facade and exported-runtime-facade settings. Other facade/source occurrences are not automatically changed; their use of `__file__` may intentionally refer to a generated script or selected output, and each needs separately grounded caller review. This is **actual semantic review of this bounded source-root contract**, not full review of all active Python functions. Production ETABS/OpenSees and original thesis physics gates remain `NOT_VERIFIED`.

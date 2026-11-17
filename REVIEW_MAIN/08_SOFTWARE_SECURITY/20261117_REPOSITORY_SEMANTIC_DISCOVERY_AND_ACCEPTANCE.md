# 2026-11-17 — repository-wide semantic discovery and release gates

## 0. Evidence status

**DISCOVERY/STATIC REVIEW IN PROGRESS — NOT COMPLETE NATIVE SEMANTIC OR ENGINEERING VALIDATION.**

Original base: `main` commit `c2bc828e5b34fc04698ea005a8fdc9b3e72db8c9` on 2026-11-17. GitHub recursive tree `fe96a3db824fe43f2fbdf35ebed8478e48d6b2c9` was **not truncated**: 3,685 tree entries, 3,149 blob files, 786 Python files and 1,268 Markdown files. The counts are GitHub snapshot data, not measured from the user's Windows machine.

Existing `tools/audit_active_repository.py` parses/compiles root Python plus components/src/tests/tools but records only *top-level* imports. A helper called from a GUI callback can import a missing module only at click-time without appearing in its dependency inventory. Existing `tools/audit_repository_layout.py` lists Git-tracked filenames and static root references, but cannot certify safe file moves or path consumers. Existing documentation coverage checks verify guide paths, not semantic content. These tools should be retained, not mislabeled as complete engineering analysis.

## 1. Source class and review depth

| Source | Initial Git tree entries | Review method | Release meaning |
| --- | ---: | --- | --- |
| `docs/` | 1066 | source links, integrity and provenance; audit docs against current code | documentation coverage only |
| `Saved_Project_V156/` | 566 | preserved snapshot, version and checksums, never production substitution | historical |
| `tests/` | 230 | parse/compile, executable regression and test source traceability | software evidence |
| `components/` | 200 | active AST + nested imports, targeted manual engineering review and dynamic tests | production critical |
| `Worked_Example_V132/` | 168 | preserved examples and benchmark provenance | literature/example only |
| `REVIEW_MAIN/` | 166 | issue history and acceptance register; preserve each analysis case folder | unresolved/accepted separately |
| `excel/` | 147 | workbook provenance, formulas and model audit references | not live source code |
| `archive/` | 122 | integrity and dependencies before any move/delete | archived |
| `Research_Components/` | 120 | benchmark provenance, not production | research-only |
| `Verification_V159/` | 96 | reference experiment source versions | historical tests |

Counts are tree entries and include directories. The machine-readable audit further classifies every Git-tracked file and hashes active Python source (SHA256) without storing file content or private absolute paths.

## 2. Consolidated static findings and decisions

| ID | Priority | Finding | Confidence | Action / gate |
| --- | --- | --- | --- | --- |
| AUD-001 | P1 | Existing active inventory misses function-local imports and literal `importlib.import_module` calls | confirmed by direct code inspection | Add recursive AST dependency graph, unresolved local candidate register and synthetic tests |
| AUD-002 | P1 | Root-level and nested script dependency/entrypoint reachability not established by source guide existence | verified limitation | Do not declare full review from navigation or documentation tests; inspect actual dependency graph and run native GUI callback tests |
| AUD-003 | P1 | Existing broad static file relocation scans cannot prove dynamic path consumers | verified limitation | NO bulk moves/deletions; keep folder skeleton and defer migration until writer/reader compatibility is demonstrated |
| AUD-004 | P0 engineering | 32/76/97 ETABS/OpenSees gravity reactions redistribute at 44 wall-edge nodes despite global weight equilibrium | prior repository audit numerical evidence, **not re-run here** | Export native ETABS analysis-element restraints, wall base force cuts and map OpenSees shell forces; keep gate open |
| AUD-005 | P0 engineering | NLTHA first-step X wall element 110280 localForce non-finite; material/calibration and source-mesh equivalence unresolved | prior project records, **not re-run here** | Isolated patch/material/P-Delta and no-motion trials before full M0–M6 publication |
| AUD-006 | P1 software | Previous source converter 1,614.536-s gravity formula workbook stage was deferred in PR #94 | merged code and historical log; **runtime recovery unverified** | Compare Windows before/after runtime with source EDB hash and 4×4 mesh invariants |
| AUD-007 | P1 security/provenance | Public repo contains generated historical and benchmark artifacts, potentially misleading if treated as current model output | structural tree classification, not a secret finding | Preserve history; no unreviewed disclosure or file moves; use model/source SHA gate for results |

## 3. Output and folder ownership

Canonical local analysis root remains the selected EDB export case. Ownership is by `01_ETABS_EXPORT`, `02_GRAVITY`, `03_ESM`, `04_MODAL`, `05_MRSM`, `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY`, plus existing `00_PROCESSING_METADATA` and software diagnostic sections. The folder layout is enforced by existing output-contract and reader compatibility tests. File renaming/relocation is NOT an acceptable substitute for fixing the upstream writer and every consumer.

Repository-scoped outputs: `audit/repository_semantics.json` (generated CI artifact, not checked-in case evidence), `docs/source/tools/audit_repository_semantics.py.md` (audit specification) and `REVIEW_MAIN/08_SOFTWARE_SECURITY/` (human triage and acceptance). Do not reorganize preserved `Saved_Project_`, `Verification_`, worked examples or thesis literature merely to look neat.

## 4. Acceptance gates

- **G0 / inventory:** Git source tree complete, tracked metadata counted, role of every tracked entry defined; all active sources SHA256 fingerprinted.
- **G1 / static dependency:** Every active Python source parse/compile passes; missing local imports are listed and investigated; dynamic GUI callbacks assessed separately. Advisories do not automatically block.
- **G2 / software integration:** Canonical numbered workflow and GUI callbacks, ETABS source export, model assembly, output writer/reader, profile warnings, action buttons and module imports pass regression tests.
- **G3 / gravity:** ETABS source joint restraints, generated mesh/MPC, global source-to-assembled mass and wall/column support region force/moment resultants match adopted tolerances for independently solved 32/76/97 cases. Current: **FAIL/UNVERIFIED**.
- **G4 / dynamics:** NBC 105:2025 code assumptions, adopted IS P-Delta special cases, modal X/Y, ESM/MRSM base shear/element force/drift, LTHA ground motions, complete NLTHA and source hashes verified on native Windows system. Current: **NOT CERTIFIED**.
- **G5 / security/privacy:** Unredacted EDB/XLSX/source locations/results/secrets excluded; no new unmanaged generated files at repo root; append-only evidence preserved. Current: requires separate live scan.
- **G6 / release:** Green CI on exact PR SHA, independent diff review, no physical code changes without native acceptance; unresolved issues explicitly documented. A static CI pass never changes G3/G4 to PASS.

## 5. Follow-up review sequence

1. Collect CI artifact `audit/repository_semantics.json` from PR workflow, evaluate each genuinely unresolved local import and inspect its source/call site.
2. Rank active Python by dependency centrality and workflow criticality: import/assembly, gravity, modal, ESM, MRSM, linear and nonlinear runners, source ID mapping, GUI/event hooks, security/output routing.
3. Fix independently reproducible software bugs one at a time with failing-to-passing tests, keeping all historical numerical outputs unaltered.
4. Run Windows ETABS and OpenSees with source-matched EDB, model config, gravity and physical acceptance; attach private evidence externally, not in public GitHub.
5. Keep the review register OPEN until function-level and engineering acceptance is demonstrably complete. No declaration of "fully audited/validated" is made by this discovery PR.

## 6. Provenance and limitations

Only repository code, filename metadata and prior documented gravity/solver evidence were available. The private Windows EDB, full raw solver model/results and 531 MB workbook were not executed or evaluated in this static audit. GitHub CI can check syntax/dependency/provenance and Linux-compatible unit tests, but cannot certify ETABS v23 OAPI and nonlinear physical calibration.

## 7. Audited CI discovery evidence and confirmed workflow defects

The first expanded GitHub Actions run on the audit branch reported **3,154 tracked files** (five new tracked audit artifacts on top of the 3,149-file baseline), 348 active runtime Python modules, 225 test Python modules, 1,216 historical snapshot files, 1,362 tracked non-Python files and 3 other provenance-only Python files. The source graph contained 1,038 local dependency edges. After correcting PEP 420 namespace and relative `__init__` handling, active parsing/compilation and resolvable local import checks both reported **zero exceptions**. This is a *static gate only*.

The analyzer reports 147 advisory patterns: 71 dynamic `exec`/`eval` calls and 76 pass-only exception handlers. Manual GitHub code search shows that many dynamic-execution calls are **root compatibility facades** that execute local component module code to preserve older exported source contracts; they are not automatically arbitrary command injection. Several exception suppressions are intentional cleanup or GUI parsing fallbacks, but they need contextual review on critical paths. Do not automatically remove them. The priority queue identifies `components/inputs/project_workbooks.py` (63 import edges), `components/inputs/output_contract.py` and `components/inputs/output_layout.py` (44 each), plus the numbered export/GUI facades and engineering assembly code as central modules.

**CI-001 CONFIRMED:** The `.github/workflows/repository-integrity.yml` multi-command block did not stop after a failed Python test. Earlier Actions jobs returned green despite explicit `FAILED (failures=1)` in logs. The audit branch now sets `set -euo pipefail` and enables `--fail-on-active-errors`; this is a genuine continuous-integration reliability correction. This strict gate subsequently exposed two pre-existing brittle Plotly regression assertions:
- `tests/test_assembled_mesh_view.py` compared an unescaped literal `4×4` to Plotly's JSON-escaped Unicode title. The visual model was unchanged; assertion now checks the serialized title.
- `tests/test_source_view_compaction.py` compared a list of expected triangle indices to a tuple of identical values, triggering a false failure. The test now compares equivalent tuple representations.

These fixes concern **tests and CI correctness**, not physical ShellMITC4 element formulation or ETABS load flow. All later CI tests must still be run under strict exit handling before any merge.

## 8. Review hold points

- Open: specific root compatibility `exec` facades and ignored exceptions in gravity/export, modal, ESM/MRSM and NLTHA require targeted manual trust-boundary audit; code-search advisories are not proof of attack.
- Open: all gravity/analysis outputs must retain source model SHA, exact load pattern and support labels; static output folder inventory cannot certify old consumer compatibility after renames.
- Open: equivalent wall support regions, ETABS native analysis joints, material and damper benchmark calibration, NBC 105:2025 code-purpose matrix and full nonlinear completed history acceptance remain native-model gates.
- The new `audit/repository_semantics.json` is an ACTIONS ARTIFACT; it must not be committed as a research result nor conflated with a final physics review.

# Consolidated Repository Semantic Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development to implement this plan task-by-task. Checklist state is evidence-based; don't mark unsolved native engineering gates done.

**Goal:** Review all tracked repository files systematically, fix proven software defects with regression evidence and maintain honest function-level/native-engineering acceptance states.

**Architecture:** Use the existing authoritative `tools/audit_repository_integrated.py` and `audit/integrated/` output tree, plus `tools/audit_active_repository.py`, output writer audits, `REVIEW_MAIN/` and GitHub issue #75. Do not create a parallel inventory. Existing `08_SEMANTIC_REVIEW/function_review_register.csv` contains source-tagged *not-yet-reviewed* function units for detailed future verification.

**Tech Stack:** Python 3.12, stdlib AST/Git, openpyxl/Plotly test dependencies, GitHub Actions, native Windows ETABS/OpenSeesPy for structural and time-history acceptance.

**Spec:** User's 2026-11-17 repository-wide semantic audit request; `AGENTS.md`, `docs/00_THESIS_ACCEPTANCE_GATES.md`, `REVIEW_MAIN/README.md`, GitHub issue #75.

## Global constraints

- Preserve all EDB/XLSX original files and public/private result boundaries.
- Keep actual 4×4 ShellMITC4 model, gravity/ESM/MRSM/NLTHA calculations, source restraints and 32/76/97 comparison cases unchanged without native engineering evidence.
- Active code and tests: detailed dependency/contract inspection; historical snapshots and docs: integrity, provenance, references; do not claim all functions were manually reviewed.
- Maintain one canonical `audit/integrated` system and review register, no duplicate root-level tools or unsafe bulk moves.
- Current CI acceptance is **static/automated only**. Native physical-model checks remain explicitly unverified.

## Review focus

- Function-local and constant literal dynamic imports, including package submodules and missing local targets.
- Root compatibility facades with `exec(compile(...))`, their source identity and `__file__` context.
- Every GUI callback's lazy inputs/outputs and exception propagation.
- Gravity wall-edge support representation, load source, mesh/beam/wall transfer, 32/76/97 native source restraints.
- M0–M6 nonlinear material/device calibration and full completed XY/YX records.

---

### Task 1: Authoritative inventory and dependency gap

**Modify:** `tools/audit_repository_integrated.py`, `tests/test_repository_integrated_audit.py`

- [x] Confirm complete untruncated Git tree: base 3,149 tracked blobs.
- [x] Inspect existing integrated scanner before adding anything; avoid duplicate report generation.
- [x] Add synthetic failing test for `importlib.import_module("components.package.module")` and literal `__import__` inside deferred functions.
- [x] Extend existing graph with those static edges and missing-target candidates; dynamic variable import remains review only.
- [ ] Verify integrated CI output against the full tracked repository and review literal dynamic candidates.

### Task 2: Correct actual CI reliability defects

**Modify:** `.github/workflows/repository-integrity.yml` and failing unit assertions.

- [x] Confirmed old workflow could report success despite Python `FAILED (failures=1)` logs.
- [x] Add per-command failure accounting with nonzero end-of-job exit.
- [x] Repair incorrect Plotly Unicode/list-vs-tuple test assertions, invalid-UTF8 fixture and outdated launcher action count, without changing physics.
- [ ] Run complete aggregate suite on exact PR SHA and inspect **every** failed command.
- [ ] Make regression test demonstrate fail-state propagation and avoid falsely green CI.

### Task 3: Consolidated review and native-engineering acceptance

**Modify:** `REVIEW_MAIN/08_SOFTWARE_SECURITY/20261117_REPOSITORY_SEMANTIC_DISCOVERY_AND_ACCEPTANCE.md`, `REVIEW_MAIN/README.md`.

- [x] Classify production, test, archived and documentary sources.
- [x] Document high-centrality source modules, 32/76/97 issue, wall-first-step failure, source identity and output contracts.
- [ ] Record exact integrated audit snapshot counts/findings and review each high-priority advisory with source line and test evidence.
- [ ] Keep engineering acceptance gates OPEN until source-matched Windows ETABS/OpenSees and experiment comparison evidence is supplied.

### Task 4: Branch verification and integration

- [ ] Run full focused CI and integrated tracked source audit; all tests must pass on the exact head SHA.
- [ ] Review diff to ensure source physics and runtime data paths have not been changed unintentionally.
- [ ] Merge only validated software audit and test corrections to `main`.
- [ ] Keep issue #75 open for function-by-function semantic review and native physics acceptance.

## Acceptance gates

G0: whole Git tree accurately classified with immutable Git blobs.
G1: active Python imports/compilation and facade targets pass.
G2: test failures propagate; all CI checks pass; no stale data consumers introduced.
G3: 32/76/97 ETABS vs OpenSees reaction equivalence verified physically (CURRENTLY OPEN).
G4: NBC 105:2025 dynamic and nonlinear response, calibration and full records verified (CURRENTLY OPEN).
G5: no private files/secrets or unapproved output migrations.
G6: exact PR head checks green, independent code diff reviewed, unresolved issues documented.

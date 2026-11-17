# Repository-Wide Semantic Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Obtain a reproducible, SHA-scoped, evidence-ranked inventory of all tracked thesis repository files, identify production dependency and semantic review risks, safely fix demonstrable defects, and document engineering acceptance gates without treating static CI as native solver validation.

**Architecture:** Extend existing repository audits, not replace canonical folder routing. A new standard-library-only static checker reads tracked Git paths, recognizes active Python/test/historical artifacts, parses *nested* imports and dynamic literal imports, verifies local module resolution, and records risky patterns as human review candidates. Engineering review and corrections stay on an isolated GitHub branch; generated report files are GitHub Actions artifacts under `audit/`, not tracked numerical results.

**Tech Stack:** Python 3.12 (conda-forge); stdlib ast, pathlib, subprocess, hashlib/json, unittest; GitHub Actions on Ubuntu for static tests; native Windows ETABS v23/OpenSees and NBC 105:2025 required for physical checks.

**Spec:** User request, 2026-11-17; existing `AGENTS.md`, `docs/00_THESIS_ACCEPTANCE_GATES.md`, `REVIEW_MAIN/README.md`.

## Global Constraints

- Never upload, move or rewrite source EDB/XLSX, confidential model files, ground motions, solved results, LFS data or archived evidence.
- Preserve 4×4 model mesh and 32/76/97 diagnostic support alternatives; no unverified changes to mass, gravity, material or nonlinear solver.
- Distinguish ACTIVE_RUNTIME, TEST, HISTORICAL, documentation and generated/snapshot evidence; static checks cannot declare engineering equivalence.
- Reuse existing project audit output root `audit/`; use `REVIEW_MAIN/08_SOFTWARE_SECURITY/` for discrepancies and source/evidence review.
- Every significant change requires a reproducible before/after test; blockers prevent merge. All physically significant changes are out of scope until native engineering acceptance.

## Review Focus

- Nested/dynamic imports that are not recorded by the current top-level-only AST audit.
- Lazy GUI callbacks whose targets do not exist until clicked, source-missing Python modules.
- Historical snapshots mislabelled as active code, duplicated run entry points.
- Generated outputs/paths with unresolved readers or stale mixed source-model provenance.
- Security hazards (shell=True/eval/pickle) that require review but must not be auto-labelled as exploitation.

---

### Task 1: Inventory and dependency discovery

**Files**
- Create: `tools/audit_repository_semantics.py`
- Test: `tests/test_repository_semantics_audit.py`
- Output: `audit/repository_semantics.json` (CI artifact)

**Interfaces:** `audit_repository(root: Path) -> dict`; `main(argv=None) -> int`.

- [ ] Add failing fixture tests for deep imports, unresolved local imports, historical files and no external path leakage.
- [ ] Implement tracked-path metadata, SHA-256, active and historical categories, recursive AST imports, static-risk triage.
- [ ] Run tests on synthetic tree, then full checkout in CI; fail only confirmed active missing local dependencies and parse/compiler failures.
- [ ] Emit a reproducible JSON report and small, publicly safe terminal summary; review actual violations.

### Task 2: Consolidated output and engineering acceptance matrix

**Files**
- Create: `REVIEW_MAIN/08_SOFTWARE_SECURITY/20261117_REPOSITORY_SEMANTIC_DISCOVERY_AND_ACCEPTANCE.md`
- Update: `REVIEW_MAIN/README.md`
- Update: `.github/workflows/repository-integrity.yml`

- [ ] Add precise coverage/classification method, issue statuses and limits.
- [ ] Record required native gravity/ESM/MRSM/LTHA/NLTHA acceptance gates, source hashes, numerical tolerances and unverified issues.
- [ ] Add CI command and artifact retention, no source-model result commits or path migrations.

### Task 3: Independent review and release

- [ ] Review CI failure details and source-specific cases; fix only confirmed software defects with tests.
- [ ] Compare branch diff against original main and check no numerical physics modules were modified without evidence.
- [ ] Mark coverage status honestly: inventory != complete line-by-line semantic review; native validation remains unresolved.
- [ ] Merge only with all relevant CI green, then record commit and open risks.

## Acceptance Gates

- **G0 Inventory:** no Git tree truncation; all tracked Python paths classified and historic paths kept provenance-only.
- **G1 Static:** no unreadable/syntax-invalid active Python; confirmed local imports resolve or are documented optional runtime plugins.
- **G2 Integration:** launcher, GUI callback, source/reader output contracts, original regression suite and tracking tests pass.
- **G3 Physics:** gravity reaction wall-base resultants and 32/76/97 source restraining evidence reconciled; no passing test currently certifies this.
- **G4 Dynamics:** eigen/ESM/MRSM/LTHA/NLTHA uses original model SHA, load and mass, code choices, solver completion and native Windows runs.
- **G5 Security/provenance:** no secrets/source EDB or private outputs committed; originals remain unchanged and outputs under canonical analysis stage roots.
- **G6 Release:** branch reviewed, checks passed, only then merge; unresolved work itemized without "full engineering pass" claims.

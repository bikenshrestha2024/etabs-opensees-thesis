# NBC 105:2025 Multi-Agent Clause 1–10 Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate the Codex/Claude/ChatGPT NBC 105:2025 clause changes into ten source-grounded, individually owned, tested and auditable Python modules without changing validated engineering behavior silently.

**Architecture:** The sole numerical authority for each NBC clause lives in `components/nbc105/clause_NN_<slug>.py`; existing ESM, MRSM, linear time-history, nonlinear time-history and GUI paths call these pure-Python modules via narrow adapters. Each clause has a page-by-page matrix, a source guide, hand-derived tests, parity tests, and explicit open native-model gates.

**Tech Stack:** Python 3.12 (conda-forge), pytest, ETABS 23 OAPI on user Windows machine, OpenSeesPy/XARA for independent analysis, GitHub Actions.

**Spec:** `docs/nbc105/README.md`, `AGENTS.md`, `docs/nbc105/PROJECT_DECLARATIONS.md` and NBC 105:2025 printed Clauses 1–10. Read the source PDF pages; neither workspace chat claims nor unit tests are substitutes for the printed standard.

## Global Constraints

- Do not upload private EDBs, support reactions, project spreadsheets or ground motions to public GitHub.
- Follow printed NBC clause text, footnotes, tables and units. If ambiguous, record the original wording and a review question; never guess.
- Keep IS 16700 supplementary and project-declared only; see `AGENTS.md`.
- No changed ETABS load patterns, spectrum coefficients, wall groupings, supports, solver model, or Rayleigh adopted periods without before/after numerical evidence.
- Existing launcher and public import paths must remain compatible; avoid circular imports.
- Pin source model hashes and distinguish code regression from physical engineering validation.
- Do not claim 'complete' until every clause has source matrix, implementation coverage, branch integration, and verified callers.

## Snapshot / conflicts to reconcile first

At GitHub `main` SHA `3125564e4861e67a7d5c7ac3d623ef52a8859009` (2026-11-21), **3,299 tracked files and 616 active Python files** were reported by the native integrated audit. Dedicated modules currently exist only for clauses 1, 4 and 5; the register explicitly marks 2, 3, 6, 7, 8, 9, 10 as `NOT_STARTED`. An earlier assistant's workspace-only report claiming complete Clause 5–10 module implementation is NOT evidence those modules reached `main`.

Open PRs #126, #127, and #128 overlap main's clause 1/4/5 code, provenance, documents and tests. They must be rebased/diff-reviewed against current main before any merge. Do not blindly merge all branches; recover only additions not already present and check for semantic regressions.

CI on SHA `3125564e` has a **failed** 'Integrated tracked-tree, dependency and output review' job: `tools/audit_repository_integrated.py --repo . --output audit/integrated --fail-on-static-blockers` exits 2, reporting stale/unsafe source-review attestations, legacy output references, static import cycles and persistent physics acceptance gates. The separate headless pytest and native Rayleigh CI checks passed; that does not mean the integrated audit passed.

## Review Focus

1. Conflicting newer branch and main implementations: compare by Git SHA and exact function behavior, not by author names; tests must assert existing output parity.
2. Clause 5 midpoint-weight allocation versus saved Rayleigh evidence: reconstruct source level weights and invalidate incompatible historical cache rather than silently reusing old periods.
3. Clause 7 force scaling must not contaminate original MRSM drift/displacement; test separate unscaled response path.
4. Clause 9 nonlinear wall element 110280 first-step failure: tests must preserve failure provenance and never label partial history runs complete.
5. Clause 10 Table 10-1 `a_p`: source table, period-difference boundary values and printed footnotes must be verified independently; missing table entries or ambiguous equality must block acceptance.

---

### Task 1: Establish a conflict-free canonical clause register

**Files:** Update `docs/nbc105/README.md`, `engineering/registry/CANONICAL_MODULES.csv`; add `tests/test_nbc105_clause_register.py`.

**Interfaces:** Produce ten records containing clause number, canonical module path, source page range, matrix, source guide, pytest, integration state, and native-evidence state.

- [ ] Write failing tests asserting unique 1–10 clause ownership and that every claimed `INTEGRATED` entry exists with its matrix, guide and verified calling sites.
- [ ] Run `python -m pytest tests/test_nbc105_clause_register.py -q`; expect RED on incomplete claims.
- [ ] Implement the register with truthful `NOT_STARTED`, `PARTIAL`, `INTEGRATED`, `NATIVE_PENDING` states, without creating empty modules merely to satisfy counts.
- [ ] Run the focused test and commit.

### Task 2: Source-verify Clauses 1–4 and repair baseline conflicts

**Files:** Existing `components/nbc105/clause_01_scope_definitions.py`, `clause_04_seismic_hazard.py`; create clause 2 and clause 3 modules and matching source matrices, guides and tests.

**Interfaces:** Pure numerical rule functions and explicit requirements/status dataclasses; active code remains adapter-only.

- [ ] Transcribe printed Clauses 2 and 3 into one-row-per-requirement matrices with citation and implementation status.
- [ ] Write baseline/boundary tests for scope applicability, accidental torsion, stiffness modification, seismic design category, load combinations, SLS/ULS and applicability to 95 m building, using exact printed provisions.
- [ ] Implement clause 2 and clause 3 rule functions only after tests and source verification. Do not assume an IS 16700 exception is an NBC rule.
- [ ] Verify `is_soft_story` strict 70% / 80% boundaries with exact equality cases and production parity; fix any floating-point threshold error before merge.
- [ ] Run parity tests for existing spectrum and zoning/site classification; reject nonfinite Z and incomplete site-profile evidence where required.
- [ ] Commit each reviewed clause independently.

### Task 3: Complete Clause 5, including actual Rayleigh mass/COM proof

**Files:** `components/nbc105/clause_05_dynamic_characteristics.py`, `components/modal/rayleigh.py`, `components/modal/rayleigh_mass_audit.py`, `components/model/assembly.py`, `components/inputs/project_workbooks.py`; clause 5 matrix and focused tests.

**Interfaces:** Authoritative `storey_index_for_elevation(z_m, floor_elevations_m)` and adopted-period / seismic-weight functions. Stored mass ledgers and imported Rayleigh reports must declare compatible mass, gravity and model config versions.

- [ ] Add midpoint and exact-elevation boundary tests, and an end-to-end source mass-ledger reconstruction test.
- [ ] Verify authentic 12 m wall grouping and Aw dimensions against ETABS first-storey sections; preserve 6 m alternate as a sensitivity case only.
- [ ] Verify `g=9.81` NBC Rayleigh quotient and distinguish the earlier 9.80665 mass conversion; prevent cache reuse with mismatched mass/elevation provenance.
- [ ] Compare reference load `Fi`, retained diaphragm translations and physical COM displacements with native ETABS/XARA at matched gravity/P-Delta state.
- [ ] Do not convert a passing synthetic 1D Rayleigh test into a full 25-storey equivalence claim.
- [ ] Commit after source and full regression checks.

### Task 4: Canonicalize Clause 6 ESM

**Files:** Create `components/nbc105/clause_06_equivalent_static.py` and associated matrix/guide/tests; adapt `components/equivalent_static/calculation_and_gui.py`.

**Interfaces:** Period-bound `C_d(T_1)`, design seismic weight, base shear, `k`, per-level `F_i`, torsional actions and both ULS/SLS branches, pure functions accepting verified source inputs.

- [ ] Source-derive each Eq./Table 6-1 numeric and boundary test from printed pp. 38–39.
- [ ] Implement one cumulative floor-force path reused by CSV, chart, GUI and workbook.
- [ ] Verify 25-storey floor-force total / distribution against saved ETABS snapshots **using matching model hashes**.
- [ ] Preserve distinction between pre-PDelta seismic base shear and governing case reactions.
- [ ] Commit.

### Task 5: Canonicalize Clause 7 MRSM

**Files:** Create `components/nbc105/clause_07_modal_response_spectrum.py`, matrix/guide/tests; adapt existing `components/modal/analysis.py` and MRSM paths.

**Interfaces:** Modal participation, CQC, grouped SRSS where permitted, missing-mass decision/procedure, code base-shear scaling with **force-only** output and original displacement/drift channels.

- [ ] Write spectrum/mode-pair and near-degenerate-frequency tests from printed pp. 40–41.
- [ ] Compare ETABS native Ritz modes, mass participation and missing-mass policy before enabling numerical outputs.
- [ ] Assert that adjusting force design scaling never changes saved unscaled drift and displacement values.
- [ ] Commit.

### Task 6: Canonicalize Clause 8 elastic time history

**Files:** Create `components/nbc105/clause_08_elastic_time_history.py`, matrix/guide/tests; route existing linear time-history preflight/report outputs.

**Interfaces:** Input record requirements, damping, discretization, scaling, pair-response combination and service/ultimate acceptance statuses.

- [ ] Verify record count, duration, scale bounds, time step, damping and combination rules from printed pp. 42–43.
- [ ] Add invalid-record, wrong-units, wrong-direction and truncated-duration negative tests.
- [ ] Run matched-record validation on source-bound case (not a synthetic sample) before marking ready.
- [ ] Commit.

### Task 7: Canonicalize Clause 9 nonlinear static/dynamic

**Files:** Create `components/nbc105/clause_09_nonlinear_analysis.py`, matrix/guide/tests; retain native model calibration in nonlinear subsystems.

**Interfaces:** N2 pushover target and both-signed lateral patterns, nonlinear time-history input/convergence/status summaries, distinct 'partial' vs 'full-duration' run stamps.

- [ ] Verify source Eq. and limitations from printed pp. 44–48.
- [ ] Preserve P-Delta and inelastic constitutive state and demonstrate single-wall first-step finite force/convergence first.
- [ ] Validate 224 full histories by unique model/record/direction/time span with raw logs; never infer completion from manifest or stub.
- [ ] Commit only verified pure-rule part without claiming physical convergence.

### Task 8: Canonicalize Clause 10 and Table 10-1

**Files:** Create `components/nbc105/clause_10_parts_and_components.py`, matrix/guide/tests; then adapt related component-force checks.

**Interfaces:** `component_amplification_factor(building_period_s, component_period_s, ...)` with source-defined Table 10-1 threshold behavior, component force `F_p`, importance `I_p`, `W_p`, connection check and Tables 10-2/10-3.

- [ ] Check original Table 10-1 image, exact `a_p` values, threshold endpoints, period-difference interpretation and footnotes. No approximated table values before checking the printed table.
- [ ] Add hand-verified boundary tests for equal periods, inner threshold, endpoint and beyond-range behavior; invalid/nonfinite periods must fail closed.
- [ ] Implement Table 10-1 once; no second table embedded in spreadsheet, GUI or nonlinear code.
- [ ] Validate Tables 10-2/10-3 component categories, importance, attachments and force combinations with independent unit tests.
- [ ] Commit.

### Task 9: Cross-module integration and final acceptance

**Files:** `docs/nbc105/README.md`, `docs/nbc105/PROJECT_DECLARATIONS.md`, `engineering/registry/CANONICAL_MODULES.csv`, new clause calling-path tests, CI workflows.

- [ ] Audit imports and actual call sites; assert each source equation is owned by only one clause module.
- [ ] Run `python -m pytest -q`, `python tests/verify_ref_tags.py` and `python tools/audit_repository_integrated.py --repo . --output audit/integrated --fail-on-static-blockers`.
- [ ] Resolve stale source attestation only after verifying attested function bytes; address static import cycles and output migration with real owners.
- [ ] Run native ETABS/OpenSees parity gates for mass, gravity, Rayleigh, modes, supports, ESM/MRSM, time-history and wall convergence on the user's Windows machine.
- [ ] Merge PRs only after independent source review and mandatory CI; record exact SHA, PASS/FAIL/SKIP and unresolved technical limitations.

# NBC 105:2025 clauses 1-3, Annex C, g = 9.81 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put clauses 1, 2 and 3 of NBC 105:2025 (in that order), Annex C Table C-1 and the Figure 4-3 zoning data into `components/nbc105/` with matrices, tests and docs; restore g = 9.81 per printed p. 7; make Vs,30 optional for the thesis while documenting the clause requirement; record the UBC/SEAOC wall-grouping sources.

**Architecture:** Same pattern as clauses 4 and 5: one module per clause under `components/nbc105/`, a compliance matrix under `docs/nbc105/`, hand-computed tests, parity tests against existing implementations, a module guide under `docs/source/components/nbc105/`, a registry row and an agent_edits note. Data tables (Annex C) live in a CSV data file plus a thin loader module.

**Tech Stack:** Python 3 (Windows/Spyder compatible), pytest, existing repo test tooling.

**Spec:** the user's messages of 2026-11-21 (summarised under Global Constraints) and the PDF `/mnt/user-data/uploads/3aaf535f-NBC_105_2025_Seismic_Design_of_Buildings_in_Nepal_lqqvx6a_2.pdf`. Page offset: printed N = PDF N+21 up to printed p. 26, +23 from printed p. 27 (contents list is PDF 15-21). Read `docs/nbc105/README.md` first: it holds the procedure, naming convention and page-offset method.

## Global Constraints

- g: use 9.81 m/s2 everywhere (NBC 105:2025 notation list, printed p. 7, "to be taken as 9.81"). Supersedes the earlier USER_DECISION of 9.80665. Single source `components/nbc105/constants.py`; every module that converts weight to mass routes through it (including `tools/etabs_period_review/reconcile.py`).
- Vs,30: optional for this thesis (USER_DECLARED 2026-11-21), but the clause 4.1.3 requirement (mandatory above 40 m; Table 4-3 default-D rule) stays documented exactly and the code must not silently drop it: it must report the requirement as a documented issue/warning, not raise.
- Clause order: 1, then 2, then 3. Each clause: read the printed pages from the PDF images, transcribe every requirement into the matrix with printed page, module with `[REF NBC105-2025 ...]` tags, hand-computed tests, parity tests against existing implementations, matrix status columns, `docs/source` guide, `engineering/registry/CANONICAL_MODULES.csv` row, agent_edits section (model UNKNOWN).
- Table 3-1 has no RC slab entry: IS 16700 is used for the slab (user instruction). Cite IS 16700 only from a source present in the repo or fetched and read in this task; record edition/clause/table. If the value cannot be verified, write `REFERENCE DETAILS PENDING` and do not invent a number.
- No duplication: one implementation per rule inside `components/nbc105/`; existing production copies are guarded by parity tests, not rewritten, unless the printed text proves them wrong (list before/after numbers).
- Preserve CRLF/LF per file; Windows/Spyder compatible; do not modify source EDBs, `Saved_Project_V156/`, solver, material or damping numerics; never label solver/unit-test PASS as engineering acceptance.
- Tests: `python -m pytest -q` (baseline after PR #127: 1321 passed, 34 skipped) and `python tests/verify_ref_tags.py`. New modules need `[REF ...]` docstring tags and a `docs/source/<path>.md` guide.
- Commit trailers (blank line before): `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, `Claude-Session: https://claude.ai/code/session_017mBtraFUtWaW28cxEzcjz7`, `AI-Assisted-By: Claude Code`, `AI-Model: not recorded`, `Engineering-Validation: unit tests only, no native ETABS/OpenSees`.

## Review Focus

- Saved Rayleigh results recorded with 9.80665 after the g revert: behaviour and the I1 import note must stay truthful (the note appears only when the saved g differs from the constant).
- Annex C transcription errors (swapped digits, shifted rows, merged names, Nepali/English spellings, duplicates, rows spanning pages): total row count, per-page counts and every Z value must match the printed table.
- Vs,30 optional must not change results for existing inputs that supply Vs,30, and must not hide the mandatory-above-40 m requirement.
- Table 3-1 values applied to the right element and slab handled via IS 16700 without silently using a Table 3-1 number.
- Docs duplication or contradictions between README, PROJECT_DECLARATIONS, matrices and guides (g value, page offsets, status words).

---

### Task 1: Restore g = 9.81 and make Vs,30 optional with documented requirement

**Files:**
- Modify: `components/nbc105/constants.py`, `components/nbc105/clause_04_seismic_hazard.py` (`select_soil_type`), `tools/etabs_period_review/reconcile.py`, every module that defines or uses 9.80665 (find with `rg -n "9\.80665" --glob '!Saved*' --glob '!*.md'`), tests that pin 9.80665, `docs/nbc105/PROJECT_DECLARATIONS.md`, `docs/nbc105/clause_04_seismic_hazard_matrix.md`, `docs/nbc105/clause_05_dynamic_characteristics_matrix.md`, `docs/nbc105/README.md`, `components/inputs/project_workbooks.py` (import note wording only), `engineering/agent_edits/20261121_nbc105_clauses_1_3_annexc.md` (create).
- Test: `tests/test_nbc105_constants.py`, `tests/test_nbc105_clause04.py`, `tests/test_rayleigh_saved_g_note.py`, plus any test that pinned 9.80665.

**Interfaces:**
- Consumes: `components.nbc105.constants.GRAVITY_M_S2`, `NBC_NOTATION_GRAVITY_M_S2`; `select_soil_type(*, height_m, vs30=None, n_spt=None) -> dict` with keys `soil`, `basis`, `issues`.
- Produces: `GRAVITY_M_S2 == 9.81 == NBC_NOTATION_GRAVITY_M_S2`; `select_soil_type` no longer treats a missing Vs,30 above 40 m as an error: it returns `issues` containing a documented-requirement entry (code `VS30_REQUIRED_ABOVE_40M_NOT_SUPPLIED`, text citing clause 4.1.3.1 and "optional for this thesis, USER_DECLARED 2026-11-21"), and `soil` is still None unless n_spt (or another basis) supplies one; Vs,30 supplied above 40 m behaves as before.

- [ ] **Step 1: Write failing tests**: `GRAVITY_M_S2 == 9.81`; no remaining 9.80665 literal outside docs history (a scan test over `components` and `tools`); `select_soil_type(height_m=95, vs30=None, n_spt=20)` returns the documented issue code and does not raise; with `vs30=300` no such issue; the saved-g note test updated: a saved result with g=9.81 imports cleanly with no gravity note, one with 9.80665 shows the cause note.
- [ ] **Step 2: Run them, confirm failure.**
- [ ] **Step 3: Implement.** Change the constant; route every weight-to-mass site and `reconcile.py` through it; adjust `select_soil_type` and its docstring; adjust the import-note wording so it is symmetrical (names both values).
- [ ] **Step 4: Documentation.** PROJECT_DECLARATIONS: g = 9.81 per printed p. 7 (supersedes 9.80665 decision; keep the 0.0341 % history as a superseded note, results saved with 9.80665 are rejected on import and must be re-run); Vs,30 optional as USER_DECLARED with the exact clause requirement quoted by paraphrase and page; matrices updated; README link. Create the agent_edits note with a Task 1 section.
- [ ] **Step 5: Run `python -m pytest -q` and `python tests/verify_ref_tags.py`, all pass. Commit "Restore g = 9.81 per NBC 105:2025 p. 7; make Vs,30 optional with documented requirement".**

### Task 2: Clause 1 Title, Scope, Definitions and Notations (printed pp. 1-9)

**Files:**
- Create: `components/nbc105/clause_01_scope_definitions.py`, `docs/nbc105/clause_01_scope_definitions_matrix.md`, `docs/source/components/nbc105/clause_01_scope_definitions.py.md`, `tests/test_nbc105_clause01.py`.
- Modify: `engineering/registry/CANONICAL_MODULES.csv`, `docs/nbc105/README.md` (register row), `docs/source/00_SOURCE_GUIDE_INDEX.md`, agent_edits note.

**Interfaces:**
- Consumes: `components.nbc105.constants`.
- Produces: the machine-checkable parts of clause 1 only: scope applicability (what building types/heights/structure types the code covers and excludes, as stated), the printed notation symbols that the repo uses (symbol, meaning, unit, printed page; as a data table, not prose), and `scope_check(...)` helpers only if the clause states checkable limits. Definitions that are prose-only go to the matrix as `DEFINITION_ONLY` rows.

- [ ] **Step 1: Read printed pp. 1-9 (PDF 22-30, verify offset on each page); transcribe every clause row into the matrix.**
- [ ] **Step 2: Failing tests** pinned to printed values (notation table entries including g = 9.81 on p. 7 and any numeric scope limits), plus rejected inputs.
- [ ] **Step 3: Implement the module; audit existing code for scope/notation misuse (symbols whose repo meaning or unit differs from the printed notation): list findings in the matrix, parity-test where a production copy exists.**
- [ ] **Step 4: Matrix status columns, guide, registry row, README register (status CLAUSE_1), agent_edits section; run the full suite and ref-tag check; commit "Add NBC 105:2025 clause 1 scope, definitions and notations module, matrix and tests".**

### Task 3: Clause 2 General Principles (printed pp. 10-16)

**Files:** same pattern: `components/nbc105/clause_02_general_principles.py`, `docs/nbc105/clause_02_general_principles_matrix.md`, `docs/source/components/nbc105/clause_02_general_principles.py.md`, `tests/test_nbc105_clause02.py`; modify registry, README register, source-guide index, agent_edits.

**Interfaces:**
- Consumes: Task 2's notation table (no duplicated symbols).
- Produces: the checkable principles of clause 2 (design philosophy, limit states, performance objectives, irregularity classifications and limits, regularity checks, structural-system rules, load-path and similar rules; whatever the printed pages contain) as data tables and validated helpers; non-checkable prose rows as `PRINCIPLE_ONLY`.

- [ ] **Step 1: Read printed pp. 10-16 (PDF 31-37; verify each page); transcribe every requirement into the matrix.**
- [ ] **Step 2: Failing hand-computed tests for every numeric rule/threshold (both sides of each limit) and rejected inputs.**
- [ ] **Step 3: Implement; audit existing repo checks of the same rules (regularity/irregularity, torsion, drift, stiffness, ductility) and add parity tests; list mismatches with before/after numbers.**
- [ ] **Step 4: Matrix, guide, registry, README (CLAUSE_2), agent_edits; full suite + ref tags; commit "Add NBC 105:2025 clause 2 general principles module, matrix and tests".**

### Task 4: Clause 3 Scope of Analysis (printed pp. 17-21) including Table 3-1 and IS 16700 for RC slab

**Files:** `components/nbc105/clause_03_scope_of_analysis.py`, `docs/nbc105/clause_03_scope_of_analysis_matrix.md`, `docs/source/components/nbc105/clause_03_scope_of_analysis.py.md`, `tests/test_nbc105_clause03.py`; modify registry, README register, source-guide index, agent_edits; create `docs/nbc105/IS16700_RC_SLAB_STIFFNESS.md` (source record).

**Interfaces:**
- Consumes: Tasks 2-3 tables where cross-referenced; clause 4/5 modules are not modified.
- Produces: every rule of clause 3 as code or matrix row: scope of analysis, Table 3-1 (all rows/columns, with the element each applies to), 3.6 limit-state combinations (every combination with its factors), 3.7 working-stress combinations, 3.8 bearing-pressure increase; `slab_stiffness_source()` returning a record that states IS 16700 governs the RC slab, with the verified edition/clause/value or `REFERENCE DETAILS PENDING`; no Table 3-1 number may be returned for a slab.

- [ ] **Step 1: Read printed pp. 17-21 (PDF 38-42; verify each page); transcribe into the matrix; find IS 16700 in `LITERATURE`/repo records or by web search (read the source; record edition, clause, table; copyright: cite and paraphrase only).**
- [ ] **Step 2: Failing tests: every Table 3-1 entry and every load-combination factor pinned literally from the printed pages, boundary/rejected cases, slab returns IS 16700 record and never a Table 3-1 value.**
- [ ] **Step 3: Implement; audit existing repo implementations (load combinations in model/ETABS setup, stiffness modifiers, allowable-bearing increase) and add parity tests; list mismatches with before/after numbers; do not change model numerics without listing them.**
- [ ] **Step 4: Matrix, guide, registry, README (CLAUSE_3), agent_edits; full suite + ref tags; commit "Add NBC 105:2025 clause 3 scope of analysis module, matrix, tests and IS 16700 slab record".**

### Task 5: Annex C Table C-1 and Figure 4-3 zoning data

**Files:** Create `components/nbc105/annex_c_zoning.py`, `components/nbc105/data/annex_c_table_c1.csv`, `docs/nbc105/annex_c_zoning_matrix.md`, `docs/source/components/nbc105/annex_c_zoning.py.md`, `tests/test_nbc105_annex_c.py`; modify `components/nbc105/clause_04_seismic_hazard.py` only to expose a lookup that delegates to the Annex C loader (no duplicate data), registry, README register, agent_edits.

**Interfaces:**
- Consumes: clause 4 `default_soil_type_d` naming conventions (reuse its normalisation; do not duplicate).
- Produces: `z_factor_for(district, municipality)` -> float (raises KeyError with close-name suggestions for unknown names), `annex_c_rows()` -> list of dict (province, district, municipality, Z, printed page); Figure 4-3: a documented record of the printed map's contours/zones as printed (Z range 0.25-0.40) and the printed rule for using Figure 4-3 versus Annex C; interpolation is implemented only if the printed text prescribes it; otherwise record that none is prescribed.

- [ ] **Step 1: Locate Annex C (printed p. 100 onward; PDF = p+23 here, verify) and read every page. Extract the table text programmatically (pdftotext/pdfplumber if the PDF has a text layer) and verify against the page images for every page; record per-page row counts.**
- [ ] **Step 2: Write the CSV (all rows, exact spellings as printed, printed page column) and failing tests: total row count equals the sum of printed per-page counts; no duplicate (district, municipality); every Z in the allowed printed set; at least ten rows per page spot-pinned literally including first and last row of each page and the Kathmandu Valley municipalities.**
- [ ] **Step 3: Implement loader and lookups; Figure 4-3 record; delegate from clause 4.**
- [ ] **Step 4: Matrix (per-page counts, ambiguous/duplicated names, discrepancies between printed pages), guide, registry, README, agent_edits; full suite + ref tags; commit "Transcribe NBC 105:2025 Annex C Table C-1 and Figure 4-3 zoning data".**

### Task 6: UBC/SEAOC wall-grouping sources, clause-by-clause documentation

**Files:** Modify `docs/nbc105/WALL_GROUPING_AW_METHOD.md`, `docs/nbc105/PROJECT_DECLARATIONS.md`; create `docs/nbc105/WALL_GROUPING_SOURCES.md`.

**Interfaces:** Produces a source register for the wall-grouping (Aw) method: for each reference actually used (UBC 1997 §1630.2.2 and Eq. 30-9, SEAOC Seismic Design Manual Vol. I/III, SEAOC Blue Book latest edition, and any other the repo records), the exact edition, section/example/page, what it says about effective shear wall area/period, whether the source file is in the repo `LITERATURE` (path) or only found online (URL and access date), and the latest edition available online.

- [ ] **Step 1: Search the repo (`rg -n 'UBC|SEAOC' -i --glob '!Saved*'`, `REVIEW_MAIN/02_ESM/Aw_Validation/`, LITERATURE files) for every UBC/SEAOC record; read them.**
- [ ] **Step 2: Web search for the latest editions (SEAOC Blue Book 2019 or newer; the UBC 1997 as last edition and ICC archive access; ASCE 7 relation if relevant) and fetch what is publicly readable; paraphrase only, no long quotes; state anything that cannot be accessed.**
- [ ] **Step 3: Write the register and update the two docs; keep `REFERENCE DETAILS PENDING FROM USER` only where the user's own validation edition remains unknown, now phrased as a short confirmation list for the user.**
- [ ] **Step 4: Full suite + ref tags; commit "Document UBC and SEAOC sources for the wall grouping Aw method".**

### Task 7: Consistency audit across the NBC 105 documentation

**Files:** Modify any of `docs/nbc105/*.md`, `docs/source/components/nbc105/*.md`, `docs/NBC105_PERIODS_AND_MATERIAL_PROVENANCE.md`, `README.md`, `docs/00_REPOSITORY_ORGANIZATION.md`, `docs/source/00_SOURCE_GUIDE_INDEX.md`; create `tests/test_nbc105_docs_consistency.py`.

**Interfaces:** Produces a test that checks: every register row links to an existing module/matrix; statuses use one vocabulary; g appears as 9.81 in all NBC docs (history notes marked superseded); page-offset statements agree; every matrix row has a code location or an explicit `NOT_APPLICABLE`/`DEFINITION_ONLY`/`PRINCIPLE_ONLY`; no module under `components/nbc105/` lacks a guide and a registry row.

- [ ] **Step 1: Write the consistency test; run it and list the failures.**
- [ ] **Step 2: Fix duplicated, contradictory or stale statements in the docs (single source of truth per fact; link instead of repeating).**
- [ ] **Step 3: Full suite + ref tags; commit "Add NBC 105 documentation consistency test and fix discrepancies".**

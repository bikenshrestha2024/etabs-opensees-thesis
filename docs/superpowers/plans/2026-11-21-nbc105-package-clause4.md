# NBC 105:2025 Package, Clause 4 Audit and Project Declarations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every NBC 105:2025 main clause one module and one doc page under a uniform layout, start with clause 5 (moved) and clause 4 (new, audited line by line against printed pp. 21-27), and record the project declarations (no basement, wall grouping references, gravity constant).

**Architecture:** `components/nbc105/` package: `constants.py`, `clause_04_seismic_hazard.py`, `clause_05_dynamic_characteristics.py` (moved from `components/modal/nbc105_clause5.py`, which stays as a thin re-export shim). Existing implementations keep their public names; parity tests compare each against the clause module. Docs under `docs/nbc105/` (index, per-clause matrix, project declarations).

**Tech Stack:** Python 3.12 stdlib, pytest. No OpenSeesPy/ETABS/tkinter.

**Spec:** user messages 2026-11-21 (basement: none, use full height; wall grouping validated against UBC and SEAOC references, document all; gravity: use higher-precision g; "do for all NBC main clauses"; "check clause 4 pp. 21-27 line by line"). Authority: the user-supplied PDF `/mnt/user-data/uploads/3aaf535f-NBC_105_2025_Seismic_Design_of_Buildings_in_Nepal_lqqvx6a_2.pdf` (printed page N = PDF page N+21 for the body). Verified clause 4 text:
- §4.1.1 Eq. 4.1(1) `C(T) = Ch(T) Z I` (p. 22).
- §4.1.2 (p. 22-23): Ch(T) from Fig 4-1 (ESM) and Fig 4-2 (MRSM, nonlinear time history, vertical loading, parts and components) or Eq. 4.1(2): `1+(α-1)T/Ta` for T<Ta; `α` for Ta<=T<Tc; `α Tc/T` for Tc<=T<Td; `α Tc Td/T²` for Td<=T<=6. Table 4-1 (p. 24): Ta 0.1/0.1/0.1/0.5, Tc 0.5/0.7/1.0/2.0, Td 4.0/4.0/4.0/5.0, α 2.5/2.5/2.5/2.25 for soil A/B/C/D; footnote: Ta is zero for the Equivalent Static Method (Fig 4-1 is flat at α from T=0).
- §4.1.3 (p. 24-25): classify by Vs,30 if available, else N_SPT; for buildings taller than 40 m Vs,30 is mandatory; `Vs,30 = 30 / Σ(hi/Vi)` over the top 30 m. Table 4-2: A Vs>800; B 350<Vs<=800 (N>50, Cu>250 kPa); C 150<Vs<=350 (N 10-50, Cu 25-250); D Vs<=150 (N<10, Cu<25).
- §4.1.3.3 / Table 4-3 (p. 25-26): listed Kathmandu-Valley municipalities/wards are Soil Type D by default unless tests to 30 m show otherwise.
- §4.1.4 (p. 26): Z = PGA for 475 years, interpolated from Figure 4-3 (contours 0.25, 0.30, 0.35, 0.40) or taken from Table C-1 of Annex C for listed cities/municipalities (table wins over interpolation).
- §4.1.5 Table 4-4 (p. 26): importance class I 1.0, II 1.25, III 1.5; 1.5 applies to class II facilities used as disaster shelter.
- §4.2 (p. 27): `Cs(T) = 0.20 C(T)`. §4.3 (p. 27): `Cv(Tv) = 2/3 Z`, applied to horizontal members spanning >= 20 m, cantilevers longer than 5 m, prestressed horizontal members, beams supporting columns, base-isolated structures.
- Notation list (printed p. 7): "g: acceleration due to gravity, to be taken as 9.81 m/s²". The user instructed a higher-precision g; this is a recorded USER_DECISION deviation (9.80665, about 0.03 %).

## Global Constraints

- Preserve scientific source and existing public names; no change to solver/material/damping numerics; nothing under `Saved_Project_V156/`. Numeric changes only where printed text requires (list each in the agent_edits note with before/after).
- Windows/Spyder compatible; keep original line endings of every existing file touched (check with `git diff --stat`); tkinter files `py_compile` only.
- `[REF NBC105-2025 §x, printed p. N]` tags; guide in `docs/source/components/nbc105/*.md`; `CANONICAL_MODULES.csv` rows; agent_edits note `engineering/agent_edits/20261121_nbc105_package_clause4.md` (model UNKNOWN).
- User-attested facts (no basement; wall grouping validated against UBC/SEAOC; g choice) are recorded as `USER_DECLARED`, with the date 2026-11-21, never as verified by the agent. Cite only references that exist in the repo; where the UBC/SEAOC edition and section are not in the repo, write `REFERENCE DETAILS PENDING FROM USER` instead of inventing them.
- No document may call a code calculation engineering acceptance.

## Review Focus

- Ch(T) exactly at T = Ta, Tc, Td, 6 s for each soil (continuity), T = 0 for ESM (Ta treated as 0), T > 6 s (rejected or flagged, never extrapolated), negative/NaN T.
- Soil boundaries exactly at Vs,30 = 150, 350, 800 and N = 10, 50 (Table 4-2 inequality directions); Vs,30 absent for H > 40 m must be reported as a missing mandatory input; Kathmandu-Valley listed site must not be silently accepted as Soil C.
- All four existing Ch(T) implementations agree with the clause module on a dense T grid for all soils and both variants; any mismatch is a finding.
- `g` has one definition used by rayleigh.py, assembly.py and the clause modules.
- Shim import path `components.modal.nbc105_clause5` keeps working with identical names.

---

### Task 1: Package scaffold, constants, clause 5 move

**Files:**
- Create: `components/nbc105/__init__.py`, `components/nbc105/constants.py`, `docs/source/components/nbc105/constants.py.md`
- Move: `components/modal/nbc105_clause5.py` -> `components/nbc105/clause_05_dynamic_characteristics.py` (keep `components/modal/nbc105_clause5.py` as a shim re-exporting every public name); move its guide to `docs/source/components/nbc105/clause_05_dynamic_characteristics.py.md`; `git mv docs/validation/NBC105_CLAUSE5_COMPLIANCE_MATRIX.md docs/nbc105/clause_05_dynamic_characteristics_matrix.md` and fix every link
- Modify: call sites that import the clause 5 module (use the new path), `components/modal/rayleigh.py`, `components/model/assembly.py` (use the shared g), registry, source-guide index
- Test: `tests/test_nbc105_constants.py`, existing clause 5 tests updated to the new path plus a shim test

**Interfaces:**
- Produces: `components.nbc105.constants.GRAVITY_M_S2: float = 9.80665` (USER_DECISION, docstring states the printed p. 7 value 9.81 and the 0.0306 % difference), `NBC_NOTATION_GRAVITY_M_S2 = 9.81` (reference only, not used in calculations), `PRINTED_PAGE_OFFSET = 21`.
- Consumes: every public name currently in `components/modal/nbc105_clause5.py` (including `storey_index_for_elevation`).

- [ ] Tests: constant values; `rg -n "9\.81\b|9\.80665" components --glob '!Saved*'` scan test that fails if a numeric literal gravity appears outside `constants.py` in the files named above (list in the test the files checked); shim exposes identical `__all__`/public callables (identity `is` the new module's objects).
- [ ] Implement; make `rayleigh.py` (Eq. 5.1(1) g) and `assembly.py` (weight to mass) import `GRAVITY_M_S2`. Report any numeric change (Rayleigh T changes by about 0.015 %). Update the clause 5 matrix: the g row says USER_DECISION with both values.
- [ ] Run the full suite; commit.

### Task 2: Clause 4 module with hand-computed tests

**Files:**
- Create: `components/nbc105/clause_04_seismic_hazard.py`, `tests/test_nbc105_clause04.py`, `docs/source/components/nbc105/clause_04_seismic_hazard.py.md`
- Modify: registry

**Interfaces (Produces):**
- `TABLE_4_1: dict[str, dict[str, float]]` keys `"A","B","C","D"` with `Ta, Tc, Td, alpha` per Table 4-1 above; `T_MAX_S = 6.0`.
- `spectral_shape_factor(period_s: float, soil: str, *, method: str) -> float`; `method` is `"equivalent_static"` (Ta = 0, so Ch = alpha for 0 <= T < Tc) or `"dynamic"` (modal response spectrum, nonlinear time history, vertical, parts and components; full Eq. 4.1(2) with Ta from Table 4-1); raises ValueError for T < 0, NaN, T > 6, unknown soil/method.
- `importance_factor(importance_class: int, *, disaster_shelter: bool = False) -> float` (class 1 -> 1.0, 2 -> 1.25 or 1.5 if shelter, 3 -> 1.5).
- `elastic_site_spectrum(period_s, soil, z, importance_factor_i, *, method) -> float` = Ch Z I (Eq. 4.1(1)); `serviceability_spectrum(...)` = 0.20 x that; `vertical_spectrum_coefficient(z) -> float` = 2/3 Z; `VERTICAL_LOADING_CASES: tuple[str, ...]` the five clause 4.3 conditions as text.
- `vs30_from_layers(layers: Sequence[tuple[float, float]]) -> float` (thickness m, Vs m/s; thicknesses must sum to 30 within 1e-6, else ValueError) = 30 / sum(h/V).
- `soil_type_from_vs30(vs30: float) -> str`, `soil_type_from_n_spt(n: float) -> str`, `soil_type_from_cu(cu_kpa) -> str` per Table 4-2 inequalities.
- `select_soil_type(*, height_m, vs30=None, n_spt=None) -> dict` `{soil, basis ("Vs30"|"N_SPT"), issues:[str]}`; Vs30 preferred; if `height_m > 40` and Vs30 missing, `soil=None` and an issue `"Vs,30 is mandatory for buildings taller than 40 m (clause 4.1.3.1)"`.
- `KATHMANDU_VALLEY_SOIL_D_SITES: dict[tuple[str,str], frozenset[int] | str]` keyed `(district, municipality)` with the ward set or `"ALL"` or empty frozenset for Nil, transcribed from Table 4-3 (p. 26; keep the printed duplicate `32,32` as 32 and note the possible misprint in the docstring); `default_soil_type_d(district, municipality, ward=None) -> bool`.
- `zoning_factor_from_table(...)` is NOT created in this task (Annex C table not transcribed); `validate_zoning_factor(z: float) -> float` only checks finite and 0 < Z <= 0.4 per Figure 4-3 contours, with the docstring saying Annex C governs for listed municipalities.

- [ ] Write tests first with hand arithmetic from the printed table: Ch continuity at Tc and Td for all soils (e.g. soil C at T=2.0: alpha*Tc/T = 1.25; soil D at T=5 gives 2.25*2*5/25 = 0.9; soil B at T=4: 2.5*0.7/4 = 0.4375 and 2.5*0.7*4/16 = 0.4375), soil D ramp: T=0.25 gives 1+(2.25-1)*0.5/... use Ta=0.5 -> 1.625, ESM variant returns 2.25 at T=0 and 0.25, boundary soils, Vs30 formula example (layers 10 m at 200 and 20 m at 400 -> 30/(0.05+0.05)=300), importance classes, `0.20 C`, `2/3 Z`, rejection cases, Kathmandu lookups (Madhyapur Thimi any ward True; Kirtipur ward 10 True, ward 9 False; Budhanilkantha any ward False), taller-than-40 m mandatory-Vs30 rule.
- [ ] Implement; keep functions pure; docstrings with `[REF NBC105-2025 §4.x, printed p. N]`.
- [ ] Run tests, `python tests/verify_ref_tags.py`; commit.

### Task 3: Parity audit of existing clause 4 implementations and compliance matrix

**Files:**
- Create: `tests/test_nbc105_clause04_parity.py`, `docs/nbc105/clause_04_seismic_hazard_matrix.md`
- Modify (only if a mismatch with the printed text is proven): `components/response_spectrum/nbc105_dual_target.py` (`ch_modal_nltha`), `components/response_spectrum/site_spectrum_and_scaling.py` (`spectral_shape_ch`, `elastic_site_spectrum_g`), `components/equivalent_static/code_basis.py` and `legacy_code_basis.py` (`esm_spectral_shape_factor`, `soil_type_from_vs30`, `soil_type_from_n_spt`), plus any importance-factor, serviceability 0.20 and vertical 2/3 Z usage found by `rg`

**Interfaces:** Consumes everything from Task 2.

- [ ] Parity tests: for soils A-D and a T grid (0, 0.05, 0.1, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0 plus each Ta/Tc/Td +- 1e-9), compare each existing implementation (call with its real signature; read it first) against `spectral_shape_factor` for the variant it serves; compare soil classifiers on 149.999, 150, 150.001, 350, 350.001, 800, 800.001 and N 9.9, 10, 50, 50.1; locate importance, `0.2`, `2/3` constants by `rg` and add scan/behaviour tests. A failing parity test is a finding: first prove from the printed text, then fix the code minimally, keep CRLF endings, and list before/after in the agent_edits note.
- [ ] Matrix document: one row per printed rule (4.1.1, 4.1.2 eq and Table 4-1, footnote Ta=0 ESM, Fig 4-1/4-2 variant choice, 4.1.3.1 Vs30 vs N_SPT and the 40 m rule, 4.1.3.2 Vs30 formula, Table 4-2, 4.1.3.3 and Table 4-3, 4.1.4 Z, Table 4-4, 4.2, 4.3) with code location, test, status (`IMPLEMENTED_AND_TESTED`, `REFERENCE_ONLY` where production code does not call the clause module, `USER_RESPONSIBILITY` for site data, `NOT_TRANSCRIBED` for Annex C Table C-1 and Figure 4-3 interpolation). Add a "Project use" section: the repository's soil-C target spectra and the Kathmandu-Valley default-D rule of clause 4.1.3.3; state that Vs,30 testing is mandatory above 40 m and that soil C for a listed Valley site requires demonstrated test results; do not decide the project site.
- [ ] Full suite; commit.

### Task 4: Index, project declarations, wall-grouping documentation

**Files:**
- Create: `docs/nbc105/README.md` (index and clause register), `docs/nbc105/PROJECT_DECLARATIONS.md`, `docs/nbc105/WALL_GROUPING_AW_METHOD.md`
- Modify: `docs/00_REPOSITORY_ORGANIZATION.md`, `README.md` pointer, `docs/NBC105_PERIODS_AND_MATERIAL_PROVENANCE.md` links, source-guide index

- [ ] README: naming convention `components/nbc105/clause_NN_<slug>.py`, `docs/nbc105/clause_NN_<slug>_matrix.md`, `tests/test_nbc105_clause_NN.py`; a register table of every main clause 1-10 and Annex A-C with title and printed page read from the PDF's table of contents (the executor reads the contents pages from the user-supplied PDF, PDF pages 8-14 are the likely range; do not guess titles) and status (`CLAUSE_5`/`CLAUSE_4` = module + matrix; others `NOT_STARTED`); procedure to add a clause; link to the verification method (printed page = PDF page - 21).
- [ ] PROJECT_DECLARATIONS: `USER_DECLARED 2026-11-21`: (1) structure has no basement, so H is the full height from the base to the roof (Figure 5-1 exclusion not applicable; `base_z_m` must be the foundation/ground base and the code takes H = max node z - base_z_m); (2) wall grouping of Aw: validated by the user against UBC and SEAOC references (details pending); (3) gravity constant: `GRAVITY_M_S2 = 9.80665` per the user's instruction, deviation from printed p. 7 value 9.81 and its size; each item states what it affects (files/functions) and how to revert.
- [ ] WALL_GROUPING_AW_METHOD: describe what `components/inputs/grouped_wall_aw.py` and `aw_sources.py` actually do (read them; contiguous shell intervals, openings, gross vs net lengths, 0.9 limit, workbook override) and which repository references already exist (`rg -n "UBC|SEAOC" -i --glob '!Saved*'` and the LITERATURE folder). Quote none; cite titles/paths only. The user's UBC/SEAOC validation is recorded as USER_DECLARED with `REFERENCE DETAILS PENDING FROM USER` for edition/section unless the repo already contains them. State clearly that NBC 105:2025 §5.1.2 itself defines Awi as the effective first-storey wall cross-section area and Lwi as the first-storey wall length in the considered direction, and that its grouping around openings is not defined by the clause.
- [ ] Update the clause 5 matrix "Open items" (basement and wall grouping resolved as USER_DECLARED; g USER_DECISION) and the agent_edits note; full suite; commit.

# NBC 105:2025 Clause 5 Period Compliance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One tested source of truth for NBC 105:2025 clause 5 (printed pp. 28-30: §5.1.1 Rayleigh, §5.1.2 empirical, §5.1.3 amplification and lesser-of rule, §5.2 seismic weight), with every period call site routed through it and a compliance matrix document.

**Architecture:** New pure-Python module `components/modal/nbc105_clause5.py`; existing call sites keep their public names and delegate to it; the 1.25 factor becomes a fixed constant (a different user value is rejected or reported as a deviation, never silently applied).

**Tech Stack:** Python 3.12 stdlib, pytest. No OpenSeesPy/ETABS/tkinter.

**Spec:** user request 2026-11-21 ("page 28, 29 and 30 of NBC 105:2025 clause 5 ... must be fully followed"); clause text verified from the official PDF text: §5.1 lesser-of rule, §5.1.1 Eq. 5.1(1), §5.1.2 Eq. 5.1(2) with kt 0.075 concrete MRF / 0.085 steel MRF / 0.075 steel EBF / 0.05 other, concrete shear-wall kt from Aw with Lwi/H <= 0.9, H = base to roof with basement excluded only if basement walls connect to the ground-floor slab or sit between columns (Figure 5-1), §5.1.3 amplification 1.25, §5.2 Table 5-1 (storage 0.60, other 0.30, roof 0). The equation images were then read directly from the user-supplied PDF (PDF pages 49-53 = printed pp. 26-30) and match the implementation: printed p. 28 = §5.1, §5.1.1 Eq. 5.1(1); p. 29 = §5.1.2 Eq. 5.1(2), kt list, H definition and Figure 5-1 (a)-(d), Aw = sum_{i=1..Nw}[Awi{0.2+(Lwi/H)^2}], Awi first-story effective wall cross-section area; p. 30 = Lwi (first-story wall length in the considered direction, Lwi/H <= 0.9), Nw (walls in the considered direction), §5.1.3 (1.25 applies to the §5.1.2 approximate period), §5.2, Table 5-1. Status for these items is therefore VERIFIED_AGAINST_PRINTED_PAGE, not UNVERIFIED_IMAGE_ONLY. Existing doc: `docs/NBC105_PERIODS_AND_MATERIAL_PROVENANCE.md`.

## Global Constraints

- Do not change any numeric result at 1.25 amplification; existing tests must keep passing. Do not edit `Saved_Project_V156/`, solver, material or damping code.
- Windows/Spyder compatible; tkinter code edited minimally and checked with `python -m py_compile` (no tkinter here).
- `[REF NBC105-2025 §5.x, printed p. N]` docstring tags on every public function; `docs/source/components/modal/nbc105_clause5.py.md` guide; `CANONICAL_MODULES.csv` row (NEW_WITH_JUSTIFICATION, NOT_REVIEWED); `engineering/agent_edits/20261121_nbc105_clause5.md` (model UNKNOWN).
- A period is a design-input calculation, never engineering acceptance of the building.

## Review Focus

- `period_factor` other than 1.25 coming from a workbook cell or GUI field: shared function raises ValueError; the workbook autofill path must report a DEVIATION note and leave the period field unset, not crash.
- Lwi/H above 0.9 clamps to 0.9; zero or negative Awi, Lwi or H rejected.
- Missing Rayleigh period: adopted period is None with status INCOMPLETE, never silently the empirical value.
- Basement height: excluded only when the caller declares the Figure 5-1 condition true; default is to include it.
- Seismic weight roof live load is zero whatever the input.

---

### Task 1: Clause 5 module and tests

**Files:**
- Create: `components/modal/nbc105_clause5.py`, `tests/test_nbc105_clause5.py`, `docs/source/components/modal/nbc105_clause5.py.md`
- Modify: `engineering/registry/CANONICAL_MODULES.csv` (one row)

**Interfaces (Produces):**
- Constants: `AMPLIFICATION_FACTOR = 1.25`, `LWI_OVER_H_MAX = 0.9`, `KT_BY_SYSTEM = {"concrete moment-resisting frame":0.075,"steel moment-resisting frame":0.085,"steel eccentrically braced frame":0.075,"other structural system":0.05}`, `SHEAR_WALL_KT_NUMERATOR = 0.075`, `LIVE_LOAD_FACTORS = {"storage":0.60,"other":0.30,"roof":0.0}`.
- `building_height_m(top_z_m, base_z_m, *, basement_height_m=0.0, basement_excluded=False) -> float`: H = top - base; when `basement_excluded` is True the basement height is not part of H (caller supplies base_z at the ground-floor level OR passes basement_height_m, which is then subtracted, never below zero H); default includes it.
- `effective_wall_area_m2(walls: Iterable[tuple[float,float]], height_m) -> float`: walls are `(Awi_m2, Lwi_m)`; Aw = sum(Awi*(0.2+min(Lwi/H,0.9)**2)).
- `empirical_period_s(height_m, system_type, aw_m2=None) -> float`: `kt*H**0.75`; shear-wall system string contains `concrete shear-wall` and needs `aw_m2` (kt = 0.075/sqrt(aw)); unknown system -> ValueError.
- `amplified_period_s(empirical_s, factor=AMPLIFICATION_FACTOR) -> float`: raises `ValueError` if `factor != 1.25`.
- `adopted_period_s(empirical_s, rayleigh_s=None, factor=AMPLIFICATION_FACTOR) -> dict` `{amplified_s, rayleigh_s, adopted_s (None if rayleigh missing), status}` with lesser-of rule.
- `rayleigh_period_s(weights_kN, displacements_m, forces_kN, g=9.81) -> float` = 2*pi*sqrt(sum(W d^2)/(g sum(F d))); validates equal lengths, positive denominators.
- `seismic_weight_kN(dead_kN, storage_live_kN=0.0, other_live_kN=0.0, roof_live_kN=0.0) -> float` = dead + 0.6 storage + 0.3 other + 0 roof.
- `period_factor_deviation(factor) -> str|None`: None if factor == 1.25 else a DEVIATION message.

- [ ] **Step 1: Tests** in `tests/test_nbc105_clause5.py` with hand-computed values (write the arithmetic in the test): `test_kt_table`, `test_empirical_concrete_mrf` (H=25 -> 0.075*25**0.75), `test_empirical_shear_wall_uses_aw`, `test_aw_clamps_lwi_over_h_at_0_9`, `test_aw_rejects_nonpositive`, `test_amplification_is_1_25_and_other_rejected`, `test_adopted_is_lesser_of_rayleigh_and_amplified` (both orderings), `test_adopted_none_without_rayleigh`, `test_rayleigh_single_dof_equals_2pi_sqrt(m/k)` (W=m*g, F=k*d consistency), `test_seismic_weight_table_5_1_roof_zero`, `test_building_height_basement_rules`, `test_period_factor_deviation_message`.
- [ ] **Step 2:** run, expect import error. **Step 3:** implement. **Step 4:** run + `python tests/verify_ref_tags.py`. **Step 5:** commit.

### Task 2: Route call sites, deviation reporting, compliance matrix

**Files:**
- Modify: `components/modal/analysis.py` (`nbc105_period_estimate` delegates; same return keys/values), `components/modal/rayleigh.py:~196`, `components/inputs/analysis_autofill.py:74`, `components/equivalent_static/calculation_and_gui.py` (three sites: ~1252, ~1694, ~1752; field label stays but a factor != 1.25 raises/reports via the shared helpers), `components/inputs/grouped_wall_aw.py` and `aw_sources.py` only if they duplicate the 0.2+(L/H)^2 factor (reuse `effective_wall_area_m2` factor logic without behaviour change)
- Create: `docs/validation/NBC105_CLAUSE5_COMPLIANCE_MATRIX.md`, `tests/test_nbc105_clause5_callsites.py`
- Modify: `docs/NBC105_PERIODS_AND_MATERIAL_PROVENANCE.md` (link), `docs/source/00_SOURCE_GUIDE_INDEX.md` (guide), `engineering/agent_edits/20261121_nbc105_clause5.md`

**Interfaces (Consumes):** all Task 1 functions.

- [ ] **Step 1: Tests** in `tests/test_nbc105_clause5_callsites.py`: `test_estimate_matches_clause5_module` (nbc105_period_estimate numbers equal module numbers for shear-wall and MRF), `test_autofill_reports_deviation_for_factor_1_5` (extract `populate_linear` period block or the extracted helper; no tkinter), `test_no_literal_0_075_wall_formula_left_in_call_sites` (rg-style scan of the modified files for `.075*H**.75/math.sqrt` string patterns, allowing only `nbc105_clause5.py`). The existing suite must pass unchanged.
- [ ] **Step 2:** run, expect fail. **Step 3:** route the sites; where a site cannot be unit-tested (tkinter GUI) keep the edit to replacing the arithmetic with the shared call and run `python -m py_compile` on it.
- [ ] **Step 4:** write the compliance matrix: one row per rule (clause, printed page, requirement, code location, test name, status among `IMPLEMENTED_AND_TESTED`, `IMPLEMENTED_AND_TESTED` with the clause text verified against the printed page for Eq. 5.1(1), the shear-wall kt equation, Figure 5-1 text and Table 5-1, `CALLER_RESPONSIBILITY` for basement-condition judgement, wall-grouping around openings). State the limits plainly; a matrix is not design acceptance.
- [ ] **Step 5:** `python -m pytest -q` all pass; commit.

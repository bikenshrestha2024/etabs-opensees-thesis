# NBC 105:2025 §3 — scope of analysis

**Source:** The user's NBC 105:2025 second revision PDF, **printed pp. 17–21** (PDF page = printed page +23 in this range).

**Canonical module:** `components/nbc105/clause_03_scope_of_analysis.py` — source-grounded numerical reference layer, not automatic proof of project compliance.

**Implemented reference operations:** §3.2 ESM ULS/SLS method eligibility; §3.4 Table 3-1 six components; §3.8 maximum soil-bearing increase.

**Limitations / mandatory external checks:** §3.6/3.7 load combinations need independently verified canonical expression sets; Table 3-1 governs in absence of rational cracked-section assessment. Source incorrectly points irregularity to §5.5; actual §5.4.

**Example:** `esm_applicability(height_m=95,period_s=1.98,irregular=True,limit_state='ULS')`

**Tests:** `tests/test_nbc105_clauses_02_03_06_10.py` includes numerical and rejection tests. Actual ETABS and OpenSees analyses are outside this reference-only run; full module-to-GUI call-site migration remains open.

## Verified 2025 source load-combination addition

Clause 3 now also provides `load_combination_coefficients` for **printed §3.6.1 parallel LSM, §3.6.2 non-parallel LSM, and §3.7 WSM**, plus `vertical_seismic_combination` for printed §3.6.3: `(1.1 + 2Z/3)DL + λLL ± E`. The canonical record keys are `DL, LL, Ex, Ey, S`; the source additional-load multipliers are 1.2 snow, 1.2 static-liquid, 1.5 earth (LSM) and 1.0 each (WSM). The 30% orthogonal component is included for §3.6.2. Tests: `tests/test_nbc105_clause3_load_combinations.py`. These are coefficient records—not ETABS OAPI load-case creation or proof that actual load cases follow them. The project's supplementary IS 16700 P-Delta initial loading cases are separate and must never be relabeled NBC §3.6.

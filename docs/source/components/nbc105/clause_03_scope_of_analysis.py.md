# NBC 105:2025 §3 — scope of analysis

**Source:** The user's NBC 105:2025 second revision PDF, **printed pp. 17–21** (PDF page = printed page +23 in this range).

**Canonical module:** `components/nbc105/clause_03_scope_of_analysis.py` — source-grounded numerical reference layer, not automatic proof of project compliance.

**Implemented reference operations:** §3.2 ESM ULS/SLS method eligibility; §3.4 Table 3-1 six components; §3.8 maximum soil-bearing increase.

**Limitations / mandatory external checks:** §3.6/3.7 load combinations need independently verified canonical expression sets; Table 3-1 governs in absence of rational cracked-section assessment. Source incorrectly points irregularity to §5.5; actual §5.4.

**Example:** `esm_applicability(height_m=95,period_s=1.98,irregular=True,limit_state='ULS')`

**Tests:** `tests/test_nbc105_clauses_02_03_06_10.py` includes numerical and rejection tests. Actual ETABS and OpenSees analyses are outside this reference-only run; full module-to-GUI call-site migration remains open.

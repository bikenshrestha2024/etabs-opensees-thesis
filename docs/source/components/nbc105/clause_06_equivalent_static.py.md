# NBC 105:2025 §6 — equivalent static

**Source:** The user's NBC 105:2025 second revision PDF, **printed pp. 38–39** (PDF page = printed page +23 in this range).

**Canonical module:** `components/nbc105/clause_06_equivalent_static.py` — source-grounded numerical reference layer, not automatic proof of project compliance.

**Implemented reference operations:** §6.1 ULS/SLS coefficient, §6.2 V=CdW, §6.3 Fi distribution and k exponent, §6.5 six-row deflection factor Table 6-1.

**Limitations / mandatory external checks:** §6.4 load application/eccentricity and production Excel/GUI/ETABS adapter parity remain native-run dependent.

**Example:** `distribute_forces(100,[100,200],[3,6],1)`

**Tests:** `tests/test_nbc105_clauses_02_03_06_10.py` includes numerical and rejection tests. Actual ETABS and OpenSees analyses are outside this reference-only run; full module-to-GUI call-site migration remains open.

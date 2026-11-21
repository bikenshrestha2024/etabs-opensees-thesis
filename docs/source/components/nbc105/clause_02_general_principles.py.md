# NBC 105:2025 §2 — general principles

**Source:** The user's NBC 105:2025 second revision PDF, **printed pp. 10–16** (PDF page = printed page +23 in this range).

**Canonical module:** `components/nbc105/clause_02_general_principles.py` — source-grounded numerical reference layer, not automatic proof of project compliance.

**Implemented reference operations:** §2.1 ULS/SLS declarations; overturning, sliding, foundation and evacuation functional prerequisites. Qualitative §2.2–2.5 require engineering review.

**Limitations / mandatory external checks:** Actual stability capacity, seismic detailing, SSI, performance evidence and capacity design cannot be inferred from booleans.

**Example:** `verification_check(uls=True,sls=True,overturning=True,sliding=True,foundation=True,evacuation_components=True)`

**Tests:** `tests/test_nbc105_clauses_02_03_06_10.py` includes numerical and rejection tests. Actual ETABS and OpenSees analyses are outside this reference-only run; full module-to-GUI call-site migration remains open.

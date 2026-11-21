# NBC 105:2025 §8 — elastic time history

**Source:** The user's NBC 105:2025 second revision PDF, **printed pp. 42–43** (PDF page = printed page +23 in this range).

**Canonical module:** `components/nbc105/clause_08_elastic_time_history.py` — source-grounded numerical reference layer, not automatic proof of project compliance.

**Implemented reference operations:** §8.1.1 3D, gravity, P-Delta, torsion and damping<=5%; §8.1.3 aggregation for <7 and >7; §8.1.3.2 member action reduction.

**Limitations / mandatory external checks:** Source is silent on exactly seven records in §8.1.3; return a BLOCKED error instead of inventing an averaging rule. §8.1.2 defers all ground-motion rules to §9.3.2. Actual case duration/convergence need native proof.

**Example:** `record_response_aggregate([1,4,2])`

**Tests:** `tests/test_nbc105_clauses_02_03_06_10.py` includes numerical and rejection tests. Actual ETABS and OpenSees analyses are outside this reference-only run; full module-to-GUI call-site migration remains open.

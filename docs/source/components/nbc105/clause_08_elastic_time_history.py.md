# NBC 105:2025 §8 — elastic time history

**Source:** The user's NBC 105:2025 second revision PDF, **printed pp. 42–43** (PDF page = printed page +23 in this range).

**Canonical module:** `components/nbc105/clause_08_elastic_time_history.py` — source-grounded numerical reference layer, not automatic proof of project compliance.

**Implemented reference operations:** §8.1.1 3D, gravity, P-Delta, torsion and damping<=5%; §8.1.3 aggregation for <7 and >7; §8.1.3.2 member action reduction.

**Limitations / mandatory external checks:** Source is silent on exactly seven records in §8.1.3; return a BLOCKED error instead of inventing an averaging rule. §8.1.2 defers all ground-motion rules to §9.3.2. Actual case duration/convergence need native proof.

**Example:** `record_response_aggregate([1,4,2])`

**Tests:** `tests/test_nbc105_clauses_02_03_06_10.py` includes numerical and rejection tests. Actual ETABS and OpenSees analyses are outside this reference-only run; full module-to-GUI call-site migration remains open.

**Project record set (added 2026-11-26):** `PROJECT_DECLARED_GROUND_MOTION_COUNT = 8` (USER_DECLARED, see `docs/nbc105/PROJECT_DECLARATIONS.md` section 5). `project_record_set_evaluation(accepted_responses, declared_count=8)` returns the rule, the value and `declared_count_met`: 8 accepted -> AVERAGE, fewer than 7 -> MAXIMUM, exactly 7 -> `BLOCKED` (value None). Tests: `tests/test_nbc105_followup_ground_motions.py`. Production wrapper for the NLTHA path: `components/nonlinear_time_history/nbc105_2025_audit.py::project_response_aggregation`.

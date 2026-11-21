# NBC 105:2025 §9 — nonlinear analysis

**Source:** The user's NBC 105:2025 second revision PDF, **printed pp. 44–48** (PDF page = printed page +23 in this range).

**Canonical module:** `components/nbc105/clause_09_nonlinear_analysis.py` — source-grounded numerical reference layer, not automatic proof of project compliance.

**Implemented reference operations:** §9.2 both-sign pushovers; §9.3 minimum records/pairs, XY/YX, scale factor 0.33–3, target interval [Tn,sqrt(Rmu)T1], timestep cap min(record_dt,T1/100,Tn,0.01).

**Limitations / mandatory external checks:** Actual N2 target calculation, true material hysteresis and wall convergence, completed XY/YX histories, exactly-seven-record aggregation and M0–M6 matrix remain OPEN. Positive test declarations are NOT native simulation proof.

**Example:** `history_time_step_limit_s(.8,.02,.025)`

**Tests:** `tests/test_nbc105_clauses_02_03_06_10.py` includes numerical and rejection tests. Actual ETABS and OpenSees analyses are outside this reference-only run; full module-to-GUI call-site migration remains open.

# NBC 105:2025 §10 — parts and components

**Source:** The user's NBC 105:2025 second revision PDF, **printed pp. 49–52** (PDF page = printed page +23 in this range).

**Canonical module:** `components/nbc105/clause_10_parts_and_components.py` — source-grounded numerical reference layer, not automatic proof of project compliance.

**Implemented reference operations:** §10.1 component weight cutoff 25%, reduced friction; §10.2 shutdown <=0.2g; §10.3 component Fp; Table 10-1 ap interpolation; Table 10-2 μp, Table 10-3 Ip.

**Limitations / mandatory external checks:** Table 10-1 omits an explicit equality at ΔT=0.5s; take continuous endpoint ap=1.0 and report it. Research-supported μp up to 3.5 is NOT automatically approved. Attachment/anchor design, safety cables and equipment serviceability require additional evidence.

**Example:** `component_amplification_factor(1.0,1.25)`

**Tests:** `tests/test_nbc105_clauses_02_03_06_10.py` includes numerical and rejection tests. Actual ETABS and OpenSees analyses are outside this reference-only run; full module-to-GUI call-site migration remains open.

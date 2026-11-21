# NBC 105:2025 §7 — modal response spectrum

**Source:** The user's NBC 105:2025 second revision PDF, **printed pp. 40–41** (PDF page = printed page +23 in this range).

**Canonical module:** `components/nbc105/clause_07_modal_response_spectrum.py` — source-grounded numerical reference layer, not automatic proof of project compliance.

**Implemented reference operations:** §7.2 modal effective gravity load, signed floor modal forces; §7.3 directional mass coverage; §7.4 SRSS helper; §7.5 force-only scaling.

**Limitations / mandatory external checks:** CQC correlation coefficient/damping, ≤15% close-frequency grouping, >33 Hz missing-mass correction and ETABS/solver 90% coverage are NOT implemented in this reference module. Source wording for close-mode direct summation is retained for engineering review.

**Example:** `force_only_scale(esm_shear=100,mrsm_shear=50,member_forces=[10],story_shears=[30],base_reactions=[-50],drifts=[.003],displacements=[.2])`

**Tests:** `tests/test_nbc105_clauses_02_03_06_10.py` includes numerical and rejection tests. Actual ETABS and OpenSees analyses are outside this reference-only run; full module-to-GUI call-site migration remains open.

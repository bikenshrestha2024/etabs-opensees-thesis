# NBC 105:2025 §7 — modal response spectrum

**Source:** The user's NBC 105:2025 second revision PDF, **printed pp. 40–41** (PDF page = printed page +23 in this range).

**Canonical module:** `components/nbc105/clause_07_modal_response_spectrum.py` — source-grounded numerical reference layer, not automatic proof of project compliance.

**Implemented reference operations:** §7.2 modal effective gravity load, signed floor modal forces; §7.3 directional mass coverage; §7.4 SRSS helper; §7.5 force-only scaling.

**Limitations / mandatory external checks:** CQC correlation coefficient/damping, ≤15% close-frequency grouping, >33 Hz missing-mass correction and ETABS/solver 90% coverage are NOT implemented in this reference module. Source wording for close-mode direct summation is retained for engineering review.

**Example:** `force_only_scale(esm_shear=100,mrsm_shear=50,member_forces=[10],story_shears=[30],base_reactions=[-50],drifts=[.003],displacements=[.2])`

**Tests:** `tests/test_nbc105_clauses_02_03_06_10.py` includes numerical and rejection tests. Actual ETABS and OpenSees analyses are outside this reference-only run; full module-to-GUI call-site migration remains open.

## Canonical CQC kernel integrated with native MRSM (2026-11-21)

`cqc_correlation_matrix(omega_rad_s,damping_ratio=0.05)` is pure Python and implements the former MRSM kernel's equal-modal-damping correlation expression for `§7.4`. All `omega_rad_s` are positive finite rad/s, ratio is positive finite and damping is positive and not greater than 5% under the active elastic MRSM settings. `components.response_spectrum.model_analysis.cqc_matrix` now delegates and returns the same NumPy matrix. Existing `combine(values,rho)` remains in the solver package, so vectorized envelope operations are unchanged.

Numerical test: `tests/test_nbc105_source_numerical_integrity_v2.py`. No native nonlinear time history or ETABS equivalence inference.

**Modal mass coverage to 100 percent (added 2026-11-26):** `modal_mass_participation_profile(per_mode_percent, periods_s=None)` and `modal_mass_participation_by_direction` give the cumulative effective mass out to 100 percent, `reached_90_at_mode`, `reached_100_at_mode`, `period_at_90_s`, `compliant_90` (threshold stays 90 percent, printed 7.3 p. 40) and a per-mode `regions` list (`REQUIRED_FOR_90` with `highlight_90_region`, `BEYOND_90_TO_100`, `BEYOND_100`). `components/modal/analysis.py::run_nbc105_modal_audit` stores them under `mass_coverage`, `reached_90_at_mode`, `reached_100_at_mode` and per-row `mass_region_X/Y`. Tests: `tests/test_nbc105_followup_modal_mass.py`.

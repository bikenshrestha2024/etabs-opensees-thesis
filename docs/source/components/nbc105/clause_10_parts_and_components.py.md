# NBC 105:2025 §10 — parts and components

**Source:** The user's NBC 105:2025 second revision PDF, **printed pp. 49–52** (PDF page = printed page +23 in this range).

**Canonical module:** `components/nbc105/clause_10_parts_and_components.py` — source-grounded numerical reference layer, not automatic proof of project compliance.

**Implemented reference operations:** §10.1 component weight cutoff 25%, reduced friction; §10.2 shutdown <=0.2g; §10.3 component Fp; Table 10-1 ap interpolation; Table 10-2 μp, Table 10-3 Ip.

**Limitations / mandatory external checks:** Table 10-1 omits an explicit equality at ΔT=0.5s; take continuous endpoint ap=1.0 and report it. Research-supported μp up to 3.5 is NOT automatically approved. Attachment/anchor design, safety cables and equipment serviceability require additional evidence.

**Example:** `component_amplification_factor(1.0,1.25)`

**Tests:** `tests/test_nbc105_clauses_02_03_06_10.py` includes numerical and rejection tests. Actual ETABS and OpenSees analyses are outside this reference-only run; full module-to-GUI call-site migration remains open.

## §10.4(d) hanging/swinging light safety cables

The uploaded 2025 code (printed p.51; PDF p.73 in the 137-page edition) requires safety cables fixed to the structure and fixture to resist a **lateral load equal to four times the hanging or swinging light's weight**. The canonical `light_safety_cable_design_capacity(component_weight_kN)` returns `4Wp` in kN and rejects zero, negative or nonfinite weights. Tested in `tests/test_nbc105_printed_table_verification_2025.py`. This checks the demand only; real cable/anchor capacity, connection detailing and installation remain engineering evidence requirements.

The same test independently checks Tables 3-1, 4-1, all 21 rows of 5-2, 6-1 and 10-1/2/3 against source-transcribed values rather than importing implementation constants.

**Printed ranges enforced (added 2026-11-26):** `component_design_force` rejects ap outside 1 to 2.5 (10.3.1, p. 50), mu_p below 1.5 or above 2.5 unless `research_supported_mu_p=True` (then at most 3.5; 10.3.2, p. 50) and Ip other than 1.0 or 1.5 (Table 10-3, p. 51). Clause and page of every symbol: `docs/nbc105/clause_10_component_factor_locations.md`. Tests: `tests/test_nbc105_followup_component_factors.py`.

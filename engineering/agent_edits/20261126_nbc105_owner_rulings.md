# NBC 105:2025 owner rulings follow-up (2026-11-26)

Editor Claude Code (model label UNKNOWN). Branch `feat/nbc105-normative-sentence-audit`, base `250c695` (head 70b6da5 at start). Unit tests only; no native ETABS/OpenSees; source EDB untouched. Nothing here is engineering acceptance and the register stays NOT CERTIFIED.

## Ruling 1: ground motions N_GM = 8
`clause_08_elastic_time_history.py` (+`PROJECT_DECLARED_GROUND_MOTION_COUNT`, `project_record_set_evaluation`), `nbc105_2025_audit.py::project_response_aggregation`, tests `tests/test_nbc105_followup_ground_motions.py`, `PROJECT_DECLARATIONS.md` section 5, register rows N8-0019..21 and N9-0066/67. Print confirmed: <7 maximum, >7 average, 7 undefined (kept BLOCKED).

## Ruling 2: mass irregularity 5.4.1.5
`clause_05_dynamic_characteristics.py::mass_irregularity`, `components/validation/response_checks.py::irregularity` (new `mass_exempt_storeys` argument), `tests/test_nbc105_followup_mass_irregularity.py`, rows N5-0106/0107. The print compares consecutive storeys only and names no base for the 50 percent; the earlier max/min > 1.5 reading is kept as the conservative default, the heavier-storey reading is reported beside it, and the roof/penthouse/mezzanine exemption is user-declared only.

## Ruling 7: single source of drift limits
`clause_05_dynamic_characteristics.py` (`DRIFT_LIMITS`, `drift_limit_ratio`, `drift_ratio_status`), literals replaced in the LTH/NLTHA runners, ESM `code_basis.py` and `legacy_code_basis.py`, MRSM `reports.py`/`model_analysis.py`, `validation/design_checks.py`, `nonlinear_performance.py`, `case_review.py`, `response_checks.py` and `tools/plot_results.py`; dead `DRIFT_LIMITS` of `nbc105_2025_audit.py` removed; `history_drift_check` added; `tests/test_nbc105_followup_drift_single_source.py`; rows N8-0023, N9-0069. Numeric values unchanged (0.025 / 0.006).

## Ruling 3: two separate drift outputs
`clause_05_dynamic_characteristics.py` (`etabs_comparison_drift`, `opensees_actual_drift`, `separate_drift_outputs`, `require_same_drift_basis`, `drift_basis`), `response_checks.py::drift_check(drift_basis=...)` with explicit labels at all production callers (static/MRSM = ETABS_COMPARISON, history = OPENSEES_ACTUAL), MRSM result JSON and `reports.py` columns, ESM generated response rows, LTH/NLTHA summaries; `tests/test_nbc105_followup_drift_bases.py`; rows N5-0127/0129/0137. The Rmu-scaled basis is stated in 5.5.1.1 (not 5.5.3).

## Ruling 4: Lwi/H > 0.9
`clause_05_dynamic_characteristics.py` (`effective_wall_area_result`, `LwiOverHExceeded`; `effective_wall_area_m2` no longer clamps), `components/inputs/project_workbooks.py::_wall_aw_from_lines` (CRLF preserved; per-segment flag, numeric value unchanged), `components/modal/analysis.py` docstring, `tests/test_nbc105_followup_lwi_over_h.py`, `tests/test_nbc105_clause5.py` (clamp test replaced), row N5-0030. Printed p.30 words it as a restriction on Lwi; the formula on p.29 has no cap, so no clamp.

## Ruling 5: ap, mu_p, Ip
`clause_10_parts_and_components.py::component_design_force` range enforcement (+`research_supported_mu_p`), `docs/nbc105/clause_10_component_factor_locations.md`, `tests/test_nbc105_followup_component_factors.py`, rows N10-0013/0019/0027/0029.

## Ruling 6: modal mass coverage
`clause_07_modal_response_spectrum.py` (`modal_mass_participation_profile`, `modal_mass_participation_by_direction`, `MODAL_MASS_THRESHOLD_PERCENT`), `components/modal/analysis.py` (result fields `mass_coverage`, `reached_90_at_mode`, `reached_100_at_mode`, row region flags), `tests/test_nbc105_followup_modal_mass.py`, row N7-0016.

## Ruling 11: scope update, DEFERRED_DESIGN_PHASE
`components/nbc105/normative_register.py` and `tools/nbc105_normative_extract.py` (new disposition in vocabulary, notes required, counted as open external), `DISPOSITION_RULES.csv` (27 Annex B rules rewritten: 156 rows PROJECT_NOT_APPLICABLE -> DEFERRED_DESIGN_PHASE; 9.2 pushover notes record the user declaration; the file round-trips byte-identically through csv), `PROJECT_DECLARATIONS.md` section 6, guide, `tests/test_nbc105_normative_register.py::DeferredDesignPhase`. Gate stays fail-closed and never certified.

## Ruling 10: Annex C project rows
New `components/nbc105/annex_c_zoning.py` (+ guide, registry row), `docs/nbc105/annex_c/TABLE_C1_PROJECT_ROWS.csv` (generated from the pdftotext layer of printed p.106 and checked against the page image; header, serial 346, Kathmandu block 340-350, rows 326 and 335, Figure 4-3 usage record, scope record, SHA-256 per row), `tests/test_nbc105_followup_annex_c.py`, rows NC-0001, N4-0078/0079/0080. Remaining rows stay EXTERNAL_DATA_REQUIRED.

## Ruling 9a: missing mass 33 Hz
New `components/nbc105/clause_07_missing_mass.py` (+ guide, registry row), gate wired into `components/modal/analysis.py` (result `missing_mass_gate`) and `components/response_spectrum/model_analysis.py` (same fail-closed refusal, now with the exact missing-input list), `tests/test_nbc105_followup_missing_mass.py`, row N7-0018. Full-building residual-force integration is not done and is documented.

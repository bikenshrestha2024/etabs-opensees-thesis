# NBC 105:2025 owner rulings follow-up (2026-11-26)

Editor Claude Code (model label UNKNOWN). Branch `feat/nbc105-normative-sentence-audit`, base `250c695` (head 70b6da5 at start). Unit tests only; no native ETABS/OpenSees; source EDB untouched. Nothing here is engineering acceptance and the register stays NOT CERTIFIED.

## Ruling 1: ground motions N_GM = 8
`clause_08_elastic_time_history.py` (+`PROJECT_DECLARED_GROUND_MOTION_COUNT`, `project_record_set_evaluation`), `nbc105_2025_audit.py::project_response_aggregation`, tests `tests/test_nbc105_followup_ground_motions.py`, `PROJECT_DECLARATIONS.md` section 5, register rows N8-0019..21 and N9-0066/67. Print confirmed: <7 maximum, >7 average, 7 undefined (kept BLOCKED).

## Ruling 2: mass irregularity 5.4.1.5
`clause_05_dynamic_characteristics.py::mass_irregularity`, `components/validation/response_checks.py::irregularity` (new `mass_exempt_storeys` argument), `tests/test_nbc105_followup_mass_irregularity.py`, rows N5-0106/0107. The print compares consecutive storeys only and names no base for the 50 percent; the earlier max/min > 1.5 reading is kept as the conservative default, the heavier-storey reading is reported beside it, and the roof/penthouse/mezzanine exemption is user-declared only.

## Ruling 7: single source of drift limits
`clause_05_dynamic_characteristics.py` (`DRIFT_LIMITS`, `drift_limit_ratio`, `drift_ratio_status`), literals replaced in the LTH/NLTHA runners, ESM `code_basis.py` and `legacy_code_basis.py`, MRSM `reports.py`/`model_analysis.py`, `validation/design_checks.py`, `nonlinear_performance.py`, `case_review.py`, `response_checks.py` and `tools/plot_results.py`; dead `DRIFT_LIMITS` of `nbc105_2025_audit.py` removed; `history_drift_check` added; `tests/test_nbc105_followup_drift_single_source.py`; rows N8-0023, N9-0069. Numeric values unchanged (0.025 / 0.006).

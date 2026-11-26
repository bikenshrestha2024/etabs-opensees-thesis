# NBC 105:2025 owner rulings follow-up (2026-11-26)

Editor Claude Code (model label UNKNOWN). Branch `feat/nbc105-normative-sentence-audit`, base `250c695` (head 70b6da5 at start). Unit tests only; no native ETABS/OpenSees; source EDB untouched. Nothing here is engineering acceptance and the register stays NOT CERTIFIED.

## Ruling 1: ground motions N_GM = 8
`clause_08_elastic_time_history.py` (+`PROJECT_DECLARED_GROUND_MOTION_COUNT`, `project_record_set_evaluation`), `nbc105_2025_audit.py::project_response_aggregation`, tests `tests/test_nbc105_followup_ground_motions.py`, `PROJECT_DECLARATIONS.md` section 5, register rows N8-0019..21 and N9-0066/67. Print confirmed: <7 maximum, >7 average, 7 undefined (kept BLOCKED).

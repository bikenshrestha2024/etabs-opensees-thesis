# Six-lot ETABS consistency audit, 2026-11-28

Editor: Anthropic Claude (Claude Code, Sonnet 5.5, session recorded in commit trailer). Base/head SHA: see the commit. Branch: main (requested explicitly by the user).

Read-first triad and existing reader (`components/inputs/etabs_table_bundle.py`, support filter, assignment audit) reviewed; no existing method rewritten. Added `components/validation/etabs_lot_consistency.py`, `tools/audit_etabs_lot_consistency.py`, tests, three source guides, registry row, README link and the evidence files under `docs/validation/`.

Actual workbook inspection: all nine supplied workbooks streamed with openpyxl read-only (55 sheets, 173,117,043 cells); six distinct lots ingested through the repo reader; results in the evidence JSON. Raw workbooks, rows and local paths are not committed.

Not changed: model, solver, supports, gravity (1.0D+1.0L), NBC Table 5-1 ledger, `GRAVITY_M_S2` (9.81 vs export 9.80665 reported for a decision). Not verified: native ETABS/OpenSees equivalence, 768.045 kN residual, rigid end zones, NLTHA M0-M6, NBC certification. Beam workbooks 1/2/3 were not supplied.

Tests: `tests/test_etabs_lot_consistency.py` (21 passed), `tests/test_current_etabs_table_bundle.py`, `tests/test_documentation_coverage.py` (48 passed, 7 skipped before the evidence file existed); component README and documentation coverage gates clean.

## Follow-up: gravity constant decision (2026-11-28)

User decided to keep project g = 9.81 and asked to commit to main. No code or constant changed; the decision and its expected 0.034% mass offset are recorded in `docs/validation/20261128_ETABS_LOT_CONSISTENCY_AUDIT.md`. Model label: Claude Sonnet 5.5 (self-reported).

## Verification follow-up (2026-11-28)

* Row-count and double-count errors in the beam audit record/code fixed; CLI behaviour tests added (`tests/test_etabs_audit_cli.py`); beam evidence re-run on the three real workbooks reproduced the committed JSON exactly.
* `tests/test_linear_th_directional_autofill.py::test_missing_modal_clears_previous_verified_metadata` failed only where `tkinter` is absent (the patched `components.response_spectrum` imports it); it now skips there, unchanged elsewhere.
* `tests/verify_review_ledger.py::test_baseline_complete` failed only in a shallow clone (a required commit was absent); it passes with full history (`git fetch --unshallow`). No code change.
* `tools/build_json_documentation.py` regenerated: 34 missing per-JSON docs added and the stale `ref_tag_baseline.json` entry refreshed; `--check` now passes (540 files, no issues).
* Full suite: 2058 passed, 86 skipped, 0 failed. Public-model disclosure gate: 0 forbidden paths; 8 older OpenSees model JSON files (`Saved_Project_V156/`, `Worked_Example_V138/`) still need the owner's manual content/history review — not touched.

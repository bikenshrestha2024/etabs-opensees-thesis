# Agent edit — V135 run-owned report tables

- Model-side data inspected: user-uploaded current index, complete JSON report schema, 9 derived CSV tables and V135 log. No private source uploaded to public GitHub.
- Main baseline: `fc081128738148c5a5d40c11dac8e2e5087096bd`.
- Existing code inspected: `components/validation/design_checks.py` (entire run/combination/output block), `components/inputs/output_contract.py::write_table`, `components/inputs/output_layout.py`, `tests/test_v135_drift_source_completion_v13.py`.
- Defect: legacy flat same-name derived CSV remained stale on latest zero-result table; index said it was stale, but current physical CSV absent.
- Correction: append-only run-owned CSV bundle for all 9 V135 tables with empty-header explicit files; stable index now contains exact run/relative-file references; no legacy deletion/move.
- Regression: `tests.test_v135_drift_source_completion_v13`, + CI.
- Engineering native validation: NOT_RUN; full semantic review: incomplete; root legacy-migration: incomplete and must not be misrepresented.

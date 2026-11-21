# Fix wave: failed-case accounting in run-log analyser, doc accuracy (2026-11-21)

Agent: Claude Code. Model label: UNKNOWN (not recorded).

Edits: `tools/analyze_run_log.py` (only `completed` [CASE TIMING] counts as completed; other statuses go to `failed_cases`; non-numeric stage values skipped; truncation wording conditional on the log; projection states how many declared cases are excluded), `tests/test_analyze_run_log.py` (failed-case probe, robust path printing), `components/nonlinear_time_history/runner_and_gui.py` (gate prefix wording only, text not pinned by tests), docs (analyser guide, source-guide index, output folder standard, readiness workflow, gap register), regenerated `docs/validation/run_findings/LTHA_V115_PRELIM_20261120.{md,json}`.

Verified by grep: LTHA runner ad hoc fallback folder; `.xlsx`/`.png` written to `02_RESULTS` and copied to `03_EXCEL`/`04_FIGURES` only when the completion gate passes; run config value overrides model config in `_model_options`; `assembly.py` skips the reviewed check for the research profile.

Evidence: unit tests only. No native ETABS or OpenSees run. Not engineering acceptance. Source EDB and `Saved_Project_V156/` untouched.

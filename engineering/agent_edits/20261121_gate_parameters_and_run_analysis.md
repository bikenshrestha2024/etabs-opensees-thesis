# 2026-11-21 slice: gate parameters, run-log analysis, output-folder standard

- Model: UNKNOWN (not available to the agent).
- Branch: feat/gate-material-blockers-run-analysis (PR, not merged).
- Changed: readiness gate raises `parameters_not_reviewed` for approved manifests; `tools/analyze_run_log.py` + findings under `docs/validation/run_findings/`; `tools/audit_output_layout.py` + `docs/OUTPUT_FOLDER_STANDARD.md`; gap register run-evidence section.
- Per-task notes: `20261121_gate_parameters_not_reviewed.md`, `20261121_run_log_analyser.md`, `20261121_output_layout_audit.md`.
- Verified: full pytest suite on Linux (see PR); unit tests only.
- Unverified: Windows/Spyder, ETABS COM, tkinter GUI, GitHub Actions run, any OpenSees run.
- Not engineering acceptance: the V115 log is a preliminary linear 0.5 s diagnostic.

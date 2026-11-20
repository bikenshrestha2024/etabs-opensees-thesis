# NLTHA readiness diagnosis and bound draft (Tasks 1 and 2)

Editor Claude Code (model label UNKNOWN). Base SHA `7b573fa`, branch `feat/nltha-readiness-gate-20261120`. The Task 3 note is `20261120_etabs_ingest_guards.md`.

Edited paths
- Task 1: `components/model/readiness.py` (READINESS_CHECK_KEYS, `diagnose_nonlinear_readiness`, `format_readiness_blockers`); `components/nonlinear_time_history/runner_and_gui.py` (`_require_nonlinear_readiness` keeps its raises and messages, appends the blocker list); `tests/test_nltha_readiness_diagnosis.py`.
- Task 2: `components/model/readiness.py` (`bind_readiness_draft`, `material_prerequisite_notice`); `components/model/readiness_gui.py` (`prepare` delegates to `bind_readiness_draft`, launch notice); `tests/test_nltha_readiness_bound_draft.py`.

Tests run (headless, `PYTHONPATH=$PWD python -m pytest`, as stated in the task reports)
- `tests/test_nltha_readiness_diagnosis.py`: 12 passed.
- `tests/test_nltha_readiness_bound_draft.py` with the diagnosis file: 22 passed.
- `tests/verify_readiness_dashboard.py`: 12 passed (Task 1 run); with `tests/test_main_launcher_workflow_layout.py` 16 passed (Task 2 run).
- `tests/verify_v134.py`: 3 failed, 4 passed, identical to baseline by stash comparison; cause tkinter not installed in the sandbox.

Scientific gates: code never sets `approved_for_nltha` or any check True; drafts are UNAPPROVED with every check False. No solver PASS is claimed as engineering acceptance.

PENDING: native Windows/ETABS runs, tkinter GUI behavior (`readiness_gui.launch` notice not exercised headless), full-model NLTHA, project reinforcement and FVD/BRB calibration. Known limits: the gate test loads the runner function via AST because tkinter is absent; `READINESS_CHECK_KEYS` duplicates the runner's literal tuple (an equality test enforces it); the missing-manifest `FileNotFoundError` message has no blocker list.

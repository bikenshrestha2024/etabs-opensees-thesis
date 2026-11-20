# NLTHA approval binding and stale runtime-copy guard (follow-up Tasks 1 and 2)

Editor Claude Code (model label UNKNOWN). Base SHA `54f8ff4`, branch `feat/readiness-binding-ci-audit`. Plan: `docs/superpowers/plans/2026-11-20-binding-ci-audit.md`. Follows `20261120_nltha_readiness_gate.md`.

## Task 1: bind approval to config, material file and FSAM tags
Edited paths
- `components/model/readiness.py`: `current_binding`, `record_binding`, `canonical_fsam_tags_hash`, `approval_binding_problems`, `gate_binding_blockers`, binding blockers in `diagnose_nonlinear_readiness`, `bind_readiness_draft` records hashes.
- `components/nonlinear_time_history/runner_and_gui.py`: `_require_nonlinear_readiness` keeps every earlier raise and message; adds one final raise on binding mismatch or an approved manifest with no material file / FSAM tags.
- `components/model/readiness_gui.py`: save and rebind record the hashes; save refuses an approval that cannot be bound.
- `tests/test_nltha_readiness_binding.py` (new); `tests/test_nltha_readiness_diagnosis.py` (`_bound` helper now records the binding so "current-format manifest" cases keep their meaning).
- `docs/NLTHA_READINESS_WORKFLOW.md` sections 2 and 5 and the PENDING list.

Tests run (headless, `cd /home/claude/etabs-opensees-thesis && PYTHONPATH=$PWD python -m pytest -q <files>`): 

Original Task 1 and 2 runs (before this fix wave; counts re-run and confirmed, then rising with the fix-wave tests):
- `python -m pytest -q -p no:cacheprovider tests/test_nltha_readiness_binding.py tests/test_nltha_readiness_diagnosis.py tests/test_nltha_readiness_bound_draft.py` -> 40 passed originally; 48 passed now (8 fix-wave tests added to the binding file).
- `python -m pytest -q -p no:cacheprovider tests/test_nltha_stale_runtime.py` -> 12 passed (unchanged).
- `python -m pytest -q -p no:cacheprovider tests/test_nltha_stale_runtime.py tests/test_nltha_readiness_*.py tests/test_etabs_ingest_guards.py tests/verify_readiness_dashboard.py tests/test_main_launcher_workflow_layout.py` -> 89 passed originally; 97 passed now.
- `python -m pytest -q -p no:cacheprovider tests/test_repository_integrated_audit.py tests/test_repository_semantic_discovery.py` -> 20 passed, 6 subtests passed (unchanged).
- `PYTHONPATH=$PWD python tests/verify_ref_tags.py` -> Ran 4 tests OK.
Fix wave (same note): approval reset on changed config/material/FSAM inputs (`rebind_if_binding_changed`, `binding_change_notice`), `binding_unreadable` fail-closed for locked files; GUI wiring in `readiness_gui.launch` is not executed here (no tkinter).

Scientific gates: code never sets `approved_for_nltha` or any check True. Hashes prove files are unchanged since a human saved the checklist, not that their contents are correct. No solver PASS is claimed as engineering acceptance.

## Task 2: stale runtime-copy guard
Nothing under `Saved_Project_V156/` was added or edited (immutable evidence); a test snapshots the real `OpenSees_Runtime_V118/` before and after and compares hashes.

Edited paths
- `components/model/readiness.py`: `detect_stale_runtime`, `runtime_copy_notice`, `ACTIVE_GATE_RUNNER_MARKERS`, `ACTIVE_GATE_MODULE_MARKERS`; `diagnose_nonlinear_readiness` adds blocker `stale_runtime_copy`.
- `components/model/readiness_gui.py`: launch notice shows the stale-runtime warning.
- `tests/test_nltha_stale_runtime.py` (new): synthetic fixtures plus the real `OpenSees_Runtime_V118` as read-only fixture.
- `docs/NLTHA_READINESS_WORKFLOW.md` section 5a (exact rule) and the PENDING list.
No new module and no CANONICAL_MODULES.csv change (existing module extended).

PENDING: tkinter GUI behavior of the new warning (not run; sandbox has no tkinter); native Windows/ETABS runs; the saved runtime copy is detected and warned about, not refreshed, and can still be launched directly; full-model NLTHA, project reinforcement and FVD/BRB calibration.

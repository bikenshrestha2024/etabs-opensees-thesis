# NLTHA approval binding and stale runtime-copy guard (follow-up Tasks 1 and 2)

Editor Claude Code (model label UNKNOWN). Base SHA `54f8ff4`, branch `feat/readiness-binding-ci-audit`. Plan: `docs/superpowers/plans/2026-11-20-binding-ci-audit.md`. Follows `20261120_nltha_readiness_gate.md`.

## Task 1: bind approval to config, material file and FSAM tags
Edited paths
- `components/model/readiness.py`: `current_binding`, `record_binding`, `canonical_fsam_tags_hash`, `approval_binding_problems`, `gate_binding_blockers`, binding blockers in `diagnose_nonlinear_readiness`, `bind_readiness_draft` records hashes.
- `components/nonlinear_time_history/runner_and_gui.py`: `_require_nonlinear_readiness` keeps every earlier raise and message; adds one final raise on binding mismatch or an approved manifest with no material file / FSAM tags.
- `components/model/readiness_gui.py`: save and rebind record the hashes; save refuses an approval that cannot be bound.
- `tests/test_nltha_readiness_binding.py` (new); `tests/test_nltha_readiness_diagnosis.py` (`_bound` helper now records the binding so "current-format manifest" cases keep their meaning).
- `docs/NLTHA_READINESS_WORKFLOW.md` sections 2 and 5 and the PENDING list.

Tests run (headless, `cd /home/claude/etabs-opensees-thesis && PYTHONPATH=$PWD python -m pytest -q <files>`): see the commit report; exact commands and counts are in the task report.

Scientific gates: code never sets `approved_for_nltha` or any check True. Hashes prove files are unchanged since a human saved the checklist, not that their contents are correct. No solver PASS is claimed as engineering acceptance.

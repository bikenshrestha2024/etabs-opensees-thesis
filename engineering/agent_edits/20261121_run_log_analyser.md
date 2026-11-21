# Run-log analyser and V115 preliminary LTHA findings

Editor Claude Code (model label UNKNOWN). Branch `feat/gate-material-blockers-run-analysis`. Plan Task 2.

Edited paths
- `tools/analyze_run_log.py` (new), `tests/test_analyze_run_log.py` (new), `docs/source/tools/analyze_run_log.py.md` (new).
- `docs/validation/run_findings/LTHA_V115_PRELIM_20261120.{md,json}` (generated from `tests/fixtures/ltha_v115_prelim_log_excerpt.txt`).
- `engineering/registry/CANONICAL_MODULES.csv`: one NEW_WITH_JUSTIFICATION row, NOT_REVIEWED.

Tests (headless): `python -m pytest tests/test_analyze_run_log.py -q` -> 10 passed; `python tests/verify_ref_tags.py` run, see commit.

Scientific gates: log evidence only, no solver PASS claimed as engineering acceptance; projection is a lower bound for nonlinear. PENDING: native ETABS/OpenSees runs.

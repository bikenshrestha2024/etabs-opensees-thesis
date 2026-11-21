# Gate raises on unreviewed nonlinear parameters for approved manifests

Editor Claude Code (model label UNKNOWN). Base SHA `dbd98dd`, branch `feat/gate-material-blockers-run-analysis`. Plan: `docs/superpowers/plans/2026-11-21-gate-material-blockers-run-analysis.md` Task 1.

Edited paths
- `components/model/readiness.py`: `APPROVED_CONTRADICTION_CODES` adds `parameters_not_reviewed`; `gate_binding_blockers` docstring updated. `_NON_GATE_BLOCKER_CODES` unchanged on purpose (it only drives the display notice, and the existing notice test expects the code listed).
- `docs/NLTHA_READINESS_WORKFLOW.md`: sections 2 and 5 state which codes the gate raises on; `binding_not_recorded` stays advisory.
- `tests/test_nltha_gate_parameters_reviewed.py` (new).

Tests (headless): `python -m pytest tests/test_nltha_readiness_*.py tests/test_nltha_stale_runtime.py tests/test_nltha_gate_parameters_reviewed.py -q` -> 67 passed; `python tests/verify_ref_tags.py` OK.

Scientific gates: no approval or check is ever set True by code; no solver PASS claimed as engineering acceptance. PENDING: native ETABS/OpenSees and GUI runs.

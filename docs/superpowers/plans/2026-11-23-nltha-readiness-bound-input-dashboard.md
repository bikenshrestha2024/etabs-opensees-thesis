# NLTHA readiness-dashboard source-binding consistency (2026-11-23)

> **Execution:** superpowers systematic-debugging, TDD and verification-before-completion. No subagent available; perform reproducible red-green testing in the isolated branch.

## Problem
Current `components/model/readiness_dashboard.py::_load_draft` validates model-script path and SHA, then the dashboard `audit()` can report `approved_for_nltha=true` and `MODEL_BOUND_SIGNOFF_RECORDED_NOT_AUTOMATICALLY_VERIFIED` from a signed draft. The canonical `components/model/readiness.py` run gate additionally binds the model config, external nonlinear materials file and nonlinear wall FSAM tags. A mutated input can invalidate the real run gate while the dashboard still displays a historical sign-off claim.

## Scope and controls
- Base `main@1af9eb89501ddee5cb9153a80407fe4b41081d7a`; new branch `fix/nltha-dashboard-source-binding-20261123`.
- EXTEND only existing `components/model/readiness_dashboard.py`; import the canonical `current_binding`, `BINDING_FIELDS`, `approval_binding_problems` and `BindingUnreadableError` from `components/model/readiness.py`. No duplicate hash calculation or approval logic.
- Keep returning signed status only for exact current model path + SHA and unchanged, complete input bindings and configured nonlinear materials. Missing/legacy bound fields fail closed as `INPUT_BINDING_NOT_RECORDED`; changed hashes as `INPUT_BINDING_MISMATCH`; unreadable source as `INPUT_BINDING_UNREADABLE`; missing material or FSAM approval prerequisites as `INPUT_BINDING_INCOMPLETE`.
- Preserve all original source data, human checklist and historical evidence. The dashboard remains read-only; does not alter the signed draft.
- Physical model unchanged: 32 supports +44 wall mesh points; 76/97 diagnostic only; 100% D+L gravity distinct from NBC Table 5-1 mass; X two 12m walls/Y three 6m walls. No native Windows ETABS/OpenSees or EDB/workbook evidence available. No physics, code or convergence approval.

## TDD red
1. Add `tests/test_nltha_dashboard_input_binding_20261123.py` with synthetic model/config/materials/FSAM and full signed checklist. Prove that an unchanged bound draft can show a *human claim* (not native pass).
2. Prove the old dashboard incorrectly accepts a previously signed draft after config/FSAM changes, after material-file changes, and after deleting the material file; prove legacy drafts without the recorded input-binding fields must not appear as current source-bound claims.
3. Verify status detail and that no draft file was rewritten.

## Green and verification
4. Implement minimal `_load_draft` input-binding checks using shared production functions. Reuse existing caller and report design, no new status framework. Add explanatory source-guide entries.
5. Run focused tests, existing readiness dashboard tests, all headless CI, NLTHA compatibility, security and dependency/compilation gates. Update old synthetic signoff fixture to include credible synthetic config/material and recorded binding.
6. Keep all native source/equivalence/performance claims pending and document prior all-module risks in `REVIEW_MAIN/09_SOFTWARE_SECURITY/20261123_ALL_MODULE_HANDOFF_FOLLOWUP.md`. Include actual editor/preflight/CI gate record under `engineering/agent_edits/`.
7. Merge into `main` only if latest-head CI passes, with explicit validation boundaries. No rewrite of archives or data.

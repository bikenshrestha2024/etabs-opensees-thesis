# Cross-module declared run-stage call inventory — 2026-11-24

> Executes the user's request for consistent output stage ownership across active ETABS/OpenSees modules, as a **static review instrument** only.

**Base:** `main` `8bcf7a23aba08d57d43c802df4cb78e1629f2af9`. Read first: `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `.agents/skills/etabs-opensees-read-first/SKILL.md`, CORE_RULES, ENGINEERING_GATES, MODULE_BOUNDARIES, current `tools/audit_output_stage_ownership.py`, `tools/audit_live_output_writers.py`, the source guide and `tests/test_crossmodule_output_stage_ownership.py`. No original EDB/source Excel or native solver present.

## Defect reproduced from source
The existing ownership audit catches only hard-coded GUI guards and a few ESM wrappers. Other direct `create_case_run`, `owned_run_destination` and `analysis_output_folder` call sites are not enumerated as owning-stage declarations. Thus a new accidentally cross-stage call can hide in a passing output-audit result. Since readers may legitimately target another stage, static detection must **never** automatically change paths or label every mismatch defective.

## Safe tasks
- [ ] Write a synthetic test **first** requiring a cross-module call registry with exact file, AST line, called API, literal stage (or dynamic), source owner and status: same owner, cross-owner review, dynamic review, or shared module review.
- [ ] Observe expected RED on baseline; then extend **existing** `tools/audit_output_stage_ownership.py` only. Reuse existing `scan_source` to enumerate active files and source owner map. Never execute imports, run solver or inspect user's native models.
- [ ] Enrich JSON with `declared_run_stage_calls`, `cross_owner_run_stage_review`, `dynamic_run_stage_review`; add a local CSV tab/report to the existing local output bundle. No new root-level scripts or active source modules.
- [ ] Preserve strict CLI behavior: only existing hard stage guards and parse errors may fail; cross-stage findings are review candidates, not physical errors.
- [ ] Update original tool guide and engineering edit ledger; run focused scanner tests, complete pytest and GitHub Actions. Merge only if green.

**Invariants:** 32 real supports + 44 mesh points; gravity 1.0D+1.0L separate from NBC 105:2025 seismic weight Table 5-1; two 12 m X walls, M0–M6; no solver/EDB/Excel/source-model changes. All native acceptance remains NOT_VERIFIED.

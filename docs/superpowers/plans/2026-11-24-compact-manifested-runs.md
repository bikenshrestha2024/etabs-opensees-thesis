# Compact manifested run folders — implementation plan (2026-11-24)

> For agentic workers: use superpowers:test-driven-development and verification-before-completion. This plan is scoped to **new manifested runs**, not historical migration or native model changes.

**Baseline:** `main` `1cd4fcadfa4ffda40ca73443d6830548e45ddad7`. Issue #177. Existing source-of-truth: `components/inputs/output_contract.py` has `compact_case_id`, `create_case_run` and `inspect_case_manifest`; `output_layout.py` owns stage folders. Current time-history `prepare_history_run` opts into compact IDs, while long case IDs supplied to the shared run creator are not shortened. Root launchers and historical runtime snapshots have no safe bulk-rename path.

## Source/acceptance preflight

- Read `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `.agents/skills/etabs-opensees-read-first/SKILL.md`, `engineering/rules/CORE_RULES.md`, `ENGINEERING_GATES.md`, `MODULE_BOUNDARIES.md`, `engineering/migration/README.md`, module guide and active tests.
- **32 physical supports, 44 shell mesh transfer nodes; 1.0D + 1.0L full gravity, NBC 105:2025 §5.2 Table 5-1 seismic weight:** all unchanged.
- Original source EDB SHA, adopted V10.7 workbook SHA, active M0–M6 model: **UNAVAILABLE** for native testing. This change must not read them or infer solver equivalence.
- Avoid editing native model/element/stiffness/mass/load, changing numerical case logic or moving any output.

## Task 1 — red: manifest run folder length and exact source identification

- Add `tests/test_compact_manifested_runs_20261124.py` with deterministic temp-file coverage for every canonical stage and auxiliary folder.
- Verify that an existing valid, long case (>48 but <=128 chars) with a supplied source/model SHA produces a path component <=48 characters; two source SHA values or two long scopes produce distinct IDs; case manifest stores exact original case label, compact-ID provenance and full SHA.
- Require `inspect_case_manifest` to detect tampered compact `original_case_id`/SHA while preserving legacy manifests.
- Check no-digest run remains unmodified and labeled unsourced; invalid path components, URLs and missing/invalid hashes fail before side effects; no symlink escape.

## Task 2 — green: authoritative shared source contract

- Extend `compact_case_id` stage vocabulary to all canonical stage keys (including auxiliary output modules) using the existing registry; keep 48-char default and reject unknown.
- Auto-compact **only long, valid, source-hashed new** names in `create_case_run`; preserve nonhashed/normally short names and old manifests; full requested case name remains in manifest.
- Validate `case_label_mode` + original name + source basis against the path on `inspect_case_manifest`. No other writer/reader may infer ETABS equivalence from hash equality.

## Task 3 — verify and document

- Update `docs/source/components/inputs/output_contract.py.md` and an agent edit register with precise changed interface, non-affected paths and native blockers.
- Run focused Python test, output compatibility suite and GitHub CI; review PR patch; merge only if all checks green, no native-physics claim.
- Defer separate ESM legacy `analysis_output_folder`/reader migration until a deterministic model hash and all legacy readers are pinned and tested. Never silently retarget prior solver artifacts.

**Acceptance:** new manifested run paths portable/short, exact source-bound full name retained, no name ambiguity or historical rename, mixed load/support model unaffected. `SOURCE_CHECKED`, `NUMERICALLY_CONVERGED`, `ETABS_OPENSEES_MATCHED`, `EXPERIMENT_VALIDATED`, `CODE_ACCEPTED`: **NOT_VERIFIED** by this patch.

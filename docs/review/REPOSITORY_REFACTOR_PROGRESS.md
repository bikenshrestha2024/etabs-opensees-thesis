# Repository refactor progress — V4 baseline

**State:** Phase 1 in progress — read-only inventory, GUI/dynamic-call candidate reports, AST duplicate audit and GitHub CI added; no physical model or numerical solver edited.

**Source main commit:** `a7e26466c1613fb0db32cee88c322444167d5343` (2026-11-10)

**Feature branch:** `refactor/v4-inventory-and-compatibility-baseline-20261110`

## Inspected once
- `AGENTS.md`
- `engineering/rules/CORE_RULES.md`
- `engineering/rules/ENGINEERING_GATES.md`
- `docs/review/00_CANONICAL_RUN_ORDER_AND_NAMING.md`
- `docs/programs/00_PROGRAM_INDEX.md`
- Open draft PR #15 (changes four paths: Gravity GUI, ESM GUI, MRSM analysis and its regression test)

## Repository snapshot
- 2,658 tracked blobs in the complete main Git tree (not truncated).
- Current default branch: `main`.
- PR #15 is draft and not merged; do not independently duplicate its new GUI behavior.
- Existing guidance states that `components/` holds active named implementations; any later migration to `src/` is conditional on full compatibility checks.

## Implemented in this branch
- `tools/audit_repository_structure_v4.py`: read-only Git tracked-file inventory; content SHA256; static AST imports; conservative SHA duplicate candidates; flat/tree output; JSON summary.
- `tests/verify_repository_structure_audit_v4.py`: offline tests for cautionary classifications, non-executing AST imports, fixture ZIP-free output and duplicate grouping.
- This ledger.

## Work completed after initial baseline (2026-11-10)
- `.github/workflows/repository-inventory-v4.yml`: Python 3.12 compilation, offline unittest, full checkout read-only inventory, schema/hash assertions and 14-day audit artifact.
- Extended `tools/audit_repository_structure_v4.py` with `GUI_ACTION_INVENTORY.csv`, `DYNAMIC_REFERENCE_AUDIT.csv`, `AST_DUPLICATE_CANDIDATES.json` (candidate reports; never deletion approval).
- Extended `tests/verify_repository_structure_audit_v4.py` with static GUI/dynamic reference and normalized AST equivalence fixtures.
- `docs/architecture/V4_SAFE_MIGRATION_CROSSWALK.md`: existing shared components and V4 navigation, without copying or moving active engines.
- Current implementation code was checked against `components/ui/output_folder.py`, Gravity and ESM evidence modules, seismic review bundler and `engineering/registry/CANONICAL_MODULES.csv`. These exist and must be extended, not duplicated.
- Latest verified audit-test commit: `409eb8cdea4633e61c5444e76b2af366e64c2df6`; GitHub Actions run `42849406492` COMPLETED SUCCESS. See https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/42849406492.

## Verification performed
- GitHub API verified new files and commits on isolated feature branch.
- **PASS on GitHub Actions:** Python 3.12 compile, offline test fixtures, complete tracked-file audit generation and output-schema checks for commit `409eb8cde`. See workflow run URL above. Audit artifact is downloadable from the run.
- **NOT RUN:** Windows Spyder GUI, ETABS COM, OpenSees native model, numerical engineering regressions.
- Repository inventory outputs are generated on a local clone with:
  `python tools/audit_repository_structure_v4.py --output docs/architecture/generated`
- Run tests using: `python -m unittest discover -s tests -p verify_repository_structure_audit_v4.py`
- No source input, engineering results, EDB, Excel workbook, ground motions or application launcher changed.

## Limitations and immediate next action
- This first audit intentionally does **not** claim dynamic import coverage, source equivalence, redundancy safety, or all requested per-file metadata.
- Next: download full CI audit artifact, inspect duplicate candidate groups, add precise runtime-path and callback ownership mapping, reconcile PR #15 before changing GUI or physically migrating modules. Current static reports are only screening candidates.
- Native engineering validation and first-step wall element 110280 diagnosis remain unresolved. No equivalence, reduction in duplicate runtime implementations, or speed improvement has been demonstrated.
- Do not automatically merge into main.

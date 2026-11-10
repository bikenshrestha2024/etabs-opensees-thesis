# Repository refactor progress — V4 baseline

**State:** Phase 1 started — read-only inventory tooling introduced; no physical model or numerical solver edited.

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

## Verification performed
- GitHub API verified new files and commits on isolated feature branch.
- **NOT RUN:** local Python tests, Windows Spyder, ETABS COM, OpenSees, numerical regressions.
- Repository inventory outputs are generated on a local clone with:
  `python tools/audit_repository_structure_v4.py --output docs/architecture/generated`
- Run tests using: `python -m unittest discover -s tests -p verify_repository_structure_audit_v4.py`
- No source input, engineering results, EDB, Excel workbook, ground motions or application launcher changed.

## Limitations and immediate next action
- This first audit intentionally does **not** claim dynamic import coverage, source equivalence, redundancy safety, or all requested per-file metadata.
- Next: execute offline tests and inventory on a full checkout; review generated CSV/tree; add targeted AST symbol and dynamic-callsite analysis; inspect PR #15 overlap and merge strategy before GUI refactoring.
- Native engineering validation and first-step wall element 110280 diagnosis remain unresolved.
- Do not automatically merge into main.

# Historical source-review attestation invalidation — 2026-11-22

The integrated audit found one **stale and no longer qualified** attestation. This change does not erase the previous review. It moves the original exact-source evidence to a historical register, while its former active claim is removed so the static evidence gate no longer represents a changed file as independently reviewed.

- Source: `components/inputs/project_workbooks.py`
- Symbol: `read_explicit_excel_calculation`
- Prior attested Git blob: `d0879ac0973b33b92149be7a5cb72626241a752c`
- Current Git blob: `bff3398068c39d3ec183b710672fda2a6739cead`
- Original evidence: `REVIEW_MAIN/02_ESM/20261117_EXPLICIT_EXCEL_STREAMING_SOURCE_IDENTITY_REVIEW.md`
- Original test: `tests/verify_esm_explicit_excel_method.py`
- Outcome: **REVIEW_REQUIRED** for current source; no new attestation is invented.

This is an audit **static-evidence integrity correction only**. It does not validate model-aligned Aw, NBC 105 equations, native ETABS COM or OpenSees solver parity. Legacy output-path and import-cycle findings continue in the review register. Avoid re-adding an active attestation merely by copying the latest SHA; a new source-level review and reproducible test/evidence record are required.

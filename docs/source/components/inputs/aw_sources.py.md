# aw_sources.py — implementation guide

**Source:** [components/inputs/aw_sources.py](../../../../components/inputs/aw_sources.py)
**Workstream:** 01 Import/geometry → 04 Modal / ESM period. Added on branch `improve/damping-energy-viz` (2026-11-07).

## What it does

Returns a labelled wall index Aw for the modal audit and ESM windows, so the fields are no longer blank when no same-EDB SCALING SUMMARY workbook exists. Sources, in order of authority:
1. **ORIGINAL_EXCEL_METHOD_ETABS_LINKED**: the newest `*_ETABS_LINKED_ESM.provenance.json` in the state's analysis folder. Its source EDB must be the export's source EDB (same path or same SHA256), its condition must match the limit state, and its direct thickness check must not be MISMATCH.
2. **OpenSees geometry candidate** from `opensees_nbc_sync._source_snapshot` (read-only), e.g. `PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC`. This is never NBC acceptance.

A result from a different EDB is not auto-filled; it stays available through the explicit buttons with an identity warning. The modal GUI writes the chosen source to `Modal_<state>/Wall_Aw_Source.json`.

## References

NBC 105:2025 §5.1.2 (R10); docs/review/20261106_THESIS_EXCEL_METHOD_DECISION_REGISTER.md. Tag convention: [REF_TAG_CONVENTION.md](../../../../docs/REF_TAG_CONVENTION.md).

## Verification

Test: `tests/verify_aw_sources_and_thickness.py`. Fake-ETABS and synthetic-file tests only; a live ETABS session is not exercised.

[Guide index](../../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../../docs/00_THESIS_ACCEPTANCE_GATES.md)

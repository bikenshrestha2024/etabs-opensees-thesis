# Source-level follow-up audit V9 — missing stiffness evidence and late [OK]

**Date:** 2026-11-14. **Scope:** Current `main` source files after PR #61. This is not proof of a native Windows ETABS/OpenSees run, full source-model equivalence, NBC 105:2025 code acceptance or full GUI end-to-end coverage.

## Verified source-level defects

**S-02 (P0): missing soft-storey stiffness could look reassuring.** `components/validation/saved_stiffness.py::merge_saved_stiffness` only appended missing ULS/SLS X/Y coverage rows *inside* `if imported`. When no matching irregularity JSON existed (for example a first-time model or a different serialized model hash), `coverage` was empty and `overall` could become `NO TRIGGER FOUND` with no `NOT EVALUATED` rows. A missing numerical analysis cannot establish that soft-storey irregularity is absent.

**Fix:** each call now produces explicit `NOT EVALUATED` entries for every missing (ULS/SLS × X/Y) source-matched centered case, even if no result has been imported. Synthetic coverage notices are removed and rebuilt on refresh for idempotence. Real imported source-matched rows retain their original irregularity status and the overall status remains `IRREGULAR` when warranted.

**H-02 (P1): late success could erase a truncated case.** The history progress parser accepted `[OK] <case>:` even after the same record had already been marked `TRUNCATED` (or `FAILED`, `NOT COMPLETED`). This could defeat the V7 ledger-based completion gate when a runner printed a generic cleanup success line after its diagnostic interval.

**Fix:** `update_history_case` no longer promotes these terminal unsuccessful states to `COMPLETED` from a late `[OK]`. Independent reruns keep their own fresh case/run identity and ledger.

**I-01 (P1): nonhexadecimal SHA labels were treated as real hashes.** `components/validation/saved_case_identity.py` accepted any 64-character value for saved MRSM/ESM/Deformation sources (although canonical manifest validation already enforced hexadecimal SHA256). This could wrongly exclude a historical response as a proven model mismatch. Now all saved-source digest inputs use the same exact 64-character hexadecimal validator; invalid labels remain `NOT_VERIFIED`.

## New regression checks

`tests/test_post_v8_missing_coverage_v9.py`: 4 missing source cases, repeated refresh without duplicated warning rows, partial one-axis source import, a truncated record followed by a misleading late `[OK]`, and malformed 64-character source hash labels.

**Limits:** The saved stiffness merger still needs native validation that source case data represent the same ETABS stiffness, actual load setup and geometry; source hash only establishes exact serialized JSON identity. A structured history completion message is still not independent evidence that every requested ground motion reached its physical end time; inspect accepted time vectors and original record metadata. The ongoing 32/76/97 support reaction, MESH_04/08/16 load path, P-Delta, slab stiffness, pinned outrigger and wall-material calibration gates remain open.

**Source file preservation:** no ETABS EDB, Excel, project reinforcement, ground motion, existing result or support constraint was modified.

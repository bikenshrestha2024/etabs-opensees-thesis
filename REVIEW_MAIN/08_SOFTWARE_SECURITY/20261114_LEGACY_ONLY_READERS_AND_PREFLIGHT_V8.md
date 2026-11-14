# Missed legacy-only paths — correction V8 (2026-11-14)

**Scope:** A targeted follow-up audit of `saved_stiffness.py`, `analysis_autofill.py` and `nonlinear_preflight.py`. They were still coupled to `OpenSees_Analysis_Results` even after the canonical stage contracts and V7 completion guard had been merged.

## Implemented software corrections

1. **Saved irregularity/stiffness screens:** `merge_saved_stiffness` now looks for source-model-matched E0 irregularity results in both canonical `03_ESM/05_MRSM` stages and historical results. Previously it read the legacy root only. Excludes `REVIEW_SNAPSHOTS` and review ZIP copies; retained SHA comparison avoids showing a different source model's screen.
2. **Modal period/Tn autofill:** `matching_modal_reference` scans `04_MODAL` and historical modal files and requires an exact serialized-model SHA and ULS/SLS state before returning modal rows. `populate_linear` and `populate_site` no longer fall back to the first saved file when the chosen project source does not match. Missing data produces an explicit note, not a silently imported mode period. This is especially important when ULS and SLS use different elastic stiffness.
3. **Nonlinear dependency preflight:** Saving a dependency inventory now writes under `09_SOFTWARE_DIAGNOSTICS/NONLINEAR_PREFLIGHT` using the shared atomic JSON writer instead of creating more files under `OpenSees_Analysis_Results`. Existing archived reports remain untouched and usable.

## Still open

- Legacy ESM multi-script production output and dependent export/ZIP readers have not all been migrated to the canonical stage.
- Full Windows GUI tests for these three changes and any stale state cached during a previously opened session are needed; always restart after updating `main`.
- Correct Tn file provenance does **not** validate the OpenSees nonlinear initial tangent, damping coefficients, modal participation, shear-wall stiffness or ETABS physical equivalence.
- Foundation 32/76/97 support reaction mismatch, MESH_04/08/16 slab–wall–beam force transfer, member release/brace equivalence, P-Delta and full nonlinear wall/device calibration remain native numerical gates.

## Test

`python -m unittest discover -s tests -p "test_legacy_reader_migration_v8.py" -v`. The test uses synthetic files only. Protect source EDB and Excel SHA; no original ETABS inputs are edited.

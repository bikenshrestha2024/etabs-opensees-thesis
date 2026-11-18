# 2026-11-18 — M0–M6 comparison manifest must not reuse model export paths

**Classification:** Confirmed fail-open research-summary source-provenance defect. **No native ETABS, OpenSees, FVD, BRB or shear-wall analysis performed by this patch.** Existing `soil_c_run_matrix.create_configs` enforces unique folders when planning 112 configurations, but `variant_comparison.validate_variant_manifest` independently parses existing M0–M6 result-summary manifests and previously did not enforce unique canonical model-export paths.

## Reproduction (test-first)

- Added `tests.verify_variant_comparison.CompareTests.test_duplicate_canonical_variant_export_path_is_rejected` to reject identical M1/M2 `model_export_path` and normalized alias paths (`M1/../M1`).
- Added `test_missing_or_malformed_variant_manifest_fails_clearly` for non-object root and non-dict row values.
- **RED:** GitHub Actions integrated review [run 44255349094](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44255349094), exact test-only commit `90c13156e73c88016e31fd395398b02e0050df83`: `FAILED (failures=1, errors=3)`. The duplicate path was accepted and malformed types raised uncontrolled AttributeError.

## Smallest source correction

- Require a manifest object containing a list of seven dictionary records, one per M0–M6.
- Normalize nonblank `model_export_path` strings with `Path(...).expanduser().resolve()`, rejecting canonical duplicates across variants.
- Preserve original four cross-variant invariant SHA checks, M0 no-outrigger check, model file SHA syntax, case-source SHA matching, accepted full-duration gates, ULS/SLS separation, cross-orientation record pair consistency, and existing seven-variant metrics.
- Existing test fixtures use synthetic model-file SHA values for several variants; **do not** assert those fixtures represent seven physically different model contents.

**GREEN required:** All affected regression tests and integrated source-review CI must pass on the exact corrected PR head. Documented source inspection status remains `SOURCE_INSPECTED_TESTED_NOT_NATIVE_VERIFIED`, and a source file change invalidates its Git blob attestation until reattested.

## Independent engineering acceptance still OPEN

Distinct paths are a **necessary, not sufficient**, condition. A copied identical model can live in a different directory, or a genuine M0–M6 model can differ in unintended masses/loads/materials rather than just outriggers. The original seven models need immutable source EDB/export checksums, geometry/mass invariants, verified member/device topology, FVD law and source accelerogram hashes. The native 76-support gravity configuration needs analytical ETABS joint data and matching six-component OpenSees physical cuts, not global FZ alone. Wall tags 110280/112778 require clean-domain transient reproduction and independent constitutive/panel calibration; 224 native XY/YX histories require complete duration and structural energy validation.

**Do not promote this source-input fix to G02, G05, G07 or G09.** No numerical result or physics parameter changed by this documentation/source patch.

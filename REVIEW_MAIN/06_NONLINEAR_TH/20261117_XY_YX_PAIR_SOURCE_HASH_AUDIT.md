# 2026-11-17 — XY/YX matched-record identity defect and review evidence

**Scope:** Narrow software provenance defect in the research M0–M6 result aggregation. No ETABS source, OpenSees native calculation, wall elements, damper coefficients, ground motion or user private files changed. Do not declare any completed 224-case NLTHA.

## Reproduced input contract violation

Source: `components/nonlinear_time_history/variant_comparison.py::compare_completed_cases`.

The code requires that `record_sha256` match the M0 reference **across variants**, separately for each `(limit_state,pair_id,orientation)`. It did **not** require the underlying paired source to match **between XY and YX orientations for the same pair**. This permits each variant to use the same incorrect YX record, giving cross-variant agreement while violating the physical premise of an orientation swap.

Test: `tests/verify_variant_comparison.py::CompareTests::test_reject_different_record_hash_for_xy_yx_same_pair` constructs a realistic case: all M0–M6 models have `ULS/P1/XY` using SHA A and `ULS/P1/YX` using valid but different SHA F. Previous validation incorrectly accepted it.

**RED proof:** Integrated PR workflow [run 44083506351](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44083506351), test-only head `7e6cc1c2ad595687de76e0f3639fbdf92ec71281`: `AssertionError: ValueError not raised` for the regression. The earlier single-variant mismatch was already rejected by the existing cross-variant guard; that was not the confirmed defect.

## Correction and acceptance

The comparator now checks for identical `record_sha256` between XY and YX in the M0 reference, **within each limit state and pair ID**. Existing cross-variant SHA checks propagate this invariant to all seven models. ULS and SLS can legitimately use different seismic input/scaling and are not conflated. Missing orientations are still rejected by the pre-existing paired-case completeness gate.

**GREEN proof:** GitHub Actions [run 44083700311](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44083700311) completed successfully on source-fix commit `1cccacdbe960faa9ee00911776384123a4f86a1f`. The integrated workflow's focused audit regression step passed; the other three workflows (repository compilation, pinned source discovery and public model disclosure) also completed successfully. Any later document-only commit receives its own required checks. Where recorder provenance uses an ordered concatenation of XY/YX components rather than orientation-invariant pair hash, normalize that upstream contract before this gate can be used; do not silently hash different physical files into one fabricated identity.

## Still open

- Full-function semantic review of active engineering/source/GUI and all dynamic readers/writers, despite machine-wide static inventory.
- ETABS v23 source-object and analysis-mesh support reconciliation at 32/76/97 nodes; nodal and physical-wall-cut force/moment equivalence.
- First-step nonlinear E-SFI/FSAM X-wall element 110280 native reproducer and converged complete seismic record.
- Verified material laws, FVD SI/unit consistency, Rayleigh/damper energy, strict XY/YX ground motion provenance and signed results for all M0–M6 models.

**Statuses:** source-focused fix passed CI on pinned source commit; native physical/model/experiment acceptance **NOT VERIFIED**. Public repository contains authored source and narrative only.

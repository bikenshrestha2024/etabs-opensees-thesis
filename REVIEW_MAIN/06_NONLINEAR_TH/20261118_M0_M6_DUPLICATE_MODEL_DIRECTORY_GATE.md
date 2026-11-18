# 2026-11-18 — M0–M6 duplicate model export identity gate

**Issue:** `NLTHA-MATRIX-MODEL-DIR-01`. **Scope:** repository software source-input provenance, **not** a finished structural analysis. Exact baseline main `0a217b4ef7a8b60f7b2111964c9353b506c3ed49` (3,188 tracked files).

## Reproduction and root cause

`components/nonlinear_time_history/soil_c_run_matrix.py::create_configs` accepts a JSON mapping for `M0`–`M6` and verifies each folder exists. It previously did **not** verify that canonical resolved paths are unique. If `M2` points to `M1`'s exported model folder, all **112** case configuration files and **224** intended XY/YX orientations are still generated under different labels; such a comparison would be confounded by identical source physics.

**RED verification:** [GitHub Actions integrated audit 44212503468](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44212503468), test-only commit `7aaf599a01f72a656961df04113b1d1de87e7c44`. The added `tests.verify_soil_c_run_matrix.RunMatrixTests.test_duplicate_m0_m6_model_export_is_rejected_without_outputs` failed with `AssertionError: ValueError not raised`; the normal 112-config creation path remained intact.

## Minimal correction

After each path is normalized using `Path(...).resolve()` and before any waveform lookup or output creation, `create_configs` now rejects any pair of different M labels sharing a canonical model export directory. The exception includes both labels and the duplicated path. The failed call must not create `output_dir`.

**GREEN criterion:** repeat exact regression on patched PR head plus all relevant repository CI. Update `docs/review/ledger/semantic_review_attestations.csv` to source Git blob SHA `ca9ae10e9d976fbcdb83f98fc99b5887d8356f8b` and rerun integrated source attestation checks.

## Limitations and follow-up

- Distinct directories are **necessary but insufficient**: two folders may contain copied or byte-identical models. A stronger physical-variant gate must compare source geometry, topology, material and device assignments, excluded variants, and exported model-file SHA-256 values.
- The generator is **configuration-only** and explicitly sets `CONFIGURATION_ONLY_NOT_EXECUTED`; no OpenSees model or earthquake history was run. Existing conditions `source_evidence_not_yet_complete=True`, `rayleigh_device_exclusion_reviewed=False`, missing damping modes and Gorkha/Loma processing review remain accepted as configuration placeholders only.
- No model geometry, supports, material law, wall formulation, damper coefficient, earthquake source data or performance criterion was modified by this code correction.
- The 32/76/97 ETABS/OpenSees gravity reaction discrepancy remains unexplained physically; the first-step X-wall nonfinite after solver failure remains unresolved. Configuring 224 orientations cannot close G02/G05/G07.
- Model folders must be created from original source exports without altering the baseline M0–M6 comparison. Do not silently rename duplicate models into distinct folders merely to satisfy this guard.

## Prioritized physical qualification chain

**S1** source EDB/export checksum and exact seven model-to-differences crosswalk; **S2** original analytical joint/diaphragm/6-DOF support + physical wall-base force/moment parity; **S3** coupon, panel, brace/FVD and zero-excitation benchmarks; **S4** reproduce and eliminate the X-wall first-step failure with the same material/geometry; **S5** finish all 224 input-SHA-verified native XY/YX histories with temporal/energy/convergence data; **S6** compare performance only for independently accepted histories.

**Gate result:** source-directory uniqueness check is a regression-tested *software prerequisite*, not proof of actual seven distinct structural models or finished physical validation. Independent engineering acceptance remains **OPEN**.

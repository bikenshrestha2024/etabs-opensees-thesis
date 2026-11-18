# 2026-11-18 — Strict Soil C input-waveform source-map verification

**Issue:** NLTHA-MATRIX-SOURCE-MAP-02. **Scope:** configuration input provenance, not verified seismic excitation or material/structural numerical response.

## Root cause and test-first proof

The prior `soil_c_run_matrix.create_configs` accepted a supplied nonempty `source_map` without validating that it had **exactly** the 16 expected `(event, A/B)` entries. Missing keys might produce a later uninformative `KeyError` during generation, extra keys were silently ignored, and the same source file could appear under two different event/component labels. This is unacceptable when building the 112 case configurations and 224 intended XY/YX orientations.

**RED:** [integrated run 44213076527](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44213076527), test-only commit `6111b1cda028d28b4bd739f34a94f2d13d663aa5`: `tests.verify_soil_c_run_matrix.RunMatrixTests.test_explicit_waveform_map_requires_exact_16_distinct_sources` failed with `AssertionError: ValueError not raised` for a duplicated source path. The test also covers missing and extra mappings and verifies no output directory is written.

## Source correction

- Require the set of supplied `(event, component)` keys to equal exactly the registered eight-event × two-component set; reject missing/extra entries before writing any configuration.
- Normalize user-provided paths via `expanduser().resolve()` and reject a canonical path reused under multiple waveform labels (including symlinks resolving to the same source).
- Require source-path values to be a nonblank string or `Path` object; use normalized path strings in configurations.
- Preserve normal `source_map=None` behavior, where `resolve_sources` discovers the original `register_rows` SHA-verified exports. The explicit source-map path still permits **nonexistent paths** in configuration-only synthetic tests and therefore is **not** source-byte verification.
- Keep original seven model-directory uniqueness guard (PR #114) and missing-damping/record evidence flags unchanged.

**GREEN criterion:** Exact PR-head Python `tests.verify_soil_c_run_matrix` and integrated audit plus NLTHA-quality CI pass; canonical `docs/review/ledger/semantic_review_attestations.csv` records the changed `create_configs` Git blob. An accepted *path map* does not establish an accepted or spectrum-matched accelerogram: production validation still needs file existence, real SHA-256 of each original SeismoMatch waveform, sample count, dt, units, scale, Gorkha duration and Loma endpoint assessment.

## Native engineering distinction

No original ETABS EDB, private accelerogram, native OpenSees transient, RC wall experiment or device calibration was run. M0–M6 distinct directories and 16 distinct waveform *paths* do not prove physically different models or registered *bytes*. No change to material, damper `C/alpha`, wall, releases, supports, mass, damping or timestep.

**Open gates:** full semantic function review; source-equivalent 32/76/97 support/physical wall cut and point-force/moment parity; wall element 110280 initial X transient convergence; and all 224 physically accepted M0–M6 nonlinear earthquake histories. The software input contract correction alone **cannot** mark any of these as accepted.

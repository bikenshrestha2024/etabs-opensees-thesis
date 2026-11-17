# 2026-11-17 — First-step X-wall transition evidence: mixed-source and stage-order rejection

**Issue:** `WALL-TRANSITION-PROVENANCE-01`. **Affected function:** `components/nonlinear_time_history/first_step_transition.py::compare_first_step_stages`.

## Source inspection and reproducer

The existing wall diagnostic captures read-only snapshots from `GRAVITY_FROZEN`, `AFTER_EIGEN`, `BEFORE_EXCITATION`, and `FIRST_ACCEPTED_STEP`. Its comparator previously iterated over user-supplied files and designated `last_finite_stage` / `first_nonfinite_stage` using the supplied order. It did **not** reject (a) different source model SHA-256 values between snapshot files, (b) one file with a source model SHA and another without it, or (c) reverse/duplicate stages.

That can fabricate an apparent temporal bracket from files taken from different building models or supplied out of sequence. A bracket is at most a diagnostic finding, **not** proof of which RC wall, constitutive model or element triggered nonlinear divergence.

**Independent RED evidence:** GitHub Actions integrated run [44091525583](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44091525583) at test-only commit `7dbea662b00203d161b33879a6a0ead772672727` failed with two regression failures:
- `tests.test_first_step_transition.FirstStepTransitionTests.test_stage_comparison_rejects_mixed_source_model_hashes`
- `tests.test_first_step_transition.FirstStepTransitionTests.test_stage_comparison_requires_strict_chronological_stages`

The new regression checks mixed `a*64`/ `b*64` SHA, present/missing identity, reversed `BEFORE_EXCITATION`→`GRAVITY_FROZEN`, and duplicate stages. No private EDB/waveform was used or uploaded.

## Minimal correction

- Require snapshots' `source_model_sha256` fields to be identical; reject a mixed populated/missing identity. If **all** files are legacy snapshots without source SHA, preserve comparison for backwards compatibility without interpreting it as verified source identity.
- Require strictly increasing original stage order and no duplicates; nonadjacent stages may still be compared as a **limited bracket**, but skipped stages must not be assumed normal or finite.
- Reject an invalid populated SHA-256 field; retain existing numeric-response/force evidence and source-mapping statuses.
- No OpenSees element response, material, nonlinear solver command, time-step setting, boundary condition or mass is changed.

**GREEN acceptance:** exact code-commit GitHub CI run must execute both new tests and existing `test_stage_comparison_reports_onset_not_causation`. The integrated audit, syntax/import navigation, private-data boundary and any path-triggered NLTHA quality workflow must pass. New function review attestation binds to exact changed Git blob and is invalidated on later edits.

## Native wall-verification questions remaining OPEN

1. Establish identical input model and area-element tag map for 110280/112778 with exact model SHA-256 and solver version.
2. Produce real `GRAVITY_FROZEN`, `AFTER_EIGEN`, `BEFORE_EXCITATION` and `FIRST_ACCEPTED_STEP` records from a clean, native OpenSees domain; keep the first failed attempt and last accepted state, not merely postfailure `localForce`.
3. Verify finite material stress, strain and tangent through independent ConcreteCM/SteelMPF/FSAM tests, then the wall panel, connected frame/core and complete 25-storey original model.
4. Check gravity and diaphragm compatibility, source mesh connectivity, mass, fixed DOFs, activation of both horizontal components, region damping and numerical integration/timestep sensitivity.
5. Only after the **same** source model completes the full requested seismic record with finite accepted channels and independent force/energy benchmarks can this wall gate advance beyond exploratory.

**Acceptance outcome:** snapshot *provenance* software defect addressed; actual first-step wall convergence **UNVERIFIED / OPEN** and full M0–M6 earthquake suite still **NOT VERIFIED**.

# 2026-11-17 — NLTHA time-step comparison source identity guard

**Classification:** Confirmed source-level software defect; regression-driven fix; no engineering physics changes. **Does not verify** 32/76/97 ETABS–OpenSees reactions, element 110280 nonlinear wall convergence, or the 224 required M0–M6 XY/YX full-duration analyses.

## Reproduction, original root cause and test evidence

`components/nonlinear_time_history/full_record_gate.py::compare_time_step_results` checks `model_sha256`, `record_sha256`, `limit_state`, `orientation`, `diagnostic_excitation`, status and accepted time-step sizes, but previously omitted identity checks for `variant_id` and `pair_id`. Identically hashed data reused or mislabeled for different variants/events could pass as a time-step convergence study even when the named case was inconsistent.

A failing test was committed *first* in `tests/verify_full_record_gate.py::GateTests::test_timestep_rejects_different_variant_and_pair_identifiers`, using equal model and motion hashes but different `variant_id` or `pair_id` between coarse and fine summaries. Four negative cases—M2 vs M4, Kobe vs Chi-Chi, and one missing identifier on either side—were incorrectly accepted by the previous implementation.

**Red:** GitHub Actions [run 44085012203](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44085012203), test-only commit `832edcf3b2b4fe238a61833d27d1bb65271862d6`, recorded `FAILED (failures=4, skipped=1)`, with `AssertionError: ValueError not raised` for each of four subtests.

## Source fix and compatibility constraints

If either summary explicitly claims `variant_id` or `pair_id`, the two reports must provide the same nonblank value; otherwise comparison raises a clear `ValueError`. If neither provides these optional identifiers, the existing older synthetic/legacy summaries remain supported. **Legacy missing IDs still cannot establish source authenticity.** Do not interpret compatibility with such summaries as model validation or publish comparison metrics as accepted thesis results without exact variant/record provenance. Actual production results should carry both IDs.

**Green acceptance:** Run the exact PR-head `.github/workflows/integrated-repository-audit.yml` test including `tests.verify_full_record_gate`; all four required CI workflows must finish successfully. This source note does not claim an unobserved test result. No material law, solver settings, motion scale, model mass/stiffness, support restraint, device law, nonlinear wall or research result changed.

## Pending substantive acceptance

- **Semantic review:** Full AST inventory is not a function-by-function review; retain source SHA, inspected lines, cross-caller contract, test and evidence per attested symbol.
- **ETABS–OpenSees:** Original Windows ETABS v23 EDB/source analysis joint connectivity + six-DOF object/element reactions, common physical wall-base cut and native OpenSees reaction evidence must be compared for 32/76/97.
- **Nonlinear wall:** Reproduce failing wall element 110280 (first X step) with matched full native build, exact node/element mapping, constitutive calibration, mass/tangent/constraint/energy checks and an accepted full history; do not adjust convergence blindly.
- **M0–M6 full NLTHA:** 112 study configs × XY/YX = 224 completed source-hashed numerical histories with matched pair and solver/dt/time/energy evidence, plus independent experiment/NBC engineering review.

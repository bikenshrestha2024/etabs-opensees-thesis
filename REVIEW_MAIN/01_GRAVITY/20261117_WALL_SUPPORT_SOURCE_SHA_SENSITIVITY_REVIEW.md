# Gravity wall-restraint sensitivity — source SHA cross-case verification (17 November 2026)

**Defect:** `components/gravity/support_scenarios.py::compare_wall_support_gravity` accepted a pair of independently executed `ETABS_SOURCE_SUPPORTS` and `CONTINUOUS_WALL_BASE_FIXED` gravity results if reported loads and common node XYZ agreed, without checking their underlying source model SHA. If exports from **different building model versions** coincidentally shared such values, the resulting nodal reaction differences would be falsely interpreted as an isolated boundary-restraint sensitivity.

## Reproducible failing test before fix

`tests/verify_gravity_support_scenarios.py::DualWallGravityTests::test_reject_mixed_source_model_identity` supplies the same valid synthetic 300-kN equilibrium and same shared geometry but model SHA `a*64` versus `b*64`; it also removes one hash and requires rejection. **RED:** [integrated CI run 44092603858](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44092603858), test-only commit `f26931725814563b80806ef590b32a4a6baecd88`, confirmed `AssertionError: ValueError not raised` at the cross-model mismatch. The same source hash on both cases is a positive control.

## Narrow implementation and limits

When **either** `source_result["model_sha256"]` or `continuous_result["model_sha256"]` is provided, both must be valid 64-hex-character SHA-256 strings and equal; an invalid, missing or different value fails before generating any comparison. All-absent legacy inputs remain eligible for legacy **boundary sensitivity only**, because making SHA mandatory would break old saved records and synthetic tests; they **cannot** be relabeled independently source-verified. This change does not alter source loads, reaction signs, section or shell constitutive behavior, 32/76/97 support DOFs, or native model execution.

**GREEN criterion:** exact PR-head GitHub integrated audit must pass the new positive/negative tests and the complete static/compilation/disclosure checks. No green status is inferred from this document alone.

## Full engineering parity still blocked

The private workbook `ETABS_OpenSees_Full_Gravity_Reaction_Comparison.xlsx` had globally matching reaction sums (`311367.313600` vs `311367.313880` kN), yet OS76 allocated `104463.013534 kN` to 44 wall-connected source-restraint points where ETABS point-object FZ was zero. See [independent partition](20261117_INDEPENDENT_REACTION_PARTITION_32_76_97.md). This fix excludes cross-source comparisons, but **cannot explain** ETABS internal analytical-joint/MPC force recovery. Native ETABS v23 analysis-element/joint six DOF supports, 6-component physical wall cuts, rigid offsets and self-weight, plus original OpenSees loaded 32/76/97 runs and one-bay ShellMITC4 load-path convergence are required. Do **not** delete the 44 original restraints to force agreement or promote passing global equilibrium to structural equivalence.

**Acceptance:** source identity check software contract = pending exact-CI PASS; local ETABS↔OpenSees physical parity = **NOT VERIFIED**. Native solver and peer-reviewed thesis acceptance remain independently OPEN.

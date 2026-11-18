# 2026-11-18 — Gravity ETABS/OpenSees screening numeric integrity regression

**Classification:** Confirmed source-level diagnostic-contract defect. **No native ETABS/OpenSees physics modified or executed.** Baseline main `0a217b4ef7a8b60f7b2111964c9353b506c3ed49`, untruncated Git tree of 3,188 files.

## Root cause, source inspection, reproducer

`components/gravity/validation_scorecard.py::create_gravity_scorecard` accepted unvalidated numerical screening thresholds `global_tolerance_percent`, `node_relative_tolerance_percent`, and `node_absolute_tolerance_kN`. Python booleans can be treated as floats; `NaN`/infinity, negative and unparseable values could silently bypass the intended comparisons or crash inconsistently. Its helper `_num(True)` returned `1.0`, treating a boolean flag as measured gravity reaction evidence.

Added regression `tests.verify_gravity_validation_scorecard.GravityScorecardTests.test_invalid_diagnostic_tolerances_fail_closed`: for all three tolerance fields test `True`, `False`, `-1.0`, `NaN`, `Infinity` and a nonnumeric string. Added `test_boolean_reaction_value_is_not_numerical_evidence` to prevent spurious numeric equality.

**RED evidence:** GitHub Actions integrated audit [run 44215005273](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44215005273), test-only/CI-wired head `1dd99b74d63b1e96503b4b1c964dc27df414fc00`, reported `FAILED (failures=16, errors=3)`. The workflow previously did not execute the gravity scorecard tests; the PR adds `tests.verify_gravity_validation_scorecard` to the focused audit CI command before source modifications.

## Minimal source correction

- All three screen values are cast to finite, nonnegative floats; reject boolean, negative, NaN, Infinity and unparseable values before file I/O or comparison. Numeric zero remains permitted as an intentionally strict screening tolerance.
- `_num` returns `None` for bool and now catches OverflowError. Numeric evidence from source files is still screened for finite values.
- Same structural scorecard conclusion `NOT_STRUCTURALLY_VALIDATED`, even where global and individual support-reaction values fall within diagnostic tolerances.
- Existing gravity loads, six-DOF source restraints, support choice, wall/beam stiffness, solver step and comparison node mapping unchanged.

**GREEN evidence and exact head:** Must be checked after full focused suite and all GitHub workflows have completed, and the result recorded on the pull request; a code change alone is not an accepted test.

**SHA-pinned semantic ledger:** newly attested `create_gravity_scorecard` Git blob `170ebdb8878714ae1e4ff3778f0236ee376e3737` in `docs/review/ledger/semantic_review_attestations.csv`. Status is `SOURCE_INSPECTED_TESTED_NOT_NATIVE_VERIFIED`, not whole-module or physical-model approval.

## Physical engineering gate remains blocked

Existing independent private-workbook analysis: ETABS total FZ `311367.313600 kN` vs OpenSees total Rz `311367.313880 kN` for 1.0D+1.0L; however, the OS76 wall-connected 44 source-restrained nodes attract `104463.013534 kN` (33.55% of total), whereas ETABS point-object FZ is zero for these objects. Zero difference in overall support vertical force does **not** establish identical stiffness/connectivity, point-object vs analysis-mesh transfer, or six-component physical wall-base resultants.

**Native next tests:** original ETABS EDB SHA and source analytical-joint six-DOF restraint/constraining links; exact 76-source-restrained OpenSees equivalent and 32/97 sensitivity cases; wall physical cuts FX/FY/FZ/MX/MY/MZ, same origin; 1 kN/m² slab/beam/wall load path, geometric mesh refinements, rigid ends, and member deformations. No native equivalence declaration until these are reproduced with physical criteria approved before testing. X-wall element 110280 first-step, full 224 M0–M6 records and total function-by-function semantic review remain unverified.

## FEMA P-58-1 (2018) boundary

The user has provided both an unreadable 96-MB `Fema p-58-1 December 2018.pdf` object and a page-accessible but image-only 340-page `Fema p-58-1 December 2018(1).pdf` copy. FEMA P-58 performance-loss assessment depends on explicit performance groups, demand intensity, fragility components, inventories/quantities, occupancy, consequences and uncertainty. A structural displacement or peak drift alone does **not** justify an economic loss, repair cost or functionality conclusion. No full image-only equation-by-equation review or FEMA-specific PACT computation was conducted here. Do not promote exploratory component-level building metrics to FEMA P-58 loss outputs.

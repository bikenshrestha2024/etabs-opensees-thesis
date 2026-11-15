# V26 — X-wall first-step failure evidence preservation
Date: 2026-11-15. Base Git main SHA: `dd893861d89b32bcab50bd5c35108dce53fba32f`.
**Classification:** `SOFTWARE_DIAGNOSTIC_CAPTURE_FIXED_NATIVE_X_WALL_ROOT_CAUSE_OPEN`.

## Concrete source defects and implications

Inspected `components/nonlinear_time_history/failure_evidence.py` and `tests/verify_failure_evidence.py`. Previously both accepted-state and post-failure snapshots encoded `ops.getTime()` as a raw float and then serialized a JSON document with `allow_nan=False`: once the solver produced NaN/Inf time, the recorder itself failed, erasing critical evidence. The post-failure recorder also parsed the external element source map before the report existed; a malformed JSON map or conflicting element tag stopped evidence generation. Tags passed through `int()`, silently turning fractional element IDs into different observed IDs, and an empty focused tag list could create a report with zero queried elements.

## Fixes committed

1. Nonfinite clock is stored as JSON `null` in `time_s` (committed snapshot) or `analysis_time_s` (failed attempt), with explicit `time_status`/`analysis_time_status` of `NONFINITE_NAN` or `NONFINITE_INFINITY`. Normal finite numeric time remains unchanged.
2. Source mapping failures become `element_map_status=INVALID_SOURCE_MAPPING` with `element_map_error`; nonfinite element response is still captured. A missing or corrupt source mapping is **not** a wall-element attribution or physical cause.
3. Focused suspect element tags must be nonempty, at most 16 distinct, positive integer IDs. Neither fractional, boolean nor empty tag identities can be silently accepted; plain positive decimal strings remain supported.
4. Both snapshot documents use the existing atomic JSON output writer. Post-failure responses remain explicitly labeled rollback/contaminated and are not used as completed nonlinear analysis.
5. `.github/workflows/nltha-quality.yml` now executes `tests/verify_failure_evidence.py`, not merely watches changes to the source. The test suite uses synthetic OpenSees-like FakeOps and can never establish material or wall qualification.

## Native diagnostic output contract

Keep files associated with **one run**, never append to an unrelated model or historical output folder:
```text
<SELECTED_EXPORT_CASE>/07_NONLINEAR_TIME_HISTORY/RUNS/<ULS_OR_SLS>/<VARIANT_EVENT_XY_OR_YX>/<UTC_RUN_ID>/
  00_INPUT_SOURCE/      CASE_MANIFEST.json; source model SHA; source motions; source mesh mapping SHA; material provenance
  01_LOGS/              solver_stdout.txt; solver_stderr.txt; original failure traceback
  02_RESULTS/           accepted_history.csv; last finite accepted state index; failed step time and return code
  03_EXCEL/             numeric metrics (if completed; never invented)
  04_FIGURES/           available finite-history figures (never plot contaminated failed states as accepted)
  05_COMPARISONS/       zero-motion/X/Y/XY, timestep and wall panel/connected-bay evidence
  06_REVIEW/            FIRST_STEP_FAILURE/Last_Accepted_Committed.json
                       FIRST_STEP_FAILURE/First_Step_Failure_Evidence.json
                       FIRST_STEP_FAILURE/MAPPING_STATUS.json
  07_EXPORT_ZIP/        zipped reproducible review bundle with source hashes
```

This is a **target output taxonomy**; the snapshot functions honor the caller's provided `output_path`. No untested mass writer/reader relocation is claimed.

## Root-cause hypothesis checklist, not diagnoses

- Match element tag 110280 to a source quadrilateral with exact source model SHA, node IDs/XYZ, local axes, material region and original wall section.
- Independently verify reinforcement, confinement, source M30/Fe500 treatment, concrete/steel/FSAM constitutive units and all model initialization calls.
- Record gravity preload convergence/reactions, actual restraints and 32/76/97 scenario label, mass and Rayleigh damping, initial stresses.
- Perform separate clean-domain zero-input transient, X-only, Y-only and paired X/Y trace at the original time step; preserve last committed response **before** the failed solve, then record attempted dt, return code, iteration convergence and post-failure observations.
- Use single source wall quad and a connected bay with independently derived boundary/interface demands before treating a panel test as a building-level conclusion.
- Run timestep sensitivity and full 224 native M0–M6 ULS/SLS XY/YX cases only after demonstrable material and source model qualification. No short exploratory or uncalibrated run can be counted as a completed sensitivity analysis.

**Engineering acceptance:** still `PENDING_NATIVE_SOURCE_SOLVER_REPRODUCTION`, because no live X-wall transient model was executed by this source revision.

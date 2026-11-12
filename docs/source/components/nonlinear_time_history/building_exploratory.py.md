# building_exploratory.py — Research full-building nonlinear runner

**Python source:** [components/nonlinear_time_history/building_exploratory.py](../../../../components/nonlinear_time_history/building_exploratory.py)
**Current Git blob SHA:** 7c7141c691ac44906b60837b4b2d95876f6121a7
**Review status:** Source content was inspected for these specific behaviors. Physical/numerical validation not executed.

## What this file currently implements
Copies source export to isolated_model, reads paired PEER histories, creates ULS/SLS cases and fresh XY/YX models, performs gravity preload and initial modal analysis, applies UniformExcitation, records accepted transient histories and separate failure evidence.

## Explicit assumptions and known deficiencies
Materials are explicitly research assumptions. It supports ZERO, X, Y, XY first-step diagnostics, optional Rayleigh overrides and UmfPack/SparseGeneral. A completed 0.005 s trial must be distinguished from full record; post-failure element localForce can be contaminated. Status COMPLETED_EXPLORATORY_RECORD is not accepted by the separate performance assessor as COMPLETED_FULL_RECORD.

## Required thesis engineering changes
Require identical model and record hash for each orientation; record first accepted state, dt sensitivity, solver retry changes, complete earthquake duration and finite response. Verify wall/beam/column plastic states and device outputs. Fix X-only AREA:354/482 diagnostics before M0-M6 ranking.

## Cited scientific context
R01, R02, R03, R10, R12, R13.
References are indexed in [the research source register](../../../00_RESEARCH_REFERENCES.md). Paper citations establish appropriate model context, not code validation.

## Required regression output
Unit/metadata tests, isolated material or wall benchmarks, complete solver log, model+record hashes, type-safe status, full-record duration and independent ETABS/experiment comparison. Avoid marking a case verified if any gate remains unresolved.

[Source module index](../../00_SOURCE_GUIDE_INDEX.md) · [G00–G10 acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md)


## Accepted-state early failure and source provenance (2026-11-04)

During every accepted nonlinear step, `capture` validates each recorded numeric channel with `verify_numeric_accepted_row` before appending response rows. The full-duration history gate then checks timestamps, schema stability, provenance and completeness. A malformed/nonfinite row now stops a diagnostic immediately instead of being stored as a valid nonlinear result. The 0.005s X-only wall failure remains an independent native-model issue.


## 2026-11-12 numerical evidence: nonlinear modal T1 and directional Tn90

After the current gravity-preloaded **nonlinear** model is built, the exploratory runner computes 20 eigenperiods and now calls `ops.modalProperties('-return')`. It saves `Nonlinear_Initial_Modal_Audit.json` per orientation with source model SHA, every inspected period and participating-mass cumulative ratios `partiMassRatiosCumuMX` / `partiMassRatiosCumuMY`. The reported `Tn90_X_s` and `Tn90_Y_s` are each the eigenperiod of the **first mode that actually crosses 90%**, or **null** when that directional participation is not established by the inspected modes. The solver's last 20th mode is not automatically Tn90. A modalProperties error is saved as `NOT_VERIFIED`. The production `THESIS_NLTHA` intent fails closed when both directional thresholds are not demonstrated by that initial-tangent domain; exploratory diagnostics may continue with explicit warning. This does **not** replace NBC empirical/Rayleigh-period design input, independent damping calibration or dynamic model validation.

The user's 2026-11-12 full-model exploratory trial gave initial-period list beginning **2.211471682 s, 1.540590680 s, 1.023394633 s**. These are unverified *nonlinear initial-tangent eigenperiods*, not NBC 105 §5.1.1 Rayleigh period (previously 3.8985/5.5904 s), not empirical design adopted 1.98128/1.92198 s, and **not directional Tn90** absent modalProperties evidence. Native OpenSees E-SFI nonlinear simulation needs a Windows run to verify actual cumulative participation values and Rayleigh damping ratios.

The saved `TRUNCATED_DIAGNOSTIC` `0.1/45.29 s` result with 21 finite accepted steps has **physical-time completion 0.22%**, not completed NLTHA. It is useful as a finite-state solver smoke test. It does not prove realistic cyclic behavior, peak drift, residual drift or full-record convergence. Source material selection, group identity and first-step characterization are strictly separate from code design acceptance.

# Gravity-preload → transient earthquake: adopted research procedure (2026-11-13)

**Governing:** NBC 105:2025 §§5.2, 8.1.1.2–8.1.1.3 and 9.3.1.2–9.3.1.3. **Supplementary mandatory initial-case rule:** IS 16700:2023 §7.2(d) for signed EQ P-Delta initialization (2025 BIS amendment text pending). **Status:** method selection; building's native equivalent analysis and full NLTHA still not validated.

> **Engineering questions answered:** [Nine questions on compulsory signed IS P-Delta initial cases, NBC §5.2 gravity and nonlinear state transfer](../09_ENGINEERING_QA/02_PDELTA_INITIAL_STATES/01_SIGNED_EL_VS_GRAVITY_START.md). Here we retain the canonical adopted decision and open validation gates.

## Decision

The nonlinear time-history analysis starts from a *converged NBC §5.2 gravity equilibrium*, retaining actual gravity-induced axial forces, strains and displacements and geometric nonlinearity. Freeze already-applied gravity patterns with `ops.loadConst('-time',0.0)` and remove **only** existing analysis objects with `ops.wipeAnalysis()` before defining the transient solver. New `UniformExcitation` patterns are added **after** the freeze. `ops.wipe()` is forbidden because it destroys the domain/state.

The separate four signed, compulsory project `IS16700_PD_INIT` cases (`1.2DL+0.5IL±1.5EL`, EL derived from NBC design seismic coefficient) are still solved and independently checked first. **Their ±1.5EL lateral loading is NOT automatically retained as a background force during full transient ground acceleration**: the signed static case verifies stability/linearization and methodology; transferring its full internal state requires separate signed case-specific equivalence proof, unloading strategy or other approved derivation. This ensures no artificial doubling of initial static EL and dynamic acceleration. The user-described ETABS dependent linear static EQ uses initial-case tangent stiffness but excludes initial-case load actions; a native nonlinear time history needs the physically consistent **gravity** equilibrium and P-Delta geometry, not a fabricated single equivalent stiffness matrix.

## Source code findings (checked at main before this change)

- `components/linear_time_history/runner_and_gui.py`: model builder already executes before `ops.loadConst('-time',0.0)`, and a later `ops.wipeAnalysis()` configures transient analysis. Do not repeat gravity.
- `components/nonlinear_time_history/runner_and_gui.py`: same gravity freeze, and transient setup calls `ops.wipeAnalysis()`. This is **the requested command structure already present**, not a newly proven project-valid gravity preload.
- `components/nonlinear_time_history/building_exploratory.py`: fresh complete model with `preload=True` per orientation, nonlinear gravity before input histories; check its own loadConst/analysis-switch path, support reactions and time-zero manifest before interpreting full wall response.
- `components/model/initial_pdelta.py`: currently classifies D/IL with `mass_factors`; this is **a known high-priority source-classification error risk**, because mass participation 0.3/0.6 is not identical to explicit dead/live patterns. **No silent fix without actual ETABS load categories.**
- New reusable `components/shared/gravity_transient_handoff.py` provides an **opt-in verified-evidence freeze helper**; it intentionally is **not auto-invoked by legacy runners** because those runners do not yet provide trusted proof of native preload completion. Integrate only once source-checked gravity convergence evidence is available; otherwise it must fail closed.

## Required implementation gate before accepting any full 25-storey NLTHA

1. Verify precise NBC dead + 0.6 storage live + 0.3 other live + 0 roof live ledger from actual ETABS patterns (not a gravity 1D+1L comparison or IS 1.2D+0.5IL).
2. Verify same model, support, modal state, ULS/SLS effective stiffness and gravity-equilibrium force balance. Collect reactions, deflections and axial forces with absolute and gravity-relative references.
3. Validate geometric nonlinearity for frames and walls independently (3D PDelta/corotational transforms and actual wall formulation; double offsets checked). No claim from simply calling loadConst.
4. Independently converge four IS signed initial cases with NBC-sourced EL and document sign, load factor, reactions, convergence and exact source hash. Do not use an ESM design case as compliant when high-rise is ineligible.
5. Start fresh XY and YX cases from the **appropriate physical gravity equilibrium** after `loadConst` and `wipeAnalysis`, apply *only new* input acceleration patterns, record zero-motion, X-only, Y-only then full XY/YX probes. No 0.1s probe can be called a full time history.
6. Compare no-P-Delta (noncompliant diagnostic only) versus with-P-Delta histories on identical record, timestep, damping, mass and nonlinear parameters; explicitly document the physical differences.
7. Only after material/FSAM calibration and first-step wall failures resolved, run the full suite and mark `COMPLETED_NUMERICALLY`, `ETABS_MATCHED`, `NBC_ACCEPTED` separately.

## Where, when and who

**Location:** this review + `REVIEW_MAIN/00_MODEL/20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md`; runtime evidence in the numbered analysis module's unique run case, **not** scattered next to original EDB. **When:** after verified model/gravity+modal; before each static/dynamic comparison or full NLTHA. **Who:** researcher prepares native logs, independent engineer signs source load and state-transfer rules, numerical reviewer checks response identity; neither CI compilation nor a source-code comment substitutes for that.

## References

- [Official NBC 105:2025, DUDBC](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf)
- [OpenSees `loadConst` command](https://opensees.github.io/OpenSeesDocumentation/user/manual/misc/loadConst.html)
- [OpenSees `wipeAnalysis` command](https://opensees.github.io/OpenSeesDocumentation/user/manual/misc/wipeAnalysis.html)
- [OpenSees static/transient analysis change](https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/analysis.html)
- [OpenSees `PDelta` coordinate transformation](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/geomTransf/PDelta.html)
- [Initial P-Delta case and transfer audit](../00_MODEL/20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md)

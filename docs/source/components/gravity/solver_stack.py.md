# solver_stack.py — source documentation

**Python source:** [components/gravity/solver_stack.py](../../../../components/gravity/solver_stack.py)
**Git baseline content SHA:** 0e62584ef3dfa1847c399e042b0ad51313e9ba5b
**Subsystem:** Gravity-load and support equilibration
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the gravity implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)

## 2026-11-15 numerical-input safety review

`run_gravity_stage` now rejects non-finite applied vertical loads and non-finite equilibrium tolerances *before any solver call*. Previously `float("nan")` bypassed comparisons such as `<= 0` and `error_percent > tolerance`, which could let an invalid gravity-equilibrium result appear successful and freeze gravity loads. No acceptance is now possible with a NaN/Inf source magnitude or tolerance. The source must still carry independent gravity load and reaction provenance; a finite value is not evidence of correctness.

`run_static_analysis`, `configure_nonlinear_static`, `run_gravity_stage` and `run_transient_analysis` share exact-positive-step-count validation instead of silent `int(nsteps)` truncation. Integral `int`, ASCII decimal text (such as `"20"`) and integral floats are retained for compatibility. Booleans, negative/fractional/nonfinite values are rejected before solver setup. `run_transient_analysis` additionally refuses non-finite or nonpositive `dt`.

Regression `tests/test_solver_numeric_input_contract.py` uses a call-recording fake solver to ensure failed inputs generate **zero solver calls**, and verifies accepted transient call signatures. These checks do not repair the first-step 3D wall nonfinite response or validate native nonlinear convergence; native full-case time history remains `NOT_VERIFIED`.

Independent *output* acceptance now also refuses non-finite **summed support reaction**, non-finite resulting equilibrium percentage, and non-finite vertical displacement sampled from requested model nodes before calling `loadConst`. Previously, `error_percent=NaN` made the `error_percent > limit` failure condition false and could mark physically undefined gravity as passed. This safeguard is separate from input validation. Regression tests inject NaN into `nodeReaction` or `nodeDisp` while making the fake solver report convergence, then assert that the gravity load case cannot be frozen. Actual 32/76/97 foundation reactions and OpenSees shell load transfer are still not verified.

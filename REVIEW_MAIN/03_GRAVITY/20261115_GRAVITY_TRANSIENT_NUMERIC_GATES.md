# Gravity and transient numerical input acceptance — 2026-11-15

## Evidence basis
Actual active source reviewed from the full CI source-only ZIP at Git revision `4e837643a11345c99e0bbec3f4e4eea674f7fbf2`, plus current `components/gravity/solver_stack.py` source and existing regression tests. This is a bounded semantic review of the reusable gravity/static/transient helper API, not certification of the nonlinear building solver.

## Confirmed defects and physically relevant consequences

1. `run_gravity_stage` previously evaluated `applied <= 0.0` and `float(equilibrium_tolerance_percent) < 0.0`. For NaN those comparisons are false. Likewise `error_percent > NaN` is false; a NaN source load or equilibrium threshold could evade the intended pass/fail gate, allowing `freeze_gravity_loads` despite no meaningful equilibrium evidence.
2. The same helper and `run_static_analysis`, `configure_nonlinear_static` and `run_transient_analysis` used `int(nsteps)` conversion. Fractional `nsteps=2.9` could be silently treated as 2, changing load increments or expected transient steps without explicit review.
3. `run_transient_analysis` accepted `dt=NaN`/Inf under `dt <= 0.0` and passed the invalid scalar into OpenSees configuration/execution.

## Coordinated code correction

- Fail-closed `_finite_load_quantity`: refuses booleans, strings that are nonnumeric, NaN, ±Inf and nonpositive gravity magnitudes or dt before configuring solver. Equilibrium tolerance is independently required finite and nonnegative.
- `_positive_exact_steps`: true positive integers, exact numeric text and exactly integral finite floats remain supported for compatibility; booleans, fractional floats, nonfinite values, zero, and negatives fail before solver setup. Python `numbers.Integral` supports NumPy integer values when available.
- Applied to `configure_nonlinear_static`, `run_static_analysis`, `run_gravity_stage` and `run_transient_analysis`. No change to actual iteration scheme, response recorder, numerical damping, load combinations, model supports or adopted source geometry.
- `tests/test_solver_numeric_input_contract.py` adds a no-ETABS/no-OpenSees mock solver and requires zero solver commands for all invalid values, plus accepted exact step-call signatures.

## Distinct acceptance gates

| Gate | State |
| --- | --- |
| Source-level root cause confirmed | YES |
| AST and no-solver fake API regression | PENDING_CI |
| ETABS/OpenSees gravity agreement, 32/76/97 support cases | NOT_VERIFIED |
| 3D X-wall first-step nonfinite response | UNRESOLVED |
| Full bidirectional NLTHA and NBC 105:2025 compliance | NOT_VERIFIED |

A clean input validator only prevents clearly invalid data from entering a solver. It is not evidence that the nominal model geometry, mass, gravity load path, supports, stiffness modifiers, nonlinear constitutive law or time integration is correct.

## Critical reaction-output guard identified during follow-up

The initial input-only correction is insufficient if the **solver itself** returns NaN after reporting an analysis success code. Source inspection confirmed `run_gravity_stage` computed `error_percent = 100*abs(reaction-applied)/applied` and then used `if error_percent > tolerance`: with NaN this condition is false, so gravity could be frozen. The coordinated fix now explicitly verifies finite summed support reaction, finite error percentage and finite requested nodal vertical displacements before any freeze. Regression tests make `analyze` return success but inject NaN `nodeReaction` or `nodeDisp`; both must raise `RuntimeError`, with no `loadConst` invocation. This does **not** validate the absolute numerical value or ETABS comparison of finite reactions.

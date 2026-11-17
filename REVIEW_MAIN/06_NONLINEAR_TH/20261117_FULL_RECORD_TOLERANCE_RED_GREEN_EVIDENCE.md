# 2026-11-17 — Full NLTHA completion-time tolerance fail-open repair

**Engineering status:** software contract correction only. Does not establish a completed native NLTHA, wall first-step convergence, ETABS equivalence, component calibration or NBC approval.

## Defect and independent red test

Affected source: `components/nonlinear_time_history/full_record_gate.py::verify_accepted_history`. The supplied `time_tolerance_s` was applied to accepted-history start/end and record-duration comparisons without validating its value. With `NaN`, comparisons such as `abs(last-requested)>NaN` evaluate false, bypassing missing-duration rejection. With `Infinity` or a duration-sized tolerance, truncated histories may pass duration comparisons or be treated as numerically full record. Negative and boolean tolerances were also accepted as input types.

The regression was added first: `tests/verify_full_record_gate.py::GateTests::test_time_tolerance_cannot_bypass_full_duration`. It submits two accepted states at 0.0 and 0.1 seconds against a requested one-second record; the invalid tolerances are `NaN`, `Infinity`, `-0.01`, `True`, and `1.0`. All must raise `ValueError` with `time tolerance` in the message.

**RED evidence:** GitHub Actions integrated audit run [44081995860](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44081995860), head `cda731b4477186222f356f77871a3f548e7c0851`, failed with **five subtest failures** for the five invalid tolerance inputs. Its logs confirm the expected behavior was missing. This was an intentional failing pre-fix test, not a passing release run.

## Minimal source change and scope

The completion gate now fails before examining the history rows if `time_tolerance_s` is a boolean, nonnumeric, NaN/Infinity, negative, or at least as large as the shorter of the full record and requested durations. Finite nonnegative tolerances strictly below both durations remain accepted; the prior default `1e-7 s` remains unchanged. No solver calls, material/section assignment, response computations, model geometry, motion scaling or run duration settings changed. The returned gate retains `experimental_materials_validated=False`, `device_qualification_verified=False`, and `model_verification_complete=False`.

**GREEN evidence and exact SHA:** attach the exact PR-head integrated GitHub Actions run after it completes; do not claim pass from the existence of this patch. Manual spot-check the CI test output and review no positive status is assigned to an incomplete native earthquake history.

## Remaining acceptance gates

- G0 metadata inventory / source syntax: independent GitHub CI; per-function review remains incomplete.
- G1 narrowed numeric completion tolerance: pending green test evidence.
- G2/3 ETABS-versus-OpenSees restraint topology and gravity force/moment equivalence: **NOT VERIFIED**.
- G4 first-step wall element 110280 and complete material/device/case-based numerical response: **NOT VERIFIED**.
- G5 all required M0–M6 XY/YX motion histories and duration/timestep convergence: **NOT VERIFIED**.
- G6 physical engineering sign-off: **NOT VERIFIED**.

This issue is a necessary data-quality gate, not a physical-model solution. Preserve exact source files and hashes outside public GitHub, and do not mark the thesis analyses complete based solely on software CI.

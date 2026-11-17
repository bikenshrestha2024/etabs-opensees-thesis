# first_step_transition.py — focused NLTHA onset review

**Canonical module:** `components/nonlinear_time_history/first_step_transition.py`.

This read-only research diagnostic is **opt-in** via the run configuration:

```json
{
  "diagnostic_first_step_wall": true,
  "first_step_focus_tags": [110280]
}
```

Enable only in an approved, source-matched diagnostic run. Tags are **live OpenSees element tags**, not ETABS object IDs; choose the actual tag from `OpenSees_Complete_Element_Map_V118.json`. Default 110280 is an earlier observed suspect, **not** a verified universal wall tag. No source mapping is silently inferred.

## Source and scope

Reference implementation reviewed: `bikenshrestha2024/Framework_for_Seismic_Assessment_of_RC_Buildings`, fork `main` at 2026-11-17; `Test_Models/Groups/CCP/single/Unidirectional_Multiple_Eq.py`, `Materials.py`, `FiberSectionBuilder.py`, `Gravity_Analysis.py`, and `Final_Codes/NBC_105_2020/NBC_105_2020_parallel_runs.py`. The source fork uses RC fiber frames, `forceBeamColumn`, Concrete02, Steel02 and a multi-algorithm Newton/Broyden recovery approach. Your thesis already uses Newton/line-search/Krylov/ModifiedNewton and bounded bisection in `runner_and_gui.py`; direct transplantation of forceBeamColumn/infill material models or fork's 5% Rayleigh setup to `E_SFI_MVLEM_3D` walls is **not** warranted. The user-selected Fe500 materials, E-SFI wall/FSAM, 4x4 mesh, 32/76/97 supports and NBC 105:2025 damping/record basis are untouched.

## Evidence stages

All output is beneath each case folder:
`09_SOFTWARE_DIAGNOSTICS/NLTHA_FIRST_STEP/<pair>_<orientation>/`.

- `GRAVITY_FROZEN.json`: after existing `ops.loadConst('-time',0)`, before eigenanalysis.
- `AFTER_EIGEN.json`: after existing eigen solve, before damping mode application.
- `BEFORE_EXCITATION.json`: after both damping and ground-motion creation and the existing transient analysis setup.
- `FIRST_ACCEPTED_STEP.json`: after the first solver-accepted transient substep.
- `FIRST_STEP_TRANSITION_REVIEW.json`: ordered finite/nonfinite stage-onset bracket, never identified as cause.

`capture_transition` reuses the existing bounded `snapshot_selected_state` wall and connected-node coordinate/displacement/velocity/acceleration/element response sampler. It additionally records translational `nodeMass` DOF 1/2/3 for the watched nodes, explicit unsupported status, the model script SHA256, and an exact stage ID. No load is added, no algorithm set, no `analyze` call made, and no material variable or physical parameter changed by the diagnostic. Nonfinite responses are retained as strings in strict JSON; support for an element response channel is not assumed.

The existing `_advance_nonlinear_interval` fail-safe continues to capture `<case>_First_Step_Failure_Evidence.json` on failed solver attempts. For this opt-in diagnostic, such post-failure evidence is retained even if a later fallback accepts a substep. For ordinary production runs, the previous handling and solver sequence remain unchanged. The comparison only reports the earliest observed nonfinite stage; a linearsolver failure could result from untracked matrix properties with fully finite sampled wall states.

## Interpretation / next engineering experiment

Use **fresh** runs with identical model script SHA, gravity load, solver version, record hash, selected `dt`, supports and materials. Reproduce these separate experiments before claiming the cause:

1. No eigenanalysis / zero ground excitation / zero damping.
2. Eigenanalysis / zero ground excitation / zero damping.
3. No eigenanalysis / nonzero excitation / zero damping.
4. Eigenanalysis / nonzero excitation / zero damping.

The standard production runner **always performs eigenanalysis and its regular Rayleigh/Modal damping checks**, so the four-experiment matrix belongs in the existing dedicated research diagnostic harness, **not** as an undocumented production config override. The new capture/checkpoint controls do not implement that matrix and cannot by themselves infer the non-finite source. Use previous `Diagnostic_Evidence/diagnose_nl_first_step.py`, material coupon checks, one-wall-panel patch and output from the current solver as a starting point. A one-panel specimen is not a whole 25-storey building.

## Acceptance and limits

- No change to model builder, element types, FE coordinates, gravity mass, Rayleigh coefficients, damping region, records, dynamic time step, integration scheme or acceptance criteria.
- The displayed source tag must actually exist. `FOCUSED_ELEMENT_ABSENT` is not a passed case.
- Pass only if an accepted-step report and full-history gate pass independently; diagnostic outputs cannot certify model physics.
- Do not treat unsupported `eleResponse` or `nodeMass` channels as zeros.
- Unit regression `tests/test_first_step_transition.py` exercises fake OpenSees read-only behavior. Real native OpenSees/XARA first-step and wall material calibration remain OPEN.

**Source reference licensing:** the inspected fork has an MIT license. This module is independently written and does not paste any fork source code, but engineering inspiration and original attribution remain documented in this source guide and `REVIEW_MAIN/04_NONLINEAR/FORK_RC_ASSESSMENT_20261117/`.

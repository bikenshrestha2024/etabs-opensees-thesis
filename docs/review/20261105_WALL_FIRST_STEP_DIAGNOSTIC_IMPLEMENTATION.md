# V169 first-step X wall: implemented diagnostic evidence (2026-11-05)

**Status: software diagnostic enhancement. Wall first-step cause UNRESOLVED; native OpenSeesPy on user's 25-storey model NOT RUN.**

## Current baseline and PR #1

Historical V168 reported gravity and modal solved, ZERO at 0.005 s passed, Kobe X at 0.005 s failed, with post-failure nonfinite `localForce` on tags `110280`, `112778` tentatively mapped to `AREA:354` and `AREA:482`. The mapping must be confirmed against the **current** model's `OpenSees_Complete_Element_Map_V118.json`. Nonfinite forces after the failed global step do not establish initiating failure.

[PR #1](https://github.com/bikenshrestha2024/opensees-nbc105-research/pull/1) is an old draft and was **NOT** merged as part of this change. Instead, safe source-rebased diagnostic functionality is added to the current main-compatible branches. No physical material law, wall parameters, diaphragm, mass or solver tolerances have been modified to force convergence.

## Safe fixed-model workflow

1. Use one real source ULS/Ultimate or SLS/Service EDB export. The probe generator preserves its existing `limit_state`, `dt_s`, source accelerograms, gravity configuration, materials and solver settings. Historical ULS/Kobe 0.005 s is an *example*, not a forced default for every model.
2. Save the source model, actual X and Y matched record files and `RunConfig.json` locally. Source model data `OpenSees_Complete_Model_Data_V118.json` and both motion files **must exist**. Do not create dummy inputs.
3. Set `analysis_intent="RESEARCH_DIAGNOSTIC"`, `limit_state="ULS"` for actual Ultimate or `"SLS"` for actual Service, and `dt_s=0.005` only when actual modal/record sampling limits support it. Optional `diagnostic_probe_duration_s` can set an integer multiple of dt. Zero damping is a *diagnostic* control, not a project damping design assumption.
4. Generate separate source-hash-bound ZERO/X/Y/XY configs using `python 21_NLTHA_TRIAGE.py --config "D:/Existing_Run/RunConfig.json" --output "D:/NLTHA_Probes"`. The generator **never launches analysis**. It rejects missing model/records, mixed states, production THESIS_NLTHA intent, nonfinite dt, and output collisions. A `00_Probe_Evidence_Manifest.json` stores SHA256 for the current assembled model and both motions; it explicitly says `CONFIGS_ONLY_NO_SOLVER_RUN`.
5. Run each config independently, in a new process, as in `docs/programs/21_NLTHA_TRIAGE.md`. Do not reuse an OpenSees domain after failure.
6. Focused element list defaults to `diagnostic_suspect_tags=[110280,112778]`. Tags may change with the exported model; missing tags are reported in committed snapshots. Inspect the current source map before interpreting them. The `Last_Accepted_Wall_State.json` file includes actual live element-node tags, coordinates, nodal displacement/velocity/acceleration, and supported element response channels. Unsupported queries are reported as `UNSUPPORTED_OR_ERROR`/`UNSUPPORTED_EMPTY`; no artificial zeros are substituted.
7. `First_Step_Failure_Evidence.json` records the post-failure trial response. If suspect tags are configured the failure snapshot queries only those elements (bounded overhead) rather than sweeping every element. The committed and failed-state files must **never** be conflated.
8. Run `python 21_NLTHA_TRIAGE.py --review "D:/NLTHA_Probes"`. The reviewer checks elapsed trial time against the manifest and the reported state, excitation and model hash when available. A short `PROBE_PASSED` is *not* full-record convergence, NBC design approval, or validated wall constitutive physics.

### Minimum four native tests

| Probe | X input | Y input | Primary discriminator |
|---|---|---|---|
| ZERO | 0 | 0 | initialization, effective dynamic tangent/mass/constraints |
| X | source A | 0 | reproduce X-only failure |
| Y | 0 | source B | isolate alternate horizontal direction |
| XY | A | B | test simultaneous shear/axial/torsion coupling |

All use one cloned model, same baseline gravity and solver settings, identical input source bytes. Only the declared diagnostic excitation changes. Damping is zero for all four initial cases as a controlled screen.

### Minimal output package for engineering triage

Save the four folders `ZERO`, `X`, `Y`, `XY` and their model map plus these files (if available):
- `00_Probe_Evidence_Manifest.json` and actual current `RunConfig.json`
- `NLTHA_Input_Quality.json`, `OpenSees_Bidirectional_Input_Commands.json`, gravity reaction and modal screen
- `NLTHA_Wall_Geometry_Preflight.json`, opening/manifests, research constitutive assignments
- `OpenSees_Complete_Element_Map_V118.json` and `OpenSees_Complete_Model_Data_V118.json` **locally only**, never public repository
- `Last_Accepted_Wall_State.json`, `First_Step_Failure_Evidence.json`, `FAILED.json` or `INCOMPLETE.json`, accepted histories and native solver stdout/stderr
- Element tags 110280 and 112778 current node order and coordinates, width/height/thickness, material parameters, axial-load state, supported force/shear/deformation channels and unsupported errors.

## Root-cause discriminating sequence

1. Check source AREA:354/482 current map against mesh, openings, macro-fiber node ordering (bottom i–j horizontal, i–l upward), 0.4 × 1.5 m panel dimensions, E-SFI width/height, thickness and local material integration.
2. Reconcile all source-mapped masses/support DOFs, diaphragm master/polar inertia, gravity frozen state, nonfinite initial tangent, eigenperiods and X/Y inertial forcing; matched `Acc(g)` uses OpenSees Path factor 9.80665 (kN–m–s) with additional scale 1.0.
3. Compare ZERO/X/Y/XY first accepted and attempted snapshots. If X fails, repeat with genuinely refined dt (e.g. 0.0025 s only if compatible with original sampling); do not alter the source acceleration factor.
4. Compare a second matrix/solver configuration while preserving original physical model; then independently isolate panel tests with real confinement, reinforcement, axial load, cyclic response and specific E-SFI constitutive version.
5. Only after first-step reproduction is explained, run full-record and time-step-converged XY and YX simulations, accepting records solely through G00–G10 numerical/material/demand/code gates.

**Limits:** CI uses deterministic fake OpenSees, not the user's private .EDB or full nonlinear E-SFI element. Native solver failure remains unresolved. A converged probe is a numerical event, not validation of wall shear-flexure behavior or thesis acceptance. This change does NOT introduce automatic constitutive parameter edits or attempt to merge the stale, unverified PR #1 into the modern code.

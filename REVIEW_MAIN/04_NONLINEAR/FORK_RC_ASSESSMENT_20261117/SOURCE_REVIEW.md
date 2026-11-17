# External OpenSeesPy fork — NLTHA source review and bounded thesis integration

## Baseline and provenance

- Reference fork: https://github.com/bikenshrestha2024/Framework_for_Seismic_Assessment_of_RC_Buildings (main). Inspected source paths: `Test_Models/Groups/CCP/single/Unidirectional_Multiple_Eq.py`, `Materials.py`, `FiberSectionBuilder.py`, `Gravity_Analysis.py`, `ReadRecord.py` and `Final_Codes/NBC_105_2020/NBC_105_2020_parallel_runs.py`.
- Reference model: RC frame/infill, Concrete02 and Steel02, `forceBeamColumn` fiber sections, gravity preload, ground motion and transient Newmark, Newton/Broyden/ModifiedNewton/line-search/KrylovNewton fallback. Original repository's MIT license applies to original source; no code copied verbatim.
- Authoritative target: `bikenshrestha2024/etabs-opensees-thesis` `components/nonlinear_time_history/runner_and_gui.py`, `failure_evidence.py`, `first_step_transition.py`, `components/shared/gravity_transient_handoff.py`, `one_storey_wall_probe.py`.
- Existing proof: historical model once passed gravity and a zero-motion transient step, while an excitation case after eigenanalysis failed at the first step with UmfPack error, and another run recorded nonfinite localForce for wall element 110280. These are **different diagnostic observations**; do not claim eigenanalysis causes a wall material singularity.

## Reuse decisions

| Method | Fork scope | Existing thesis implementation | Decision |
| --- | --- | --- | --- |
| Gravity preload and freeze | Fiber RC frames | Gravity builder and `loadConst` handoff, source/load audit | Retain target implementation; add read-only gravity-frozen checkpoint |
| Cyclic frame materials | Concrete02 / Steel02 and fiber beam-column | ConcreteCM/SteelMPF/FSAM E-SFI wall, and various frame material options | Use only as independent coupon comparisons; do not replace Fe500, wall, FSAM, damping parameters |
| Solver recovery | Newton, ModifiedNewton, Broyden, NewtonLineSearch, KrylovNewton | Newton, NewtonLineSearch, KrylovNewton, ModifiedNewton, bounded bisection, fail-safe nonfinite guards | Keep current sequence and strict success gates; Broyden is *not* enabled without a native benchmark |
| Time history workflow | Record conversion, motion + time integration | Unit audited PEER/SeismoMatch, XY/YX, NBC 105:2025, source SHA | Keep target; do not import original developer paths or overwrite matched record scaling |
| First-step diagnostic | Recovery on frame structures | Source mapped wall and failed step evidence | **Integrate new opt-in mass/wall checkpoint protocol** |
| Output reaction/energy | Fiber section curvature and energy | Wall/base shear, FVD/BRB histories, accepted-substep records | Never replace unknown/missing responses with zeros; use only source-matched valid recorders |

## First-step failure triage decision matrix

1. **GRAVITY_FROZEN**: verify existing gravity equilibrium elsewhere; record focused wall/connected-node finite states and translational mass. Absence of element tag = unmapped, not passed.
2. **AFTER_EIGEN**: record the same channels and source SHA after unchanged modal solve. Difference indicates the observation occurs across these stages, not that eigen caused it.
3. **BEFORE_EXCITATION**: record after existing damping, UniformExcitation and transient setup. If first nonfinite appears here, separate each operation with controlled native experiments.
4. **FIRST_ACCEPTED_STEP**: only emit after existing `analyze` success and accepted row numeric gate; record first accepted full solver state. Capture first failed attempt separately via original `failure_evidence.py` (post-failure data may be contaminated).
5. **UNRESOLVED**: if responses stay finite but UMFPACK fails, investigate singular/ill-conditioned effective tangent, constraints and mass nodes with native solver diagnostics. No material parameter edits are justified solely by failure code.
6. **CANONICAL FOUR-WAY A/B**: no eigen/zero motion; eigen/zero motion; no eigen/motion; eigen/motion, damping held zero and source/hash/solver identical, in dedicated *research* harness, not by bypassing production guard.

## Required acceptance gates

**Software G0:** Source compile/import, automated tests and output structural JSON. **G1:** identical model script SHA, first-step tag mapping and evidence pre/post. **G2:** replay native XARA/OpenSees with exact version, support and mass, gravity and dynamic initial state. **G3:** isolated first-storey E-SFI wall component with verified ConcreteCM/SteelMPF and convergence, including first nonfinite material element response. **G4:** original ETABS vs OpenSees gravity base support/force equivalence for 32/76/97; **G5:** NBC 105:2025 matched record scales and modal damping/frequency bounds, no FVD damping double count; **G6:** complete accepted XY and YX records for all M0–M6 without truncation; independent expert review.

**Current status:** Software diagnostic implementation under review; the native four-way test, physical cause, 32/76/97 equivalence, wall coupon benchmark and NLTHA completion remain UNVERIFIED.

## Output ownership

```text
<case output root>/
  09_SOFTWARE_DIAGNOSTICS/
    NLTHA_FIRST_STEP/
      <pair_id>_<orientation>/
        GRAVITY_FROZEN.json
        AFTER_EIGEN.json
        BEFORE_EXCITATION.json
        FIRST_ACCEPTED_STEP.json
        FIRST_STEP_TRANSITION_REVIEW.json
```

Existing post-failure `<case>_First_Step_Failure_Evidence.json` remains available. No source EDB, original model data, private record or calibrated parameter is uploaded into the public repository.

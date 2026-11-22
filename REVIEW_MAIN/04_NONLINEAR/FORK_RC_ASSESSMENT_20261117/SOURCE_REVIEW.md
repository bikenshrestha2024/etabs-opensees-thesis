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


## 2026-11-22 — upstream original-repository inspection and production NLTHA follow-up

**Original source inspected:** [nirajkyadav/Framework_for_Seismic_Assessment_of_RC_Buildings](https://github.com/nirajkyadav/Framework_for_Seismic_Assessment_of_RC_Buildings) `main`, NOT only the user's historical fork. Specific checked Git blobs: `Test_Models/Groups/CCP/single/Unidirectional_Multiple_Eq.py` `1201cee5959464fe97d5290851a455ecfab921e7`, `Gravity_Analysis.py` `75950dcdb55828c938dee62d17ce13b1bb9c6a59`, `ReadRecord.py` `e5f9953ce467d60d159046dd05f25444d3ae5fe4`, `Final_Codes/NBC_105_2020/NBC_105_2020_parallel_runs.py` `0a0c14b9bfcade47a20b0fce18e4210cfd00b517`. Upstream MIT license ©2025 Niraj Kumar Yadav; license and attribution remain in upstream, no upstream source functions copied verbatim.

**Observed original methods:** gravity `analyze(1)` followed by `loadConst('-time', 0.0)`; Rayleigh/eigen/Path/UniformExcitation; Newmark average-acceleration; Newton, ModifiedNewton, Broyden, NewtonLineSearch and KrylovNewton attempts; floor/section recording and multiprocessing over building/motion cases. The reference code uses fixed fallback `.002` or `.001` transient increments in several branches, independent of the current motion digitization interval, and gravity calls do not consistently gate the return code. **Neither behavior is safe to transfer to the current thesis.** Reference NBC 105:2020 models and its low-rise RC frame/infill constitutive and geometric assumptions are **not** a substitute for NBC 105:2025 25-storey asymmetric two-12m-wall damped-outtrigger models, actual ConcreteCM/SteelMPF/FSAM calibration or the user's 32-physical-support / 44-wall-mesh transfer constraints.

**Production correction adopted, without physical parameter changes:**
- `components/nonlinear_time_history/full_record_gate.py::verify_committed_transient_increment` requires the solver's actual `getTime()` difference to match the requested adaptive substep and remain finite. `rc==0` by itself is insufficient; no accepted response or good-`dt` statistic is recorded first.
- The existing `_advance_nonlinear_interval` is the **single shared solver owner** for both `runner_and_gui.py` and `building_exploratory.py`. Recovery retains Newton/LineSearch/Krylov/ModifiedNewton and bounded half steps. If a **failed** attempt changes the solver clock, it is not silently reused for another algorithm; preserved existing failure report remains available. No blanket tolerance relaxation, Broyden substitution, stiffness edits or reset of the original source occurs.
- Each successful increment records `first_accepted_step` (algorithm, requested/actual dt, depth, clock) and accepted-step counts in existing solver diagnostics **only after** `on_accept` finite/recorder callback completes.
- Opt-in `first_step_transition.py::require_accepted_focused_step` rejects a first solver-accepted wall diagnostic with nonfinite watched responses or an absent watched tag. The watched snapshot and comparative stage report are written **before** the history CSV row; nonfinite response cannot become an accepted row.
- Source-specific test coverage: `tests/test_nltha_step_clock_contract_20261122.py`, with existing `tests/test_first_step_transition.py`, `tests/verify_v133.py`, and `tests/verify_failure_evidence.py`.

**Independent evidence needed before scientific acceptance:** fresh Windows OpenSees/XARA runs at an identical EDB/model/data hash and origin wall tag; ZERO/X/Y/XY/YX same source/case, gravity and signed P-Delta state, the wall coupon/patch, response channel finite evidence and reproducible full-duration 25-storey runs for M0–M6. The 2026-11-22 patch tightens software evidence; it does **not** demonstrate resolution of historical 110280/112778 first-step nonfinite X-wall or the 768.045 kN maximum gravity joint reaction discrepancy.

**Research attribution:** upstream README lists supervisor **Dr. Kshitiz C. Shrestha**; user's own thesis documentation specifies **Assoc. Prof. Dr. Kshitij Charan Shrestha**. Preserve the exact spelling in each original source. No claim of independent identity verification is made from differing transliterations.

**Cross-agent provenance:** project `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` and accessible repository history were checked. Connected ChatGPT project context was consulted for previously recorded constraints; raw private Claude/Codex conversations are not available here and must never be invented or attributed to this change. Actual editor: OpenAI ChatGPT GPT-6 via GitHub connector, 2026-11-22; no private source files published.

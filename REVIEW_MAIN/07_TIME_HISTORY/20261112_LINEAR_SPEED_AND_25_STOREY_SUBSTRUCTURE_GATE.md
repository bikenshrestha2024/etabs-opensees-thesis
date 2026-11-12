# 2026-11-12 — Linear transient performance and nonlinear 25-storey substructure gate

Status: **IMPLEMENTED AS OPT-IN EXPERIMENT / NATIVE BENCHMARK PENDING**.
Applies to the active repository, not archived V156 runtime. No claim of accelerated production validation or nonlinear convergence.

## Evidence from the supplied 2026-11-12 Kobe XY log

- 11,097 nodes, 14,262 elements, 37,776 equations; 20 eigenmodes in approximately 25.5 s.
- Gravity/preload: 20 steps / 94.206 s; total gravity reaction error about 5.83e-12%.
- 4,094 XY and 4,094 YX requested steps, dt approximately 0.01 s.
- At 3,033/4,094 XY steps: elapsed 5,810 s; observed requested rate approximately 0.52 step/s.
- Slow linear transient is a recorded *performance blocker*, not a solver failure or a converged full-record result.
- Log excerpt terminates before the 4,094-step XY completion; do not treat it as completed.
- Source: user-supplied local output `Pasted text(20261112-115124).txt`. **Never commit the user's model/input files or sensitive source path.**

## Changes on main

`components/linear_time_history/runner_and_gui.py` has two mutually visible GUI controls:
1. **Experimental speed: reuse constant linear matrix factorization (opt-in)**, config key `linear_factor_once_experimental` (default false).
2. **I independently verified the assembled tangent remains constant** (`elastic_constant_tangent_verified`, default false).

Opt-in runs `ops.algorithm("Linear", "-factorOnce")`; default remains `ops.algorithm("Linear")`.
The trial rejects non-boolean config, changing/short final-step duration, or missing explicit tangent verification. New profiler keys:
`native_transient_solve` stage, `solver_diagnostics.native_solve_seconds`,
`solver_diagnostics.recorder_seconds`, `solver_diagnostics.constant_dt` and
`solver_diagnostics.linear_factor_once_experimental`.

**Important caveat:** An `algorithm("Linear")` call does not turn an actual nonlinear material/element into an elastic system. Verify **each** frame, wall, link, brace, damper and P-Delta/tangent dependency. If the effective stiffness or damping formulation varies within steps, never enable this factorization-reuse mode. OpenSees modal damping specifically requires iteration and is *not* interchangeable with `Linear -factorOnce`.

## Deterministic benchmark — required before using new solver in research

1. Freeze/checksum model .py, model-data JSON, 2 ground-motion files, config, interpreter, OpenSeesPy build and baseline git commit; no changes to engineering inputs between runs.
2. Select one short **identical** Kobe XY record trial with original mode (both checkboxes off); record CPU, RAM, solver timings and native trace.
3. Repeat with two checkboxes on only after inspecting elastic constitutive/constant effective-matrix assumptions. Preserve separate output directories; do not overwrite original.
4. Compare **every sampled time**, component and floor for Ux, Uy, Rz, acceleration, X/Y drift and foundation base reactions; compare roof extrema and record-length counters. Use both maximum absolute discrepancy and normalized discrepancy, including near-zero handling. Agree tolerances in advance, not after looking at results. Flag sign errors and missed samples.
5. Run YX, a second record with a different dt, ULS/SLS states, then full records, each with separate status. Run linear-vs-ETABS independent check. Check for slow drift, differing Rayleigh damping and gravity baseline.
6. If any differences exceed tolerance or a native solver fails, disable optimization and retain baseline. No extrapolation of short-test speed to complete suite without measured sustained full run.
7. Record speedup = baseline native solve seconds / experimental native solve seconds, and total wall-clock speedup separately. Do not report estimated speedup as measured.

Candidate further optimizations, **not implemented**:
- Profile `append_base_shear`, including costly `reactions()`, separately from node sampling, without reducing scientific recorder content.
- Reuse project-validated modal matrices or numerical initialization only where all case inputs and dynamic state are equivalent; never reuse a nonlinear damaged domain.
- Benchmark sparse solver choices (UmfPack, MUMPS if available) and process-level threading on the actual Windows build; do not assume that more CPU threads are faster.
- Keep GUI on Tk's main thread, solver in child process; queue/batch log events, add bounded log window + full persistent log, stop/kill child tree, cancellation evidence, no high-frequency cross-thread widget mutation.
- Avoid simultaneous solver jobs until memory pressure and result isolation have been benchmarked.
- Revisit time integration only within actual NBC and input digitization bounds; do not increase dt solely for speed.

## Verification hierarchy — no confused scope labels

| Tier | Scope | Valid inference |
| --- | --- | --- |
| N0 | one 4-node wall quadrilateral | element orientation, material call, basic stiffness and local solver smoke |
| N1 | wall piers and coupling beams around an opening | wall layout, connectivity, static and cyclic force transfer |
| N2 | a **full-height** 25-storey selected frame/wall bay and its connecting substructure | axial-load/gravity sequence, height-dependent nonlinear response, P-Delta and propagation of panel anomalies |
| N3 | 25-storey full asymmetric 3D frame + core + outriggers | overall mass, higher modes, bidirectional XY/YX, diaphragm torsion, boundary force paths and global seismic demands |
| N4 | M0–M6 variants, all required motions/levels with sensitivity | controlled research comparison only after N3 full-record validation |

An N2 bay is **not** a one-storey model, and N0 is **not** a whole first floor.
A cropped N2 bay cannot give building-level response unless equivalent interface effects are derived and verified. Removing neighboring bays or entire upper storeys without transferring their gravity, seismic inertia, stiffness and interface actions invalidates direct building-level comparison. Retain all relevant 25 elevations and true ETABS geometry; identify cut boundary nodes, apply parent-derived interface stiffness/forces or explicit boundary approximations with error study, compare gravity and linear modal/static demands to parent. An isolated wall line may miss inherent torsion and off-axis connection effects.

**Critical blocker:** The source repository's current accepted gate notes ZERO first step passed, Kobe X failed at t=0.005 s, with nonfinite wall data *after* failure. Tags 110280 and 112778 are localization clues, not proven root cause; do not reset or replace material parameters merely to obtain convergence. Each ZERO/X/Y/XY probe must start in a fresh OpenSees domain, preserving source hashes and the exact last accepted step.

## Thesis sources to keep with the audit

- OpenSees `Linear -factorOnce`: https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/algorithm/LinearAlgorithm.html
- OpenSees modal damping warning: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/damping/modalDamping.html
- Kolozvari, Orakcal & Wallace 2015 PEER 2015/12: https://peer.berkeley.edu/publications/2015-12
- Kolozvari et al. / 3D E-SFI-MVLEM documentation: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html
- Kolozvari et al., *New OpenSees models...*, 2018: https://www.sciencedirect.com/science/article/pii/S0045794917303693
- López et al., *Validation of an efficient shear-flexure interaction model*, 2022: https://doi.org/10.1016/j.engstruct.2021.113590
- Waezi, Dhakal & Kolozvari, *A Refined SFI-MVLEM...*, 2026 PREPRINT (not implemented or independently validated here): https://ssrn.com/abstract=6880782
- NBC 105:2025 official source: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf

No citation-count claim is made: current citation ranking, visits and downloads are not reliably available from the sources above.

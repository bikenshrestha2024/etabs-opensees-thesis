# NLTHA thesis methodology and reproducible research evidence

**Study:** *Time-history analysis of damped outrigger systems in a high-rise building with an asymmetric plan*. **Primary emphasis:** nonlinear, three-dimensional response-history investigation of existing OpenSees models M0–M6. **Research/evidence status (2026-11-22):** methodology drafted; one-case direct solver launcher added; the native 25-storey model is **NOT** claimed to have passed nonlinear wall convergence, ETABS structural equivalence or any completed 224-run matrix.

This structure follows research-paper reporting practice: model idealization → constitutive laws and component verification → ground-motion selection → nonlinear analysis protocol → demand metrics → uncertainty/sensitivity → controlled comparison. It does **not** import laboratory specimen parameters into the project as if calibrated.

## Chapter 3.1 — Structural system and controlled research variables

Model an asymmetric, approximately 25-storey, 95 m RC building, core/shear wall with openings, frame and selected steel outriggers/belt/cap systems. Preserve actual source model geometry. X walls: two 12 m lines with actual openings, not historic four isolated 6 m source panels. Preserve 32 physical support joints and 44 analytical shear-wall mesh transfer points; never ground-fix all 76 mapped points. Document a case-bound ETABS model fingerprint, mass ledger, support set, section properties, shell discretization and local axes.

Define exactly seven independent model states (no reused directories under different names): M0 no outriggers; M1 conventional; M2 damped conventional; M3 conventional + belt; M4 damped + belt; M5 conventional + belt + cap; M6 damped + belt + cap. Verify which physical members/devices and boundary conditions differ. Maintain unchanged material assignments, mass, seismic loading, gravity procedure and model geometry where a comparison requires controlled attribution.

**Required evidence:** model and section export SHA, independent support/mass/reaction reconciliation, floor/element counts, source geometry drawings, source wall openings, device inventory and actual seven models.

## Chapter 3.2 — Constitutive idealization and independent benchmarks

**RC frame:** nonlinear concrete and steel behavior, axial-bending interaction, cyclic unloading/reloading, confinement, reinforcement from actual source drawings, hinge/fiber integration and geometric transformation. ConcreteCM/Concrete02 and SteelMPF/Steel02 are candidate models, not calibration by their presence. Document each beam/column section's longitudinal/restraining steel, tension/compression limits, cyclic parameters and units.

**RC core:** E-SFI-MVLEM-3D shear–flexure interaction with four correctly ordered corners, horizontal local i→j fiber width, vertical i→l height, real thickness and opening/coupling-beam mesh. Calibrate source boundary/web steel and FSAM stress–strain laws. Compare isolated panel, axial-cyclic and wall with openings against published measured specimens before interpreting global structural response. Do not infer the cause of a 0.005 s X-only failed solver from a post-failure NaN force alone.

**Steel outriggers, braces, FVD and optional BRB:** establish actual element orientation, end-joint compatibility, connection compliance, yielding/buckling assumptions, force–velocity loops and stable cyclic dissipated energy from source devices. For ideal nonlinear fluid viscous damper,
```text
F_d(t) = C |v_rel(t)|^alpha sign(v_rel(t))
Energy_dissipated = integral[F_d d(delta_rel)] with an explicit consistent sign
```
In kN–m–s, `C` must use dimensions kN/(m/s)^alpha. A literature example written in mm/s cannot be entered unchanged in a m/s OpenSees material. No chosen damper exponent/coefficient is qualified without independently checking the tested law, frequency and displacement range.

**Literature basis:** R01 PEER 2015/12 (Kolozvari et al., reversed-cyclic wall shear–flexure), R02 Kolozvari, Lopez & Massone (2023), DOI 10.1016/j.engstruct.2023.116700 (3D E-SFI-MVLEM), R03 wall axial force sensitivity, R05/R06 supplementary damping methods; original source details in `docs/00_RESEARCH_REFERENCES.md`. Supplement: NIST GCR 17-917-46v1 (2017), DOI 10.6028/NIST.GCR.17-917-46v1.

## Chapter 3.3 — Gravity, modal basis and geometric nonlinearity

Reconcile source physical supports and six-DOF foundation force cuts, section forces and ETABS/OpenSees reaction distribution **before claiming equivalent global behavior**. Keep the comparative `GRAVITY_1.0D_1.0L` case separate from seismic weight per NBC 105:2025 §5.2/Table 5-1. Qualify the adopted project's IS 16700:2023 §7.2(d) signed initial P-Delta cases independently; static preloads must not double-count the full dynamic earthquake action. Gravity must equilibrate and remain frozen appropriately for each independent dynamic domain.

Extract current T1-X, T1-Y, Tn90-X, Tn90-Y, modal effective mass and torsional modes for *each actual variant and state*. Damping reference modes and nonlinear Rayleigh formulation require source-backed audit; avoid adding unintended damping into viscous links or using an obsolete ETABS model period. A diagonalized mass or distributed mass assumption is a studied physical choice, not an output formatting setting.

## Chapter 3.4 — Ground-motion selection and site-hazard linkage

Use the eight registered, separately reviewed Soil-C matched earthquake **pairs**: Gorkha, Landers, Northridge, Kobe, Kocaeli, Chi-Chi, Hector Mine and Loma Prieta. Research near-field/far-field classification must be verified from original epicentral/fault distances, mechanism, site information and pulse/directivity descriptors before drawing distance-class conclusions.

Source files `Acc(g)`, exact component A/B SHA, dt, duration and SeismoMatch original scaling/session logs are immutable evidence. Extra OpenSees spectral amplitude scale is **1.0** after matching; timeSeries Path source acceleration conversion is **9.81 m/s² per g**. Do not infer original SeismoMatch factors from final PGA. Use NBC 105:2025 §9.3.2 period range and selected paired-component scale; `dt=0.005` s is provisional until checked against the actual Tn90/first-mode bounds. Preserve Gorkha 120 s versus 322.94 s processing chronology and the Loma Prieta one-sample discrepancy for a named engineering reviewer; no hidden rematching, trimming or padding.

**Per pair:** simultaneous A→X/B→Y (XY) and A→Y/B→X (YX), each from a fresh independent gravity-preloaded domain. The seven configurations × eight pairs × two states × two orientations produces 224 planned native histories. The generated manifest alone is NOT solution evidence.

## Chapter 3.5 — Nonlinear dynamic solver protocol

Governing relative-motion equation for an ideal base-excited system:
```text
M u_ddot(t) + C u_dot(t) + f_int(u, history, t)
    = - M r a_g(t)   [appropriate multidirectional influence vectors]
```
Track physical units, geometric stiffness, constitutive history, gravity state and all excitation components. For each record, instantiate a fresh native OpenSees model; solve the verified gravity/P-Delta state, check initial eigen/damping and wall panel finite response, then execute an integration method with documented initial dt, iteration test, tolerance, line search/Newton fallback, and bounded time-step subdivision. Record **actual accepted solver time**, not just a returned zero status, before storing numerical response. A failed step that changed the solver clock is contaminated evidence and must not be retried as though still at the old state. Retain first failure/traceback and a complete diagnostic chronology.

Before full runs, perform independent ZERO, X, Y, XY probes to identify the old X-wall early-step failure, and benchmark the same wall under axial force and cyclic shear. Re-run after source-grounded correction; do not relax a material model merely to make one analysis converge.

**Implemented owners:** `components/nonlinear_time_history/building_exploratory.py` (existing native builder and recorder), `runner_and_gui.py` (shared nonlinear interval), `first_step_transition.py`, `full_record_gate.py`, `wall_diagnostics.py`, `wall_topology.py`; Stage 38 adds *only subprocess orchestration*, not solver physics.

## Chapter 3.6 — Nonlinear response quantities and recorder requirements

| Demand metric | Source channel / computation | Physical check |
|---|---|---|
| Floor/roof displacement and residual | Gravity-referenced relative displacement, m | Max XY/YX transient and terminal residual; not maximum of artificially combined times |
| Interstorey drift | Relative floor edge displacement / actual storey height | Both building axes, re-entrant edges, torsion and peak histories |
| Peak floor acceleration | Relative nodal acceleration + corresponding input ground acceleration | Report m/s²; differentiate relative/absolute |
| Base shear and overturning | Common foundation force cut about fixed origin, signed kN/kNm | Native 32-support and wall-mesh load path; no mixing inconsistent cuts |
| RCC beams/columns | Fiber strain/curvature and force-deformation hysteresis | Actual bar buckling/confinement and qualified limit states |
| RC wall | E-SFI shear deformation, boundary strain, axial force, curvature | Panel ordering, local axes, open-core and source confinement |
| FVD | Force, relative velocity/stroke and energy | Signed dissipative work, connection alignment, no artificial Rayleigh double counting |
| BRB / steel braces | Plastic axial strain/force, deformation and cumulative demand | Element law, physical connections and tested fatigue limits |

A postprocessor must never treat zero or absent response channels as a passed engineering demand. Only committed finite response states may enter peak calculation. Define IO/LS/CP acceptance thresholds from an explicitly reviewed source and *actual* component detailing; do not apply generic hinge rotations indiscriminately to shell walls or FVD elements.

## Chapter 3.7 — Numerical convergence and sensitivity

For the same input/model, halve dt and compare peak roof UX/UY, MIDR both directions, wall boundary force/strain and device response/energy. Check systematic mass, support, mesh, stiffness, and damping sensitivity separately (one physical variable at a time). Record solver iterations, fallbacks, accepted vs rejected increments, wall tags, energy-balance trends and full-duration completion. A clock-only or CSV-only check is NOT independent confirmation of materially accurate response.

## Chapter 3.8 — Statistical analysis and comparative hypotheses

For each **physically qualified, complete, matched** XY/YX pair, compute specimen-level response histories first, then the NBC 105:2025 §9.3.3 aggregation applicable to the selected set and limit state. Do not assume an exact seven-record averaging rule where the published clause is ambiguous. Preserve orientation effects, per-record dispersion and independent source/input identity.

Model contrasts: M1 vs M0 (outrigger), M2 vs M1 (viscous device), M3 vs M1 (belt), M4 vs M3 (damper with belt), M5 vs M3 (cap), M6 vs M5 (damper with belt and cap). Report both improvements and deterioration in drift, torsion, floor accelerations, device force/energy, residual drift and element damage. A failure/nonconvergence cannot be omitted from the denominator without an explicit failure policy and objective assessment.

## Chapter 3.9 — Reproducible results and thesis figures

Required per run: `Executed_RunConfig.json` (exact adopted parameters), SHA256 identities, native console/transient log, `Execution_Status.json`, both orientation `Case_Summary.json` files, accepted-history completion gates, accepted numerical time histories, mass/damping summaries, device/energy ledgers, response plots and named reviewer checks. Preserve original private source files outside public Git.

Suggested chapter figures: 3D geometry and core openings; seven system configurations; floor/story-mass and eigenmodes; hazard target vs pair spectra; tested wall cyclic loop; diagnostic ZERO/X/Y/XY wall chronology; selected per-record roof histories; story drift/torsion envelopes; FVD hysteresis and cumulative dissipated energy; full M0–M6 normalized response comparison; convergence mesh/dt plots.

## Chapter 3.10 — Software execution, evidence status and limits

Use Stage 35 to audit matched records; Stage 36 to create source-bound matrix; Stage 21 for the X-wall first-step probes; Stage 38 (`38_EXECUTE_SOIL_C_NLTHA.py --config ... --run`) to launch **one actual existing model case** (full XY/YX) in a fresh process; Stage 27 only when comparable completed source-qualified histories exist.

Explicit evidence tiers (independent): `SOURCE_CHECKED`, `NUMERICALLY_CONVERGED`, `ETABS_OPENSEES_MATCHED`, `EXPERIMENT_VALIDATED`, `CODE_ACCEPTED`. Stage 38's `FULL_DURATION_SOFTWARE_SCREEN_ONLY` means a two-orientation file/solver screen, **not any of these acceptance flags** by itself. Unresolved items remain: native X-only wall at first 0.005 s, 32-support pointwise gravity mismatch, source wall material/rebar and section calibration, proven source preprocessing/damping/periods, full M0–M6 solution.

## Source bibliography for this chapter

1. Government of Nepal, DUDBC, *NBC 105:2025 Seismic Design of Buildings in Nepal*, particularly §§5.2 and 9.3.1–9.3.3: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf
2. NIST, *Guidelines for Nonlinear Structural Analysis for Design of Buildings, Part I – General* (2017), NIST GCR 17-917-46v1, DOI 10.6028/NIST.GCR.17-917-46v1: https://nvlpubs.nist.gov/nistpubs/gcr/2017/NIST.GCR.17-917-46v1.pdf
3. Kolozvari, Orakcal & Wallace, *Shear-Flexure Interaction Modeling for RC Structural Walls and Columns under Reversed Cyclic Loading*, PEER 2015/12: https://peer.berkeley.edu/publications/2015-12
4. Kolozvari, Lopez & Massone, *Efficient Three-Dimensional Shear-Flexure Interaction Model for RC Walls*, Engineering Structures (2023), DOI 10.1016/j.engstruct.2023.116700.
5. OpenSees manual, E-SFI-MVLEM-3D: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html
6. Project R01–R13 scientific source register: [../00_RESEARCH_REFERENCES.md](../00_RESEARCH_REFERENCES.md).

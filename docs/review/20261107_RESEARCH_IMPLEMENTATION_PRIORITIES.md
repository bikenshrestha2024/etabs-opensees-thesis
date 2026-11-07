# 2026-11-07 — Research review → corrective engineering backlog

**Status:** implemented source-safety improvements plus evidence plan. **No project-specific native model validation, NBC design approval, or M0–M6 optimum is claimed.** Review the current code and actual case evidence before changing physics assumptions.

## Corrected in this commit series

| Item | Previous risk | Correction | Verification |
|---|---|---|---|
| ETABS-linked Excel provenance | The adapter emitted a field called `C` containing `Cd_uls` or `Cd_service`, conflating elastic seismic coefficient with reduced design coefficients | Separate `C_elastic`, `Cd_ultimate`, `Cd_service`, `Cd_selected`; report input wall cells F/G/H/J for every contribution | `tests/verify_esm_dual_module.py`; **static** check, not native ETABS |
| Cross-stage evidence | Readiness was distributed among many specialist tools, making it easy to quote a run without identifying missing upstream evidence | Read-only manifest SHA256 identity dashboard; 11 ordered stages, JSON/Excel-compatible CSV/PNG, conservative non-approval semantics | `tests/verify_thesis_evidence_dashboard.py` |
| Workflow navigation | Source-level gates were not visible as one thesis audit | Extend canonical sequence to include optional `37_THESIS_EVIDENCE_DASHBOARD.py`; preserve all native component-specific gates | Documentation and CI static tests |

## P0: do these BEFORE any production NLTHA or optimum claim

1. **First-step X-wall failure (previously reported element 110280).** Run actual ZERO, X, Y and XY native probes in fresh domains; capture converged gravity state, coordinate/node mapping, first nonfinite channel, material/fiber response, solver iteration logs and last accepted time. A wall tag recording nonfinite `localForce` is a symptom until earliest causal evidence is available. Do not downgrade wall to elastic to hide it. Existing anchors: `components/nonlinear_time_history/runner_and_gui.py`, `components/nonlinear_time_history/building_exploratory.py`, `21_NLTHA_TRIAGE.py`.
2. **Actual core topology and openings.** Generate an ETABS↔OpenSees floor-by-floor overlay including wall pier centerlines, flanges/webs, coupling beams, opening polygons, thickness, node ordering/local axes, boundary zones and reinforcement; compare joint geometry by ID and physical connectivity. The original Excel shear-wall `Aw` calculation is authoritative for the user's ESM research comparison, but it must NOT silently replace the nonlinear physical core model. NBC 105:2025 §5.1 and §9.3 should be verified directly against the issued PDF.
3. **Calibrate core & frame materials.** For RC sections: actual bar coordinates, confined core/cover fibers, transverse reinforcement and cyclic degradation; for E-SFI-MVLEM-3D: panel/fiber orientation, local shear-flexure interaction and axial sensitivity. Require native specimen overlays for pier, pier–coupling–pier and corner U-/C-shaped core subassemblages. Never treat a synthetic numerical smoke test as experimental validation. OpenSees reference: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html
4. **Mass/gravity/damping equivalence.** Compare ETABS vs OpenSees per-storey dead/live seismic mass, gravity reactions and axial loads, supported period/modal shapes/torsional mass and explicit Rayleigh allocation. Keep ULS and SLS independent and reject source mismatches. Static source hashes do not prove mechanical equivalence.

## P1: once P0 physical validation passes

5. **Matched orthogonal records and site verification.** Verify original input pair hashes, SeismoMatch scaling log, target code spectrum, `Tn90` and `T1`, scale-factor interval, actual record dt and complete duration before 8-pair XY/YX production. Keep Gorkha duration and Loma Prieta one-sample inconsistencies explicitly review-blocking pending evidence. Do not re-scale already-matched `Acc(g)` in OpenSees except for unit conversion.
6. **Native FVD & BRB benchmarks.** FVD force-velocity and force-displacement loops, Maxwell stiffness, stroke and energy; BRB compression/tension stable cyclic strength, cumulative plastic strain/ductility, residual drift and low-cycle fatigue. Verify device-axis sign conventions by benchmark; recorder work is signed and can be negative until conventions are qualified. OpenSees FVD: https://opensees.berkeley.edu/wiki/index.php/ViscousDamper_Material
7. **Numerical and research comparison.** After stable native full-duration runs, check time-step refinement, damping sensitivity and energy balance. Compare M0–M6 with identical geometry/source mass/record sets except for precisely recorded variant changes. Never aggregate shortened, failed or nonfinite histories. Preserve separate ULS/SLS, XY/YX and record-level metrics.

## P2: figures and thesis knowledge base

The intended Excel analysis batch should hold `RUN_METADATA`, `CODE_CLAUSES`, `ETABS_GEOMETRY`, `OPENSEES_GEOMETRY`, `MODEL_DIFFERENCE`, `MASS_GRAVITY`, `MODAL`, `GROUND_MOTIONS`, `RESPONSE_SPECTRA`, `DRIFT_TORSION`, `CORE_FRAME`, `FVD_BRB`, `ENERGY`, `CONVERGENCE`, `NBC_REVIEW`, `M0_M6_COMPARE` and `THESIS_SUMMARY`. **Proposed schema, not a claim all sheets have been implemented.** Use SI/kN/m/s consistently, original source hash and variant/record/orientation/state in each table. Plot acceleration time history, 5%-damped spectra, modal shapes, story shears, maximum *corner* interstorey drifts, roof twist, core stress/curvature, damper and BRB hysteresis, dissipated energy and solver-step acceptance. Maintain separate physically measured and calculated response quantities.

### Explicit design principles

- A program line deserves a **requirement → equation/assumption → function → tests → evidence** mapping. Not every source line has a codal clause; numerical implementation choices have solver documentation and algorithm tests.
- Use NBC 105:2025 as primary seismic reference; treat IS/ACI/ASCE/AISC as **supplementary** unless adopted by the Nepal project authority. Preserve exact PDF edition and page/section in each code-ledger row and never invent codal limits.
- Distinguish `STATIC_SOURCE_CHECKED`, `NUMERICAL_SMOKE_TEST`, `NATIVE_MODEL_VERIFIED`, `EXPERIMENTALLY_VALIDATED`, `NBC_DESIGN_REVIEWED` without automatically promoting results.

### Selected research foundations (bibliographic links, not parameters imported into this building)

- Kolozvari et al., *Efficient three-dimensional shear-flexure interaction model for reinforced concrete walls* (2023): https://www.sciencedirect.com/science/article/pii/S014102962301115X
- Malik & Kolay, *Optimal parameters for tall buildings with a single viscously damped outrigger considering earthquake and wind loads* (2023): https://doi.org/10.1002/tal.2003
- Xue et al., *Application of amplified damped outrigger in seismic design of high-rise buildings* (2024): https://doi.org/10.1002/tal.2077
- *Shaking table test of a buckling-restrained brace outrigger system* (2024): https://www.sciencedirect.com/science/article/abs/pii/S0143974X23006429
- Hojaji et al., *A new ground-motion scaling and record selection procedure for asymmetric-plan buildings using the 2DOF-modal pushover method* (2026): https://doi.org/10.1007/s11803-026-2370-8

**Applicability caveat:** experimental specimen geometry and parameters in those papers are not interchangeable with a 25-storey Nepal project. Cite individual equations, specimens and calibration limits only after confirming the paper text. The existing research framework cannot presently declare NBC compliance for its full nonlinear response-history models.

# 00 — Independent engineering code review: asymmetric RCC high-rise damped outrigger

**Review stage:** source structure and selected active modules only; **not a completed line-by-line review of all 2,700+ repository entries**. This is an initial, reproducible engineering baseline and explicit backlog for progressive full review. Source survey undertaken 2026-11-04. Historical archives, backups and older V1xx snapshots remain retained but are **not authoritative implementation**.

## Project and evidence basis

- User's MSc earthquake engineering thesis, Thapathali Campus, on a roughly 25-storey asymmetrically planned RCC dual frame/core structure with opening-bearing RCC walls, steel outrigger braces, optional belt/cap systems, FVDs and BRBs. Variant comparison M0 to M6.
- Governing Nepal seismic standard: [NBC 105:2025, second revision, DUDBC](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf), especially §§4.1, 5.2, 5.3, 5.5 and 9.3.
- Primary site/record case **Soil C**; user workbook Z=0.35, I=1.0, R_mu=3.5, Omega_u=1.4, Omega_s=1.2; 0.05–6.0 s, 5%-damped SeismoMatch matching; 8 paired events and 16 already-matched Acc(g) files. Soil D research is secondary and not interchangeable with the 16 Soil-C-matched sources.
- **Do not** infer original X/Y component scale factors from final/initial PGA ratios. Already matched recordings use additional spectrum multiplier 1.0; with kN-m-s OpenSees model `Path -factor 9.80665` converts source g to m/s².
- Current unsolved defect: a first-step X-direction wall/localForce failure around element 110280 at approximately t=0.005s in a previous nonlinear analysis. The tag/localForce is an *observed failure symptom*, not independently established causality.
- This review does not supply actual ETABS drawing reinforcement, test-grade FSAM parameters, source concrete confinement, geometric openings or calibrated FVD/BRB device histories; these remain externally evidenced steps.

## Scope and line-review method

The repository contains numerous repeated root launchers with identical numeric prefixes and historical whole-runtime copies. A literal mass rename would break import paths, user automation and source hashes. Instead:

1. Treat [the 01–20 primary work-order list](../../00_READ_FIRST_RUN_ORDER.md) and [01–37 research stages](../programs/00_PROGRAM_INDEX.md) as **canonical navigation**, not an instruction to execute unverified stages in sequence.
2. Static inspect active `components/`, `tools/` and `tests/` with the [AST inventory tool](../../tools/audit_active_repository.py). Its JSON records every active Python file SHA256, lines, top-level functions, classes, imports, syntax errors and missing individual source guide.
3. Maintain a per-file audit register: specific lines/function, physical hypothesis, units, source citation, input provenance, test coverage, unresolved native results. **AST inventory is not a semantic line-by-line or solver validation**.
4. Audit each active module progressively with tests and before/after native evidence; keep untouched legacy aliases and archives until import graph and CLI regression coverage prove a safe migration.

### Reviewed source-level inventory (evidence-backed initial pass)

| File | Approx. lines | Examined purpose | Engineering risk and action |
|---|---:|---|---|
| `components/model/assembly.py` | 829 | ETABS mesh, material/source/loads, `build_complete_model` | **P0:** actual source mass, partitions, wall openings, constraint connectivity, source reinforcement, unique tags and geometric transformations must be tested with a real ETABS export. A large function is an auditability issue, not itself a failure |
| `components/model/load_and_diaphragm_audit.py` | 103 | shell loading, diaphragm and kinematics audit | **P0:** reconcile with current ETABS slab/self-weight, gravity reactions, no duplicated mass; independent native model required |
| `components/model/reinforcement_mapping.py` | 85 | evidence-gated RC fiber register | **P0:** simplified bars-per-side templates cannot replace actual irregular bar positions, stirrups, boundary region and confinement from source drawings |
| `components/sections/wall_adapters.py` | 40 | simplified wall adapter and E-SFI panel call | **P0:** current source explicitly limits no-boundary adapter; if core has boundary elements, do not silently map paper section materials |
| `components/nonlinear_time_history/wall_topology.py` | 92 | axis-aligned rectangular openings check | **P0:** this is not validation of nonrectangular re-entrant core, web flange junction, rotating local axes, coupling-beam/transfer load path |
| `components/nonlinear_time_history/building_exploratory.py` | 826 | gravity-preloaded model, modal/damping and transient histories | **P0:** verify actual wall material behavior, first X step, accepted-step forces, Rayleigh inclusion, damping mode choice and full XY/YX paired histories; no shortened diagnostic can be counted as completed NLTHA |
| `components/nonlinear_time_history/soil_c_physics_preflight.py` | ~185 | source target/damping/period and original scale-review gates | **P0 fixed:** reject unrecognized analysis intent, incorrect workbook hash, wrong target identity; this is configuration safety, not nonlinear calibration |
| `components/nonlinear_time_history/device_recording.py` | 91 | FVD and BRB accepted-step demands | **P1:** confirm device local axes and signed forces/strokes and energy against isolated native specimen benchmark; acceptance cannot derive from recorder existence |
| `components/nonlinear_time_history/full_record_gate.py` | 79 | complete accepted history tests | **P1:** detect unsuccessful time steps, do not count truncated runs; cross-case dt refinement and energy balance also required |
| `components/nonlinear_time_history/variant_comparison.py` | 184 | M0–M6 source-hashed comparisons | **P1:** distinct ULS and SLS data, comparison invariants (mass, source geometry, damping), XY/YX and all 8 events; note NBC 9.3.3 exact-7 ambiguity but 8-event suite avoids it |
| `components/nonlinear_time_history/soil_c_nltha_suite.py` | ~300 | 8-pair hash verification and fit-period source preflight | **P0:** Gorkha 322.94s duration and Loma Prieta one-sample tail must have approved policy; source hashes do not prove site selection or 0.33–3 initial scale factors |
| `components/nonlinear_time_history/soil_c_run_matrix.py` | ~170 | 7 variants × 8 events × 2 states | **P1:** 112 configurations × XY/YX = 224 intended analyses, **not 224 completed**; preserve independent fresh-domain output IDs and failure logs |

## Structural engineering and OpenSees cross-check matrix

| Priority | Physical model requirement / source | OpenSees implementation or audit target | Required evidence |
|---|---|---|---|
| P0 | 3D torsion and center-of-mass offsets, NBC §9.3.1 | `ops.model('basic','-ndm',3,'-ndf',6)`; diaphragm constraints and P-Delta transformations | source ETABS geometry, COM, torsional modes, story inertias, drift at eccentric corners |
| P0 | RCC frame concentrated/distributed plasticity | RC fiber section `patch`, `layer`, calibrated `ConcreteCM`/`Steel02`/`SteelMPF`, displacement- or force-based beam/columns | source bar coordinates/area, cross-section discretization, confinement tie layout and cyclic material tests |
| P0 | RCC core with openings | `E_SFI_MVLEM_3D` requires **four counterclockwise nodes**, m fibers, each thickness/width/FSAM nDMaterial tag | actual ETABS web/flange geometry, wall openings and pier/spandrel connection, axial-load reversal and native elemental wall benchmark |
| P0 | Wall cyclic shear-flexure | FSAM panel, appropriate concrete/steel laws, confinement and mesh/objectivity tests | PEER 2015/12 and Kolozvari et al. 2023 specimen-to-model comparison; avoid paper rebar transfer to user's building |
| P0 | OpenSees first-step numerical instability | output gravity pre-state, local element/section forces at last **accepted** step, zero-ground and isolated X/Y probes | exact failing state/time/element and its nodes, section/material response; stable solver selection and timestep refinement |
| P1 | Steel outrigger/BRB | validated local brace orientation, section material, connection axial/rotational behavior, `Steel02`/appropriate cyclic BRB fatigue criteria | connection/BRB geometry, brace yielding and compressive instability, explicit material/element tag map |
| P1 | Fluid viscous dampers | `ViscousDamper(K,Cd,alpha)` + proper link element; `F=C|v|^alpha sign(v)` only in appropriate model approximation | verified SI kN-m-s and fractional dimensions, real cyclic force/stroke/velocity, nonlinear energy sign, no extra Rayleigh device damping |
| P1 | 8 × bidirectional motion pairs | `timeSeries('Path',...,'-factor',9.80665)`, simultaneous `UniformExcitation` DOF 1/2 in XY and YX | exact paired source SHA256, 0.05–6s modal band review, no second matching, full duration, correct units |
| P1 | Rayleigh/dynamic energy | `rayleigh(alphaM,betaK,betaKInit,betaKcomm)` uses modes documented by actual eigenperiods; device/wall damping selection | inspect damping basis under yielding, numerical energy input/dissipation and possible device double counting |
| P1 | Output and performance | relative vs absolute floor acceleration, signed FVD/BRB power/energy, roof displacement/twist, interstory drift, member plastic rotations/strains | NBC drift limits §5.5.3 and §9.3.3; material-specific acceptance and independent engineering review |

**OpenSees sources**: [E-SFI-MVLEM-3D element and recorders](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html), [UniformExcitation relative output and parameters](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html), [Rayleigh command](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/damping/rayleigh.html), [ViscousDamper](https://openseespydoc.readthedocs.io/en/stable/src/ViscousDamper.html).
The E-SFI 3D element requires 3D model **-ndm 3, -ndf 6** and records `globalForce`, `Curvature`, `ShearDef`, `RCPanel fibTag Response`. Verify actually installed OpenSees binary supports the exact element; documentation alone cannot prove compilation.

## Evidence maturity: precise language

- `STATIC_SOURCE_CHECKED`: source files parsed, supported headers/fields/links checked; no claim of running OpenSees.
- `NUMERICAL_SMOKE_TEST`: a finite native element step, not physical calibration.
- `NATIVE_MODEL_VERIFIED`: fresh-domain representative gravity/modal/transient analyses passed with recorded solver outputs and input hashes.
- `EXPERIMENTALLY_VALIDATED`: material/device/wall response reproduced independently against real specimen curves and declared criteria.
- `NBC_DESIGN_REVIEWED`: complete code/clause checks, correct site/record/limit state and qualified engineering review. None of the lower stages implies a higher one.

## Immediate P0 blockers before production NLTHA

1. Reproduce and locate **earliest causal** X-direction core-wall failure; do not mistake a post-failure nonfinite force (earlier element tag 110280) for its source.
2. Load actual ETABS **reinforcement and confinement schedule**, coupling beams, wall pier openings, core junctions and exact coordinate/orientation tags.
3. Native isolated E-SFI 3D wall benchmark in the intended OpenSeesPy build; verify shear-flexure interaction, cyclic pinching, axial-load sensitivity, native recorders.
4. Verify gravity, source mass, P-Delta and modal 90%-mass participation and Rayleigh modes.
5. Review Gorkha source duration, Loma Prieta tail, original SeismoMatch 0.33–3 and paired scale logs; current 0.05–6s period band with actual model periods.
6. Then native FVD/BRB calibration/energy recorder and complete 8 × 2 orientations × M0–M6 evidence; preserve failure output rather than auto-marking passes.

**No full-building native NLTHA was run in this source-review stage.** `tools/audit_active_repository.py` produces reproducible *static* source inventory and is intended to guide a staged real line-by-line examination, not disguise an automated scan as one.

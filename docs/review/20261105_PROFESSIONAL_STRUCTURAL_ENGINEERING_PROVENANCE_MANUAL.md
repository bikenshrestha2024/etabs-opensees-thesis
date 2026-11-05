# Engineering verification and parameter-provenance manual — asymmetric damped-outrigger high-rise

**Audit date:** 2026-11-05. **Primary code:** Government of Nepal, NBC 105:2025 (second revision). **Scope:** research workflow for the ETABS-to-OpenSeesPy asymmetric RC frame/core system (M0–M6), including steel outrigger/belt/cap bracing, FVDs and research BRBs. **Status:** incomplete engineering review; not a certified design, experimentally calibrated full building, or completed NLTHA.

> **Evidence taxonomy used here:** `CODE` = actual published code rule; `SOURCE` = verified project export/test/drawing; `LITERATURE` = published specimen or methodology but **not** the project's value; `ASSUMPTION` = named research scenario; `COMPUTED` = reproducible output conditional on inputs; `PENDING` = missing verification. A program default or a passing test is never automatically `SOURCE`.

## 0. Source-of-truth and working-code protection

1. NBC 105:2025 official [DUDBC code catalog](https://dudbc.gov.np/pages/24231978/) and [Government of Nepal PDF](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf) govern code checks. Consult printed clauses and amendments; do **not** combine 2020 and 2025 formulas.
2. The **current** `main` commit and `AGENTS.md` govern executable repository semantics. `docs/review/ledger` snapshots are frozen by Git revision. The earlier project repository [`etabs-to-opensees-outrigger`](https://github.com/bikenshrestha2024/etabs-to-opensees-outrigger) has a modelling basis, not the authoritative active code. The [`SFI-MVLEM-3D` fork](https://github.com/bikenshrestha2024/SFI-MVLEM-3D) is documentation of the **original** element; it is not an independently verified build of `E_SFI_MVLEM_3D`.
3. ETABS `.EDB`, model export JSON, shell assignments, seismic weights, original/matched waveform files and source reinforcement schedules are **read-only**. Track sha256 and state `ULS/SLS` separately. No private exports are committed.
4. Preserve public launchers/compatibility imports, root launch aliases, GUI names, native binaries and historical evidence. A source-code correction starts with a reproducible failing test, ends with a passing test and a source/verification ledger, and never redefines wall physics to make a solver run pass.
5. Never infer acceptance from gravity reaction balance, modal participating mass alone, a nonlinear return code, truncated record or a plotted response. Required gates are source consistency, mass/load/geometry equivalence, component-level material validation, native full-duration bidirectional analysis, convergence and engineering acceptance.

## 1. System, hazards and geometrical controls

The fixed building is a nominal 25-storey re-entrant/asymmetric plan RC dual system with RC shear core openings, perimeter columns, RC beams and optional outrigger/belt/roof cap configurations. These are **study descriptions**, not automatically reconciled exports. All candidate cases must have identical base geometry, mesh-quality basis, gravity load and seismic mass (except documented added system mass), diaphragm assumptions, core detailing and material cards. Treat roof cap as roof-fixed while moving the candidate outrigger elevation.

For every real model record: analysis case ID; EDB SHA256; source export SHA256; axes and transform; story-base and top coordinates; diaphragm master tags; story slab extent; first-storey web and flange pier lengths; wall openings per story; beam/column section and bar geometry; outrigger elevations; belt/cap/connection geometry; mass and gravity source; FVD/BRB instance identifiers and local-axis vector.

**H (m)**: NBC §5.1.2 figure 5-1 seismic base to roof; review basement inclusion/exclusion criteria, not blindly `max(z)-min(z)` of every node (which can include excavated basements or rooftop artifacts). **b (m)**: horizontal plan dimension perpendicular to considered earthquake axis at the evaluated level, not automatically the full-model global bounding box at every story. Eccentricity = ±0.05b under NBC §5.6; separate actual inherent eccentricity and accidental eccentricity.

**Floor-mass and stiffness correspondence:** model geometric mass center and translational/torsional inertia per diaphragm, rigid/semi-rigid selection, compatibility with beam axial/vertical motion and ETABS constraints. Check plan re-entrant corner joint tags, wall/beam coupling, shared core corner nodes and support boundary conditions. *Do not* tie two ends of an FVD to an identical rigid diaphragm DOF and then assume useful relative motion.

## 2. Equivalent-static method: every value and why it is used

Implementation: `components/inputs/project_workbooks.py`, `components/equivalent_static/calculation_and_gui.py`, `components/equivalent_static/code_basis.py`, `components/modal/analysis.py`. Launch `12_EQUIVALENT_STATIC.py`, not an old archived V156 runner.

| Parameter / unit | Where obtained | Governing use and verification |
|---|---|---|
| `H` (m) | Actual ETABS seismic base and roof, NBC Fig. 5-1; not arbitrary maximum node elevation | §5.1.2 empirical `T`. Confirm basement/roof logic and story-height export |
| `Awi` (m²) | Reviewed first-storey structural wall i net effective cross-section in the considered axis | §5.1.2; thickness × actual effective segment length, excluding openings as justified, not summed gross mesh shell area |
| `Lwi` (m) | Independently grouped structural wall length in first storey aligned with X or Y | `Lwi/H≤0.9` in effective-wall-index term. Do not merge noncontinuous piers across openings; check mesh/segment grouping |
| `Aw-X, Aw-Y` (m²) | `Σ Awi[0.2 + (min(Lwi/H,0.9))²]` from independently reviewed wall geometry | §5.1.2. Workbook `SCALING SUMMARY!B14/B15` is a **reference**, not proof; store discrepancies against current geometry |
| `T_emp,X/Y` (s) | `0.075H^.75/sqrt(Aw,X/Y)` for concrete shear-wall type, only if §5.1.2 classification is appropriate | Must keep each plan direction separate; no imported specimen T |
| `T_emp,amplified` (s) | `1.25×T_emp` | §5.1.3, **not** 1.25× ETABS modal T |
| `T_Rayleigh,X/Y` (s) | Model-specific §5.1.1 `2π sqrt[Σ(Wi di²)/(g Σ(Fi di))]` calculated from actual stiffness, mass and force/displacement | ULS/SLS models may differ; hash-match model, story weight, limit state and Aw. A modal eigenperiod or workbook C14/C15 is not equivalent evidence |
| `T_adopted,X/Y` (s) | `min(T_Rayleigh,1.25T_emp)` for matching case | §5.1. Record source/method and both arguments; reject nonfinite values and cross-state substitution |
| `Wi` (kN) | Actual self-weight/dead + storage-live 0.60 + other-live 0.30, roof-live 0 per NBC Table 5-1 | Export story-by-story source loads. Check partitions, finish, slab/wall gravity and double counting; NBC §5.2 |
| `Z` (dimensionless) | Official NBC site municipality/Annex C selection + project location | Do not infer from workbook filename; verify municipal zoning and selected hazard |
| `I` (dimensionless) | Importance class and occupancy under NBC Table 4-4 | Needs user/project occupancy evidence |
| `soil_type` | Site Vs30 report or applicable geotechnical evidence; code Tables 4-1/4-2 | Soil C primary **research input** is not automatically an approved site-class determination; for H>40m check §4.1.3.1 measured Vs30 requirement |
| `Rμ, Ωu, Ωs` | NBC Table 5-2 for the **actual qualified** structural system | RC dual system study candidates 3.5,1.4,1.2; verify classification, connections and ductile design before acceptance |
| `Ch(T)` | ESM spectrum NBC Table 4-1 and Fig. 4-1(a) using adopted T and soil | Do not confuse ESM spectrum with MRSM or nonlinear matching target |
| `Cd,U/S` | Implementation in `code_basis.py` based on NBC §§4.1,4.2,6.1 and system factors | Record all Z,I, Ch, Rμ, Ω and limit-state operations separately; cross-check workbook and hand calculation |
| `V` (kN) | `Cd × ΣWi` | Reconcile modeled lateral forces against story force sum and source ETABS base shear under identical settings |
| `k` (dimensionless) | NBC §6.3 function of adopted T | Recalculate separately for X/Y and limit state; no hard-coded X k applied to Y |
| `Fi` (kN) | `V Wi hi^k / Σ(Wj hj^k)` | Verify `Σ Fi=V`, overturning moment and tagged diaphragm application |
| ULS ESM eligibility | NBC §3.2.1 | A tall asymmetric building is generally **not** eligible for ULS ESM by the height/period/regularity gates. Report `DIAGNOSTIC REFERENCE`, not design-compliant |
| ESM drift | NBC §5.5.3 | ULS 0.025, SLS 0.006; use matching drift amplification/deflection rule; torsion and perimeter edge drift need actual node response |

**Excel source map:** `NBC Calculator!B9/B10/B11/B15/E10` supplies named soil, Z, I, empirical factor and system **references**; `SCALING SUMMARY!B4` is the target EDB identity; `B14/B15` wall effective indices; `C14/C15` workbook adopted reference periods. Always retain file path, sheet, cell, hash, author/date and reconciliation status. No workbook formula is evaluated by `openpyxl(data_only=True)`; cached cells must be inspected for missing/stale results. The EDB identity and first-story projection checks are software screens, not physical certification of pier selection.

**Bug policy:** Wrong EDB reference or z-varying wall footprint prevents automatic wall-geometry acceptance. The active ESM PR adds source/floor identity matching and z-slice geometry checks. The user may supply independently verified net effective areas after documenting a nonrectangular-core pier interpretation. Do not silently replace physical project properties with the geometric heuristic.

## 3. Analysis hierarchy and modelling choices

1. **Reconcile source:** ETABS floor elevations, wall openings, area/beam/column assignments and local transformations. Check sums of nodal loads/reactions and seismic masses; no shell/beam duplicate self-weight. Verify bare linear reference model against ETABS at matching stiffness/load cases first.
2. **Gravity:** source `DL` and sustained live load factors; self-weight path; convergence, P-Delta and foundation assumptions. `ops.loadConst('-time',0)` after accepted gravity equilibrium. Do not interpret that step as verified nonlinear materials.
3. **Modal:** use source-matched mass, assign actual ULS/SLS cracked elastic stiffness and damping assumptions; report X/Y dominant translations, Rz torsion, modal mass accumulation, T1 and **Tn90**. Tn90 is not arbitrarily the 20th eigenperiod.
4. **ESM / MRSM / linear history:** diagnostic and independent source cross-checks. Use correct NBC ESM eligibility, MRSM participation/scaling clauses and structural irregularity rules.
5. **Components:** cyclic RC beam and column, 3D E-SFI core with openings, ordinary steel connection/brace, Maxwell FVD, BRB—only after each baseline and parameter uncertainty check.
6. **Nonlinear:** one fresh OpenSees domain per hazard, pair, XY/YX orientation and outrigger configuration; retain last accepted states, first failure, full trace, early stop and source hashes. ZERO/X/Y/XY diagnostic probes may be exploratory only; no truncated case enters the thesis comparison.
7. **Acceptance:** same analysis model basis, motion records, hazard assumptions and output extraction definition across variants. Calculate envelope of signed edge/interstory drift, roof response, torsion, floor accelerations, residual displacements, wall/member demands, device force/stroke/energy and intact gravity stability. Rank only complete accepted cases.

## 4. Material and device register — units, provenance and limitations

All structural actions use **kN–m–s**, stress `kN/m²` (1 MPa = 1000 kN/m²). FVD `Cd` units are `kN·(s/m)^α` for `F=Cd·|v|^α`, and spring `K` is kN/m. Do not confuse `v` across Maxwell dashpot with full element deformation velocity.

| Model | OpenSees command / field | Research value source | Mandatory before project transfer |
|---|---|---|---|
| `Concrete01` | `uniaxialMaterial('Concrete01',tag,fpc,epsc0,fpcu,epsU)` | M30→24 MPa cylinder conversion and strains in modelling basis are **assumptions**, compression stresses negative | Actual cylinder/compression and confinement, unconfined cover versus tie core, tension omission limits |
| `Concrete02` | `Concrete02` includes `lambda,ft,Ets` | Nominal initial tension/softening; element characteristic length impacts Ets | Cyclic stress/strain including tension, fracture energy/mesh sensitivity, no unverified steel-bond transfer |
| `ConcreteCM` | `ConcreteCM` envelope/tension/crushing/unloading | PEER wall specimen or nominal research card; not building concrete | Published specimen parameters separated from source M30; panel test under imposed cyclic reversals |
| `Steel02` | `Fy,E0,b,R0,cR1,cR2,a1..a4` | Fe500 and transition coefficients are assumed unless coupon measured | Rebar stress/strain, grade, low-cycle failure and connection slip |
| `SteelMPF` | `fyp,fyn,E0,bp,bn,R0,cR1,cR2`, optional hardening | Nominal symmetric profile is research-only | Test tension/compression asymmetry and buckling where relevant |
| `FSAM / E-SFI-MVLEM-3D` | `ops.model('basic','-ndm',3,'-ndf',6)`; `element('E_SFI_MVLEM_3D',tag,i,j,k,l,m,'-thick',...,'-width',...,'-mat',...)` | Kolozvari et al. 2023 formulation; 4 nodes ordered CCW, width i→j horizontal, i→l story vertical | Actual wall regions, openings and junctions, reinforcement ratios, finite axial load, convergence, strain/energy output, mesh-objectivity |
| `FVD` | `uniaxialMaterial('ViscousDamper',tag,K,Cd,alpha, ...)`, attach via reviewed link/local axis | The V115/V149 example parameters describe a **separate specimen**, not a specified device | Test K/Cd/alpha in kN–m–s, device quantity, source design velocity/force/stroke/temp, series spring and energy |
| `BRB` | Axial element and tested cyclic uniaxial law / `Steel02` or calibrated brace model | Literature WEN or hypothetical core values are demonstration-only | Actual yielding steel, A, length, joint details, axial cyclic strength, buckling, cumulative low-cycle fatigue |
| Conventional outrigger | Steel brace section, end fixity/release, possible belt/cap | Existing nominal SHS and connection assumed until ETABS steel specs verified | Outrigger force transfer into wall core and perimeter columns, panel-zone/connection, erection stages and axial shortening |

**Material-source test:** model input card must record material formulation, tags, units, signs, DOI/author, specimen/test protocol, actual source versus assumed values, calibration metric (peak strength, unloading stiffness, pinching, cumulative energy, strain peaks), validation plotting input hash and geometric transfer limitations. A benchmark calibration on a paper specimen does not validate an entire irregular core. For E-SFI documented optional defaults include CoR 0.4, ThickMod 0.63, Poisson 0.25 and Density 0; these are **formulation defaults**, not automatic design selections, and mass must not be duplicated.

**Core torsion and differential axial shortening:** outriggers transfer large axial couple to edge columns; inspect connection rotation, axial deformation/stiffness, temporary construction condition, sequential gravity column/core shortening, and global torsional response. The 2017 CTBUH *Outrigger Design for High-Rise Buildings* (2nd edition) addresses differential shortening, construction effects and hybrid/damped outrigger design; it is guidance, not a Nepal code mandate.

## 5. Ground motions and NBC §9.3 verification

Research basis: **eight** already SeismoMatch-matched Soil C pairs, each with original A/B SHA256 and full synchronized time vector; six near-field and two far-field as documented in `AGENTS.md`. Both **simultaneous XY and YX** orientations required; do not use one motion then sequentially the other. No arbitrary third vertical component is required merely because the *structural model* is 3D; separately evaluate actual code vertical-action triggers.

- NBC §9.3.1: three-dimensional nonlinear model; gravity, P-Delta, inherent torsion, hysteretic behaviour, foundation/basement requirements. Concrete01 alone does not establish degradation/pinching in nonlinear RC.
- NBC §9.3.2.1: hazard-appropriate pairs and event properties; number of pairs and independence must be checked, not inferred from file count.
- NBC §9.3.2.2: matching target is `C(T)/Ωu`; fit over relevant period range `Tn90 ... sqrt(Rμ)T1`, scale factors 0.33–3, and lower of independently fitted X/Y factors applied equally to both components. The *already-matched* `Acc(g)` files have **extra spectral multiplier 1.0**; applying `Path -factor 9.80665` converts g→m/s² and is not a second spectral fit. SeismoMatch original scale logs still needed before stating 9.3.2.2 compliance.
- NBC §9.3.2.3: paired components along principal X/Y axes then swapped YX.
- NBC §9.3.2.4: `dt_analysis <= min(dt_digitized, T1/100, Tn90, 0.01 s)` in each plan axis; check minimum of both. Source waveform duration and any one-sample mismatch must not be silently padded/truncated.
- NBC §9.3.3: the printed text describes *less than seven* versus *more than seven* record aggregation, leaving exactly seven ambiguous; the eight-record research set avoids that wording ambiguity. Only full accepted histories enter mean comparisons. §9.3.3.1's cross-reference to §5.6 is inconsistent with drift limits in §5.5.3; record this instead of silently changing the citation.

Store: case/state/variant/pair/orientation; EDB/model/material/record hashes; `dt_record,dt_analysis,t_end,n_expected,n_accepted`; initial scale proof; relative **and absolute** floor accelerations; response direction/sign; last accepted step; wall local force and source-area lookup; device force/stroke/velocity/energy; PASS/FAIL/NOT RUN/REQUIRES EVIDENCE. No nonfinite post-failure `localForce` value is proof that a particular wall material initiated the problem.

## 6. Outrigger optimization: what can and cannot be called optimal

Compare M0 no outrigger; M1 conventional; M2 damped conventional; M3 conventional+belt; M4 damped+belt; M5 conventional+belt+roof cap; M6 damped+belt+roof cap. BRB is a separately declared design variable (not invisibly substituted for SHS steel). Candidate elevations are **research hypotheses**; they must be physically constructible and compared at equal geometry, mass, hazard and consistent device resource budget. Minimum roof translation is not necessarily optimum for torsion, edge drift, accelerations, energy or serviceability. Use a Pareto front or constrained objective with explicit acceptance rules; do not borrow a universal h/H optimum from a 60-storey idealized literature model.

Recommended outputs: storey/edge drift envelopes by X/Y and torsion, roof rotation/translation, residuals, floor accelerations, base shear, member actions/plastic hinges and strain, core/spandrel/coupling-beam damage, outrigger and perimeter-column axial demand, FVD peak force/stroke/speed and cumulative signed work, BRB ductility/strain and cumulative demand, solver failures, computation time, capacity and comparison method. Include record-to-record variability and uncertainty in material/damper sizes. The PEER 2017-06 tall-buildings guidance is informative for performance-based evaluation, but a non-Nepal alternative method needs appropriate design-review authority.

## 7. Cross-repository comparison and identified open risks

| Repository (reviewed head 2026-11-05) | Reusable | Not established |
|---|---|---|
| `opensees-nbc105-research`: `82080acc44c9b66cc2d2ec6b26e1f283d1dcd831` starting `main` | Current numbered GUI/component architecture, native/solver-free validation gates, ESM provenance, 8-pair manifest and conservative status handling | Full semantic review of all code; actual ETABS equilibrium/mass match, wall cyclic calibration and first-step wall failure resolution |
| `etabs-to-opensees-outrigger`: `d0ac53c0c28ac309ec4d25e838dafcf70fcd06b4` | `02_MODELLING_BASIS.md` material modelling hypotheses, separate RC wall/frame/FVD and BRB assumptions | Hypothetical M30/Fe500 cards do not prove the actual ETABS reinforcement, wall boundary properties or damper sizing |
| `SFI-MVLEM-3D`: `57c2ff41fafb98357e4a9bac983c71eda7b3dbff` | Published original 24-DOF 4-node wall conceptual/recorder documentation | Cannot claim this README demonstrates the exact E-SFI formulation, local installed OpenSeesPy availability, core with openings and thesis convergence |

## 8. Source references — exact use and restriction

- **G01 (governing):** Government of Nepal / DUDBC, *NBC 105:2025, Seismic Design of Buildings in Nepal*, second revision; §§3.2.1,3.4,3.6,4.1–4.2,5.1–5.6,6–7,9.3, Annexes A/B/C. [Official DUDBC catalog](https://dudbc.gov.np/pages/24231978/). Always record which clause is implemented and which remains unverified.
- **G02 (design guidance):** CTBUH (2017), *Outrigger Design for High-Rise Buildings*, 2nd ed., ISBN 978-1-864707-28-1. [Publisher entry](https://shop.cvu.org/products/outrigger-design-for-high-rise-buildings-second-edition). Guide on construction sequence, shortening, conventional/hybrid/damped configurations; not a numerical optimal height.
- **G03 (performance guidance):** PEER Report 2017/06, *Guidelines for Performance-Based Seismic Design of Tall Buildings*, v2.03, [PEER](https://peer.berkeley.edu/publications/2017-06). Supplemental assessment guidance, not an automatic local-code replacement.
- **G04 (damped outriggers):** Malik and Kolay (2023), *Optimal parameters for tall buildings with a single viscously damped outrigger considering earthquake and wind loads*, DOI [10.1002/tal.2003](https://doi.org/10.1002/tal.2003). Parametric mechanism guidance only.
- **G05 (wall element):** Kolozvari, López and Massone (2023), *Efficient Three-dimensional Shear-flexure Interaction Model for Reinforced Concrete Walls*, `Engineering Structures` 294,116700, DOI [10.1016/j.engstruct.2023.116700](https://doi.org/10.1016/j.engstruct.2023.116700), [OpenSees command](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html).
- **G06 (original wall element):** [OpenSees SFI-MVLEM-3D](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/SFI_MVLEM_3D.html). Original versus enhanced formulation must be distinguished.
- **G07 (damping and devices):** [OpenSees Rayleigh](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/damping/rayleigh.html), [UniformExcitation](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html), [ViscousDamper](https://openseespydoc.readthedocs.io/en/latest/src/ViscousDamper.html).
- **G08 (nonlinear concrete/steel):** [Concrete02](https://opensees.github.io/OpenSeesDocumentation/user/manual/material/uniaxialMaterials/Concrete02.html), [Steel02](https://opensees.github.io/OpenSeesDocumentation/user/manual/material/uniaxialMaterials/Steel02.html). These command definitions do not supply the thesis building's experimental constitutive parameters.

## 9. Required independent verification before a release

**Software:** full history clone; syntax/import checks; GUI headless smoke tests; new and historical synthetic regression; package and source guide integrity; no silent exceptions or stale runtime; traceback and cancel. **Engineering:** ETABS base elevation and H; first-story wall-grouping diagram and Aw reconciliation; all mass/self-weight source transfer; source RC reinforcement and cyclic properties; matched modal X/Y and 90%-mass mode index; FVD/BRB component validation and unit conversion; wall-opening 3D mesh, shared corners, axial loads and converged last-accepted-state evidence; NBC ground-motion original scaling and waveform duration; complete eight-pair XY/YX ULS/SLS M0–M6 response and fair optimum criteria.

At the date of this document: **CI PASS is software-only**. No real building NLTHA or calibration is certified. Corrections should go through small reviewed PRs and should not overwrite historical project analyses.

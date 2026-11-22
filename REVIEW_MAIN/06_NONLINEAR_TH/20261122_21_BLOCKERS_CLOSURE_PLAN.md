# NLTHA — 21 unresolved readiness requirements: complete evidence and closure register

**Review date:** 2026-11-22. **Application:** 25-storey asymmetric, two 12 m X-wall opening model, M0–M6. **Scope:** evidence triage of the latest private ULS Modal, MRSM and available-input audit; no unpublished project data are copied into this public code repository. **Result:** **21 checks reported unresolved; ZERO production engineering approvals asserted.**

> **Hard boundary:** Engineering items can be completed only by independently reviewed source documents, project-specific material/reinforcement calibration, same-model native ETABS/OpenSees evidence, actual nonlinear member/wall tests, and a human reviewer. An elastic solver PASS, upload ZIP or literature example does NOT authorize `approved_for_nltha=True`, `nonlinear_parameters_reviewed=True`, or any `checks[key]=True`. The research PEER 2015/12 copy is a diagnostic material draft, not a transfer of experimental reinforcement to the user's actual structure.

## 1. Case-specific observations and provenance

- Original uploaded modal/MRSM results used `PHYSICAL_32`, `SOURCE_DISTRIBUTED`, 25 storeys, gross-shell ULS stiffness. The 32 fixed physical foundations were selected; transfer through 44 other source-mapped shear-wall mesh points remains `NOT_VERIFIED`. 76 mapped IDs never means 76 physical supports.
- The uploaded OpenSees ULS gravity preload (20 increments) returned matching *global* applied/reaction vertical load. That is a configured seismic-preload load state with reduced applicable live-load fractions, **not** an independent 100%-DL + 100%-LL native ETABS gravity comparison, and does not certify nodal reactions or P-Delta initiation.
- The 40-mode modal mass coverage screen exceeded 90% in both horizontal directions; its result explicitly reports `MASS_COVERAGE_PASS_NATIVE_MODEL_UNVERIFIED`, `LEGACY_GROSS_SHELL`, and externally entered Rayleigh periods instead of independently computed NBC §5.1.1 work-sum periods. No nonlinear initial-state eigen analysis was submitted.
- ULS MRSM reports six numerical X/Y center ±5% eccentricity cases, but both supplied review manifests state `independent_ETABS_response_verified=false`, with comparison-sheet **templates** rather than native ETABS response output.
- The available-input JSON explicitly reports `nonlinear_materials_file=""`, `nonlinear_wall_fsam_tags={}`, `nonlinear_parameters_reviewed=false`. A source section name such as `RC_COLUMN_*_FIBER` is not an actual approved project rebar schedule.
- Input discovery found older, **different EDB** 6 m X-wall calculation sheets. Their old `Aw-X`/period values must not be imported as the adopted model's reviewed 12 m X-wall source. No current exact source EDB+workbook SHA was independently made available.
- Screenshots show an isolated `PEER_2015_12_SINGLE_SOURCE` research material/FSAM draft and a **published teaching portal** cyclic plot. Both are separate from project-identified frame/wall tests; neither closes production calibration.

## 2. Exactly 21 blockers, source evidence and acceptance action

`CANDIDATE_ONLY` = a source or numeric result is located but its engineering predicate is NOT accepted. `MISSING` = necessary independent artifact not supplied. `HUMAN` = reviewer attestation required. `BINDING` = the selected manifest pointer is a generic template rather than the current model-bound draft. None of these statuses is `PASS`.

| # | Exact readiness blocker / check | What is actually available | Required artifact and independent acceptance | Status |
| --- | --- | --- | --- | --- |
| 01 | `not_approved` | Explicitly false | Reviewer signs after **all** the following checks, source SHA binding, material calibration and case review; no program may set true as a workaround | HUMAN |
| 02 | `etabs_topology_and_story_mapping_reviewed` | Model data and story-master candidate files | Compare current EDB tag/XYZ/storey list, source node identity, M0–M6 variant, 2×12 m X-wall openings, 3×6 m Y-wall geometry, section dimensions and actual frame/area connectivity; preserve source ID SHA | CANDIDATE_ONLY |
| 03 | `wall_opening_and_coupling_beam_mesh_reviewed` | Area section inventory only | Reconstruct every opening, shared shell-edge node, coupling beam and local axis from same EDB; run wall/floor mesh sensitivity and stiffness/load-transfer benchmarks | MISSING |
| 04 | `wall_nonlinear_materials_and_reinforcement_cited_calibrated` | Unapproved literature research draft | Project web/boundary longitudinal/transverse rebar, concrete grades, confinement, FSAM material properties, wall cyclic and axial-flexural-shear benchmark fit, units and citation/reviewer signoff | MISSING |
| 05 | `frame_concrete_and_rebar_materials_reviewed` | Dimensions and symbolic fiber-section names only | Source-drawn longitudinal bars, ties, spacing, cover/core and joint reinforcement per floor/section; calibrated cyclic concrete/steel rules, P–M or moment–curvature response, member hinge benchmark | MISSING |
| 06 | `slab_and_diaphragm_idealization_compatible` | Slab stiffness and diaphragm configuration candidates | Compare ETABS rigid/semirigid diaphragm and shell mesh loads/displacements, correct 0.25Ig (strength) / 0.35Ig (serviceability) for adopted slab rule, edge MPC and torsional compatibility | CANDIDATE_ONLY |
| 07 | `area_and_frame_gravity_loads_reconciled_to_etabs` | OpenSees pattern load inventory + a successful *seismic* preload | Same EDB, same ETABS and OpenSees **1.0D+1.0L** pattern totals, wall/slab/beam self-weight once, clear lengths, rigid offsets, full signed reactions, 32-joint and foundation-cut discrepancies | CANDIDATE_ONLY |
| 08 | `seismic_mass_reconciled_to_etabs_by_storey` | Source nodal masses and 40-mode OpenSees mass participation | Independently extracted ETABS 25-storey diaphragm mass, X/Y and RZ mass participation, local lumping vs source distributed operator, mass centers/inertia and NBC §5.2 Table 5-1 category factors | CANDIDATE_ONLY |
| 09 | `support_conditions_and_foundation_assumptions_reviewed` | 32-support selected tags and 44 released mesh tags | Independently identify source ETABS shell edge/auto-MPC and restraint DOFs; verify 32 physical cut resultants 6DOF vs matching ETABS case, rigid-end-zone influence and foundation kinematics | CANDIDATE_ONLY |
| 10 | `is16700_initial_pdelta_plus_minus_cases_completed` | No same-model, signed initial cases supplied | Independently solve and save project-adopted IS 16700:2023 §7.2(d) `1.2DL+0.5IL±1.5EL/WL` initialization cases as appropriate; report exact model/state, signs, convergence, initial stress and no earthquake double counting | MISSING |
| 11 | `p_delta_and_gravity_preload_completed` | 20-increment gravity *elastic* configured preload | Verify gravity and geometric nonlinear effects of the **actual NLTHA nonlinear** model at selected ULS/SLS preload, source reaction/force balance, tangent state, P-Delta and all applicable initial cases before transient | CANDIDATE_ONLY |
| 12 | `modal_periods_modes_and_mass_participation_reviewed` | 40-mode **elastic** modal solution and >90% mass screening | Solve nonlinear initial-tangent/effective stiffness model separately, evaluate X/Y/torsion eigenmodes, actual NBC Rayleigh work sums and damping bands; compare ETABS with source-matched mass/stiffness | CANDIDATE_ONLY |
| 13 | `brace_fvd_brb_case_matches_selected_scenario` | Model config provides geometry/section names | Bind active variant `M0–M6`, outrigger/belt/cap level and exact source device/bracing elements; assert no FVD/BRB is added in nominal no-device cases | CANDIDATE_ONLY |
| 14 | `device_properties_cited_calibrated_or_devices_disabled` | No project-matched device test supplied | In each no-device case, explicitly document *disabled*; otherwise verify FVD `C,alpha`, units, stroke, velocity/force, connection compliance and/or BRB cyclic hardening and test-based limits | MISSING |
| 15 | `rayleigh_damping_and_device_damping_not_double_counted` | External Rayleigh inputs and GUI flags | Derive `alphaM/betaK` from independently verified nonlinear initial modes, inspect modal damping across band, prevent viscous damping being counted twice where explicit FVD exists, justify target damping | MISSING |
| 16 | `single_element_and_wall_benchmark_checks_passed` | Published **teaching-model** fiber hysteresis plot only | Real project property material tests: cyclic beam/column, wall/FSAM shear-flexure, confinement/mesh, and individual device energy/force; compare backbone, degradation, pinching and finite accepted state to cited experiments | MISSING |
| 17 | `record_pair_units_scales_and_nbc_limits_reviewed` | No source-matched original 16 accelerogram bytes/scaling logs in uploaded MRSM packages | For each paired motion, hash actual record and original SeismoMatch output, time step, units (`g` ×9.81 or already m/s²), X/Y assignment and XY/YX runs, duration, NBC spectrum match/scale bounds and physical response records | MISSING |
| 18 | `material_file_missing` | `nonlinear_materials_file` blank | Supply a **reviewed project-specific** concrete/rebar material file (not demo values) and bind its SHA-256 to the selected model config | MISSING |
| 19 | `wall_fsam_tags_empty` | Empty mapping | Populate **project wall-property-to-FSAM-region** mappings from actual wall section and reinforcement schedule; ensure every active wall section resolves with valid material IDs | MISSING |
| 20 | `parameters_not_reviewed` | `nonlinear_parameters_reviewed=false` | Complete documented calibration/limits review on concrete tension/compression, steel hysteresis, confinement, shear transfer, damping and devices; human review recorded with model/config/material SHA | MISSING |
| 21 | `template_unbound` | Saved model-bound *draft* appears in GUI; the **run request still selected a generic template** | In readiness editor press **Save model-bound checklist**; verify main NLTHA input now points to `OpenSees_Model_Readiness_Draft_<model stem>_V134.json`, with actual model path/SHA and unchanged `approved_for_nltha=false`. Do not select `OpenSees_Model_Readiness_Template_V116.json` to execute | BINDING |

### Important 21-blocker arithmetic

The error consists of **1 human approval + 16 checklist checks + 3 material/configuration problems + 1 template binding problem**. Some requirements overlap engineering mechanisms; they remain distinct program gates. A signed manifest without verified material/FSAM, or a passing MRSM without a same-state nonlinear model, cannot collapse these checks.

## 3. Correct order to resolve without rework

**A — Source integrity and elastic baseline:** lock source EDB, correct current 12 m X-wall workbook and its B4/EDB linkage; reconcile actual 32-support/44 mesh-edge force transfer and 1.0D+1.0L gravity pointwise first. Fix source mass and modal stiffness at the same level; record the saved result and model hashes.

**B — Nonlinear input calibration:** build an immutable material inventory from actual drawings, steel schedule and grade, core confinement and source wall property mapping. Benchmark one material and one element at a time using actual cited experimental tests (PEER 2015/12 is a reference method, not a license to assume the specimen's reinforcement or strength for this model). Check 3D wall mesh/opening, damping/energy and FVD device or disabled-case conditions separately.

**C — Initial-state and selected scenario:** solve production nonlinear gravity and project-specific signed P-Delta initial cases. Verify M0–M6 active devices/bracing, independently checked nonlinear modal periods and damping.

**D — Ground motions and full record:** verify the eight bidirectional Soil C record pairs by original bytes, scaling logs and site requirements. Run at least one source-bound M0/Kobe/ULS XY **and** YX full-duration case; archive exact source, accepted history, solver exit state, numerical response and nonlinear wall first-step diagnostics. A 0.005 s diagnostic or successful zero-motion step is NOT full-record completion.

**E — Human review and acceptance:** record each checklist evidence file, reviewer, test outcome and exact source SHA. Enter an actual reviewed reference rather than the auto-populated `AVAILABLE FOR REVIEW` hint, save the model-bound draft, and approve only after all engineering and code checks pass. Native ETABS vs OpenSees, experimental material validation and code compliance are separate signed gates.

## 4. Source literature and model-element contracts

1. Kolozvari, K., Orakcal, K., Wallace, J.W. (2015), *Shear-Flexure Interaction Modeling for Reinforced Concrete Structural Walls and Columns under Reversed Cyclic Loading*, **PEER Report 2015/12**. https://peer.berkeley.edu/publications/2015-12 — supports experimental benchmark methodology, NOT project material parameter equivalence.
2. OpenSees official `E_SFI_MVLEM_3D` element documentation. https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html — verify exact `-thick`, `-width`, `-mat`, `-CoR`, `-ThickMod`, `-Poisson`, `-Density` usage against the actual built element and mesh.
3. NIST GCR 17-917-46v1 (2017), *Guidelines for Nonlinear Structural Analysis for Design of Buildings, Part I — General*. https://nvlpubs.nist.gov/nistpubs/gcr/2017/NIST.GCR.17-917-46v1.pdf — analytical input/uncertainty and nonlinear dynamic quality framework; supplementary reference, NOT a replacement for NBC 105:2025.
4. NBC 105:2025, official Nepal text, source link maintained in `engineering/rules/NBC105_GOVERNING_CODE_MATRIX.md`; seismic loads/mass, site, damping and time-history acceptance follow NBC, with separately documented project IS 16700 exceptional provisions.

## 5. Program/UI enforcement and local output

- The GUI's `AVAILABLE FOR REVIEW:` entries are discovery hints **not** inspected evidence. The Save action now rejects leaving such default placeholders as affirmative review references.
- The material binding Save action requires `nonlinear_materials_file`, `nonlinear_wall_fsam_tags` and **`nonlinear_parameters_reviewed=true`** before it permits reviewer approval. This never marks them true automatically.
- A plain-text blocked-readiness report remains available in the scrollable NLTHA dialog. Model-bound drafts and research-material copies are intentionally separate. Current source checks remain false until actual review.
- All **new** local export ZIP files belong in `07_EXPORT_ZIP` of their exact run/source stage. Existing result ZIPs retain original paths for provenance; no automatic migration or overwriting. See `docs/architecture/20261122_CANONICAL_REVIEW_ZIP_ROUTING.md`.

**Engineering acceptance:** `SOURCE_CHECKED=PARTIAL`; `NUMERICALLY_CONVERGED=ELASTIC_MODAL_AND_MRSM_ONLY`; `ETABS_OPENSEES_MATCHED=NOT_VERIFIED`; `EXPERIMENT_VALIDATED=NOT_VERIFIED`; `CODE_ACCEPTED=NOT_VERIFIED`; `FULL_DURATION_NLTHA=NOT_VERIFIED`.

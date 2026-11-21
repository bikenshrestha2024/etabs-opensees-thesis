# Damped-outrigger NLTHA gap register (hand-reviewed)

Scope: the 25-storey asymmetric RC core damped-outrigger NLTHA workflow in this repository. Base commit `2348cfb`, branch `feat/readiness-binding-ci-audit`, review date 2026-11-20. Editor Claude Code, model label UNKNOWN.

This register states what the code implements, which register reference (`docs/00_RESEARCH_REFERENCES.md`, R01-R13) supports it, what project evidence is missing, the current evidence tier and the next concrete verification step. It is a statement about provenance and evidence, not a design approval.

## How this register was made

- Every "Code implements" statement was checked by reading the cited file in this session. Statements about what a function does come from reading its body, not only its docstring. Where only a docstring or comment makes a claim (for example a native OpenSeesPy result), the entry says so.
- No test, native OpenSees run, ETABS run or numerical check was executed to write this register. `openseespy` does not import in the review sandbox (the import terminates the process), so native behaviour is NOT re-verified here. Test files named below exist; their pass state is reported only in the task report and `engineering/agent_edits/20261120_literature_code_map.md`, never inferred here.
- Reference-to-code citations come from the generated [LITERATURE_CODE_MAP.md](LITERATURE_CODE_MAP.md). A citation there is provenance only.
- No parameter value is introduced by this document. Where the code or `Material_Catalog/` carries a value, the entry says whether the file itself labels it assumed, example or user-supplied. Values that no file sources are UNKNOWN.

## Evidence tiers (from `docs/00_RESEARCH_REFERENCES.md`)

`FORMULATION` -> `EXPERIMENT` -> `NUMERICAL_REPRODUCTION` -> `PROJECT_TRANSFER_ASSUMPTION` -> `PROJECT_VERIFIED`.

The tier is the highest tier the repository can currently show for that component, judged by what is in the repo. No component reaches `PROJECT_VERIFIED`. A component marked `PROJECT_TRANSFER_ASSUMPTION` applies literature or assumed values to the building without project-specific evidence; it is not a stronger tier than `FORMULATION` in terms of validation, only a statement that the transfer has been made.

## Summary

| Component | Supporting refs (register) | Tier | Largest gap |
|---|---|---|---|
| FVD | R05, R06 (R06 not cited in code) | FORMULATION | Device K, Cd, alpha, connection stiffness and force-velocity-stroke test data: UNKNOWN |
| BRB | R07, R08 (R08 not cited in code) | FORMULATION | Actual BRB product geometry, tested protocol, connection eccentricity: UNKNOWN |
| SHS / ordinary steel braces | R09 (not cited in code) | PROJECT_TRANSFER_ASSUMPTION | Buckling/reversal hysteresis not modelled; yield value source UNKNOWN |
| E-SFI-MVLEM-3D walls | R01, R02, R03, R04, R11, R13 (R03 and R11 not cited in code; R04 is cited only by URL and author names in `wall_validation.py`, not by ID or DOI) | PROJECT_TRANSFER_ASSUMPTION | No experiment reproduction; PEER card reused for building walls |
| Coupling beams / openings | R12 | FORMULATION | Geometry gate only; no coupling-beam constitutive evidence |
| Slab / diaphragm | none in R01-R13 | PROJECT_TRANSFER_ASSUMPTION | Elastic slab and rigid diaphragm idealization has no reference in the register |
| Torsion, asymmetry, accidental eccentricity | R10 | FORMULATION | Accidental eccentricity not found in the NLTHA path |
| Record pairs, NBC 105:2025 9.3.2 scaling | R10 | FORMULATION | Original SeismoMatch scale logs and spectrum fit evidence not verified |
| P-Delta and gravity preload | R10 (as cited in code) | FORMULATION | Area-element geometric nonlinearity UNKNOWN; NLTHA state transfer not certified |
| Rayleigh / damping regions | none in R01-R13 | FORMULATION | Damping value rests on non-register sources; two reference modes are project input |
| Drift, torsion, acceptance outputs | R10 | FORMULATION | No reviewed component acceptance limits; drift screen is not acceptance |

## Cross-cutting facts that apply to every row

- `components/nonlinear_time_history/research_building_materials.py` `check_project_material_qualification` raises for `analysis_intent == "THESIS_NLTHA"`, with a message that the active frame and FSAM wall assignments are literature or sensitivity templates and that the production calibrated-material path is unimplemented. For other intents it returns `project_calibrated=False` and `native_wall_benchmark_verified=False`. It is called from `components/nonlinear_time_history/building_exploratory.py`.
- `components/model/assembly.py` `build_complete_model` returns `scope='EXPLORATORY_ASSUMED_MATERIALS_NOT_DESIGN_ACCEPTANCE'` for the research route and `analysis_ready=False`.
- `docs/00_THESIS_ACCEPTANCE_GATES.md` lists gates G00-G10 and names a current critical failure (first-step X-only nonfinite wall response). Its status is a document statement and was not re-checked here.
- The register references with no citation anywhere in `components/`, `src/` or `tests/` are R03, R06, R08, R09 and R11 (see the generated map; DOI, Source URL, author-name and ID searches of those folders all came back empty). R04 (Stokley and Lowes, layered shell) is not in that list: `components/validation/wall_validation.py` cites it by its PEER 2024/11 URL and author names, which an ID-and-DOI-only scan missed, and the map now detects such citations. That means the wall axial-load, FVD-placement, BRB-connection-eccentricity, tube-brace-hysteresis and tension-shear references are background reading only; no code path or test refers to them.

---

## 1. Fluid viscous dampers (FVD)

**Code implements** (read: `components/sections/devices.py`, `components/sections/mapping_audit.py`, `components/model/assembly.py`, `components/nonlinear_time_history/device_recording.py`, `components/nonlinear_time_history/runner_and_gui.py`, `components/nonlinear_time_history/damping_regions.py`):
- `devices.define_fvd_material` creates an OpenSees `ViscousDamper` (Maxwell: spring K in series with dashpot Cd and exponent alpha) and rejects non-finite values, K, Cd <= 0 and alpha outside (0, 1]. It has no default parameter values. `devices.add_fvd_link` creates a 3D `twoNodeLink` with `-dir 1` and optional `-doRayleigh` (default off).
- `mapping_audit.add_device` (which calls `validate_device`) and `assembly.build_complete_model` route a frame whose override target is `FVD_MAXWELL` to this link, only in `mode == 'nonlinear'`. In elastic mode an active FVD/BRB scenario raises. Segmented braces raise unless solver segments are assigned individually.
- `device_recording.device_sample` records relative axial displacement and velocity projected on the initial i-j axis and `basicForce`, tagged `sign_convention="UNVERIFIED"` and `qualification="DEMAND_ONLY"`; `summarize_device_demands` reports peak force, velocity, displacement and a signed force-velocity work with `energy_sign_approved=False`.
- `damping_regions.EXCLUDED_ELEMENT_TYPES` keeps `TwoNodeLink` out of the structural Rayleigh region.
- A second, legacy `define_fvd_material` in `components/sections/definitions.py` raises unless a physical K is supplied; its other arguments carry example numbers that its own docstring calls uncalibrated.
- `devices.convert_fvd_cd_mm_to_m` and `devices.summarize_fvd_history` exist and are exercised by `tests/verify_device_parameter_finiteness.py`; I found no call to them from `components/` or `src/`.

**Reference support:** R05 (Korkmaz and Kircil 2026) is cited in `devices.py` and `device_recording.py` for methodology and unit conversion. R06 (FVD placement sensitivity) is not cited anywhere in code or tests. The OpenSees `ViscousDamper` command page is the formulation source for the command form.

**Project evidence missing:**
- Device K, Cd, alpha, installation and connection/support stiffness for the project damper: UNKNOWN. `Material_Catalog/Official_FVD.json` labels its card a published numerical example and "not an optimized building damper"; `Material_Catalog/M30_Fe500_FVD.json` exists and was not read for values here.
- Force-velocity-stroke and energy qualification of the device (G06): none in the repo.
- Recorder force sign and the sign of signed work: marked UNVERIFIED in code. `tests/audit_native_device_recorders.py` with `tests/native_device_recorders.tcl` checks recorder alignment and says it is not physical validation; I did not run it and found no stored result for it.
- Placement choice and its sensitivity (R06 workflow): no code or evidence.

**Current tier:** FORMULATION. The element and material are the documented OpenSees forms; no experiment or numerical reproduction of a device exists in the repo.

**Next verification step:** Obtain the project damper datasheet or test record, write its K, Cd, alpha, units and source into the project parameter register, then run a single-device native benchmark (prescribed sinusoidal stroke) and compare force-velocity loops against that record; settle the recorder force sign in the same run. Then wire or retire `summarize_fvd_history` so the stroke and energy metrics in `devices.py` and `device_recording.py` are not duplicated.

## 2. Buckling-restrained braces (BRB)

**Code implements** (read: `components/sections/devices.py`, `components/sections/mapping_audit.py`, `components/sections/mapping_gui.py`, `components/model/assembly.py`, `components/sections/definitions.py`):
- `devices.define_brb_core_material` creates a `Steel02` core material from caller-supplied Fy, E0, b, R0, cR1, cR2, a1-a4 and initial stress, with no defaults; `devices.add_brb_corot_truss` creates a `corotTruss` using the core area, not the casing area.
- Routing and validation mirror the FVD path. `mapping_audit.validate_device` rejects a `reference_only` parameter set, requires a project citation and a `weight_reviewed` flag, and requires finite values for every Steel02 key and the core area; a further check rejects non-positive strengths or a hardening ratio of 1 or more.
- The legacy `definitions.define_brb_core_material` in `components/sections/definitions.py` has a numeric default core yield and fixed Steel02 constants in its signature and body. I found no source for them in that file; I did not trace whether any active route uses it. `Material_Catalog/M30_Fe500_BRB.json` labels its card a "NOMINAL / ASSUMED RESEARCH BASELINE" that "does not reproduce a tested brace assembly".
- `devices.brb_cumulative_plastic_ductility` computes total absolute plastic travel over yield displacement and says it is a demand measure. It is exercised in `tests/verify_device_parameter_finiteness.py`; I found no call from `components/` or `src/`. The recorded device rows carry total relative displacement, not an elastic/plastic split, so the metric's input is not produced by the recorder.

**Reference support:** R07 (Guerrero Bobadilla et al. 2025, BRB cumulative ductility and fatigue) is cited in `devices.py` as context; the register says its DOI is not independently confirmed. R08 (out-of-plane connection eccentricity) is not cited in code or tests; the register's restriction ("do not assume pin-ended corotTruss represents full connection behavior") is therefore not addressed by any code path.

**Project evidence missing:** actual BRB product geometry, core area, yield length, tested protocol and calibrated Steel02 constants (UNKNOWN); overstrength and cumulative ductility limits (UNKNOWN); connection stiffness and out-of-plane eccentricity; fatigue life evidence. Nothing in the repo reproduces a BRB test.

**Current tier:** FORMULATION.

**Next verification step:** Take one published or manufacturer BRB cyclic test with its protocol and measured loops (R07 or the product test report), calibrate the core Steel02 constants to that record with a stated objective and fit statistic, and compare peak strength, secant stiffness, loop shape and dissipated energy. Add a plastic/elastic decomposition to the recorder so the cumulative-ductility metric has a valid input, or remove the unused function.

## 3. SHS and ordinary steel braces

**Code implements** (read: `components/model/assembly.py`, `components/sections/definitions.py`, `components/nonlinear_time_history/research_building_materials.py`, `components/model/section_tags.py`):
- Research route (`research=True`): an ETABS frame flagged `hinged_brace` becomes a `corotTruss` with a `Steel01` material using the ETABS section area and, by default, the ETABS elastic modulus. Yield stress comes from `research_building_materials.brace_steel_parameters`, whose docstring calls the 345 MPa default "user-specified"; hardening ratio default 0.01. The code comment states "no buckling/fracture capability claimed".
- Reviewed route (`research=False`): a `hinged_brace` frame raises "nonlinear end-release formulation is not implemented". The reviewed route therefore fails closed for hinged outrigger diagonals.
- Non-hinged SHS members map to the fibre section `SHS_350x350x16_STEEL_FIBER` (`definitions.define_shs_350x350x16`): Steel02 fibre section built from four rectangular patches with elastic Saint-Venant torsion. Its docstring calls the 379.5 MPa expected yield (1.1 x Fe345) "the user's expected-strength assumption" and the Poisson ratio 0.30 a stated default assumption.
- `docs/OUTRIGGER_MATERIAL_SENSITIVITY_AND_VALIDATION.md` records the 2026-11-15 researcher decision to keep pin-ended ETABS diagonals as a provisional two-force idealization and says it is not a passed gate.

**Reference support:** R09 (circular tube hysteresis, Tian et al. 2026) is not cited in code or tests, and the register states the circular tube is not the thesis SHS 350x350x16. No register reference supports the Steel01/Steel02 brace parameter values; their stated basis is a user assumption.

**Project evidence missing:** steel grade certificate or coupon data and expected-strength basis (UNKNOWN); a buckling/reversal-capable brace model and its calibration against SHS tests (none); connection stiffness and slip; evidence that the outrigger diagonals are actually pinned (G01 needs `GetReleases`, member role and drawings).

**Current tier:** PROJECT_TRANSFER_ASSUMPTION (assumed yield and an axial-only idealization applied to the building; the register's R09 transfer restriction is unmet).

**Next verification step:** Obtain SHS 350x350x16 brace test data or a mill certificate, then run a single-brace native cyclic benchmark comparing the current `corotTruss + Steel01` route with a buckling-capable alternative (fibre-section `forceBeamColumn` with an imperfection) and record the difference in peak compression, unloading and energy. Resolve the hinged-brace gate with the source member releases before relying on either route.

## 4. E-SFI-MVLEM-3D core walls

**Code implements** (read: `components/model/assembly.py`, `components/sections/area_elements.py`, `components/nonlinear_time_history/research_building_materials.py`, `components/nonlinear_time_history/one_storey_wall_probe.py`, `components/nonlinear_time_history/wall_diagnostics.py`, `components/validation/wall_validation.py`, `components/validation/material_benchmarks.py`):
- In nonlinear mode a `SHEAR WALL` shell becomes an `E_SFI_MVLEM_3D` element with `wall_macro_fibers` fibres (config key, default 5 in code; fewer than 2 raises), the same FSAM material tag on every fibre and `-Density 0`. The FSAM tag comes from the research profile or from `cfg['nonlinear_wall_fsam_tags']`.
- Research materials come from `Material_Catalog/PEER_Web_ESFI_Patch.json` or an M30/Fe500 sensitivity card via `define_building_materials`; `check_project_material_qualification` documents that these are templates and that 20 mm at 200 mm core reinforcement is assumed.
- `area_elements.instantiate_area_elements` preserves missing quads as openings and creates `ShellMITC4` floors; its header states per-panel E-SFI construction does not prove core-opening compatibility, junction bending, re-entrant torsion, calibration or mesh convergence.
- `wall_diagnostics.inspect_wall_geometry` checks quad geometry only; `one_storey_wall_probe` builds a single first-storey panel and states no single-storey response is extrapolated to the building.
- `wall_validation.py` registers `kolozvari2023` specimens `SD-06-00` and `SD-06-45` with status `PENDING_EXPERIMENTAL_REPRODUCTION` and a 14-item check list that includes cyclic experiment, mesh objectivity, biaxial/torsion, openings and building transfer. Its `esfi` function is documented as a PEER-2015-material numerical smoke test, not SD-06 validation.

**Reference support:** R02 (Kolozvari, Lopez and Massone 2023) is the element formulation and is cited in `assembly.py` and several research modules by ID and DOI. R01 (PEER 2015/12 Appendix B.3) supplies the web material card, cited by ID in the material modules. R13 (LFSAFE alternative) is cited in `area_elements.py` as comparison only. R04 (layered shell calibration, Stokley and Lowes) is cited in `wall_validation.py` only as a PEER 2024/11 URL and author names in the `SOURCES['regularization']` note (mesh and softening regularization review before transfer); no code path uses its layered-shell parameters. R03 (T-wall axial ratio) and R11 (tension-shear) are not cited in code or tests.

**Project evidence missing:** actual boundary and web reinforcement, confinement and axial load for the project core (UNKNOWN; the repo holds templates); cyclic reproduction of the cited specimens with fit statistics; mesh and macro-fibre convergence; resolution of the first-step X-only nonfinite wall response listed in the acceptance-gates note; calibrated FSAM parameter set for the building walls.

**Current tier:** PROJECT_TRANSFER_ASSUMPTION. The element is a documented formulation (R02) and the PEER card is experimental (R01), but the repo has no numerical reproduction of either, and the card is reused for building walls against the register's explicit restriction.

**Next verification step:** Run the `kolozvari2023` SD-06 specimens (or the R01 RW-A15-P10-S78 specimen) natively with the published protocol, compare peak strength, initial and secant stiffness, loops, pinching, energy and failure drift as the register lists, and record fit statistics in the validation workbench. Only then derive a project wall card with its own axial ratio and reinforcement.

## 5. Coupling beams and wall openings

**Code implements** (read: `components/nonlinear_time_history/wall_topology.py`, `components/nonlinear_time_history/building_exploratory.py`, `components/sections/area_elements.py`, `components/model/readiness.py`):
- `wall_topology.validate_openings` checks that declared axis-aligned rectangular voids (XZ or YZ planes) do not intersect assembled wall-quad interiors; `write_opening_report` writes the report and raises if the status is `BLOCKED`. For `analysis_intent == "THESIS_NLTHA"`, `verify_project_opening_manifest_required` requires a non-empty `wall_openings` manifest and returns `OPENING_DECLARATIONS_PRESENT_GEOMETRY_STILL_UNVERIFIED`.
- Its module text states it does not validate wall materials, coupling-beam flexure or wall torsion. `area_elements` notes that opening gaps are preserved and coupling beams and junctions need independent modelling checks.
- No coupling-beam element, diagonal-reinforcement model or constitutive law exists in the code I read. Readiness checklist item `wall_opening_and_coupling_beam_mesh_reviewed` is a human attestation. Whether the project's coupling beams are modelled as ETABS frames (and therefore pass through the RC frame fibre sections) is UNKNOWN; I did not inspect an ETABS export.

**Reference support:** R12 (Rezapour et al. 2026) is cited by DOI in `wall_topology.py`. R12's register entry says its proposed formulations need independent reproducible case tests; none exists here.

**Project evidence missing:** opening schedule from the ETABS source (G01); coupling-beam geometry, reinforcement and cyclic behaviour; shear-transfer and junction compatibility at wall corners; the R12 case reproduction.

**Current tier:** FORMULATION (geometry-gate logic only; no coupling-beam or opening response evidence).

**Next verification step:** Export the actual opening and coupling-beam schedule from the source EDB, run `write_opening_report` on the assembled model and file the result, then build one coupled-wall benchmark from R12 (or R13 U/H specimens) to test the chosen coupling-beam idealization before using it in the building.

## 6. Slab and diaphragm

**Code implements** (read: `components/model/assembly.py`, `components/sections/area_elements.py`, `components/gravity/load_path_formulas.py`):
- Floor shells (`FLOOR` category) are `ShellMITC4` with an `ElasticMembranePlateSection` in the elastic and nonlinear builds. The bending factor comes from config (`slab_bending_factor`, `slab_bending_factor_sls`); its value in the project config is UNKNOWN to this review. The `area_elements` header states `ShellMITC4` with that section is not a nonlinear RC slab law.
- Story diaphragms use `ops.rigidDiaphragm(3, master, *slaves)` with the master fixed in Z and rotations about X and Y; `components/gravity/load_path_formulas.py` states this constrains UX, UY and RZ and carries no vertical pressure.
- `docs/validation/20261118_RAYLEIGH_RETAINED_DOF_CORRECTION.md` documents an OpenSees 3.8.0 Transformation-handler artefact for partially fixed diaphragms that affects Rayleigh period estimates; it is project evidence about the constraint treatment, not about slab behaviour.

**Reference support:** none in R01-R13. NBC 105:2025 (R10) is cited for the model scope (`section_tags.py`, `assembly.py`) but not for a slab or diaphragm idealization. The rigid-diaphragm and elastic-shell choices rest on OpenSees command documentation.

**Project evidence missing:** diaphragm flexibility check for the asymmetric plan and openings (rigid versus semi-rigid sensitivity); slab stiffness reduction basis; slab-wall and slab-outrigger force transfer, especially at the outrigger floors; collector and chord checks. All UNKNOWN.

**Current tier:** PROJECT_TRANSFER_ASSUMPTION (rigid in-plane behaviour and elastic slab stiffness assumed for the whole building).

**Next verification step:** Run the same ULS NLTHA case with the rigid diaphragm replaced by in-plane-flexible shell floors on the outrigger floors and one typical floor, compare floor-edge drift and wall/outrigger force demand, and record the difference against the rigid result.

## 7. Torsion, asymmetry and accidental eccentricity

**Code implements** (read: `components/validation/torsion_check.py`, `components/validation/floor_end_extraction.py`, `components/response_spectrum/model_analysis.py`, `components/equivalent_static/calculation_and_gui.py`, `components/validation/irregularity_review.py`):
- `torsion_check.check_floor_end_torsion` returns max/min of opposite floor-end displacements, flagging irregularity above 1.5 and extreme above 2.5 (clauses 5.4.2.1 and 5.4.2.2 as written in the module). It returns NOT EVALUATED when the same-floor, centred-CM, same-direction, same-case and same-basis flags are not all true.
- `floor_end_extraction.map_floor_ends` first rejects (ValueError) any input row whose `centered_cm_load` is not true or whose `response_basis` is not `signed_centered_linear_increment` (lines 143-147), and also requires explicit case, step and a matching limit state. Only after those checks does it call `torsion_check.check_torsional_irregularity` (not `check_floor_end_torsion` directly) with the literal `centered_cm_load=True` and `same_end_basis=True`; that function forwards only `centered_cm_load` to `check_floor_end_torsion`, and the same-floor, same-direction, same-case and same-basis flags there keep their True defaults. Those conditions are enforced by grouping nodes per (storey, axis, case) and by the validated input columns, so the literal True values restate validated input and are not unchecked assertions. Whether the user's displacement file really is a centred-CM, signed linear-increment result is still a claim in that file that the code cannot verify.
- Accidental eccentricity (plus and minus 5 percent of perpendicular breadth) is implemented in the response-spectrum engine (`model_analysis.py`, cases E0, Eplus, Eminus) and in the equivalent-static output (`calculation_and_gui.py`). I found no accidental-eccentricity treatment in `components/nonlinear_time_history/`; `one_storey_wall_probe.py` lists accidental torsion among things it does not include. Whether an NLTHA mass-offset or eccentric-input convention is intended is UNKNOWN.
- `irregularity_review.py` states its reference forces use the centre of mass with no accidental eccentricity.

**Reference support:** R10 (NBC 105:2025). The `[REF]` tags in these modules name clauses; I did not compare the clause text against the official PDF. R13 (U/H wall torsion benchmarks) is cited only in `area_elements.py` header and no torsional benchmark is run.

**Project evidence missing:** an NLTHA convention for accidental eccentricity (and a decision on whether it is required for time-history cases); torsion ratios from actual NLTHA floor-end displacements (the extraction path is built for a static centred case); torsional benchmark from R13; verification of the extraction evidence flags against the real input files.

**Current tier:** FORMULATION.

**Next verification step:** Decide and document the NLTHA accidental-eccentricity treatment from the NBC text, implement it as an explicit config option if required, and add a test that fixes a known asymmetric two-end case.

## 8. Record pairs and NBC 105:2025 9.3.2 scaling

**Code implements** (read: `components/nonlinear_time_history/nbc105_2025_audit.py`, `nbc105_horizontal_input.py`, `seismomatch_audit.py`, `soil_c_run_matrix.py`, `soil_c_nltha_suite.py`, `building_exploratory.py`, relevant sections only):
- `nbc105_time_step_limit` takes the minimum of 0.01 s, the record dt, T1/100 on each axis and Tn90 on each axis. `paired_ground_motion_scale` requires both independent factors in [0.33, 3] and returns the lower. `scaling_period_range` returns [Tn90, sqrt(R_mu) x T1]. `response_aggregation_rule` requires at least three pairs, returns MAXIMUM below seven pairs, AVERAGE above seven, and a review-required label for exactly seven.
- `validate_nbc105_design_metadata` screens reviewer-supplied metadata (target kind, spectrum-fit SHA-256, selection-reviewed flag, XY and YX orientations, dt bound, shared pair scale). It states `independent_spectrum_reproduced=False` and `METADATA_SCREEN_ONLY_NOT_NBC_DESIGN_APPROVAL`.
- `nbc105_horizontal_input` maps XY and YX to `UniformExcitation` DOF 1 and 2 with no vertical input, and rejects a pair scale other than 1.0 for already-matched records.
- `seismomatch_audit.assess_preprocessed_sources` hashes the record files, detects the SeismoMatch export header and sets `independent_seismomatch_scale_factors_verified`, `nbc105_lower_of_pair_rule_verified`, `matching_target_formula_verified` and `target_period_window_coverage_verified` to False.
- `soil_c_run_matrix` documents 7 variants x 8 matched pairs x 2 limit states = 112 configurations and 224 analyses, generated but never executed by that module. `soil_c_nltha_suite` records `original_SeismoMatch_0_33_to_3_scale_logs_verified`, `original_SeismoMatch_lower_of_pair_factor_verified`, `gorkha_export_provenance_reviewed`, `loma_prieta_end_time_policy_approved` and `site_Vs30_and_record_magnitude_distance_metadata_verified` as False.

**Reference support:** R10 (NBC 105:2025 clauses 9.3.2.1-9.3.2.4 and 9.3.3). The scaling and aggregation functions encode the clause wording as the code authors read it; the official PDF was not compared in this review.

**Project evidence missing:** the original SeismoMatch scale-factor logs and lower-of-pair factors; an independent reproduction of the C(T)/Omega_u target fit over the period window; Tn90 and T1 from the verified project model (the preflight accepts them as inputs); record selection metadata (magnitude, distance, mechanism, Vs30); an executed full-record suite. No NLTHA suite result is stored as evidence in the files I read.

**Current tier:** FORMULATION (clause logic and provenance screens only).

**Next verification step:** Obtain the original SeismoMatch logs for the eight pairs, reproduce the target-spectrum fit independently from the waveforms with a script that reports misfit over the [Tn90, sqrt(R_mu) T1] window per axis, and record the result as the `spectrum_match_evidence` file the preflight expects.

## 9. P-Delta and gravity preload

**Code implements** (read: `components/model/assembly.py`, `components/model/initial_pdelta.py`, `components/model/eq_pdelta_initial_tangent.py`, `components/nonlinear_time_history/runner_and_gui.py`, `components/gravity/solver_stack.py`):
- Frame elements use `geomTransf('PDelta', ...)` in `build_complete_model`. I found no geometric transformation for area elements (`ShellMITC4`, `E_SFI_MVLEM_3D`) in that code. Whether `E_SFI_MVLEM_3D` includes geometric nonlinearity is UNKNOWN: I did not read the element documentation.
- `build_complete_model(preload=True)` runs `run_gravity_stage` from `OpenSees_Analysis_Stack_V110` in 20 load steps (with an adaptive option for the literature profile) and writes gravity check JSON. The NLTHA runner then calls `ops.loadConst("-time", 0.0)` and requires the model builder to have solved gravity first; the comment says it does not apply gravity or certify convergence.
- `initial_pdelta.py` and `eq_pdelta_initial_tangent.py` are diagnostic initial P-Delta checks (IS 16700:2023 section 7.2(d) combination as the project-adopted input, per their docstrings). Both state they do not certify state transfer into a time-history solver and warn that a held static EL plus full dynamic support acceleration risks double counting.
- `docs/validation/20261120_GRAVITY_REACTION_REBUILD.md` records an ETABS-versus-OpenSees gravity reaction comparison (equal total reaction, support-level differences up to 768.045 kN for the reviewed elastic model). It is an elastic gravity comparison, not a nonlinear NLTHA initial-state verification.

**Reference support:** R10 as cited in the code for P-Delta in time histories (clause references 8.1.1.3 and 9.3.1.3 in `initial_pdelta.py`, 9.3.1.2-3 in the runner comment); I did not compare these with the official text. IS 16700:2023 is a supplementary source named in `components/validation/reference_library.py`, not in R01-R13.

**Project evidence missing:** nonlinear (not elastic) gravity state with the actual wall and device models; confirmation that P-Delta acts on walls and diaphragms; a P-Delta on/off comparison of drift and base shear; verification that the NLTHA starting state matches the gravity run.

**Current tier:** FORMULATION.

**Next verification step:** Run the nonlinear gravity stage with the literature wall model on the verified source model, record equilibrium and support reactions against the elastic ETABS reference, then run one ground-motion case with P-Delta on and off and file the difference in peak drift and base shear. Read the E_SFI_MVLEM_3D documentation to settle the area-element geometric-nonlinearity question.

## 10. Rayleigh and damping regions

**Code implements** (read: `components/nonlinear_time_history/damping_regions.py`, `components/nonlinear_time_history/runner_and_gui.py`, `components/nonlinear_time_history/building_exploratory.py`):
- `damping_regions.apply_structural_rayleigh` defines `REGION_STRUCTURAL` (structural elements, aM and committed-stiffness bK) and `REGION_MASS_NODES` (orphan mass nodes, aM only). `classify_elements` excludes `TwoNodeLink`, `ZeroLength`, truss, corotTruss and damper types, plus any tags in `rayleigh_excluded_element_tags`; unknown element types stay structural.
- `resolve_inherent_damping_ratio` defaults to 0.025, allows up to 0.05 only with `inherent_damping_five_percent: true`.
- The runner takes two damping reference periods and a damping percentage from config, checks each checked mode against 5 percent, and supports `Rayleigh committed`, `Modal (initial eigenbasis)` and a `GLOBAL_LEGACY` scope. The default scope is `STRUCTURAL_REGION`. `THESIS_NLTHA` requires two explicit damping reference modes and `rayleigh_device_exclusion_reviewed: true` (`building_exploratory.py`).
- The module docstring reports a native OpenSeesPy 3.8.0 check that region `-node` captures elements and that truss and link elements ignore stiffness-proportional Rayleigh without `-doRayleigh 1`; `tests/verify_damping_regions.py` is cited for it. I did not re-run it.

**Reference support:** none in R01-R13. The tags cite Charney 2008, Zareian and Medina 2010, PEER TBI 2017, LATBSDC 2020 and NBC 105:2025 section 8.1.1 "as cited in this repository, verify clause text". Charney 2008 appears in `LITERATURE/MASTER_LITERATURE_INDEX.csv` (L045) and is cited by DOI; the others are author-year only and are not detected by the generated map.

**Project evidence missing:** justification of the damping ratio and the two reference modes for this asymmetric building (project input, UNKNOWN); sensitivity of drift, device demand and wall response to the damping model; verification of NBC 105 section 8.1.1 clause wording; confirmation that devices have no hidden Rayleigh contribution in the actual project model.

**Current tier:** FORMULATION.

**Next verification step:** Re-run `tests/verify_damping_regions.py` natively on the project's OpenSeesPy build, then run one NLTHA case with `Rayleigh committed` versus `Modal (initial eigenbasis)` damping and record the change in peak drift and device force. Check the clause 8.1.1 text against the official PDF and record the outcome.

## 11. Drift, torsion and acceptance outputs

**Code implements** (read: `components/nonlinear_time_history/runner_and_gui.py`, `components/nonlinear_time_history/building_exploratory.py`, `components/validation/nonlinear_performance.py`, `components/nonlinear_time_history/full_record_gate.py`, `components/validation/torsion_check.py`):
- The runner records story drift from floor-master displacement differences over story height and writes peak and signed extremes per axis, with a `drift_screen_X/Y` of PASS or REVIEW against 0.025 (ULS) or 0.006 (SLS). It merges floor-edge drift where recorded (`floor_edge_peak_story_drift_*`). `building_exploratory.py` reports `max_story_drift_*` and `max_floor_edge_drift_*`.
- `nonlinear_performance.template` lists peak edge drift per axis with those two limits and `reviewed=False`, and lists residual drift, plastic rotation, concrete and steel strain, wall and joint shear, BRB ductility, FVD stroke and FVD force with `limit=None`. `assess` marks a criterion NOT EVALUATED unless it has a reviewed source and clause, a model SHA-256, the expected pair IDs, matching units and `COMPLETED_FULL_RECORD` evidence; a torsion-sensitive suite with fewer than three pairs is also NOT EVALUATED. Aggregation is maximum below seven pairs, mean otherwise, and exactly seven raises.
- The drift limits and the 9.3.3.1-to-5.6 cross-reference discrepancy are carried as a warning in the runner, `nonlinear_performance.py` and R10's register entry; the code does not alter the clause.
- Torsion ratio is computed by `floor_end_extraction` from a centred static case (see section 7); the NLTHA runner does not produce a torsion-ratio output in the files I read.

**Reference support:** R10 (NBC 105:2025 sections 5.5.3 and 9.3.3). NIST GCR 17-917-46v3 is linked from the performance GUI as guidance and is not in R01-R13.

**Project evidence missing:** reviewed component acceptance limits for wall shear, plastic rotation, strains, joint shear, BRB ductility and FVD stroke and force (UNKNOWN; the template leaves them empty by design); independent review of the drift screen; a completed full-record suite; residual drift from a full record; a torsion-ratio output on NLTHA results; M0-M6 variant comparison under identical input (G09).

**Current tier:** FORMULATION.

**Next verification step:** Fill the performance template for one limit state with sourced, reviewed criteria for the two or three controlling components, feed it demands from one complete-record case, and confirm the assessor refuses (NOT EVALUATED) when any evidence field is withheld. Add an NLTHA floor-end torsion output that reuses the section 7 extraction with the correct evidence flags.

---

## What this register does not establish

- It does not establish that any component is validated for this building. No row is `PROJECT_VERIFIED`.
- It does not re-verify any native OpenSees behaviour, ETABS value or clause text.
- It does not cover Steel02 and Concrete material calibration beyond the points above (see `LITERATURE/Reinforcing_Steel/README.md` and `docs/00_RESEARCH_REFERENCES.md`, material evidence policy).
- UNKNOWN items above remain open until the named evidence is supplied.

## Run evidence received (2026-11-21)

- `docs/validation/run_findings/LTHA_V115_PRELIM_20261120.md`: a *linear* V115 preliminary setup run, 12 of 16 cases complete, each a 0.5 s `TRUNCATED_DIAGNOSTIC_NOT_CODE_ACCEPTANCE` trial. Measured native solve about 2.03 s/step with no factor reuse; the full-record projection is a lower bound for nonlinear cost.
- It exercises ETABS-derived geometry, gravity preload and eigen solve only. It contains no FVD/BRB, FSAM or material-nonlinear evidence, so no row above changes tier.

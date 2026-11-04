# Stage 37 — Soil C NLTHA JSON evidence schema, units and reviewer fields

**Scope:** Documents the existing JSON outputs created by Soil C source preflight, the Stage 36 M0–M6 generator, the existing exploratory 3D nonlinear runner and the device/response modules. It does not create code approval or assert unknown ETABS reinforcement material properties.

## 00. Input and output origin

| JSON filename | Producer and scope | Engineering use |
|---|---|---|
| `35_Soil_C_Matched_Inputs.json` (chosen path) | `35_SOIL_C_NLTHA_PREFLIGHT.py`, `soil_c_nltha_suite.write_suite_report` | Eight pair source hash + timing, exactly 16 components, optional model modal periods |
| `Soil_C_Matched_Source_Gate.json` | `building_exploratory.py` Soil-C opt-in | Actual selected event, exact input source SHA, review state, Loma approved numeric endpoint policy |
| `SeismoMatch_Source_Provenance.json` | `seismomatch_audit.assess_preprocessed_sources` | Matched header and source units; explicitly cannot verify original component scaling logs |
| `NLTHA_Input_Quality.json` | `thesis_quality.audit_ground_motion_pair` | Sample count, dt, original source SHA, peak acceleration in source units, any in-memory extension note |
| `NBC105_2025_NLTHA_Input_Screen.json` | `nbc105_2025_audit.write_preflight` | Reviewer-supplied T1/Tn90, dt bound, C(T)/Omega target category; metadata screening only |
| `OpenSees_Bidirectional_Input_Commands.json` | `nbc105_horizontal_input.write_manifest`, per orientation | Source A/B mapping to global DOFs 1,2; actual Path factor; model and source units |
| `Ground_Acceleration_Recording_Method.json` | Per-case `building_exploratory.py` | Relative node + interpolated support absolute floor acceleration method and restrictions |
| `Initial_Modal_Damping.json` | Per-case `building_exploratory.py` | Computed exploratory modes and Rayleigh coefficients; `dt_screen_s` is a preliminary mode screen, not proof that 90%-mass modal Tn90 is met |
| `ASSUMPTIONS_NOT_DESIGN.json` | `building_exploratory.py` | Declared material model scope; nominal reference-based modeling remains NOT DESIGN ACCEPTANCE |
| `RunConfig.json` | `building_exploratory.py` | Full resolved input config, exact user options and source paths |
| `FAILED.json` / `INCOMPLETE.json` | `_write_failure_report` | Failure stage, traceback, accepted-step evidence, solver state; preserve failed runs |
| `Case_Summary.json` / `NLTHA_Quality_Gates.json` | Case response postprocess / research quality gate | Full-duration and numeric-screen progress; NOT automatically experimental validation |
| `00_SOIL_C_RESEARCH_RUN_MATRIX.json` | `soil_c_run_matrix.create_configs` | 112 configs, 224 intended XY/YX analyses; NOT EXECUTED |
| `configs/M#/ULS|SLS/event.json` | Stage 36 run generator | Per-event source files, soil C target, no second amplitude factor, output isolation |
| `NBC105_2025_RC_DUAL_C_D_Target_Metadata.json` | Stage 34 spectrum generator | Soil C/D independent source code shape and chosen zoning/importance values; matched source IDs separate |

## 01. Required input fields for matched Soil C cases

```json
{
  "soil_type": "C",
  "soil_c_primary_nltha": true,
  "source_records_already_scaled": true,
  "earthquake_event": "Kobe",
  "x_path": "<actual private file A>",
  "y_path": "<actual private file B>",
  "scale": 1.0,
  "orientations": ["XY", "YX"],
  "diagnostic_excitation": "XY",
  "dt_s": 0.005,
  "duration_s": null,
  "limit_state": "ULS",
  "analysis_intent": "RESEARCH_DIAGNOSTIC",
  "nonlinear_walls": true,
  "gorkha_processing_reviewed": false,
  "loma_end_policy": "reject",
  "engineering_reviewer": null,
  "approved_frame_reinforcement_csv": null,
  "nbc105_2025_design_evidence": null
}
```

The `model_folder` and `output_dir` fields are mandatory runtime paths omitted from the illustrative fragment above. The `earthquake_event` is bound to actual A/B matched source SHA256 rather than accepted solely by name. `scale=1.0` is the **additional OpenSees spectral multiplier**, not the independent original SeismoMatch matching factor. If actual source ordinates are `Acc(g)`, the OpenSees Path factor is **9.80665** m/s² per g.

## 02. Critical `nbc105_2025_design_evidence` fields

| Key | Type/units | Must represent |
|---|---|---|
| `t1_x_s`, `t1_y_s` | positive seconds | Current verified first translational periods of the ACTUAL model |
| `tn90_x_s`, `tn90_y_s` | positive seconds | Period of modes achieving ≥90% cumulative effective mass in each axis |
| `r_mu` | dimensionless | 3.5 for reviewed RC dual shear-wall system |
| `omega_u` | dimensionless | 1.4 for same system |
| `factor_x`, `factor_y` | dimensionless | Original **independent** SeismoMatch source-fit factors per horizontal component; each 0.33–3.0 |
| `target_spectrum_kind` | string | `ULS_ELASTIC_SITE_C_OVER_OMEGA_U`, whose actual target ordinate basis is `C_h(T)*Z*I/Omega_u` |
| `spectrum_match_evidence_sha256` | 64-char lowercase/uppercase hex digest | Byte-exact original SeismoMatch spectrum-fit/session evidence; hash alone is NOT independent verification of its scientific content |
| `ground_motion_selection_reviewed` | boolean | Manually reviewed magnitude, distance, mechanism and site/station selection. Do not set true from filename |
| `orientations` (outer config) | exactly `["XY","YX"]` | Apply both simultaneous A/B orientations in independent gravity-preloaded models |

**Avoid invented data:** Nothing in the 16 matched accelerograms or target workbook establishes your current source ETABS 90%-mass `Tn90` or the original SeismoMatch scaling logs. Never auto-fill these fields with a nominal 20th mode, a thesis-workbook reference period 3.526s, or the postmatching PGA ratio.

## 03. Matched source fields

`records[].components[]` lists source label A/B, source filename, source SHA256, record dt, recorded end time and measured PGA in g. The `previous_conditional_mean_PSA_error_percent` field describes the prior 120-log-period arithmetic comparison of 5%-damped PSA with the source Soil C target; it is NOT an NBC-prescribed acceptance threshold.

`timing_policy_review_required` highlights Loma Prieta; `gorkha_export_provenance_reviewed=false` highlights Gorkha source processing. `source_and_pair_synchronization_pass` may remain false even when all source SHA values are correct; no automatic zero-padding or record mutation is performed during the eight-pair preflight.

`current_modal_period_screen`: either `UNKNOWN_NO_VERIFIED_CURRENT_MODAL_INPUTS` or `INPUT_PERIOD_SCREEN_ONLY` with X/Y actual fitting intervals, per-event dt upper bound and selected dt screen. An input-data pass is never an experimental/model approval.

## 04. Runtime endpoint policy

The existing matched Loma Prieta A/B files end at 39.975s / 39.980s. If an engineer explicitly elects `loma_end_policy="append_zero_reviewed"` with a nonempty `engineering_reviewer`, the runner extends **only the shorter in-memory acceleration series by one zero sample**. Source text files and SHA values remain unchanged. `Soil_C_Matched_Source_Gate.json.runtime_endpoint` records the extension and reviewer. Engineering acceptability depends on the original source end-time dynamics and cannot be inferred from this program.

For the Gorkha original 120s versus matched 322.94s, `gorkha_processing_reviewed=true` and named reviewer are required to permit execution. The software does not reconstruct the missing SeismoMatch processing chronology.

## 05. OpenSees equations and recorder fields

```text
Source matched accelerogram: Acc(g).
ops.timeSeries Path -factor = 9.80665 (kN-m-s).
ops.pattern UniformExcitation(DoF 1 = global X, DoF 2 = global Y).
Absolute floor acceleration X = relative floor X + support ground acceleration X.
Absolute floor acceleration Y = relative floor Y + support ground acceleration Y.
```

Time, accelerations, displacement, drift and force are separate outputs:

| Recorder field suffix | Units | Meaning |
|---|---|---|
| `time_s` | s | Accepted OpenSees time |
| `ground_AccelX_m_s2`, `ground_AccelY_m_s2` | m/s² | Interpolated support acceleration of the actually applied source components |
| `Storey_N_UX_relative_accel_m_s2`, `...UY_...` | m/s² | OpenSees `nodeAccel` relative to support under uniform excitation |
| `Storey_N_UX_absolute_accel_m_s2`, `...UY_...` | m/s² | Nodal relative + support acceleration in the appropriate global direction |
| `Storey_N_UX_m`, `...UY_m` | m | Relative structural floor displacement after gravity displacement baseline |
| `Storey_N_drift_X`, `...Y` | ratio (unitless) | Interstory displacement divided by story height |
| `..._RZ_rad` | rad | Torsional floor rotation |
| `peak_base_shear_X_kN`, `...Y_kN` | kN | Dynamic base shear demand from reaction recorder |
| FVD force/stroke/velocity/energy | kN, m, m/s, kN·m | Native device response; verify sign/orientation and positive dissipation vs signed recorder work |

The acceleration conversion is valid for **uniform two-component ground excitation only**. Do not add ground acceleration for multiple-support/SSI cases without a different kinematic reference.

## 06. FVD/BRB physics parameters are independent of ground-motion scale

- `ViscousDamper` Maxwell uniaxial `K` units `kN/m`, `Cd` units `kN*(s/m)^alpha`, `alpha` unitless, `LGap` metres; model source test/stroke and bridge stiffness explicitly. Official command described by [OpenSees ViscousDamper](https://openseespydoc.readthedocs.io/en/stable/src/ViscousDamper.html).
- For a law `F=Cd*|v|^alpha*sign(v)`, with original coefficient `Cd_mm` in `kN*(s/mm)^alpha`, the kN–m–s conversion is `Cd_m=Cd_mm*1000^alpha`, **NOT automatically ×1000 unless alpha=1**. An illustrative `Cd_mm=700, alpha=.3` would convert to approximately `5560.4 kN*(s/m)^.3`, but this is NOT a verified project calibration or device procurement specification. See `components/sections/devices.py:convert_fvd_cd_mm_to_m`.
- BRB `Steel02` parameters `Fy,E0,b,R0,cR1,cR2,a1..a4`, actual core area, link axis, brace end connections and fatigue limits need test-backed calibration. `corotTruss` axial idealization is not proof of stable full BRB buckling restraint.
- No FVD/BRB material or geometry value in this table is inferred from a record PGA, Z or the source spectral plateau.

Source studies: Korkmaz and Kirçil, *Buildings* (2026), [DOI 10.3390/buildings16040711](https://doi.org/10.3390/buildings16040711); Kolozvari et al. *Engineering Structures* (2023), [DOI 10.1016/j.engstruct.2023.116700](https://doi.org/10.1016/j.engstruct.2023.116700). These are research modeling references, not the actual ETABS rebar/damper specification.

## 07. M0–M6 aggregation outputs

The `variant_comparison.py` response table now distinguishes:
- `maximum` / `M0_maximum`: worst single accepted source-and-orientation case (engineering envelope).
- `response_per_pair_governing`: within each event, conservative maximum of its XY and YX peak response (explicit engineering rule).
- `nbc105_aggregation_rule`: 8 full pairs = AVERAGE; 3–6 = MAXIMUM; exactly 7 requires documented interpretation of ambiguous source text.
- `nbc105_aggregate`, `M0_nbc105_aggregate`: average of eight event-governing demands (for 8 pairs); **not** an average of incomplete or failed runs.
- `nbc105_aggregate_reduction_percent`: baseline comparison based on the above aggregate, kept distinct from worst-case reduction; negative values indicate demand increase.
- `aggregate_is_code_approval=false`: experimental calibration, member acceptance, damping, FVD/BRB and NBC drift must be reviewed separately.

## 08. Source and reference links

- [Stage 35 full code/record workflow](35_SOIL_C_PRIMARY_NLTHA_RUNBOOK.md)
- [Stage 36 run-matrix and paths](36_SOIL_C_M0_M6_RUN_MATRIX.md)
- [Government NBC 105:2025](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf)
- [OpenSees UniformExcitation](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html)
- [OpenSees Rayleigh damping](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/damping/rayleigh.html)

**Status:** Documentation/schema and pure Python tests are not native OpenSees validation. Future model-specific JSON outputs must be retained with source SHA256, code edition and solver version.

# Stage 35 — Soil C primary eight-pair nonlinear time-history analysis (NBC 105:2025)

**Revision:** 2026-11-04. **Engineering stage:** verified source-file metadata and matched waveform spectra; **NOT YET** full nonlinear building analysis or NBC design acceptance. **Do not commit raw earthquake samples, ETABS proprietary model data, or private structural drawings.**

**Study focus:** 3D asymmetric, approximately 25-storey RC dual moment-frame/core-wall system with damped outriggers. Soil Type **C** is the **primary thesis case**; the separately prepared Soil D target is retained only as optional sensitivity. The sixteen supplied `Matched_*.txt` files are already spectrum-matched to **Soil C**. For each earthquake apply its two horizontal components SIMULTANEOUSLY and run both XY and YX in fresh structural domains. Three-dimensional structure does **not** mean a required Z ground-acceleration component without a separate NBC §4.3 vertical-action trigger review.

## 00. Primary references and traceable source assumptions

| Basis | Exact engineering values and use | Source |
|---|---|---|
| NBC §4.1.1 Eq 4.1(1) | Elastic site spectrum `C(T)=C_h(T)*Z*I` | [Government NBC 105:2025 (official PDF)](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf) |
| NBC §4.1.2 Eq 4.1(2), Fig 4-2, Table 4-1 | Soil C `Ta=0.1s,Tc=1.0s,Td=4.0s,alpha=2.5` | Same government code |
| NBC Table 5-2, RC dual system RC shear wall | `R_mu=3.5, Omega_u=1.4, Omega_s=1.2` (check structural-system applicability) | Same government code |
| **User-supplied target workbook** | `Z=0.35, I=1.0`, soil C target `C_h(T)*0.35/1.4`, plateau **0.625g**; code shape verified on workbook 0.0005s and 0.005s grids | `Target Spectra Soil Type C and D for NLTHA.xlsx` — source in PRIVATE thesis folder |
| User's matched spectra | All sixteen uploaded matched `Acc(g)` exports fit the workbook Soil C target with mean of component-average absolute relative 5%-damped PSA differences **3.06%**, evaluated over 120 logarithmic periods in `[0.05,6]s`; component means **2.05–4.75%**, maximum single-period error **56.96%** (Gorkha B) | [Eight-pair measured-source audit](../ground_motions/seismomatch_20261104/README.md), hash-indexed [register](../ground_motions/seismomatch_20261104/matched_component_register.csv); metrics are diagnostics, not NBC tolerance |
| Current code stage | `35_SOIL_C_NLTHA_PREFLIGHT.py` verifies all sixteen registered file hashes, samples, units and periods if supplied; `building_exploratory.py` offers opt-in source identity and physics gates | [Module guide](../source/components/nonlinear_time_history/soil_c_nltha_suite.py.md) |

### Target ordinates in g (not m/s²)

| T (s) | 0.05 | 0.10 | 0.50 | 1.00 | 2.00 | 3.00 | 4.00 | 6.00 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Soil C (primary) | .43750 | .62500 | .62500 | .62500 | .31250 | .20833 | .15625 | .06944 |
| Soil D (secondary, NOT the match target of these 16 files) | .28125 | .31250 | .56250 | .56250 | .56250 | .37500 | .28125 | .15625 |

For Soil C on the code's specified `0 <= T <= 6s`, define `C_h(T)` exactly by Eq 4.1(2): `1+1.5*T/0.1` for `0<=T<.1`; `2.5` for `.1<=T<1`; `2.5/T` for `1<=T<4`; `10/T^2` for `4<=T<=6`. Multiply by `0.35/1.4=0.25` for the recorded ULS matching basis. The workbook's declared parameters must be confirmed against the actual hazard/site documents, and **actual geotechnical Vs30 must establish Soil C** for a building taller than 40m (NBC §4.1.3.1).

## 01. Complete matched earthquake pair register

These are **uploaded actual matched Soil C exports** (not recreated seismic histories). Component A is initially assigned global X and B global Y; YX swaps them. Final spectra use source units `g` and no further SeismoMatch scaling. Each full event contributes **two** analyses per limit state and per structural variant.

| Event | Study classification* | A/B matched PGA (g) | dt record (s) | final end times A/B (s) |
|---|---|---|---|---|
| Gorkha (2015) | Near | .29540 / .36868 | .005 | 322.940 / 322.940 |
| Landers (1992) | Near | .32585 / .35264 | .005 | 48.115 / 48.115 |
| Northridge (1994) | Near | .37937 / .41844 | .020 | 39.960 / 39.960 |
| Kobe (1995) | Near | .26518 / .28105 | .010 | 40.940 / 40.940 |
| Kocaeli (1999) | Near | .34635 / .32502 | .005 | 29.990 / 29.990 |
| Chi-Chi (1999) | Near | .37654 / .34578 | .005 | 89.990 / 89.990 |
| Hector Mine (1999) | Far | .34469 / .33687 | .010 | 45.290 / 45.290 |
| Loma Prieta (1989) | Far | .29403 / .33996 | .005 | 39.975 / 39.980 |

*Six near and two far are the user's research grouping. **The stations' actual rupture distance, directivity, pulse characteristics, event magnitude and site conditions are not established by waveform filenames.** Keep a separate peer-reviewed PEER/USGS station-selection register before publishing claims about near-fault versus far-fault seismic demands.

See [all 16 exact source filenames, hashes, PGA and spectral diagnostics](../ground_motions/seismomatch_20261104/matched_component_register.csv). Recompute SHA-256 for each local source; do not rename a different waveform to match the expected study ID.

## 02. PRE-SCALED time histories — EXACT OpenSees scale

```text
Matched export is already SeismoMatch-processed, units Acc(g).
Additional spectral scale in OpenSees = 1.0 (dimensionless).
g-to-m/s² unit conversion = 9.80665.
Total ops.timeSeries Path -factor = 9.80665 * 1.0 = 9.80665.
X and Y receive the SAME unit conversion, not independent multipliers.
```

**NBC §9.3.2.2(c,d) remains open:** SeismoMatch's **original component scale-factor reports** are not embedded in the waveform exports. A final PGA ratio is **not** that scale factor because time-domain spectral matching changes the waveform. Do NOT claim that the 0.33–3 interval and lower-of-two-component application are independently proven without original SeismoMatch session evidence.

**In the repository:** `source_records_already_scaled=true`, `scale=1.0`, `soil_c_primary_nltha=true`, and a matching `earthquake_event` (e.g. `"Kobe"`). The `Soil_C_Matched_Source_Gate.json` output preserves actual uploaded hashes, XY/YX orientation and any explicit in-memory endpoint policy.

## 03. NBC 105:2025 clause-by-clause check list

| Clause | Exact requirement | Code/evidence decision |
|---|---|---|
| §4.1.1–4.1.2 | Site target Eq 4.1(1), Fig 4-2, Eq 4.1(2) | Actual Soil C target `Z=.35,I=1,Ωu=1.4` source workbook; independent site/hazard validation still required |
| §4.1.3.1 | Site-soil classification / measured Vs30 for tall buildings | **UNVERIFIED** (needs site geotechnical report) |
| §4.3 | Specific vertical-action triggers | Separate five-condition applicability check; horizontal 2-component XY/YX remains 3D |
| §9.3.1.1 | 3D nonlinear model, significant yielding, pinching/degradation/hysteresis | The old `LITERATURE_FRAME_NL_ELASTIC_WALL_V138` run is **EXPLORATORY** and not an approved full nonlinear wall model |
| §9.3.1.2 | Include source gravity loads | Require source load/reaction balance, approved ETABS mapping and preload state |
| §9.3.1.3 | Include P-Delta | Verify actual gravity state and nonlinear geometric transformations, not an assumption from mode success |
| §9.3.1.4 | Inherent torsion | Keep actual asymmetric core stiffness and mass eccentricity in 3D |
| §9.3.1.5 | Hysteretic energy dissipation | Calibrate RC wall/steel/BRB and FVD; check energy sign and Rayleigh damping to avoid double count |
| §9.3.2.1 | At least 3 suitable orthogonal pairs for torsion-sensitive model | 8 pairs present as input candidates; engineering record-selection review not yet independently complete |
| §9.3.2.2(a) | Target `C(T)/Omega_u` | Source workbook Soil C ULS curve checked arithmetically |
| §9.3.2.2(b) | Fit `[Tn90,sqrt(R_mu)*T1]` | **NOT ESTABLISHED** without current independently verified modal participation `T1_X/Y,Tn90_X/Y` |
| §9.3.2.2(c–d) | Scale candidates each 0.33–3; apply smaller common factor for both | Matching already done, but ORIGINAL SeismoMatch factor provenance not supplied |
| §9.3.2.3(a–c) | Two support components in principal axes; repeat swapped XY/YX | Explicit `ops.timeSeries("Path")` and `ops.pattern("UniformExcitation")`, one clean domain per orientation |
| §9.3.2.4 | `dt_analysis<=min(dt_record,T1/100,Tn90,0.01s)` | Stage 35 optional reviewer-supplied T1/Tn90 time-step screen; no assumption that mode 20 period equals Tn90 |
| §9.3.3 | Fewer than seven → maximum; more than seven → mean | **8 pairs → average** per literal source. Exactly 7 not specified by the text and requires reviewer interpretation |
| §5.5.3 / §9.3.3.1 | Interstory drift ULS .025, SLS .006 | Evaluate service and ultimate separately; project wall and frame member deformation acceptance remains separate |
| §9.3.3.2 | Inelastic member actions/deformations under applicable material limits | Calibrated confinement, bar strain, wall shear/compression, frame hinge, damper/BRB demands still require specific checks |

**Physical source caution:** `0.05–6.0s` is the ACTUAL SeismoMatch fit range. With `R_mu=3.5`, `T_upper=1.87082869*T1`; it exceeds 6.0 s whenever `T1>3.20713s`. The **3.526s value in the uploaded workbook is a reference value, not verified current period**; if `T1=3.526s`, the required upper limit is about **6.596s**. The published Figure 4-2 extends to 6 seconds: do not silently extrapolate target or claim code compliance for the unexplained excess. Tn90 is the period associated with the mode at which 90% effective mass is reached, not the arbitrary 20th eigenperiod. Mode counts insufficient to reach 90% require more modal analysis.

## 04. Actual matched file issues: RUN BLOCKERS unless explicitly resolved

1. **Gorkha:** Original samples `6001 @ 0.020s` cover **120.00s**; matched `64589 @ 0.005s` cover **322.94s**. Source-processing provenance cannot be inferred from those files. Stage 35 and the hash-bound runner keep a **hard manual-review gate** before Gorkha is used in thesis-level analysis. A named reviewer and `gorkha_processing_reviewed=true` express reviewed responsibility, not an automatically generated certificate.
2. **Loma Prieta:** Matched A end **39.975s** (7996 samples), matched B end **39.980s** (7997 samples), both dt=.005s. Stage 35 reports this difference; the runner **defaults to rejection** until a named reviewer explicitly approves `loma_end_policy="append_zero_reviewed"`. This inserts one zero acceleration at the end of the **shorter runtime array only**; the original file bytes, filename and hash remain unchanged. Do not silently change the history or assert that padding is the only physically acceptable approach. Document the chosen end-time policy in thesis methods.

For accepted cases, preserve separately: original source bytes, source SHA256, any numerical endpoint adjustment, actual record dt and full physical duration, both applied path factors, solver `dt`, and failed/accepted substeps.

## 05. Windows + Spyder preflight (independent of OpenSees native binary)

From repository root:

```powershell
python 35_SOIL_C_NLTHA_PREFLIGHT.py --matched-dir "D:/Thesis/Target Spectra/Soil Type C Matching 0.05-6/Matched" --output "D:/Thesis/NLTHA_Audits/35_Soil_C_Matched_Inputs.json"
```

For real modal evidence (replace ALL following illustration-only periods):

```powershell
python 35_SOIL_C_NLTHA_PREFLIGHT.py --matched-dir "D:/Thesis/Target Spectra/Soil Type C Matching 0.05-6/Matched" --output "D:/Thesis/NLTHA_Audits/35_Soil_C_Modal_Screen.json" --t1-x 2.8 --t1-y 3.1 --tn90-x 0.12 --tn90-y 0.13 --analysis-dt 0.005
```

Exit status `0` means registered source hash and pair timing checks have no failures; **not** a design pass. Exit `3` indicates Loma timing review, and `2` indicates source-file mismatches or missing files. Review the actual JSON for all listed cases. The preflight **never** edits or copies the waveform samples.

## 06. Building runner config: research vs accepted thesis intent

The existing `components/nonlinear_time_history/building_exploratory.py` remains an **EXPLORATORY** analysis entry point; no automated code commit can make unvalidated materials experimentally credible.

```json
{
  "model_folder": "D:/Thesis/OpenSees_Export",
  "output_dir": "D:/Thesis/NLTHA_Results/M0/Kobe/ULS",
  "soil_type": "C",
  "soil_c_primary_nltha": true,
  "earthquake_event": "Kobe",
  "source_records_already_scaled": true,
  "x_path": "D:/Thesis/Records/Matched_RSN1120_KOBE_TAK000.txt",
  "y_path": "D:/Thesis/Records/Matched_RSN1120_KOBE_TAK090.txt",
  "scale": 1.0,
  "limit_state": "ULS",
  "orientations": ["XY","YX"],
  "diagnostic_excitation": "XY",
  "dt_s": 0.005,
  "nonlinear_walls": true,
  "duration_s": null,
  "analysis_intent": "RESEARCH_DIAGNOSTIC",
  "nbc105_2025_design_evidence": null
}
```

**Example path note:** Browser downloads may append `(1)` to source filenames. The gate uses actual file SHA256 to identify the registered A/B pair, irrespective of superficial download naming differences; any different waveform is rejected. The example source names above are placeholders; point them to the correct private local files and check the hashes.

Set `analysis_intent="THESIS_NLTHA"` **only** after the actual validated nonlinear core model is activated, independently checked frame reinforcement CSV is supplied, approved modal/matching source evidence exists, source selection is reviewed and appropriate damper/brace models are validated. The code now blocks thesis intent with elastic core walls, a truncated duration, diagnostics-only damping, missing reinforcement register, missing modal source evidence or absent paired XY/YX. Even when it runs, experimental validation and NBC acceptance are not automatically proven.

The `nbc105_2025_design_evidence` object must include reviewed `t1_x_s,t1_y_s,tn90_x_s,tn90_y_s,r_mu,omega_u,factor_x,factor_y,target_spectrum_kind,spectrum_match_evidence_sha256,ground_motion_selection_reviewed`, per `nbc105_2025_audit.py`. The original factors belong to the **SeismoMatch session logs**; they are not the OpenSees additional factor `1.0`.

## 07. Exact OpenSees commands and parameter meanings

```python
import openseespy.opensees as ops
# Actual 3D RC building is assembled from validated source data.
ops.model("basic","-ndm",3,"-ndf",6)  # 3D; 6 DOF/node for frame model
# Apply project gravity G+appropriate sustained Q, mass and diaphragms;
# check reactions, geometric transformations, P-Delta; freeze gravity.
# ops.loadConst("-time",0.0) when correctly preloaded.

# X (A) + Y (B), source ordinates in g, already spectrum-matched to Soil C:
ops.timeSeries("Path",900001,"-dt",dt_record,
               "-values",*matched_A_in_g,"-factor",9.80665)
ops.timeSeries("Path",900002,"-dt",dt_record,
               "-values",*matched_B_in_g,"-factor",9.80665)
ops.pattern("UniformExcitation",900001,1,"-accel",900001)  # X DOF 1
ops.pattern("UniformExcitation",900002,2,"-accel",900002)  # Y DOF 2
# YX is a SEPARATE model construction, swapping B -> DOF 1, A -> DOF 2.
# No Z ground acceleration pattern for this two-horizontal-component case.

# Example integration/test choices (research starting points only):
ops.constraints("Transformation")
ops.numberer("RCM")
ops.system("UmfPack")
ops.test("NormDispIncr",1e-7,30,0)  # tolerance in model displacement units
ops.algorithm("Newton")
ops.integrator("Newmark",0.5,0.25)
ops.analysis("Transient")
# Use reviewed dt_analysis <= NBC modal/digitization bound;
# successful ops.analyze(1,dt_analysis) must be checked every step.
# Reconstruct in a new clean domain between earthquake cases.
```

**Exact parameters that are NOT numerically established from ground motions alone:** ConcreteCM unconfined/confined parameters, SteelMPF calibration, FSAM wall fibers, actual core openings, ETABS bar/tie spacing, RC frame hinges, FVD `K,C_d,alpha`, BRB `Fy,K,b`, nonlinear damping coefficients, rigid diaphragm coupling, model mass, tangent stiffness solver, and per-member deformation limits. Do not copy nominal values from a research paper as if they were the as-built ETABS project schedules.

Primary reference: [E-SFI-MVLEM-3D](https://doi.org/10.1016/j.engstruct.2023.116700) (Kolozvari, López and Massone, 2023); [PEER 2015/12 RC shear-flexure](https://peer.berkeley.edu/publications/2015-12) (Kolozvari, Orakcal, Wallace); [Official OpenSees Path](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/timeseries/pathTimeSeries.html); [UniformExcitation](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html); [Rayleigh damping](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/damping/rayleigh.html).

## 08. Thesis analysis plan and acceptance sequence

| Run class | States | Source cases | Purpose |
|---|---|---|---|
| ZERO / X / Y short probes | ULS initially | Selected Kobe or other real record | Fix current X-direction first-step wall instability, not thesis earthquake evidence |
| One full-record pilot | ULS, then SLS | Kobe A/B, XY and YX | Convergence, dt refinement, P-Delta, energy and recorder consistency |
| Eight-pair nonlinear campaign | ULS and SLS separately | 8 events × 2 orientations = **16 per state** | Full paired earthquake demand evidence |
| M0–M6 controlled comparison | ULS and SLS | 7 variants × 16 cases × 2 states = **224 analysis cases** | Outrigger/damper response comparison with identical input records, mass, geometry and source definitions |
| Soil D extension | Optional after C validated | Separately matched D source files | Independent sensitivity study; DO NOT reuse C matched sources as if matched to D |

For the 8-pair results use the **same eight events** for each M0–M6 alternative. Per NBC §9.3.3 (>7 pairs), the prescribed aggregation is the **mean** across the corresponding response demands, respecting paired XY/YX and worst orientations as interpreted in the engineering evaluation method. Do not average over incomplete/nonconverged histories as if they were successful. Report peak transient drifts, roof displacement, base shear, residual drift, wall and frame inelastic demands, floor acceleration (include support-relative vs absolute difference), FVD force/velocity/stroke/energy and BRB deformation/energy independently, and retain actual case hashes.

The modern OpenSees procedure must also preserve failed solver states, accepted adaptive substeps, and an explicit convergence/refinement demonstration. Initial `0.005s` pilot success is never proof of full-duration convergence.

## 09. Mandatory unresolved items before claiming NBC acceptance

- Source site geology/Vs30 and record selection by magnitude/fault mechanism/distance.
- SeismoMatch scaling session's actual component factors (not recoverable from matched PGA).
- **Current** modal `T1_X,T1_Y,Tn90_X,Tn90_Y` in ULS and SLS model states and a defensible fitting target beyond 6s if required.
- Gorkha processing provenance and Loma Prieta final one-sample endpoint rule.
- Complete actual ETABS member reinforcement and nonlinear wall element setup with openings, shear-flexure/torsional calibration; resolve the X-direction first-step core wall failure.
- FVD/BRB native recorders, force sign/energy and device calibration, nonlinear damping model, 3D core torsional checks, full duration successful transient and time step refinement.
- Independent member acceptance and NBC drift checks, stage-by-stage documented in linked `.json`, `.csv` and source-specific `.md` files.

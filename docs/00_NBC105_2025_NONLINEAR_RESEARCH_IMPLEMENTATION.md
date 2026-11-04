# NBC 105:2025 nonlinear time-history — verified references and implementation log

**Governing source:** Government of Nepal / DUDBC, *NBC 105:2025, Seismic Design of Buildings in Nepal (Second Revision)*, authoritative publication: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf . The DUDBC building-code catalog is https://dudbc.gov.np/pages/building-code/ .

**Scope and research ethics:** This reference is a primary published building standard, not a claim that the 25-storey asymmetric RC core and damped-outrigger model has passed design requirements. Never substitute literature specimen reinforcement, copy reported FVD percentage reductions, or change source geometry just to obtain convergence.

## 1. Grounded NBC 105 code matrix

| Clause | Verified published text / engineering rule | Software behavior | Remaining evidence |
|---|---|---|---|
| §9.3.1.1 | 3D nonlinear model with significant post-elastic yielding, degradation and hysteretic pinching; at least bilinear behavior | Materials and wall models require independent calibration | A Concrete01 law alone does not establish bar buckling, degradation and pinching in a wall |
| §9.3.1.2 / §5.2 | Gravity actions must be applied to model | Existing model preload and source/load audit retained | Confirm load combinations, pattern self-weight, complete reactions and ETABS matching |
| §9.3.1.3 | Include P-Delta | Existing nonlinear assembly path checked separately | Demonstrate geometric transformations and gravity force state in each ULS/SLS run |
| §9.3.1.4 | Include inherent torsion from center-of-mass and center-of-rigidity offsets | Documented source mass and diaphragm check | 3D core torsion and accidental-eccentricity scenarios still require review |
| §9.3.1.5 | Include structural hysteretic dissipation | No material/damper numerical approval inferred | Calibrate RC/BRB hysteresis; evaluate Rayleigh damping double counting |
| §9.3.2.1 | >=3 orthogonal motion pairs for torsion-sensitive 3D NLTHA | Existing M0–M6 matcher enforces >=3 distinct pairs for ULS and SLS | Verify seismological suitability, hazard level and unique original PEER pair IDs |
| §9.3.2.2(a) | Elastic site spectrum C(T) divided by ULS overstrength factor Omega_u is target | NEW evidence gate requires an explicit *target_spectrum_kind* | This code does NOT calculate site spectrum or prove spectral matching: independently review target ordinates |
| §9.3.2.2(b) | Fit interval Tn through sqrt(R_mu) T1 | NEW gate computes two axis-specific windows | Supply T1 and Tn90 from reviewed effective modal participation; do NOT use the 20th period blindly |
| §9.3.2.2(c) | Independent scale factors must lie 0.33..3.0 | NEW validation rejects out-of-range component factors | Records failing limits must be replaced instead of clipped |
| §9.3.2.2(d) | For orthogonal pair use the LOWER of two component scale factors on BOTH motions | NEW common scaling guard; unchanged XY/YX source mapping | Verify that component factors were fitted independently and applied once |
| §9.3.2.3(a–c) | Apply scaled motions at supports; orthogonal principal axes; perform second analysis with reversed components | Optional strict gate requires XY and YX | Confirm UniformExcitation support assumptions, model orientation and case completion |
| §9.3.2.4 | Integration dt <= digitized dt, T1/100, Tn90 and 0.01 s | NEW time-step validator checks the minimum of both plan-axis bounds | Modal report must show 90% translational mass basis before a code-claim |
| §9.3.3 | Text: for **less than seven**, maximum response; for **more than seven**, mean | NEW pure helper returns ambiguity for EXACTLY 7 | The literal clause does not prescribe exactly seven. Get authorized interpretation; no silent 7-record policy |
| §5.5.3 | Interstory drift ratio 0.025 ULS and 0.006 SLS | Existing performance screen retains the literal values | §9.3.3.1 refers to §5.6 (accidental eccentricity), a cross-reference discrepancy; independent code interpretation needed |
| §9.3.3.2 | Member inelastic deformation demands shall not exceed limits in appropriate material standards | Existing member criteria default to NOT REVIEWED | Supply documented project-specific axial/load state, strain/rotation, steel/wall/BRB/device acceptance criteria |

**Source nuance:** The published §9.3.3 has no explicit rule for *exactly seven* motions. It would be incorrect to silently assume the familiar practice from other standards. The utility labels this case `REVIEW_REQUIRED_EXACTLY_SEVEN_NOT_DEFINED_IN_2025_TEXT`. For thesis research you may still report maximum and mean descriptively, but do not label one as the mandatory NBC aggregation until reviewed.

## 2. Implemented code (current repository)

- `components/nonlinear_time_history/nbc105_2025_audit.py`: pure validated functions `nbc105_time_step_limit`, `paired_ground_motion_scale`, `scaling_period_range`, `response_aggregation_rule` and `validate_nbc105_design_metadata`.
- `components/nonlinear_time_history/building_exploratory.py`: fixes premature reference to `scale` in SHA256 fingerprint construction; optional strict metadata input `nbc105_2025_design_evidence` emits `NBC105_2025_NLTHA_Input_Screen.json`. If the evidence is omitted, the run is research-only and the report says NOT EVALUATED.
- `tests/verify_nbc105_2025_nltha.py`: solver-free tests cover limits, insufficient pairs, strict XY/YX, lower scale, periods, missing evidence and exactly-seven ambiguity.
- `.github/workflows/nltha-quality.yml`: executes new tests and syntax checks on Python 3.12.

### Example additional RunConfig key (NOT verified building evidence)

The following is only a *schema illustration*, not your earthquake's actual modal period or target fit:

```json
{
  "nbc105_2025_design_evidence": {
    "t1_x_s": 3.6,
    "t1_y_s": 3.2,
    "tn90_x_s": 0.15,
    "tn90_y_s": 0.12,
    "r_mu": 4,
    "omega_u": 1.5,
    "factor_x": 1.8,
    "factor_y": 1.5,
    "target_spectrum_kind": "ULS_ELASTIC_SITE_C_OVER_OMEGA_U",
    "spectrum_match_evidence_sha256": "REPLACE_WITH_ACTUAL_64_HEX_SHA256",
    "ground_motion_selection_reviewed": false
  }
}
```

Do NOT copy this example into a production analysis. Insert measured/reviewed data from your own modal results, target spectrum and record-selection report; set the approval flag only after independent review. The top-level `scale` must equal the smaller of the pair's independently computed factors.

## 3. Official OpenSees documentation relevant to active subsystems

| Source | Verified capability | Project improvement and restriction |
|---|---|---|
| https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html | E-SFI: four counterclockwise nodes, 24 DOF, one width/thickness/FSAM tag per macrofiber; optional CoR/ThickMod/density; recorders globalForce, Curvature, ShearDef, RCPanel | Verify panel winding, widths and fiber regions against source core; never assume a nonfinite force after solver failure is the initiating wall defect |
| https://opensees.github.io/OpenSeesDocumentation/user/manual/model/damping/rayleigh.html | Rayleigh alphaM, betaK, betaKInit, betaKcomm; replaces previously assigned damping | Document eigenmode choices, nonlinear damping basis and no inadvertent extra device damping |
| https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/TwoNodeLink.html | Two-node element, local axis and optional doRayleigh; damping exclusion default | Verify actual FVD installation axis, direction, device force sign and native recorder on the specific binary |
| https://openseespydoc.readthedocs.io/en/stable/src/ViscousDamper.html | Maxwell spring K with nonlinear viscous dashpot Cd and exponent alpha; integration control options | Calibrate using measured force/stroke/velocity, including kN–m–s dimensional conversion; one demo waveform is not experimental fit |

## 4. Recent research triage — connected to specific code gaps

| Source | Published findings / problem | What to add to research rather than silently changing physics |
|---|---|---|
| Waezi & Dhakal (2026), University of Canterbury, DOI https://doi.org/10.26021/16632 | An amended SFI-MVLEM tangent formulation includes axial-shear coupling missing in its original formulation | PRIORITY P0: compare original and refined implementations on identical isolated wall benchmark; local custom build is not available by default in your Windows OpenSeesPy |
| Zhang et al. (2024), Engineering Structures, DOI https://doi.org/10.1016/j.engstruct.2024.118774 | Nonlinear RC wall response under coupled axial tension and cyclic lateral loading; comparison with test specimens | PRIORITY P0: isolate core wall panels under negative and positive axial cycles; do not assume a new material class exists in the installed binary |
| Kolozvari et al. (2023), Engineering Structures 294, 116700, DOI https://doi.org/10.1016/j.engstruct.2023.116700 | E-SFI-MVLEM-3D formulation and validation | PRIORITY P0: exact node winding, FSAM cards, boundary/web reinforcement, openings and wall joint tests |
| Ulucan et al. (2026), Buildings 16(21), 4188, DOI https://doi.org/10.3390/buildings16214188 | NLTHA comparisons for FD/FVD on RC school configurations | PRIORITY P1: compare energy, residual drift, acceleration and damper force/stroke, using consistent source mass/geometry and no paper-reduction percentages |
| APDVFD study (2026), Engineering Structures, DOI https://doi.org/10.1016/j.engstruct.2025.121846 | Newly specialized parallel double-stage viscous damper implementation | NOT automatically applicable to conventional Maxwell FVD installed in the thesis; avoid adding this model without an actual APDVFD specimen/design |

Publisher content may be paywalled; bibliographic/abstract findings are not a license to invent specimen curves or member detailing. ResearchGate reuploads are secondary and should not replace original author PDFs, official OpenSees sources and peer-reviewed publisher records.

## 5. Remaining project verification stages

1. Review the exact source ETABS export, actual longitudinal/tie reinforcement, ConcreteCM/SteelMPF core and web properties, FVD/BRB test cards and gravity/mass.
2. Reproduce the X-only at t=0.005-s wall failure in a fresh domain; record the earliest actual solver failure and compare zero-motion and single-wall cyclic tests.
3. Independently calculate target C(T)/Omega_u, modal participation and period range; verify ground-motion spectra and lower pair scaling.
4. Check time-step convergence by halving dt, mesh refinement, response energy signs and material/damper hysteresis in each accepted full-duration case.
5. Run at least 3 suitable motion pairs in BOTH orientations for each state; retain records with all scenario, model and response hashes.
6. Compare M0–M6 under controlled source geometry/mass and source records, then apply engineering/member acceptance criteria. Distinguish research comparison from NBC design approval.

**Testing status:** This update adds pure-Python checks and does not claim complete NLTHA convergence or test-calibrated structural acceptance.

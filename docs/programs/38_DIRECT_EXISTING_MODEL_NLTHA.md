# Stage 38 — Direct NLTHA from the existing OpenSees thesis model (literature-based research baseline)

**Status:** operational source/solver orchestration, NOT an assertion that the user's nonlinear 25-storey building has converged or been experimentally calibrated. **Owner:** `components/nonlinear_time_history/`. **Primary single-file runner:** `tools/run_existing_nltha.py`. **Engineering source-of-truth:** `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, and NBC105:2025. This is intentionally **not** a new ETABS converter or an independently invented model.

## 1. Thesis intent and source identity

**Research question:** time-history assessment of damped/conventional outrigger systems M0–M6 in an asymmetric plan RC high-rise with shell wall openings. Use the user's **already exported** `OpenSees_Complete_Nonlinear_Model.py`, the corresponding `OpenSees_Complete_Model_Data_V118.json`, `OpenSees_Complete_Model_Config_V118.json`, and the *current* repository builder `components/model/assembly.py`. The runner uses `building_exploratory.py::run` which itself calls `build_complete_model(... mode='nonlinear', preload=True, research_profile='LITERATURE_BUILDING_NL_V161')`; it does not create substitute geometry.

**Uploaded local evidence inspected (2026-11-22):** MESH_04 has 11,072 nodes, 3,300 beams, 450 columns, 112 braces, 7,000 floor shell elements, 3,400 wall shell elements. MESH_08/MESH_16 are alternate discretizations; do not switch mesh between variants without recording it as an independent convergence study. Current source configuration has `nonlinear_materials_file=''`, `nonlinear_wall_fsam_tags={}`, `nonlinear_parameters_reviewed=false`. It is therefore capable of *paper-baseline research probes*, **not** justified project-specific nonlinear constitutive acceptance. The published source model also records 76 mapped supports, 32 actual foundations + 44 wall-mesh points. **Do not use 76 as foundation reactions.**

**No confidential file relocation to GitHub:** project EDB, native story/geometry JSON, reinforced design drawings, matched acceleration files, absolute local Windows paths and design workbooks stay on the research workstation. Run output remains in an isolated user-selected folder, not this public repository.

## 2. Authoritative nonlinear sections and academic attribution

| Original source section | Solver section | Literature model | What is assumed versus verified |
| --- | --- | --- | --- |
| `Beam 600*800` | `RC_BEAM_600x800_FIBER` | 3D fiber section with nonlinear concrete and reinforcing-steel uniaxial materials; forceBeamColumn/beam integration | Exact geometry from source. Current bar sizes/count, confinement, steel grade are **illustrative template inputs**, not source reinforcement. |
| `Col 1100*1100` | `RC_COLUMN_1100x1100_FIBER` | Same fiber-section approach, 3D axial–biaxial bending and necessary torsional stiffness | Source size only verified; flexural cyclic, axial ratio, confinement, hinge regularization must be checked |
| `Col 1250*1250` | `RC_COLUMN_1250x1250_FIBER` | Same fiber section approach | Same source/research distinction |
| `350*350*16 SHS` | `SHS_350x350x16_STEEL_FIBER` / connected ordinary brace idealization | Existing source steel section + current brace law | Pin-ended ordinary steel diagonal transfer is provisional; **not** a qualified BRB or calibrated connection |
| `Wall 600` | nonlinear `E_SFI_MVLEM_3D` panel with `FSAM` | Kolozvari et al. (2023), shear-flexure and axial interaction | Source wall 600 mm, source M45 material geometry. FSAM web/boundary rho, ConcreteCM/SteelMPF and local axes are literature-derived **research transfers**, not actual construction schedule |

Source count and source original names are read at run time from local JSON. No hardcoded M0/M4 geometry or artificial replacement section dimensions. `NLTHA_Literature_Section_Basis.json` explicitly inventories every mapped section, source wall material, 3D fibers and uncalibrated assumptions; original source and model SHA256 are written into independent local manifests. **Source ETABS M45 is not automatically the same as the illustrative M35/Fe550 frame fiber card**. Do not silently relabel a paper's concrete-strength parameter or rebar to claim equality.

**Formulation sources (not proof of this building's calibration):**
- **R01:** Kolozvari, Orakcal & Wallace, *Shear–Flexure Interaction Modeling of Reinforced Concrete Structural Walls and Columns under Reversed Cyclic Loading*, PEER Report 2015/12, specifically the paper's appendix material constants and ConcreteCM, SteelMPF, FSAM cyclic panel formulations. https://peer.berkeley.edu/publications/2015-12 ; https://peer.berkeley.edu/sites/default/files/webpeer-2015-12-kristijan_kolozvari_kutay_orakcal_john_wallace.pdf
- **R02:** Kolozvari, López & Massone, *Efficient three-dimensional shear-flexure interaction model for reinforced concrete walls*, Engineering Structures 294 (2023) 116700; https://doi.org/10.1016/j.engstruct.2023.116700 ; https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html
- **R03:** Kolozvari et al., *New OpenSees models for simulating nonlinear flexural and coupled shear-flexural behavior of RC walls and columns*, Computers & Structures 196 (2018), 246–262; https://www.sciencedirect.com/science/article/pii/S0045794917303693
- **R10:** Nepal NBC 105:2025, especially §5.2 and §9.3; https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf
- Reference: https://github.com/nirajkyadav/Framework_for_Seismic_Assessment_of_RC_Buildings (MIT). Its nonlinear RC frame/time-history structure informs run sequencing; its arbitrary fallback time steps, 2020 NBC and low-rise reinforcement details are **not** transplanted.

### Why the papers cannot set every project rebar automatically

PEER specimen bars, axial loads, confinement, cyclic degradation, mesh widths, crack/shear transfer, and steel transition laws were established for particular measured specimens. In this application the original model reports RC member physical dimensions but does **not** provide an approved building-specific bar schedule, wall-boundary confinement and FSAM regions. This stage uses an explicitly labeled **research baseline** so the native software can be diagnosed, with separate later verification against project drawings, ETABS design and wall specimen tests. Calibration of the actual physical building is not asserted. `THESIS_NLTHA` qualification remains blocked until reviewed materials are supplied, even if an exploratory whole-building record completes.

## 3. Required local source files and internal handoffs

All six are **required and SHA-verified** by `source_model_handoff.py::stage_existing_model_sources`: `OpenSees_Complete_Model_Data_V118.json`, `OpenSees_Complete_Model_Config_V118.json`, `OpenSees_Complete_Export_Report_V118.json`, `OpenSees_Load_Conversion_Audit.json`, `OpenSees_Source_Model_Metadata_V118.json`, and **`OpenSees_Element_Connectivity.json`**. Optional original story masters, scenario overrides and element map are transferred without changes.

**Fixed source-disconnect defect:** legacy `building_exploratory.py` copied geometry/config but omitted `OpenSees_Element_Connectivity.json` before the solver attempted primary-32 physical-support selection. The stage now copies it without changing original files. **Fixed reaction audit defect:** record base shear using `build_complete_model`'s **actual returned 32 solver support tags**, validate with the shared `support_case_contract.require_runtime_support_case`; never sum the 76 exported source support rows. `NLTHA_Active_Foundation_Supports.json` records selected case/tags and explicitly marks native wall edge/MPC transfer **NOT_VERIFIED**. These changes DO NOT resolve the historical 768.045 kN per-support ETABS–OpenSees reaction discrepancy.

**Load-purpose firewall:** full gravity **benchmark** `1.0D+1.0L`, NBC 105:2025 Table5-1 **seismic weight** and production nonlinear **P-Delta initial-state combinations** are independent. Source config might have reduced live factors; `AS_CONFIGURED` is NOT interchangeable with a verified full-gravity test, nor proof of required signed EQ initial P-Delta. A native research run must label source gravity assumptions and cannot be upgraded to code-compliant response history from numerical convergence.

## 4. Running NLTHA immediately on the existing exported model

From the **current main GitHub repo checkout** in the user's Windows/Spyder Python 3.12 `etabs_env312` environment with a working native OpenSeesPy installation, run:

```powershell
python tools/run_existing_nltha.py `
  --model-folder "D:\Thesis\OpenSees_Exports\CURRENT_MODEL_RUN" `
  --x-path "D:\Thesis\GroundMotions\Matched_Kobe_A.txt" `
  --y-path "D:\Thesis\GroundMotions\Matched_Kobe_B.txt" `
  --output-dir "D:\Thesis\OpenSees_Exports\CURRENT_MODEL_RUN\07_NONLINEAR_TIME_HISTORY\Kobe\ULS\PAPER_BASELINE" `
  --event Kobe --variant-id UNVERIFIED --limit-state ULS --dt-s 0.005
```

The model, motion and output paths above are **illustrative placeholders**, not claimed existing on disk. Replace with matching real local files. The script **executes** the same local original source geometry through the repo's existing research nonlinear builder. Default is the **full motion duration** and both **XY/YX** in separate fresh OpenSees model builds. Since these sections use PEER source-transfer assumptions, even a numerical full record is **`COMPLETED_EXPLORATORY_RECORD`**, NOT `THESIS_NLTHA` material acceptance.

For a lightweight read-only input/section audit (does not solve):

```powershell
python tools/run_existing_nltha.py --model-folder "D:\Thesis\OpenSees_Exports\CURRENT_MODEL_RUN" --x-path "D:\Thesis\GroundMotions\Matched_Kobe_A.txt" --y-path "D:\Thesis\GroundMotions\Matched_Kobe_B.txt" --output-dir "D:\Thesis\NLTHA_Check\Kobe" --event Kobe --variant-id UNVERIFIED --check-only
```

For an intentionally **truncated diagnostic** transient, append `--trial-duration-s 0.02`. The result status explicitly says `EXPLORATORY_TRUNCATED_TRIAL_ONLY`, and it must **never** be treated as a complete earthquake history.

Current default `dt_s=0.005 s` is only a preliminary selection and is rejected if greater than the actual matched record's digitization interval. A modal `T1/100` or `Tn` smaller than this also governs; confirm NBC §9.3.2.4 with actual nonlinear modal values. No auto doubling/re-matching or secondary scaling: already spectrum-matched inputs have nominal additional scale `1.0` and require independent original SeismoMatch factor evidence. Actual source waveforms must be available and distinguishable by SHA before an executable case begins.

## 5. Full analysis sequence and outputs

1. **Source and paper section provenance:** compute source/config/connectivity hashes; verify original 32 support tags and all four source frame-to-fiber section mappings; count and audit shear-wall panel thickness/material. Compare explicit assumed literature cards against actual project grade/drawings.
2. **Matched record preflight:** two actual, distinct source horizontal components, sampling interval, source SHA, input unit `g` versus `m/s²`, source SeismoMatch scaling and XY/YX pair orientation. No invented sample, no double scale.
3. **Isolated nonlinear model:** copy source files read-only and reconstruct existing beams/columns/SHS, diaphragms, RC slab shells, wall opening shells and E-SFI wall macro-fibers. Check `OpenSees_Complete_Element_Map_V118.json` when diagnosing historical tag 110280/112778.
4. **Gravity and foundation handoff:** solve and freeze gravity with `loadConst('-time',0)`, preserve P-Delta design-basis qualification separately, verify actual physical 32 solver support tags, and snapshot model/element identity. Never fix 44 shear-wall mesh points independently.
5. **Initial nonlinear modes and damping:** solve modes from the fresh gravity-preloaded nonlinear tangent, inspect 90% X/Y participation, Rayleigh calibration and potential FVD double counting. No global damping override to hide first-step singularities.
6. **Bidirectional nonlinear response:** build a **fresh** OpenSees model for XY and another for YX, apply simultaneous two-component matched input, 3D Newmark integration and existing bounded Newton/line-search/Krylov/ModifiedNewton + adaptive subdivision. Use actual accepted step clock and finite snapshot guards.
7. **Engineering recorder outputs:** per accepted step store displacements, interstory drift, signed base shear, acceleration, floor torsion, tracked force/deformation, wall panel stress–strain where supported, device stroke and dissipated energy where modeled, total input/strain/damping/device energy when enabled, plus convergence algorithm/substep statistics. Missing channels are missing, not zeros.
8. **Failure evidence:** first-step wall/connected node, last accepted time, element map, original solver error, failed-stage JSON; do **not** classify postfailure NaN localForce as initiating cause. Mandatory ZERO/X/Y/XY/YX clean-domain A/B probes for the historic X-wall nonfinite if whole model fails.
9. **Full record gate:** verify valid monotonically increasing accepted states to exact requested motion end, independent input/element audit, XY/YX case identities, source hashes and no truncated trial. Numerical completion is not model, experimental or NBC design acceptance.
10. **Thesis comparisons:** repeat per independently exported **M0–M6** variant with identical mass, source, case and material assumptions except controlled outrigger/damper configuration. The intended 224 analyses require independently executed case manifests and full duration for each. Draw performance comparisons only from scientifically qualified, same-basis results.

### Output structure (per run)

```text
07_NONLINEAR_TIME_HISTORY/
  <Event>/<LimitState>/PAPER_BASELINE/
    DIRECT_EXISTING_NLTHA_SOURCE_AND_SECTION_BASIS.json
    DIRECT_EXISTING_NLTHA_STATUS.json
    NLTHA_Literature_Section_Basis.json
    NLTHA_Isolated_Model_Source_Hashes.json
    isolated_model/                # exact staged source files, never GitHub
    NLTHA_Wall_Geometry_Preflight.json
    NLTHA_Wall_Opening_Preflight.json
    SeismoMatch_Source_Provenance.json
    XY/
      NLTHA_Active_Foundation_Supports.json
      Nonlinear_Initial_Modal_Audit.json
      Building_Nonlinear_history.csv
      Accepted_History_Completion_Gate.json
      First_Step_Failure_Evidence.json       # if generated
      Case_Summary.json
    YX/
      ...                                    # independent solver model
    Exploratory_Summary.json
    INCOMPLETE.json                          # if a failure occurs
```

### Evidence acceptance table

| Evidence | Required status | What does *not* prove it |
| --- | --- | --- |
| Software syntax + deterministic unit tests | CI passed at exact PR head | Source merely imported |
| Solver progressed through a complete digitized record | Two accepted-history duration gates for XY/YX | Return code zero for a single 0.005 s step |
| Nonlinear RC wall and fiber sections calibrated | Material coupon/panel tests and actual bar schedules | PEER specimen card copied |
| 32 foundation reactions equivalent to ETABS | Direct 32-location joint or common six-DOF wall-base cut comparison | Equal global FZ reactions |
| Spectral and NBC105:2025 compliance | Verified source scale, proper gravity/P-Delta, damping and code-specific response statistic | An exploratory full record |
| Thesis M0–M6 comparison | All case-matrix results source/solver matched and independently reviewed | A single model/record completed |

## 6. Current execution constraint and explicit next local action

As of this change, the conversation's uploaded MESH source ZIPs contain the model data and Python entry points, **but none of the original 16 matched horizontal waveform files**. The current isolated execution environment also has **no installed `openseespy` native solver** and no running ETABS. Thus this session can inspect/verify section assignments, implement source/solver handoffs and test the runnable orchestration in CI; it **cannot truthfully deliver your physical Kobe X/Y, 25-storey NLTHA curves or a resolved first-step wall failure**. The full local run is directly invoked by the command above when the real waveform and native solver are present; blocked cases are recorded as `NATIVE_NLTHA_INCOMPLETE`, not fabricated success.

## Native run completion conditions — evidence gate update (2026-11-22)

For the first full M0/Kobe/ULS case, use a new output directory containing no previous trial/failure. Launch `tools/run_existing_nltha.py` with the **actual** complete six-file OpenSees export and two matched PEER/SeismoMatch horizontal components. A path or model filename alone is never a source-material calibration, SeismoMatch log, site classification or ground-motion acceptance.

On actual completion, inspect `DIRECT_EXISTING_NLTHA_STATUS.json` and `independently_checked_case_histories`. A completed numerical screen requires both XY/YX cases and for **each** the on-disk:
- `Case_Summary.json`, `Accepted_History_Completion_Gate.json`, `Building_Nonlinear_history.csv`;
- full duration, finite response values, strictly increasing accepted time from 0 through exact record end, counts matching gate;
- original source model fingerprint and identical registered component pair/limit state/model identity;
- complete native execution without any failed/written-over previous case.

A missing/corrupted/short response **fails closed** despite a positive runner return. The full-diagnostic output status is not a thesis engineering PASS. The 0.005-s Kobe X-wall obstacle, one-to-one 32-support gravity reaction mismatch, actual M45/steel detailing, core boundary/web FSAM, hysteresis, FVD, SeismoMatch provenance and NBC 105:2025 §9.3.3 remain mandatory distinct validations. The previous connectivity staging omission was corrected in current `building_exploratory` on `main`; this change does not duplicate staging or rebuild the user model.

**Scientific basis for acceptance separation:** NBC 105:2025 §§9.3.1–9.3.3; NIST GCR 17-917-46v1 (2017) `https://nvlpubs.nist.gov/nistpubs/gcr/2017/NIST.GCR.17-917-46v1.pdf`; Kolozvari, López and Massone (2023), DOI `10.1016/j.engstruct.2023.116700` for 3D shear-flexure nonlinear wall idealization; OpenSees `E_SFI_MVLEM_3D` official documentation for element node/recorder conventions.

- Stage 38's default full-record research config now requires the registered Soil-C earthquake components by their original byte SHA, not merely matching file names or different nonempty files. The audit is executed before source model load and the native gravity run; the X/Y pair must be registered in its original A/B order, while solver XY/YX rotations remain separate. A malformed, replaced, mislabeled or unreviewed Gorkha/Loma pair fails closed rather than producing a misleading first successful case.


## 7. Final integration and first-case source validation (2026-11-22)

One canonical numbered entry point now exists: `python 38_DIRECT_EXISTING_NLTHA.py --model-folder ... --x-path ... --y-path ... --output-dir ... --event Kobe --variant-id UNVERIFIED`. It is only a thin alias to the same direct module used by `python tools/run_existing_nltha.py`. The physical model is neither rebuilt differently nor duplicated. All current local example paths are placeholders and private user-owned inputs stay local.

Along with full saved history, `verify_full_duration_pair_outputs` inspects both saved `OpenSees_Bidirectional_Input_Commands.json` files for original A/B bytes-source path identities, correct XY/YX global DOF assignment, and recorded OpenSees Path acceleration factor. The manifest SHA and orientation mapping are written to `DIRECT_EXISTING_NLTHA_STATUS.json`. Recorded command provenance is **not** proof that the first-step X-wall nonfinite was corrected.

The archived source configuration lacks independently verified M0–M6 attribution. Accordingly, an exploratory run labeled `UNVERIFIED` can only be credited to that exact source SHA; do not place the result into a quantitative M0–M6 comparison until source-EDB/outrigger/damper variant fingerprints establish which state was run.

The [three-pass code/engineering/organization audit](../../REVIEW_MAIN/06_NONLINEAR_TH/20261122_TRIPLE_PASS_NATIVE_NLTHA_INTEGRATION_AUDIT.md) records checks, accepted results and outstanding native tests. Direct model formulation: Kolozvari et al. (2015), PEER 2015/12 and Kolozvari, López & Massone (2023), Engineering Structures 294, 116700; official OpenSees E-SFI-MVLEM-3D input syntax. These references describe the chosen idealization but cannot replace M45, bar/FSAM, P-Delta, damper and seismic input calibration.

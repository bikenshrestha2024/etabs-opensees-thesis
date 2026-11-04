# Engineering verification continuation — four thesis workstreams

**Review basis:** `66c5c971ea297dc9d7fb0499b871a6204297913d` (2026-11-04). This work continues [draft PR #6](https://github.com/bikenshrestha2024/opensees-nbc105-research/pull/6). [Draft PR #5](https://github.com/bikenshrestha2024/opensees-nbc105-research/pull/5) is still separate and unmerged; do not silently duplicate its full-record timing fixes. The source-level ledger [README](ledger/README.md) identifies exactly which file/function was inspected; static AST parsing is not a line-by-line semantic review.

## A. Semantic code review

The frozen ledger contains **275 baseline Python files**, with source inspection actually recorded for **10** and the rest explicitly `NOT_REVIEWED`. This follow-up inspected the `failure_evidence.py` evidence capture path; `thesis_quality.py` four-probe generation/review; `soil_c_nltha_suite.py` input register and Loma end handling; `variant_comparison.py` manifest/aggregation; `soil_c_run_matrix.py` planning/outputs; the `29_NATIVE_DEVICE_BENCHMARK.py` isolated test setup and the launcher for stage 21. These are bounded source/function inspections, not completion of all 275 semantic reviews. New code tests in this PR are independent of OpenSees native and must not be called engineering calibration.

## B. Native 3D wall t≈0.005s failure reproduction

**Native status: NOT RUN — exact real ETABS export and native OpenSeesPy build unavailable in CI.** Earlier report of `110280` / source `AREA:354` is a *post-failure symptom*, not a proven first cause. This is a 3D RCC core with openings and potential connectivity, constraint, confinement, shear-flexure interaction and local-axis issues. Source: [OpenSees E-SFI-MVLEM-3D four-node/24-DOF element](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html).

New `tools/run_native_wall_probes.py` prepares **ZERO, X, Y, XY** independent 0.005s research-diagnostic JSONs with actual source model/config SHA256, output separation and Python/platform metadata. Native execution is explicit and runs one fresh Python subprocess/domain per case, preserving stdout/stderr and the failure report. A 0.005-second short probe is **not** a full earthquake-history test, especially with diagnostic damping disabled.

```powershell
# Use the actual Windows conda-forge Spyder/OpenSeesPy interpreter, from the repository root.
python tools/run_native_wall_probes.py --config "D:/Thesis/Research_Diagnostic.json" --output "D:/Thesis/Probes_20261104"
# Review Probe_ZERO.json, Probe_X.json, Probe_Y.json, Probe_XY.json before execution:
python tools/run_native_wall_probes.py --manifest "D:/Thesis/Probes_20261104/00_WALL_PROBE_EXECUTION_MANIFEST.json" --execute --research-only
python 21_NLTHA_TRIAGE.py --review "D:/Thesis/Probes_20261104"
```

The project `model_folder` must contain the real `OpenSees_Complete_Model_Data_V118.json`; provide `OpenSees_Complete_Element_Map_V118.json` and actual reinforcement/opening schedules for source-tag mapping. Do not upload or modify the private ETABS source. Preserve last **accepted** response state, first failed integration step, tags and material response. A symptom located after failure does not establish cause.

## C. Experimental validation of RCC core, FVD and BRB

**Experimental project status: REQUIRES PROJECT EVIDENCE.** Existing source paper cards are specimen benchmarks, not proof of actual building calibration. New `tools/audit_component_experiments.py` checks **actual measured** and **native model** CSV histories, specimen ID, primary DOI/report, loading protocol and measured-file SHA256. It compares *time-aligned* force RMSE (kN), normalized RMSE, and signed hysteretic work (kN·m); it deliberately does not invent a threshold or interpolate arbitrary cyclic phases.

One JSON manifest per specimen:

```json
{
  "component_type": "FVD",
  "units": "kN-m-s",
  "source_doi_or_primary_report": "actual DOI/report",
  "specimen_id": "source specimen identifier",
  "loading_protocol": "actual cyclic and velocity loading",
  "experiment_csv": "D:/Thesis/Test/FVD_measured.csv",
  "simulation_csv": "D:/Thesis/Test/FVD_native.csv",
  "model_command": "uniaxialMaterial ViscousDamper",
  "parameter_card_sha256": "64-digit exact source card SHA",
  "experiment_input_sha256": "64-digit exact measured CSV SHA"
}
```

- **FVD CSV**: `time_s,disp_m,velocity_m_s,force_kN`. SI `Cd` in kN·(s/m)^α, `K` in kN/m, α dimensionless. Check stroke, velocity, spring effects, hysteresis and energy.
- **BRB CSV**: `time_s,disp_m,force_kN`. Also review steel core area/length, yield/hardening, fatigue, end connections, compressive stability and cumulative ductility.
- **Core 3D CSV**: `time_s,disp_x_m,disp_y_m,force_x_kN,force_y_kN`. Manifest additionally requires `axial_load_kN`, `core_geometry_source`, `reinforcement_source`. Verify coupled biaxial response, axial effects, openings and out-of-plane action.

```powershell
python tools/audit_component_experiments.py --manifest "D:/Thesis/Test/FVD_manifest.json" --output "D:/Thesis/Test/FVD_comparison.json"
```

A computed comparison returns `COMPARISON_COMPUTED_NO_ACCEPTANCE_THRESHOLD`, **not experimental validation**. Native wall/device response and actual source measured data are needed before declaring a PASS.

## D. Full Soil C XY/YX suite, outrigger elevations and optimum

**Status: NOT RUN — no project-validated optimum.** Stage 36 plans M0–M6 × ULS/SLS × eight *already matched Soil C* earthquake pairs = 112 configurations; both simultaneous XY and YX orientations = **224 intended complete transient cases**, not solved runs. A new `tools/audit_soil_c_case_completion.py` reads `00_SOIL_C_M0_M6_RUN_MATRIX.csv` and checks all 224 real case outputs, independent record/model hashes, exact identity, full-duration and finite channel gates. It reports `NOT_RUN`, `FAILED`, `INCOMPLETE`, `RESEARCH_ONLY_FULL_RECORD` and always refuses to declare an optimum without validated project materials and acceptance criteria.

```powershell
python 35_SOIL_C_NLTHA_PREFLIGHT.py --matched-dir "D:/Thesis/Matched" --output "D:/Thesis/Audit/soil_c.json"
python 36_SOIL_C_NLTHA_RUN_MATRIX.py --models-json "D:/Thesis/Models/M0_M6.json" --matched-dir "D:/Thesis/Matched" --output-dir "D:/Thesis/RunMatrix"
python tools/audit_soil_c_case_completion.py --matrix "D:/Thesis/RunMatrix/00_SOIL_C_M0_M6_RUN_MATRIX.csv" --output "D:/Thesis/Audit/soil_c_case_status.json"
```

For optimization, compare **actual outrigger floor elevations** and separately configured conventional/damped/belt/cap/BRB families. Do not treat a material/device class as an automatically optimal elevation. Use matched geometry/mass/seismic input/analysis settings and physical acceptance criteria; report roof/edge displacement and drift, torsion, residuals, floor accelerations, base shears, wall/beam/column demands and device stroke, force and dissipated energy; preserve every failure.

## Validation matrix

| Objective | Tool/implementation evidence | Native or scientific evidence status |
|---|---|---|
| 275-file complete semantic review | Frozen per-file ledger, **10** inspected at initial snapshot; bounded additional source inspections | **NOT EVALUATED** for uninspected files |
| Wall X first-step failure | Isolated 4-probe reproducible launcher, input SHA and full logs | **NOT RUN / REQUIRES PROJECT EVIDENCE** |
| RCC core, FVD and BRB experimental validation | Strict specimen CSV and comparison metrics | **REQUIRES PROJECT EVIDENCE** |
| Soil C M0–M6 full XY/YX NLTHA | Strict 224-outcome status audit | **NOT RUN; no optimum** |
| Software regression suite | GitHub CI test commands and status | Judge by current CI run only |

**Official sources:** [NBC 105:2025 DUDBC](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf); [OpenSees E-SFI-MVLEM-3D](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html); [OpenSees UniformExcitation](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html); PEER 2015/12. Clauses §4.1, Table 5-2 and §9.3.2 govern code selection and bidirectional time histories, but code applicability and full-source numerical evidence must be checked for each case.

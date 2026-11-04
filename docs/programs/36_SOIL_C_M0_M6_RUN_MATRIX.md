# Stage 36 — M0–M6 × eight Soil C earthquakes × ULS/SLS run matrix

**Purpose:** Generate a deterministic and source-hash-bound **research configuration plan only**. This tool NEVER executes OpenSees or claims a successful 25-storey nonlinear run. It is designed for the user's thesis workflow and retains the existing Stage 35 required hazard/physics input checks.

The 112 generated JSON configurations are organized by model variant (M0–M6), limit state (ULS/SLS) and event, with both orientations in each configuration: **112 × 2 = 224 intended separate horizontal bidirectional XY/YX nonlinear case analyses**. Model variants must be assembled from actual source ETABS geometry, matching mass, gravity loads and approved detailing; do not infer them from filenames.

## 1. Source requirements

- Soil Type **C** only, RC dual shear-wall system, matched 0.05–6s to `C_h(T)*Z*I/Omega_u`, model target `Z=.35,I=1,R_mu=3.5,Omega_u=1.4`.
- 16 actual SeismoMatch `Matched_*.txt` files with source acceleration `g`; expected SHA is in [matched_component_register.csv](../ground_motions/seismomatch_20261104/matched_component_register.csv).
- Do not copy original/matched PEER records into GitHub. The generator finds each local source by **SHA256**, even if the download filename includes `(1)`.
- Full source selection remains 6 research-labeled near-field events plus 2 far-field, not independently verified distance classes.
- Gorkha source processing and Loma Prieta endpoint mismatch remain explicitly UNAPPROVED in the generated configurations.

## 2. Actual workflow steps and required parameter map

Prepare a PRIVATE local `M0_M6_Directories.json` containing seven model-export directories. The shown paths are placeholders, not existing verified model paths:

```json
{
 "M0":"D:/Thesis/ETABS_Export/M0",
 "M1":"D:/Thesis/ETABS_Export/M1",
 "M2":"D:/Thesis/ETABS_Export/M2",
 "M3":"D:/Thesis/ETABS_Export/M3",
 "M4":"D:/Thesis/ETABS_Export/M4",
 "M5":"D:/Thesis/ETABS_Export/M5",
 "M6":"D:/Thesis/ETABS_Export/M6"
}
```

Execute from repository root (Spyder Python 3.12 environment, no extra nonstandard dependencies for this stage):

```powershell
python 36_SOIL_C_NLTHA_RUN_MATRIX.py --models-json "D:/Thesis/ETABS_Export/M0_M6_Directories.json" --matched-dir "D:/Thesis/Soil_C_Matched" --output-dir "D:/Thesis/RunMatrix_Soil_C" --dt 0.005
```

Each `configs/M#/ULS|SLS/Event.json` includes: actual model folder, input SHA-identified files, soil `C`, `scale=1.0`, source `g`, both `XY/YX`, `diagnostic_excitation=XY`, `nonlinear_walls=true`, `duration_s=null`, and **`analysis_intent=RESEARCH_DIAGNOSTIC`**. Reviewers must not promote `THESIS_NLTHA` until source material, wall, gravity, FVD, BRB and modal evidence are complete.

## 3. Generated output format

- `configs/M0/ULS/Kobe.json`, etc.: 112 independently editable source configs, NEVER launched automatically.
- `00_SOIL_C_M0_M6_RUN_MATRIX.csv`: 112 ordered rows, model, state, event, orientations, expected count, config file, unique result directory and blocking source review.
- `00_SOIL_C_RESEARCH_RUN_MATRIX.json`: 224 intended case slots and evidence limitations.
- `results/M#/ULS|SLS/Event/XY` and `.../YX`: output paths reserved for future complete nonlinear runs.

Example per-case invocation must use the project's existing runner/launcher; this stage does not fabricate a new execution entrypoint or claim the model is ready.

## 4. Engineering guards

- Do not silently overwrite existing config or run-matrix files.
- Do not change `scale=1.0`: already matched `Acc(g)` requires only `ops.timeSeries('Path',...,'-factor',9.80665)` for a kN–m–s model.
- The `--dt 0.005` default is a **proposal**, NOT an NBC §9.3.2.4 pass; current verified modal `T1_X,T1_Y,Tn90_X,Tn90_Y` may dictate smaller dt.
- Review the actual seismic selection and fit period interval `[Tn90,sqrt(R_mu)*T1]`.
- The runner rejects unreviewed Gorkha's 322.94-s matched duration and unmatched Loma Prieta 0.005-s end-time difference. Use a named reviewer and documented source policy; do not edit registered source files to silence the errors.
- A run configuration with nonlinear wall flag `true` does **not** establish the concrete/steel/FSAM wall is calibrated; source reinforcement, confinement and wall openings must be validated independently.
- Consistent M0–M6 conclusions require identical input record waveforms for all variants and a consistent geometric/mass modelling basis; label all partially completed cases INCOMPLETE.

**Governing standards:** [NBC 105:2025, §9.3](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf); [Stage 35 complete Soil C motion guidance](35_SOIL_C_PRIMARY_NLTHA_RUNBOOK.md). Reference OpenSees [UniformExcitation](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html).

**Testing:** `tests/verify_soil_c_run_matrix.py` verifies the 112/224 combinatorics, two orientations, default source scaling, unapproved processing flags and refusal to overwrite old configurations.

# Main program first-test checklist — merged main (2026-11-04)

**Working main when written:** `36f5fcca82006b7c07da96ed4c5143007cdf18bd`. This checklist does **not** claim native Windows/ETABS verification or resolved E-SFI wall failure.

## 1. Update safely

In a **terminal opened in your existing local clone** (not inside a downloaded ZIP):

```powershell
git status --short
git switch main
git pull --ff-only origin main
git rev-parse --short HEAD
```

If `git status` reports local edits, **copy or commit them first**; do not discard private model changes or run `git reset --hard` to force an update.

Use your existing Windows **conda-forge Python 3.12 Spyder/OpenSeesPy environment**, and keep actual ETABS exports and acceleration records in local directories. The source program remains a GitHub repository, not a compiled installer. Keep the project folder together rather than copying only one root launcher.

## 2. Inspect before invoking the native solver

```powershell
python tests/verify_review_ledger.py
python tests/verify_modal_cancel_status.py
python tests/verify_soil_c_run_matrix.py
python tests/verify_full_record_gate.py
python tests/verify_wall_geometry_preflight.py
python tests/verify_wall_openings.py
python tests/verify_project_wall_material_gate.py
python tests/verify_native_wall_probe_preparation.py
python tests/verify_component_experiment_evidence.py
python tests/verify_soil_c_case_completion.py
```

These are **source/fixture regressions**, not a real ETABS or nonlinear dynamic run. CI passing does not establish the real 25-storey building's wall stability or material calibration.

## 3. Open the current main GUI

```powershell
python 01_WORKFLOW_START.py
```

This launches `RUN_ETABS_TO_OPENSEES.py` through the documented compatibility facade.

If the ETABS project is already exported, you may open the source-input readiness panel:

```powershell
python 02_INPUT_READINESS.py
```

Always first check **actual source** elevations, nodes, local axes, wall openings and diaphragm load path, sections, mass and source model file hashes. Never merge paper-specimen material profiles into your project by convenience.

## 4. Safe analysis sequence

1. `10_GRAVITY.py` — verify applied source loads, total reactions and mass consistency **against the exact ETABS model and equivalent load case**.
2. `11_MODAL_ULS_SLS.py` — check 3D modes and cumulative X/Y effective modal mass; the GUI's existing **Stop selected batch** cancels running/queued work, now without misreporting the cancelled subprocess as a successful or naturally failed eigenanalysis.
3. `12_EQUIVALENT_STATIC.py` and `13_RESPONSE_SPECTRUM.py` — compare code assumptions, modal periods and spectrum scaling against independent ETABS output. The current `implementation_digest` source finder already resolves its own installed `components` package; the older draft PR #2 must **not** overwrite it blindly.
4. `35_SOIL_C_NLTHA_PREFLIGHT.py` — verify all eight **already matched Soil C** A/B pairs from your local source directory, correct SHA256 values and timeline/special-case review. Additional spectral scaling remains 1.0; `Acc(g)` uses `Path -factor 9.80665` in the kN–m–s model.
5. `15_BUILDING_NONLINEAR_TRIAL.py` — **research-only** limited trial after the model has passed the previous checks. This does not certify complete time histories, materials, or a suitable device design.
6. `tools/run_native_wall_probes.py` — for the first X-direction wall issue, prepare fresh ZERO/X/Y/XY 0.005-second research probes; preserve solver logs, element mapping and last accepted step; do not alter physical material parameters to obtain a PASS.
7. After actual core material/rebar/FSAM/FVD/BRB validation, `36_SOIL_C_NLTHA_RUN_MATRIX.py` prepares the 112 two-orientation configurations. `tools/audit_soil_c_case_completion.py` checks the 224 intended case outcomes. Their generation is **NOT** proof of actual NLTHA completion or optimum outrigger elevation.

**Important:** `17_BUILDING_FULL_NONLINEAR.py` currently opens a **research setup** that has an unresolved first-step X wall failure and uncalibrated project constitutive parameters. Do not describe a run from that facade as thesis-validated production analysis.

## 5. Collect exact evidence when a run fails

For each error, preserve:

- Git commit SHA from `git rev-parse HEAD` and current Python `sys.executable` and OpenSeesPy `ops.version()`.
- The exact launcher filename, GUI selection, limit state, XY/YX orientation, and fresh output folder.
- Exact JSON configuration and source export/record **SHA256 only when sharing**; keep private ETABS and waveforms local unless you independently decide to provide them.
- Complete terminal/GUI log, first Python traceback, last accepted physical timestep, first failed attempt, element/node tags and source AREA/frame mapping.
- Accepted history and `INCOMPLETE.json`/`FAILED.json` if produced. Do not overwrite an earlier failed run.

## 6. Engineering status

| Check | State |
|---|---|
| GitHub source and non-native CI | PASS at this documented commit |
| Your Windows GUI, ETABS COM connection, native gravity/modal | NOT RUN by the GitHub source audit |
| Native full 3D RCC wall first-step failure reproduction | REQUIRES PROJECT EVIDENCE |
| Project-specific Concrete/Steel/FSAM/FVD/BRB experimental calibration | REQUIRES PROJECT EVIDENCE |
| Complete ULS/SLS Soil C XY/YX 224-case convergence | NOT RUN |
| Optimum damped-outrigger type and elevation | NOT EVALUATED |

[Work order](../00_READ_FIRST_RUN_ORDER.md) · [Four-workstream engineering runbook](review/04_FOUR_VALIDATION_WORKSTREAMS.md) · [Current source audit ledger](review/ledger/README.md).

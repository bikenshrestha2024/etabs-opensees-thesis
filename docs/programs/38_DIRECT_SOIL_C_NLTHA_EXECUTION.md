# Stage 38 — Execute the existing OpenSees model for Soil C NLTHA

This stage **launches a real OpenSeesPy solver process** when `--run` is provided on a machine with the current repository, verified source exports and matched records. It does not generate substitute model geometry, invent reinforcement or silently approve an exploratory model. In this November 2026 connector environment, native OpenSeesPy and the private thesis exports were not available; **no 25-storey nonlinear solution was executed here**.

## 1. Prepare your existing model once

Use the original ETABS -> OpenSees exported `OpenSees_Complete_Model_Data_V118.json` and associated four exports required by the canonical builder, preserving two 12 m X-wall lines with actual openings, 32 physical foundation joints plus 44 transfer/mesh points, diaphragm kinematics, mass and source element identifiers. Do not overwrite the original case, alter gravity reactions to force parity or treat 76 mapped base nodes as 76 foundation supports.

The full comparative gravity case is 1D+1L; seismic gravity/mass for NLTHA is separately governed by NBC 105:2025 §5.2 Table 5-1. The project-adopted IS 16700 P-Delta initial-case review does not replace the NBC gravity and dynamic input or authorize double-applying static seismic force.

## 2. Audit 16 ground-motion inputs

From repository root in Windows Python 3.12 (same environment with OpenSeesPy installed):

```powershell
python 35_SOIL_C_NLTHA_PREFLIGHT.py --matched-dir "D:/Thesis/Soil_C_Matched" --output "D:/Thesis/Checks/Soil_C_Input_Audit.json"
```

Preserve the original hash-matched eight A/B components and `Acc(g)`, and retain the original SeismoMatch factor evidence. Extra OpenSees amplitude factor is **1.0**, with acceleration unit conversion **9.81 m/s² per g**; the event components are applied simultaneously in `XY` and `YX` to separate gravity-preloaded domains. Gorkha's matched 322.94 s versus original 120 s is not silently approved; Loma Prieta's one-sample endpoint difference requires an explicit source-preserving review. Modal `T1` and `Tn90` must come from this *exact* building model.

## 3. Generate the planned run matrix

Prepare a PRIVATE `M0_M6_Directories.json` mapping all seven actual, distinct model export paths. Then:

```powershell
python 36_SOIL_C_NLTHA_RUN_MATRIX.py --models-json "D:/Thesis/Models/M0_M6_Directories.json" --matched-dir "D:/Thesis/Soil_C_Matched" --output-dir "D:/Thesis/RunMatrix_Soil_C" --dt 0.005
```

This produces 112 configurations and 224 intended independent XY/YX histories. The dt is a preliminary choice, not verified NBC §9.3.2.4 compliance. Neither the matrix nor its text labels prove that seven independent nonlinear physical models are qualified.

## 4. Launch one actual existing model/event first

```powershell
# Preflight ONLY: confirms exact waveform SHA and required export presence.
python 38_EXECUTE_SOIL_C_NLTHA.py --config "D:/Thesis/RunMatrix_Soil_C/configs/M0/ULS/Kobe.json" --allow-research-diagnostic

# DIRECT NATIVE SOLVER: launches the existing 3D nonlinear model runner.
python 38_EXECUTE_SOIL_C_NLTHA.py --config "D:/Thesis/RunMatrix_Soil_C/configs/M0/ULS/Kobe.json" --allow-research-diagnostic --run
```

The `--allow-research-diagnostic` option means *exploratory analysis only*. Delete it only after replacing the generated diagnostic assumptions with source-reviewed `THESIS_NLTHA` configuration and documented structural/material evidence. Merely changing the JSON intent field is **not** qualification; the existing strict core-wall, reinforcement, damping, openings, seismic motion and P-Delta gates remain operative.

Do not rerun into an existing output directory. Use an explicitly separate output folder for each mesh/material/time-step variant and retain every failed-case log.

## 5. What to inspect from an actual native run

The case output has `Execution_Status.json`, `Executed_RunConfig.json`, `Native_NLTHA_Console.log`, and `XY/` plus `YX/` case folders. Only if both case summaries independently report `COMPLETED_EXPLORATORY_RECORD`, the history gate reports `FULL_DURATION_NUMERIC_SCREEN`, and the native process returns code zero will Stage 38 label the pair `FULL_DURATION_SOFTWARE_SCREEN_ONLY`. It **never** sets `engineering_accepted=true`.

If the first step fails, preserve the original traceback and solver clock evidence, and run Stage 21 ZERO/X/Y/XY controlled short probes for the exact saved model. Verify source wall panel winding and dimensions, actual boundary/web reinforcing, axial loads, FSAM constitutive response, support and coupling-beam geometry, then re-execute after source-grounded corrections. Never treat post-failure localForce=NaN as the demonstrated root cause.

## 6. From one converged case to the thesis comparisons

After source reconciliation, material/device validation and reproducible full XY/YX histories for each state, use existing `components/nonlinear_time_history/variant_comparison.py` and `27_COMPARE_OUTRIGGERS.py`. No failed, truncated, recovered-only, uncalibrated or inconsistent-input case enters accepted statistical comparison. Complete the code/experimental/model verification gates independently before IO/LS/CP or performance conclusions.

**Governing methodology:** NBC 105:2025 §§9.3.1–9.3.3 (Nepal); NIST GCR 17-917-46v1 (2017) for NLTHA modelling and response-history quality; PEER 2015/12 and Kolozvari et al. (2023) for wall component modelling. See [research source register](../00_RESEARCH_REFERENCES.md) and [thesis chapter methodology](../thesis/NLTHA_METHODOLOGY_AND_EVIDENCE_20261122.md).

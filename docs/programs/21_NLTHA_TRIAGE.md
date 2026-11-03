# 21 — Nonlinear earthquake-history failure triage (research V169)

## Purpose
This diagnostic extension addresses the current first-step transient failure without changing structural material parameters, solver tolerances or an earthquake record to force convergence.

**Current evidence:** V168 isolated X-only excitation with zero damping failed at 0.005 s, while ZERO passed. Nonfinite post-failure element forces were observed at `AREA:354` and `AREA:482` (solver tags 110280 and 112778). Because responses were queried after a failed step, these elements are **suspects, not proven root causes**.

## Run from Windows
Use the same complete current source environment and a known existing exploratory `RunConfig.json`. Generate four separate configs with:

```powershell
python 21_NLTHA_TRIAGE.py --config "D:\\Existing_Run\\RunConfig.json" --output "D:\\NLTHA_Probes"
```

The four files `Probe_ZERO.json`, `Probe_X.json`, `Probe_Y.json` and `Probe_XY.json` are written, **but they are not executed**. Use the V168 exploratory nonlinear runner on each config in a fresh process / independently rebuilt model. All probes use ULS, XY orientation, first 0.005 s, zero Rayleigh damping and separate output directories. Do not change multiple mechanical assumptions between probes. Do not overwrite earlier evidence.


Execute each generated configuration from the repository root with the exploratory runner, for example:

```powershell
python -m components.nonlinear_time_history.building_exploratory --config "D:\\NLTHA_Probes\\Probe_ZERO.json"
python -m components.nonlinear_time_history.building_exploratory --config "D:\\NLTHA_Probes\\Probe_X.json"
python -m components.nonlinear_time_history.building_exploratory --config "D:\\NLTHA_Probes\\Probe_Y.json"
python -m components.nonlinear_time_history.building_exploratory --config "D:\\NLTHA_Probes\\Probe_XY.json"
```

Run serially in separate processes, recording the exact active environment and source commit. If the first configuration fails before writing a report, preserve its console log. These commands are intentionally **not** executed in CI because a calibrated model/export and a native OpenSeesPy installation are required.

After running, review:

```powershell
python 21_NLTHA_TRIAGE.py --review "D:\\NLTHA_Probes"
```

The review classifies missing, failed and passing probes and prints an evidence-based interpretation. It never labels short probes as completed full-record simulations.

## Built-in additions to the exploratory runner
- Input acceleration vectors are required to be nonempty, finite, with valid sample timestep and declared acceleration units.
- A per-record SHA-256/source unit/duration/PGA manifest is written to `NLTHA_Input_Quality.json` **before expensive gravity/eigen solves**.
- `NLTHA_Quality_Gates.json` distinguishes truncated trial from full duration and always marks experimental validation as unestablished; a completed full record still needs model and test comparisons.
- Missing or failed probes are explicitly marked and cannot be ranked as validated thesis outcomes.

## Next engineering investigations
1. Independently reproduce each affected wall panel's FSAM / ConcreteCM / SteelMPF cyclic response using its actual axial load and imposed shear before restarting the building.
2. Compare the two 0.4 m wide X-Z wall patches with neighboring panels, local orientation, area-node order, wall boundary conditions, and effective tangent stiffness; inspect `Research_Material_Assignment_V161.json`.
3. Run fresh X-only test with zero damping at two step sizes and compare the earliest pre-failure state; do not interpret post-failure `localForce` as clean equilibrium output.
4. Compare solver/matrix choices with fixed material geometry, and independently check mass, support, diaphragm, P-Delta and floor loads.
5. Reproduce a measured wall test with the specific E-SFI-MVLEM-3D implementation; verify numerical acceptance, energy balance, convergence and full record before comparing outrigger cases.
6. Add FVD relative velocity, force, stroke and dissipated energy, and BRB axial strain/plastic demand and fatigue response using independently validated device laws.

## Limitation
This code adds reproducibility and failure classification, **not** a numerical repair, a calibrated research model or a successful full-building NLTHA.

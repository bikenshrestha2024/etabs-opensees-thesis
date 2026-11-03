# 00 — Six-stage nonlinear thesis implementation and validation guide

Status: all six software workstreams committed to main. Native OpenSeesPy/ETABS model runs and experimental replication are still required.

| Stage | Active source | New input | Evidence written | Engineering status |
|---|---|---|---|---|
| 01 X-only failure triage | components/nonlinear_time_history/wall_diagnostics.py | Isolated model data | NLTHA_Wall_Geometry_Preflight.json | Geometry screened; X-only first-step failure remains unresolved |
| 02 Actual reinforcement | components/model/reinforcement_mapping.py | approved_frame_reinforcement_csv | Research_Material_Assignment_V161.json | Opt-in approved frame geometry; no wall boundary confinement mapping yet |
| 03 Wall opening fidelity | components/nonlinear_time_history/wall_topology.py | wall_openings_manifest | NLTHA_Wall_Opening_Preflight.json | Declared void occupancy screen, not cyclic wall validation |
| 04 FVD / BRB | components/nonlinear_time_history/device_recording.py | Active device overrides | Device_Accepted_Step_History.csv and Device_Demand_Summary.json | Signed device demand only; element recorder and fatigue qualification pending |
| 05 Full record | components/nonlinear_time_history/full_record_gate.py | Accepted transient history | Accepted_History_Completion_Gate.json | Full-duration and finite-history screen; experiment and dt refinement outstanding |
| 06 M0–M6 | components/nonlinear_time_history/variant_comparison.py | Case manifest, actual seven models and common motion suite | M0_M6_Research_Comparison.json | Fails closed on incomplete or mismatched cases; seven model runs outstanding |

## Operation

1. Use the complete current GitHub checkout in Windows Spyder with Python 3.12 and conda-forge packages. Keep original ETABS exports unchanged and choose a separate output folder.
2. Configure the exploratory RunConfig.json with model_folder, output_dir, actual X and Y ground-motion paths, pair_id, variant_id (M0–M6), limit_state (ULS/SLS), orientations XY/YX, scale, dt_s, and duration_s=0 for a full record. The source model is still exploratory until calibrated.
3. When available, explicitly supply approved_frame_reinforcement_csv with independent reviewer and actual source schedule SHA256. Otherwise the code preserves the existing unverified rebar template.
4. Supply wall_openings_manifest when available. An absent manifest is UNVERIFIED, not a passed check. Confirm the model source includes the full wall mesh and any coupling beams.
5. The stage 01 wall geometry check runs before costly model solves. Stage 02 maps reviewed frame bars. Stage 03 examines declared voids. Stage 04 samples activated FVD/BRB model elements only after accepted transient states. Stage 05 checks accepted-history chronology, finiteness and full record duration.
6. Diagnose ZERO, X, Y and XY separately if the initial X step still fails. Do not loosen or replace material models merely to obtain convergence without documenting a different model hypothesis.
7. After independently producing a verified set of full-record case summaries for M0–M6, create a manifest with identical geometry-basis, mass-basis, ground-motion-set and analysis-settings SHA256 invariants, variant-specific actual model SHA256, device/level information, and case_summary_files. Call python 27_COMPARE_OUTRIGGERS.py with the manifest path. Both ULS/SLS and three or more pairs in XY/YX are presently enforced.
8. Even when comparisons are computed, full thesis acceptance requires real source detailing, component calibration, numerical convergence and reviewed criteria (G00–G10).

## Explicit unsolved physical tasks

- The X-direction first-step nonlinear core-wall failure at 0.005 s has not been solved; suspect wall AREA:354/482 source elements were only localized.
- No complete actual wall core and special boundary reinforcement mapping exists. The new CSV workflow only covers the current frame fiber section templates.
- E-SFI-MVLEM-3D experimental cyclic panel, coupled wall openings, core torsion and boundary confinement still require reproduction and verification.
- FVD/BRB device force recorder support, sign conventions, true dashpot energy, BRB inelastic history and fatigue capacities require independent native device benchmarks.
- No actual Kobe full-record paired NLTHA or validated seven-model M0–M6 response set was generated in these commits.

## Scientific and code context

PEER 2015/12 documents ConcreteCM, SteelMPF and FSAM cyclic shear-flexure experimental modeling. Kolozvari et al. (2023), DOI 10.1016/j.engstruct.2023.116700, documents E-SFI-MVLEM-3D. Stokley & Lowes (2024), PEER 2024/11, covers a separate layered shell calibration-validation approach. Korkmaz & Kircil (2026), DOI 10.3390/buildings16040711, studies supplemental FVD damping for RC buildings. NBC 105:2025 governs motion-pair and drift requirements; record its noted drift-clause cross-reference discrepancy rather than silently correcting it.

Only an actual solver run with calibrated inputs and preserved logs can advance a case from research screening to a defensible thesis result.

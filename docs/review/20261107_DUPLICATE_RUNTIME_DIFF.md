# Duplicate runtime source: `Saved_Project_V156/OpenSees_Runtime_V118/components` vs `components/`

[REF components/model/assembly.py prepare_complete_export (runtime copy)] [REF AGENTS.md: never use stale preserved V156 runtime as active code]

Generated 2026-11-07 on branch `improve/damping-energy-viz`. The active side
includes this branch's edits: three of the active-only files are new here
(`model/section_tags.py`, `nonlinear_time_history/damping_regions.py`,
`nonlinear_time_history/energy_balance.py`), and five differing files were
edited here (`model/assembly.py`, `nonlinear_time_history/building_exploratory.py`,
`nonlinear_time_history/runner_and_gui.py`,
`nonlinear_time_history/soil_c_physics_preflight.py`, `ui/application.py`); all
five already differed before this branch. Nothing was deleted or modified under
`Saved_Project_V156/`.

## What the duplicate is

`prepare_complete_export()` copies the active `components/` tree into
`<export folder>/OpenSees_Runtime_V118/components` so that the generated
`OpenSees_Complete_*_Model.py` scripts can run standalone beside the ETABS
export. `Saved_Project_V156/` is one such export **committed to Git**, so its
runtime is a frozen snapshot of the code at that time. The root facades
(`Define_Section_V109.py`, `OpenSees_Initial_PDelta_V124.py`, ...) only fall
back to an `OpenSees_Runtime_V118/components` folder **beside themselves** when
`components/` is missing, so running from the repository root never loads the
stale copy. Running a generated script **inside** `Saved_Project_V156/` does.

## Summary

| Status | Files |
|---|---|
| Identical | 42 |
| Differs (active is newer) | 36 |
| Only in active `components/` | 36 |
| Only in saved runtime | 0 |

## Per-file comparison (`+` lines only in active, `-` lines only in saved)

| File (relative to `components/`) | Status | + | - |
|---|---|---|---|
| `equivalent_static/calculation_and_gui.py` | DIFFERS | 726 | 68 |
| `equivalent_static/code_basis.py` | DIFFERS | 60 | 5 |
| `equivalent_static/etabs_linked_excel.py` | ACTIVE_ONLY |  |  |
| `equivalent_static/legacy_code_basis.py` | IDENTICAL |  |  |
| `gravity/gui_and_reports.py` | DIFFERS | 1 | 1 |
| `gravity/load_path_formulas.py` | IDENTICAL |  |  |
| `gravity/load_review.py` | IDENTICAL |  |  |
| `gravity/solver_stack.py` | DIFFERS | 257 | 16 |
| `gravity/storey_loads.py` | IDENTICAL |  |  |
| `inputs/analysis_autofill.py` | DIFFERS | 11 | 3 |
| `inputs/etabs_periods.py` | DIFFERS | 13 | 5 |
| `inputs/opensees_nbc_sync.py` | ACTIVE_ONLY |  |  |
| `inputs/pair_selection.py` | IDENTICAL |  |  |
| `inputs/project_workbooks.py` | DIFFERS | 773 | 48 |
| `inputs/records.py` | DIFFERS | 28 | 0 |
| `linear_time_history/runner_and_gui.py` | DIFFERS | 107 | 9 |
| `modal/analysis.py` | DIFFERS | 100 | 12 |
| `modal/gui_and_reports.py` | DIFFERS | 45 | 9 |
| `modal/rayleigh.py` | DIFFERS | 35 | 15 |
| `model/analysis_basis.py` | DIFFERS | 2 | 2 |
| `model/assembly.py` | DIFFERS | 124 | 19 |
| `model/id_audit.py` | IDENTICAL |  |  |
| `model/initial_pdelta.py` | IDENTICAL |  |  |
| `model/load_accounting.py` | IDENTICAL |  |  |
| `model/load_and_diaphragm_audit.py` | DIFFERS | 29 | 5 |
| `model/nonlinear_preflight.py` | IDENTICAL |  |  |
| `model/readiness.py` | IDENTICAL |  |  |
| `model/readiness_dashboard.py` | ACTIVE_ONLY |  |  |
| `model/readiness_dashboard_gui.py` | ACTIVE_ONLY |  |  |
| `model/readiness_gui.py` | DIFFERS | 6 | 1 |
| `model/reinforcement_mapping.py` | ACTIVE_ONLY |  |  |
| `model/section_tags.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/building_exploratory.py` | DIFFERS | 813 | 29 |
| `nonlinear_time_history/damping_regions.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/device_recording.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/energy_balance.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/failure_evidence.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/full_record_gate.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/ground_acceleration.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/literature_demo.py` | IDENTICAL |  |  |
| `nonlinear_time_history/literature_materials.py` | IDENTICAL |  |  |
| `nonlinear_time_history/material_draft.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/nbc105_2025_audit.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/nbc105_horizontal_input.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/paper_specimen_sources.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/research_building_materials.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/runner_and_gui.py` | DIFFERS | 283 | 18 |
| `nonlinear_time_history/seismomatch_audit.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/soil_c_nltha_suite.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/soil_c_physics_preflight.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/soil_c_run_matrix.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/thesis_quality.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/variant_comparison.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/wall_diagnostics.py` | ACTIVE_ONLY |  |  |
| `nonlinear_time_history/wall_topology.py` | ACTIVE_ONLY |  |  |
| `response_spectrum/model_analysis.py` | DIFFERS | 103 | 13 |
| `response_spectrum/nbc105_dual_target.py` | ACTIVE_ONLY |  |  |
| `response_spectrum/nbc_pair_spectrum_audit.py` | ACTIVE_ONLY |  |  |
| `response_spectrum/reports.py` | IDENTICAL |  |  |
| `response_spectrum/site_spectrum_and_scaling.py` | IDENTICAL |  |  |
| `sections/area_elements.py` | DIFFERS | 5 | 0 |
| `sections/definitions.py` | IDENTICAL |  |  |
| `sections/devices.py` | DIFFERS | 79 | 0 |
| `sections/mapping_audit.py` | DIFFERS | 2 | 2 |
| `sections/mapping_gui.py` | DIFFERS | 21 | 2 |
| `sections/wall_adapters.py` | IDENTICAL |  |  |
| `shared/case_status.py` | DIFFERS | 62 | 4 |
| `shared/eigen_solver.py` | DIFFERS | 24 | 2 |
| `shared/legacy_solver_stack.py` | IDENTICAL |  |  |
| `shared/response_recorders.py` | ACTIVE_ONLY |  |  |
| `shared/runtime_utilities.py` | IDENTICAL |  |  |
| `shared/timing.py` | IDENTICAL |  |  |
| `shared/transient_runtime.py` | IDENTICAL |  |  |
| `ui/application.py` | DIFFERS | 12 | 31 |
| `ui/building_exploratory_gui.py` | DIFFERS | 260 | 14 |
| `ui/case_selection.py` | IDENTICAL |  |  |
| `ui/history_inspection.py` | IDENTICAL |  |  |
| `ui/history_results.py` | IDENTICAL |  |  |
| `ui/literature_demo_gui.py` | IDENTICAL |  |  |
| `ui/plot_utilities.py` | IDENTICAL |  |  |
| `ui/response_viewer.py` | IDENTICAL |  |  |
| `ui/results.py` | DIFFERS | 28 | 7 |
| `ui/view_controls.py` | IDENTICAL |  |  |
| `ui/window_manager.py` | IDENTICAL |  |  |
| `validation/case_review.py` | DIFFERS | 3 | 3 |
| `validation/design_checks.py` | IDENTICAL |  |  |
| `validation/etabs_comparison.py` | DIFFERS | 190 | 57 |
| `validation/etabs_direct_api.py` | ACTIVE_ONLY |  |  |
| `validation/etabs_equivalence_report.py` | ACTIVE_ONLY |  |  |
| `validation/etabs_floor_end_api.py` | ACTIVE_ONLY |  |  |
| `validation/expanded_workbench_tabs.py` | ACTIVE_ONLY |  |  |
| `validation/floor_end_extraction.py` | ACTIVE_ONLY |  |  |
| `validation/grade_cards.py` | IDENTICAL |  |  |
| `validation/irregularity_review.py` | DIFFERS | 6 | 3 |
| `validation/material_benchmarks.py` | IDENTICAL |  |  |
| `validation/material_catalog.py` | IDENTICAL |  |  |
| `validation/material_sensitivity.py` | ACTIVE_ONLY |  |  |
| `validation/nonlinear_performance.py` | DIFFERS | 5 | 0 |
| `validation/parameter_gui.py` | DIFFERS | 1 | 0 |
| `validation/parameter_studies.py` | DIFFERS | 10 | 4 |
| `validation/reference_library.py` | DIFFERS | 52 | 1 |
| `validation/research_results_gui.py` | IDENTICAL |  |  |
| `validation/response_checks.py` | IDENTICAL |  |  |
| `validation/response_inventory.py` | IDENTICAL |  |  |
| `validation/result_interpretation.py` | IDENTICAL |  |  |
| `validation/saved_stiffness.py` | IDENTICAL |  |  |
| `validation/settings_audit.py` | IDENTICAL |  |  |
| `validation/sfi_worker.py` | IDENTICAL |  |  |
| `validation/steel_calibration_gui.py` | IDENTICAL |  |  |
| `validation/thesis_evidence_dashboard.py` | ACTIVE_ONLY |  |  |
| `validation/torsion_check.py` | ACTIVE_ONLY |  |  |
| `validation/visual_materials.py` | IDENTICAL |  |  |
| `validation/visual_workbench.py` | DIFFERS | 4 | 1 |
| `validation/wall_validation.py` | IDENTICAL |  |  |

## Proposed single-source plan (not executed in this PR)

1. **Treat every `OpenSees_Runtime_V118/` as a build artefact.** Stop committing
   it; add `**/OpenSees_Runtime_V118/` to `.gitignore` for new exports. Keep the
   existing `Saved_Project_V156/` snapshot unchanged as immutable evidence (AGENTS.md).
2. **Stamp the snapshot.** In `prepare_complete_export()`, write
   `OpenSees_Runtime_V118/RUNTIME_SOURCE.json` with the Git commit SHA and a
   SHA256 per copied file. The generated model scripts print it at start-up and
   refuse to run when it differs from the active tree unless
   `ALLOW_STALE_RUNTIME=1` is set (archived reproduction only).
3. **Prefer the installed package over the copy.** Make the generated scripts
   insert the repository root (recorded in `RUNTIME_SOURCE.json`) on
   `sys.path` first and fall back to the bundled runtime only for archive
   reproduction, so one source tree serves both the GUI and exported scripts.
4. **Test.** Add `tests/verify_runtime_snapshot.py`: the bundled copy in any
   *new* export must hash-match `components/`; `Saved_Project_V156` is listed as
   an allowed historical exception.
5. **Later (after import graph check, per `00_CANONICAL_RUN_ORDER_AND_NAMING.md`):**
   move `Saved_Project_V156/` under `archive/` with a README that states it is
   V156-era code and results.

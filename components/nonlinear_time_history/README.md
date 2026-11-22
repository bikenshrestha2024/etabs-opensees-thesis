# Nonlinear time-history analysis and M0–M6 investigations

**Active owner:** `components/nonlinear_time_history/` · **Current Python modules:** 28 · **Status:** module navigation only; engineering acceptance requires independent evidence.

## Responsibilities and interfaces

**Inputs and authority:** Verified gravity state, nonlinear constitutive models, damping and native motion records.

**Cross-module contracts:** NLTHA responses, convergence diagnostics, device and energy evidence.

**Output ownership:** 07_NONLINEAR_TIME_HISTORY; first-step X-wall and full-duration acceptance remain open.

All modules follow [the active integration and latest-source policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md) and [the uniform output structure](../../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md). Source EDB and workbook identity require actual SHA-256 verification; source file names, modification times and passing syntax tests never establish structural equivalence. Historical V134 module indexes are compatibility history, not an authoritative current file inventory.

## Current Python source files

- [building_exploratory.py](building_exploratory.py)
- [damping_regions.py](damping_regions.py)
- [device_recording.py](device_recording.py)
- [energy_balance.py](energy_balance.py)
- [failure_evidence.py](failure_evidence.py)
- [first_step_transition.py](first_step_transition.py)
- [full_record_gate.py](full_record_gate.py)
- [ground_acceleration.py](ground_acceleration.py)
- [literature_demo.py](literature_demo.py)
- [literature_materials.py](literature_materials.py)
- [material_draft.py](material_draft.py)
- [material_source_sets.py](material_source_sets.py)
- [nbc105_2025_audit.py](nbc105_2025_audit.py)
- [nbc105_horizontal_input.py](nbc105_horizontal_input.py)
- [one_storey_wall_probe.py](one_storey_wall_probe.py)
- [paper_specimen_sources.py](paper_specimen_sources.py)
- [research_building_materials.py](research_building_materials.py)
- [runner_and_gui.py](runner_and_gui.py)
- [seismomatch_audit.py](seismomatch_audit.py)
- [soil_c_case_execution.py](soil_c_case_execution.py) — direct, isolated Stage 38 execution of one existing paired case (not model approval)
- [soil_c_nltha_suite.py](soil_c_nltha_suite.py)
- [soil_c_physics_preflight.py](soil_c_physics_preflight.py)
- [soil_c_run_matrix.py](soil_c_run_matrix.py)
- [steel02_carreno_reference.py](steel02_carreno_reference.py)
- [thesis_quality.py](thesis_quality.py)
- [variant_comparison.py](variant_comparison.py)
- [wall_diagnostics.py](wall_diagnostics.py)
- [wall_topology.py](wall_topology.py)

> This list reflects the current checked-in Python files. Do not delete, rename or relocate an active module until its importers, GUI callbacks, saved-case readers and native regression evidence have been verified together. Source-specific guides are under `docs/source/components/nonlinear_time_history/` where available.

## Stage 38 direct case execution

Use [`38_EXECUTE_SOIL_C_NLTHA.py`](../../38_EXECUTE_SOIL_C_NLTHA.py) with one existing Stage 36 JSON configuration. Default is a read-only preflight; `--run` launches the actual existing OpenSees model in a separate process. Research-diagnostic input requires explicit `--allow-research-diagnostic`. Two full-duration software screens remain **not thesis engineering acceptance**. See [Stage 38 procedure](../../docs/programs/38_DIRECT_SOIL_C_NLTHA_EXECUTION.md).

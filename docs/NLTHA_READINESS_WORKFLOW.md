# NLTHA readiness workflow: from template to a human-approved manifest

Scope: what to do when the nonlinear run stops with
"The selected file is an uncompleted readiness TEMPLATE ... Your nonlinear configuration also needs a reviewed material file and wall FSAM mappings". Nothing here approves a model. Approval is a human decision recorded in the manifest. Code never sets `approved_for_nltha` or any check to True.

## 1. What the dialog means

`_require_nonlinear_readiness` (`components/nonlinear_time_history/runner_and_gui.py`) runs before every nonlinear run. It stops when:

1. the manifest file is missing (`FileNotFoundError`; message unchanged);
2. `model_script` in the manifest is blank or a placeholder (the TEMPLATE case you hit);
3. the manifest is bound to a different model script;
4. the model script SHA-256 differs from `model_script_sha256`;
5. `approved_for_nltha` is not True;
6. any of the 16 check keys is not True:

```
etabs_topology_and_story_mapping_reviewed
wall_opening_and_coupling_beam_mesh_reviewed
wall_nonlinear_materials_and_reinforcement_cited_calibrated
frame_concrete_and_rebar_materials_reviewed
slab_and_diaphragm_idealization_compatible
area_and_frame_gravity_loads_reconciled_to_etabs
seismic_mass_reconciled_to_etabs_by_storey
support_conditions_and_foundation_assumptions_reviewed
is16700_initial_pdelta_plus_minus_cases_completed
p_delta_and_gravity_preload_completed
modal_periods_modes_and_mass_participation_reviewed
brace_fvd_brb_case_matches_selected_scenario
device_properties_cited_calibrated_or_devices_disabled
rayleigh_damping_and_device_damping_not_double_counted
single_element_and_wall_benchmark_checks_passed
record_pair_units_scales_and_nbc_limits_reviewed
```

Changing the checklist alone does not clear the material and FSAM part of the message. Those are separate configuration items (step 4).

## 2. See every blocker at once

`diagnose_nonlinear_readiness(config)` in `components/model/readiness.py` returns `{ready, blockers:[{code, message, fix}]}`. It is read-only. Codes: `model_script_missing`, `manifest_missing`, `manifest_unreadable`, `template_unbound`, `bound_to_other_model`, `model_sha_mismatch`, `not_approved`, `check_false:<key>` (one per false key), `material_file_missing`, `material_file_not_found`, `wall_fsam_tags_empty`, `parameters_not_reviewed`.

The gate keeps its original exceptions and messages and now appends this blocker list to each `RuntimeError`. The material, FSAM and `parameters_not_reviewed` blockers are reported in the list but do not by themselves add a new raise; the 16 checks and approval still decide the gate.

## 3. Create a model-bound UNAPPROVED draft

`bind_readiness_draft(template_path, model_script, out_path=None)` (non-GUI, same module) is what the readiness GUI `prepare` now calls. It copies the template, records the model path and SHA-256, and sets `approved_for_nltha` and every check to False. Default output: `OpenSees_Model_Readiness_Draft_<stem>_V134.json` beside the model.

- An existing unapproved draft already bound to the same model and SHA is returned unchanged, so human-saved evidence and checks are kept.
- A stale unapproved draft (model changed) is rebuilt with all checks False.
- An approved file is never overwritten; an unreadable existing file raises.
- A fresh draft still fails the gate with `not_approved` and all 16 `check_false:*` blockers. That is correct.

In the GUI (Prepare / inspect readiness checklist) the launch notice also lists open material, FSAM and parameter-review prerequisites. The notice code has not been run here (see Pending).

## 4. Material file and wall FSAM mappings (research draft only)

The gate needs `nonlinear_materials_file`, `nonlinear_wall_fsam_tags` and `nonlinear_parameters_reviewed` in `OpenSees_Complete_Model_Config_V118.json`. To get a starting point, use `components/nonlinear_time_history/material_draft.py` `prepare(source, destination, basis=...)`. It copies an assembled export, writes `Research_Wall_Parameters.json` and `Research_Wall_Materials.py`, sets the FSAM tags per wall property, and sets `nonlinear_parameters_reviewed` to False. The source export is not modified. The destination must not already exist.

The result is labeled `RESEARCH DRAFT; NOT PROJECT CALIBRATED OR APPROVED`. Values come from `material_source_sets.py` and the Material_Catalog, with references in `docs/00_RESEARCH_REFERENCES.md`:

| Ref | Use in the draft | Transfer restriction (from the reference table) |
|---|---|---|
| R01 Kolozvari, Orakcal, Wallace 2015, PEER 2015/12 | ConcreteCM/SteelMPF/FSAM web materials (Appendix B.3) | Do not import a PEER wall material card into all building walls as experimentally calibrated |
| R02 Kolozvari, Lopez, Massone 2023 | E-SFI-MVLEM-3D element formulation and benchmarks | Benchmarked shapes and loads are not equivalent to project openings, re-entrant core or connections |
| R05 Korkmaz and Kircil 2026 | Supplemental damping methodology (FVD) | Project damper stiffness, coefficient, exponent and installation must be demonstrated |
| R06 Ozkaya and Gurbuz 2026 | FVD arrangement sensitivity workflow | Composite-structure percentages are not predictions for the asymmetric RC building |
| R07 Guerrero Bobadilla et al. 2025 | BRB cumulative ductility and fatigue | Use actual BRB product geometry and tested protocol; DOI to verify |

These are PEER specimen and literature values, not project data. The draft's wall reinforcement (two curtains of 20 mm bars at 200 mm) is a placeholder layout, not extracted from drawings. FSAM geometry and reinforcement, 3D element constants, SHS properties and FVD/BRB parameters still need independent project sources.

Consequence for the checks: `wall_nonlinear_materials_and_reinforcement_cited_calibrated`, `frame_concrete_and_rebar_materials_reviewed`, `device_properties_cited_calibrated_or_devices_disabled` and `single_element_and_wall_benchmark_checks_passed` must stay False until you supply project evidence (reinforcement schedule, material tests or specification, device data) and review it. Having a draft file only removes `material_file_*` and `wall_fsam_tags_empty` blockers.

## 5. Human steps to approval

1. Run Prepare / inspect readiness to get the bound draft (step 3).
2. Create the research material draft (step 4), point the model config at it, and keep `nonlinear_parameters_reviewed` False.
3. Replace placeholders with project reinforcement and device calibration, with documents attached.
4. Complete each of the 16 reviews. Mark a check True only after its evidence exists.
5. Set `approved_for_nltha` True yourself, last. Any later change to the model script invalidates it (SHA mismatch).

Scope of the binding: approval is bound only to the model script path and its SHA-256. Edits made after approval to `OpenSees_Complete_Model_Config_V118.json`, to the file named by `nonlinear_materials_file`, or to the wall FSAM tags are NOT detected by the gate. `diagnose_nonlinear_readiness` may report material, FSAM or parameters-reviewed blockers while the gate passes; re-check those yourself before every run.

Follow-up (not implemented): make the gate raise on the codes in `_NON_GATE_BLOCKER_CODES` (`components/model/readiness.py`), or record a SHA-256 of the model config and material file in the manifest and compare it at run time.

## 6. ETABS ingestion guards

These apply when converting an ETABS model (`components/ui/application.py`, helpers in `components/validation/gravity_etabs_direct.py`, `components/model/assembly.py`):

| Guard | What it refuses or records |
|---|---|
| Working copy | In the active `components/` code, ETABS opens a temporary copy of the EDB; the source EDB is not opened or modified. The copy is removed after ETABS exits (short bounded retry, then a logged warning; never raises). Runtime copies under saved projects are not covered; see section 8. |
| Units read-back | After setting units, the present units are read back; a mismatch raises instead of continuing in the wrong units. |
| Dropped points | Failed point-coordinate or point-diaphragm reads are collected and raise `DroppedPointsError`; no silent skipping. A nonzero trailing return code on a coordinate read now counts as dropped. |
| `assembly_errors` | Unparseable or nonzero-return material rows are recorded in the report's `assembly_errors`, which is fatal in the worker via `validate_converter_report`. |
| Connect failure | On failure after ETABS starts, the model is closed and ETABS exits; the original error is the one raised. |

## 7. What each kind of success means

| Result | Means | Does not mean |
|---|---|---|
| Solver success (run finishes, no divergence) | OpenSees converged for that model and record | ETABS equivalence, validated components, code compliance |
| ETABS equivalence | Mass, gravity, periods and geometry agree with ETABS within stated tolerance | The nonlinear components are valid |
| Component validation | Single-element and wall benchmarks pass against test data | Whole-building behavior or code acceptance |
| Code acceptance (NBC 105:2025) | Reviewed against clause limits (drift, torsion, record rules) by the responsible engineer | Anything about solver convergence |

No solver PASS is engineering acceptance.

## 8. PENDING (not run)

- Native Windows and ETABS COM runs of the Task 3 ingestion guards (OpenFile on the copy, present-units read-back, side-file cleanup, linked-file paths from the copy location).
- tkinter GUI behavior (readiness GUI prepare and launch notice); the sandbox has no tkinter.
- Runtime copies under saved projects (for example `Saved_Project_V156/OpenSees_Runtime_V118/`, launched by `17_BUILDING_FULL_NONLINEAR.py`) keep the pre-branch readiness gate and ingestion until the runtime is refreshed; the `application.py` there still opens the original EDB in place. The statement that the source EDB is not opened applies to the active `components/` code only.
- Full-model NLTHA on the project building.
- Project reinforcement schedule and FVD/BRB calibration.
- All 16 checks and `approved_for_nltha` remain False until you complete them.

Evidence notes: `engineering/agent_edits/20261120_nltha_readiness_gate.md`, `engineering/agent_edits/20261120_etabs_ingest_guards.md`.

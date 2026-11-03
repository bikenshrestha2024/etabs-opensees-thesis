# Verification_V144/Available_Inputs_Inventory.json

**Source:** [Verification_V144/Available_Inputs_Inventory.json](../../../../Verification_V144/Available_Inputs_Inventory.json)
**Classification:** VALIDATION_EVIDENCE
**SHA-256 (source bytes):** 5281ac152e93c87459f3dee663219692b7346b916a125a849555f9cd4e3c3b78
**Size:** 2246621 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.folder | str |
| $.config_file | str |
| $.configuration | object |
| $.configuration.gravity_factors | object |
| $.configuration.gravity_factors.Self Weight | number |
| $.configuration.gravity_factors.Dead | number |
| $.configuration.gravity_factors.DL | number |
| $.configuration.gravity_factors.Super Dead | number |
| $.configuration.gravity_factors.SDead | number |
| $.configuration.gravity_factors.Floor Finish | number |
| $.configuration.gravity_factors.Wall | number |
| $.configuration.gravity_factors.Partition | number |
| $.configuration.gravity_factors.Live | number |
| $.configuration.gravity_factors.Roof Live | number |
| $.configuration.mass_factors | object |
| $.configuration.mass_factors.Self Weight | number |
| $.configuration.mass_factors.Dead | number |
| $.configuration.mass_factors.DL | number |
| $.configuration.mass_factors.Super Dead | number |
| $.configuration.mass_factors.SDead | number |
| $.configuration.mass_factors.Floor Finish | number |
| $.configuration.mass_factors.Wall | number |
| $.configuration.mass_factors.Partition | number |
| $.configuration.mass_factors.Live | number |
| $.configuration.mass_factors.Roof Live | number |
| $.configuration.slab_bending_factor | number |
| $.configuration.slab_stiffness_source | str |
| $.configuration.frame_section_mapping | object |
| $.configuration.frame_section_mapping.Col 1100*1100 | str |
| $.configuration.frame_section_mapping.Col 1250*1250 | str |
| $.configuration.frame_section_mapping.Beam 600*800 | str |
| $.configuration.frame_section_mapping.350*350*16 SHS | str |
| $.configuration.nonlinear_parameters_reviewed | boolean |
| $.configuration.nonlinear_materials_file | str |
| $.configuration.nonlinear_wall_fsam_tags | object(empty) |
| $.configuration.section_overrides | object(empty) |
| $.configuration.area_property_overrides | object(empty) |
| $.configuration.slab_bending_factor_sls | number |
| $.configuration.floor_subdivisions | integer |
| $.assembly | object |
| $.assembly.version | integer |
| $.assembly.assembly_errors | array |
| $.assembly.assembly_errors[] | array(empty) |
| $.assembly.warnings | array |
| $.assembly.warnings[] | str |
| $.assembly.analysis_ready | boolean |
| $.assembly.elastic_scope | str |
| $.assembly.nonlinear_ready | boolean |
| $.assembly.storey_gravity | object |
| $.assembly.storey_gravity.rows | array |
| $.assembly.storey_gravity.rows[] | object |
| $.assembly.storey_gravity.rows[].storey | str |
| $.assembly.storey_gravity.rows[].elevation_m | number |
| $.assembly.storey_gravity.rows[].beam_self_weight_kN | number |
| $.assembly.storey_gravity.rows[].column_self_weight_kN | number |
| $.assembly.storey_gravity.rows[].brace_self_weight_kN | number |
| $.assembly.storey_gravity.rows[].shear_wall_self_weight_kN | number |
| $.assembly.storey_gravity.rows[].slab_self_weight_kN | number |
| $.assembly.storey_gravity.rows[].other_self_weight_kN | number |
| $.assembly.storey_gravity.rows[].floor_finish_kN | number |
| $.assembly.storey_gravity.rows[].partition_kN | number |
| $.assembly.storey_gravity.rows[].other_dead_kN | number |
| $.assembly.storey_gravity.rows[].live_kN | number |
| $.assembly.storey_gravity.rows[].roof_live_kN | number |
| $.assembly.storey_gravity.rows[].unclassified_kN | number |
| $.assembly.storey_gravity.rows[].dead_total_kN | number |
| $.assembly.storey_gravity.rows[].live_total_kN | number |
| $.assembly.storey_gravity.rows[].unfactored_total_kN | number |
| $.assembly.storey_gravity.rows[].applied_dead_kN | number |
| $.assembly.storey_gravity.rows[].applied_live_kN | number |
| $.assembly.storey_gravity.rows[].applied_unclassified_kN | number |
| $.assembly.storey_gravity.rows[].applied_total_kN | number |
| $.assembly.storey_gravity.details | array |
| $.assembly.storey_gravity.details[] | object |
| $.assembly.storey_gravity.details[].storey | str |
| $.assembly.storey_gravity.details[].source | str |
| $.assembly.storey_gravity.details[].component | str |
| $.assembly.storey_gravity.details[].pattern | str |
| $.assembly.storey_gravity.details[].classification | str |
| $.assembly.storey_gravity.details[].load_class | str |
| $.assembly.storey_gravity.details[].gravity_factor | number |
| $.assembly.storey_gravity.details[].unfactored_kN | number |
| $.assembly.storey_gravity.details[].applied_kN | number |
| $.assembly.storey_gravity.total_applied_kN | number |
| $.assembly.storey_gravity.assembled_total_kN | number |
| $.assembly.storey_gravity.reconciliation_error_kN | number |
| $.assembly.storey_gravity.convention | str |
| $.assembly.load_path_audit | object |
| $.assembly.load_path_audit.area_load_records | array |
| $.assembly.load_path_audit.area_load_records[] | object |
| $.assembly.load_path_audit.area_load_records[].object | str |
| $.assembly.load_path_audit.area_load_records[].pattern | str |
| $.assembly.load_path_audit.area_load_records[].area_m2 | number |
| $.assembly.load_path_audit.area_load_records[].q_global_z_kN_m2 | number |
| $.assembly.load_path_audit.area_load_records[].unfactored_vertical_force_kN | number |
| $.assembly.load_path_audit.area_load_records[].resultant_and_moment_error | number |
| $.assembly.load_path_audit.area_load_records[].beam_wall_connection_nodes | integer |
| $.assembly.load_path_audit.area_load_records[].method | str |
| $.assembly.load_path_audit.area_load_records[].gravity_factor | number |
| $.assembly.load_path_audit.area_load_records[].seismic_mass_weight_factor | number |
| $.assembly.load_path_audit.area_unfactored_global_z_kN_by_pattern | object |
| $.assembly.load_path_audit.area_unfactored_global_z_kN_by_pattern.Floor Finish | number |
| $.assembly.load_path_audit.area_unfactored_global_z_kN_by_pattern.Live | number |
| $.assembly.load_path_audit.area_unfactored_global_z_kN_by_pattern.Partition | number |
| $.assembly.load_path_audit.diaphragms | array |
| $.assembly.load_path_audit.diaphragms[] | object |
| $.assembly.load_path_audit.diaphragms[].master | integer |
| $.assembly.load_path_audit.diaphragms[].z_m | number |
| $.assembly.load_path_audit.diaphragms[].slaves | integer |
| $.assembly.load_path_audit.diaphragms[].constrained_dofs | array |
| $.assembly.load_path_audit.diaphragms[].constrained_dofs[] | integer |
| $.assembly.load_path_audit.diaphragms[].unconstrained_slab_vertical_dof | integer |
| $.assembly.load_path_audit.diaphragms[].kinematics | str |
| $.assembly.load_path_audit.coverage | object |
| $.assembly.load_path_audit.coverage.floor_nodes | integer |
| $.assembly.load_path_audit.coverage.in_rigid_diaph | integer |
| $.assembly.load_path_audit.coverage.without_rigid_diaph | integer |
| $.assembly.load_path_audit.notes | array |
| $.assembly.load_path_audit.notes[] | str |
| $.assembly.load_path_audit.load_path | str |
| $.assembly.load_path_audit.limitations | array |
| $.assembly.load_path_audit.limitations[] | str |
| $.assembly.frame_objects | integer |
| $.assembly.frame_segments | integer |
| $.assembly.area_objects | integer |
| $.assembly.shell_mesh_cells | integer |
| $.assembly.source_nodes | integer |
| $.assembly.mesh_nodes | integer |
| $.assembly.excluded_none_section_frame_objects | array |
| $.assembly.excluded_none_section_frame_objects[] | str |
| $.assembly.total_downward_load_kN | number |
| $.assembly.total_seismic_weight_including_fixed_nodes_kN | number |
| $.assembly.active_horizontal_seismic_weight_kN | number |
| $.assembly.gravity_by_pattern_kN | object |
| $.assembly.gravity_by_pattern_kN.Floor Finish | number |
| $.assembly.gravity_by_pattern_kN.Live | number |
| $.assembly.gravity_by_pattern_kN.Partition | number |
| $.assembly.gravity_by_pattern_kN.Wall | number |
| $.assembly.gravity_by_pattern_kN.Self Weight | number |
| $.assembly.elastic_assembled | boolean |
| $.assembly.story_ledger_active_weight_kN | number |
| $.assembly.story_ledger_mass_error_percent | number |
| $.gravity | object |
| $.gravity.steps | integer |
| $.gravity.applied_vertical_load_kN | number |
| $.gravity.support_vertical_reaction_kN | number |
| $.gravity.equilibrium_error_percent | number |
| $.gravity.equilibrium_tolerance_percent | number |
| $.gravity.max_downward_vertical_displacement_m | number |
| $.gravity.elapsed_seconds_before_freeze | number |
| $.gravity.gravity_frozen | boolean |
| $.gravity.elapsed_seconds | number |
| $.gravity.diaphragm_kinematics | object |
| $.gravity.diaphragm_kinematics.max_inplane_constraint_residual | number |
| $.gravity.diaphragm_kinematics.units | str |
| $.gravity.gravity_context | object |
| $.gravity.gravity_context.profile | str |
| $.gravity.gravity_context.factors | object |
| $.gravity.gravity_context.factors.Self Weight | number |
| $.gravity.gravity_context.factors.Dead | number |
| $.gravity.gravity_context.factors.DL | number |
| $.gravity.gravity_context.factors.Super Dead | number |
| $.gravity.gravity_context.factors.SDead | number |
| $.gravity.gravity_context.factors.Floor Finish | number |
| $.gravity.gravity_context.factors.Wall | number |
| $.gravity.gravity_context.factors.Partition | number |
| $.gravity.gravity_context.factors.Live | number |
| $.gravity.gravity_context.factors.Roof Live | number |
| $.gravity.gravity_context.scope | str |
| $.gravity.limit_state | str |
| $.model_counts | object |
| $.model_counts.nodes | integer |
| $.model_counts.frames | integer |
| $.model_counts.shells | integer |
| $.model_counts.diaphragms | integer |
| $.gravity_by_pattern_kN | object |
| $.gravity_by_pattern_kN.Floor Finish | number |
| $.gravity_by_pattern_kN.Live | number |
| $.gravity_by_pattern_kN.Partition | number |
| $.gravity_by_pattern_kN.Wall | number |
| $.gravity_by_pattern_kN.Self Weight | number |
| $.total_downward_load_kN | number |
| $.available_evidence | object |
| $.available_evidence.etabs_topology_and_story_mapping_reviewed | str |
| $.available_evidence.wall_opening_and_coupling_beam_mesh_reviewed | str |
| $.available_evidence.area_and_frame_gravity_loads_reconciled_to_etabs | str |
| $.available_evidence.seismic_mass_reconciled_to_etabs_by_storey | str |
| $.available_evidence.support_conditions_and_foundation_assumptions_reviewed | str |
| $.available_evidence.p_delta_and_gravity_preload_completed | str |
| $.available_evidence.modal_periods_modes_and_mass_participation_reviewed | str |
| $.available_evidence.brace_fvd_brb_case_matches_selected_scenario | str |
| $.available_evidence.slab_and_diaphragm_idealization_compatible | str |
| $.how_to_obtain_missing_values | object |
| $.how_to_obtain_missing_values.wall_nonlinear_materials_and_reinforcement_cited_calibrated | str |
| $.how_to_obtain_missing_values.frame_concrete_and_rebar_materials_reviewed | str |
| $.how_to_obtain_missing_values.is16700_initial_pdelta_plus_minus_cases_completed | str |
| $.how_to_obtain_missing_values.device_properties_cited_calibrated_or_devices_disabled | str |
| $.how_to_obtain_missing_values.rayleigh_damping_and_device_damping_not_double_counted | str |
| $.how_to_obtain_missing_values.single_element_and_wall_benchmark_checks_passed | str |
| $.how_to_obtain_missing_values.wall_opening_and_coupling_beam_mesh_reviewed | str |
| $.how_to_obtain_missing_values.area_and_frame_gravity_loads_reconciled_to_etabs | str |
| $.how_to_obtain_missing_values.seismic_mass_reconciled_to_etabs_by_storey | str |
| $.how_to_obtain_missing_values.record_pair_units_scales_and_nbc_limits_reviewed | str |

## Interpretation and provenance

- Source of truth: the original JSON file at the path above. This generated reference never changes original data.
- This is an OBSERVED FIELD INVENTORY, not a formal JSON Schema or proof every nested record has identical keys.
- Original units, code edition, specimen/ETABS source, record ID, solver version and experimental status must be checked within the source file or linked manifest.
- A value without documented units/source must be classified UNVERIFIED, not automatically assumed kN-m-s.
- For historical outputs do not use to populate current run configuration or calibrated material parameters.
- Material/source specimens are not project-approved RC bar schedules or manufacturer-qualified dampers.
- External data may be private. This script runs offline and does not upload file contents.

## Validation requirements

- Confirm valid UTF-8 JSON and expected field/type/units against the producing program.
- Verify hashes, compare input and output manifests, and preserve experiment/case identity.
- For nonlinear runs check G00–G10 acceptance gates and explicit failure/incomplete statuses.

[All JSON files](../../00_ALL_JSON_FILES.md) · [Research citations](../../../00_RESEARCH_REFERENCES.md)

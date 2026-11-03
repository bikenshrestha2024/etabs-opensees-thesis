# Saved_Project_V156/OpenSees_Complete_Export_Report_V118.json

**Source:** [Saved_Project_V156/OpenSees_Complete_Export_Report_V118.json](../../../../Saved_Project_V156/OpenSees_Complete_Export_Report_V118.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 3be45f08e306eb317b83d3d7481333d316c2abe048f91401e4d6aa5879dc5f5f
**Size:** 2108252 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.version | integer |
| $.assembly_errors | array |
| $.assembly_errors[] | array(empty) |
| $.warnings | array |
| $.warnings[] | str |
| $.analysis_ready | boolean |
| $.elastic_scope | str |
| $.nonlinear_ready | boolean |
| $.storey_gravity | object |
| $.storey_gravity.rows | array |
| $.storey_gravity.rows[] | object |
| $.storey_gravity.rows[].storey | str |
| $.storey_gravity.rows[].elevation_m | number |
| $.storey_gravity.rows[].beam_self_weight_kN | number |
| $.storey_gravity.rows[].column_self_weight_kN | number |
| $.storey_gravity.rows[].brace_self_weight_kN | number |
| $.storey_gravity.rows[].shear_wall_self_weight_kN | number |
| $.storey_gravity.rows[].slab_self_weight_kN | number |
| $.storey_gravity.rows[].other_self_weight_kN | number |
| $.storey_gravity.rows[].floor_finish_kN | number |
| $.storey_gravity.rows[].partition_kN | number |
| $.storey_gravity.rows[].other_dead_kN | number |
| $.storey_gravity.rows[].live_kN | number |
| $.storey_gravity.rows[].roof_live_kN | number |
| $.storey_gravity.rows[].unclassified_kN | number |
| $.storey_gravity.rows[].dead_total_kN | number |
| $.storey_gravity.rows[].live_total_kN | number |
| $.storey_gravity.rows[].unfactored_total_kN | number |
| $.storey_gravity.rows[].applied_dead_kN | number |
| $.storey_gravity.rows[].applied_live_kN | number |
| $.storey_gravity.rows[].applied_unclassified_kN | number |
| $.storey_gravity.rows[].applied_total_kN | number |
| $.storey_gravity.details | array |
| $.storey_gravity.details[] | object |
| $.storey_gravity.details[].storey | str |
| $.storey_gravity.details[].source | str |
| $.storey_gravity.details[].component | str |
| $.storey_gravity.details[].pattern | str |
| $.storey_gravity.details[].classification | str |
| $.storey_gravity.details[].load_class | str |
| $.storey_gravity.details[].gravity_factor | number |
| $.storey_gravity.details[].unfactored_kN | number |
| $.storey_gravity.details[].applied_kN | number |
| $.storey_gravity.total_applied_kN | number |
| $.storey_gravity.assembled_total_kN | number |
| $.storey_gravity.reconciliation_error_kN | number |
| $.storey_gravity.convention | str |
| $.load_path_audit | object |
| $.load_path_audit.area_load_records | array |
| $.load_path_audit.area_load_records[] | object |
| $.load_path_audit.area_load_records[].object | str |
| $.load_path_audit.area_load_records[].pattern | str |
| $.load_path_audit.area_load_records[].area_m2 | number |
| $.load_path_audit.area_load_records[].q_global_z_kN_m2 | number |
| $.load_path_audit.area_load_records[].unfactored_vertical_force_kN | number |
| $.load_path_audit.area_load_records[].resultant_and_moment_error | number |
| $.load_path_audit.area_load_records[].beam_wall_connection_nodes | integer |
| $.load_path_audit.area_load_records[].method | str |
| $.load_path_audit.area_load_records[].gravity_factor | number |
| $.load_path_audit.area_load_records[].seismic_mass_weight_factor | number |
| $.load_path_audit.area_unfactored_global_z_kN_by_pattern | object |
| $.load_path_audit.area_unfactored_global_z_kN_by_pattern.Floor Finish | number |
| $.load_path_audit.area_unfactored_global_z_kN_by_pattern.Live | number |
| $.load_path_audit.area_unfactored_global_z_kN_by_pattern.Partition | number |
| $.load_path_audit.diaphragms | array |
| $.load_path_audit.diaphragms[] | object |
| $.load_path_audit.diaphragms[].master | integer |
| $.load_path_audit.diaphragms[].z_m | number |
| $.load_path_audit.diaphragms[].slaves | integer |
| $.load_path_audit.diaphragms[].constrained_dofs | array |
| $.load_path_audit.diaphragms[].constrained_dofs[] | integer |
| $.load_path_audit.diaphragms[].unconstrained_slab_vertical_dof | integer |
| $.load_path_audit.diaphragms[].kinematics | str |
| $.load_path_audit.coverage | object |
| $.load_path_audit.coverage.floor_nodes | integer |
| $.load_path_audit.coverage.in_rigid_diaph | integer |
| $.load_path_audit.coverage.without_rigid_diaph | integer |
| $.load_path_audit.notes | array |
| $.load_path_audit.notes[] | str |
| $.load_path_audit.load_path | str |
| $.load_path_audit.limitations | array |
| $.load_path_audit.limitations[] | str |
| $.frame_objects | integer |
| $.frame_segments | integer |
| $.area_objects | integer |
| $.shell_mesh_cells | integer |
| $.source_nodes | integer |
| $.mesh_nodes | integer |
| $.excluded_none_section_frame_objects | array |
| $.excluded_none_section_frame_objects[] | str |
| $.total_downward_load_kN | number |
| $.total_seismic_weight_including_fixed_nodes_kN | number |
| $.active_horizontal_seismic_weight_kN | number |
| $.gravity_by_pattern_kN | object |
| $.gravity_by_pattern_kN.Floor Finish | number |
| $.gravity_by_pattern_kN.Live | number |
| $.gravity_by_pattern_kN.Partition | number |
| $.gravity_by_pattern_kN.Wall | number |
| $.gravity_by_pattern_kN.Self Weight | number |
| $.elastic_assembled | boolean |
| $.story_ledger_active_weight_kN | number |
| $.story_ledger_mass_error_percent | number |

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

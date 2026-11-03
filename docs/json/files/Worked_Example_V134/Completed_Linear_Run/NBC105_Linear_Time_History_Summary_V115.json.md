# Worked_Example_V134/Completed_Linear_Run/NBC105_Linear_Time_History_Summary_V115.json

**Source:** [Worked_Example_V134/Completed_Linear_Run/NBC105_Linear_Time_History_Summary_V115.json](../../../../../Worked_Example_V134/Completed_Linear_Run/NBC105_Linear_Time_History_Summary_V115.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** ffe23e5f20be172a1ce28936bb2658fd2cc5d57f948301d5694d14732fea2e0e
**Size:** 15785 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.standard | str |
| $.analysis | str |
| $.input_mode | str |
| $.directional_scope | str |
| $.record_metadata | object |
| $.record_metadata.site_soil | str |
| $.record_metadata.period_range_s | array |
| $.record_metadata.period_range_s[] | number |
| $.record_metadata.record_set | str |
| $.model_length_unit | str |
| $.model_acceleration_unit | str |
| $.clauses | array |
| $.clauses[] | str |
| $.model_script | str |
| $.limit_state_context | str |
| $.torsion_sensitive | boolean |
| $.record_pairs | integer |
| $.individual_record_count | integer |
| $.motion_case_count | integer |
| $.pair_aggregation_guidance | str |
| $.response_aggregation_by_record_set | object |
| $.response_aggregation_by_record_set.all_selected_pairs | object |
| $.response_aggregation_by_record_set.all_selected_pairs.set | str |
| $.response_aggregation_by_record_set.all_selected_pairs.pair_count | integer |
| $.response_aggregation_by_record_set.all_selected_pairs.statistic | str |
| $.response_aggregation_by_record_set.all_selected_pairs.response_demands | object |
| $.response_aggregation_by_record_set.all_selected_pairs.response_demands.peak_roof_UX_m | number |
| $.response_aggregation_by_record_set.all_selected_pairs.response_demands.peak_roof_UY_m | number |
| $.response_aggregation_by_record_set.all_selected_pairs.response_demands.peak_story_drift_X | number |
| $.response_aggregation_by_record_set.all_selected_pairs.response_demands.peak_story_drift_Y | number |
| $.response_aggregation_by_record_set.all_selected_pairs.response_demands.drift_screen_X | str |
| $.response_aggregation_by_record_set.all_selected_pairs.response_demands.drift_screen_Y | str |
| $.response_aggregation_by_record_set.far_field_subset | object |
| $.response_aggregation_by_record_set.far_field_subset.set | str |
| $.response_aggregation_by_record_set.far_field_subset.pair_count | integer |
| $.response_aggregation_by_record_set.far_field_subset.statistic | str |
| $.response_aggregation_by_record_set.far_field_subset.response_demands | object |
| $.response_aggregation_by_record_set.far_field_subset.response_demands.peak_roof_UX_m | number |
| $.response_aggregation_by_record_set.far_field_subset.response_demands.peak_roof_UY_m | number |
| $.response_aggregation_by_record_set.far_field_subset.response_demands.peak_story_drift_X | number |
| $.response_aggregation_by_record_set.far_field_subset.response_demands.peak_story_drift_Y | number |
| $.response_aggregation_by_record_set.far_field_subset.response_demands.drift_screen_X | str |
| $.response_aggregation_by_record_set.far_field_subset.response_demands.drift_screen_Y | str |
| $.pair_level_orientation_envelopes | array |
| $.pair_level_orientation_envelopes[] | object |
| $.pair_level_orientation_envelopes[].pair_id | str |
| $.pair_level_orientation_envelopes[].field_type | str |
| $.pair_level_orientation_envelopes[].orientations_included | array |
| $.pair_level_orientation_envelopes[].orientations_included[] | str |
| $.pair_level_orientation_envelopes[].peak_roof_UX_m | number |
| $.pair_level_orientation_envelopes[].peak_roof_UY_m | number |
| $.pair_level_orientation_envelopes[].peak_story_drift_X | number |
| $.pair_level_orientation_envelopes[].peak_story_drift_Y | number |
| $.X_only_screening_envelope | null |
| $.T1_x_s | number |
| $.T1_y_s | number |
| $.Tn_x_s | number |
| $.Tn_y_s | number |
| $.damping_target_percent | number |
| $.time_step_rule | str |
| $.member_action_rule | str |
| $.records | array |
| $.records[] | object |
| $.records[].case | str |
| $.records[].pair_id | str |
| $.records[].field_type | str |
| $.records[].orientation | str |
| $.records[].scale_factor | number |
| $.records[].acceleration_units | str |
| $.records[].record_dt_min_s | number |
| $.records[].analysis_dt_s | number |
| $.records[].duration_s | number |
| $.records[].steps | integer |
| $.records[].peak_roof_UX_m | number |
| $.records[].peak_roof_UY_m | number |
| $.records[].minimum_roof_UX_m | number |
| $.records[].maximum_roof_UX_m | number |
| $.records[].minimum_roof_UY_m | number |
| $.records[].maximum_roof_UY_m | number |
| $.records[].peak_story_drift_X | number |
| $.records[].peak_story_drift_Y | number |
| $.records[].minimum_story_drift_X | number |
| $.records[].maximum_story_drift_X | number |
| $.records[].minimum_story_drift_Y | number |
| $.records[].maximum_story_drift_Y | number |
| $.records[].drift_limit_ratio | number |
| $.records[].drift_screen_X | str |
| $.records[].drift_screen_Y | str |
| $.records[].rayleigh_alphaM_s-1 | number |
| $.records[].rayleigh_betaKcommitted_s | number |
| $.records[].rayleigh_calibration_periods_s | array |
| $.records[].rayleigh_calibration_periods_s[] | number |
| $.records[].checked_modal_damping | array |
| $.records[].checked_modal_damping[] | object |
| $.records[].checked_modal_damping[].mode | integer |
| $.records[].checked_modal_damping[].omega_rad_s | number |
| $.records[].checked_modal_damping[].period_s | number |
| $.records[].checked_modal_damping[].damping_ratio_percent | number |
| $.records[].history_csv | str |
| $.records[].master_peak_story_drift_X | number |
| $.records[].floor_edge_peak_story_drift_X | number |
| $.records[].master_peak_story_drift_Y | number |
| $.records[].floor_edge_peak_story_drift_Y | number |
| $.records[].performance | object |
| $.records[].performance.case | str |
| $.records[].performance.analysis | str |
| $.records[].performance.status | str |
| $.records[].performance.error | null |
| $.records[].performance.started_at | str |
| $.records[].performance.finished_at | str |
| $.records[].performance.elapsed_seconds | number |
| $.records[].performance.stages_seconds | object |
| $.records[].performance.stages_seconds.model_and_gravity | number |
| $.records[].performance.stages_seconds.damping_eigenanalysis | number |
| $.records[].performance.stages_seconds.transient_with_recording | number |
| $.records[].performance.stages_seconds.case_exports_and_drift | number |
| $.records[].performance.accepted_internal_steps | integer |
| $.records[].performance.recording_seconds | number |
| $.records[].performance.solver_diagnostics | object(empty) |
| $.records[].performance.scope | str |
| $.elapsed_seconds | number |
| $.selected_pair_ids | array |
| $.selected_pair_ids[] | str |
| $.preliminary_selection | boolean |
| $.assessment_scope | str |

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

[All JSON files](../../../00_ALL_JSON_FILES.md) · [Research citations](../../../../00_RESEARCH_REFERENCES.md)

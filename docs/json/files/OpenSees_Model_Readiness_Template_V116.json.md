# OpenSees_Model_Readiness_Template_V116.json

**Source:** [OpenSees_Model_Readiness_Template_V116.json](../../../OpenSees_Model_Readiness_Template_V116.json)
**Classification:** ETABS_MODEL_OR_SOURCE_METADATA
**SHA-256 (source bytes):** d38e7f35e128880109d52e2014146406021753f7689061dc331b83d0750bafd5
**Size:** 1437 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.schema | str |
| $.approved_for_nltha | boolean |
| $.model_script | str |
| $.project | str |
| $.checks | object |
| $.checks.etabs_topology_and_story_mapping_reviewed | boolean |
| $.checks.wall_opening_and_coupling_beam_mesh_reviewed | boolean |
| $.checks.wall_nonlinear_materials_and_reinforcement_cited_calibrated | boolean |
| $.checks.frame_concrete_and_rebar_materials_reviewed | boolean |
| $.checks.slab_and_diaphragm_idealization_compatible | boolean |
| $.checks.area_and_frame_gravity_loads_reconciled_to_etabs | boolean |
| $.checks.seismic_mass_reconciled_to_etabs_by_storey | boolean |
| $.checks.support_conditions_and_foundation_assumptions_reviewed | boolean |
| $.checks.is16700_initial_pdelta_plus_minus_cases_completed | boolean |
| $.checks.p_delta_and_gravity_preload_completed | boolean |
| $.checks.modal_periods_modes_and_mass_participation_reviewed | boolean |
| $.checks.brace_fvd_brb_case_matches_selected_scenario | boolean |
| $.checks.device_properties_cited_calibrated_or_devices_disabled | boolean |
| $.checks.rayleigh_damping_and_device_damping_not_double_counted | boolean |
| $.checks.single_element_and_wall_benchmark_checks_passed | boolean |
| $.checks.record_pair_units_scales_and_nbc_limits_reviewed | boolean |
| $.review_notes | str |

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

[All JSON files](../00_ALL_JSON_FILES.md) · [Research citations](../../00_RESEARCH_REFERENCES.md)

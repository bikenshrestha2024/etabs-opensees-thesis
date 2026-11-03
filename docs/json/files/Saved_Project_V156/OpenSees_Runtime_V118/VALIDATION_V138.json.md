# Saved_Project_V156/OpenSees_Runtime_V118/VALIDATION_V138.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/VALIDATION_V138.json](../../../../../Saved_Project_V156/OpenSees_Runtime_V118/VALIDATION_V138.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** ca3abb5579a0b963ac9c6df15ee664cebf165628152ab57f220c47cd454e804c
**Size:** 639 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.parsed_python_sources | integer |
| $.mapped_modules_imported | integer |
| $.gravity_plot_canvas_px | array |
| $.gravity_plot_canvas_px[] | integer |
| $.comparison_GUI_built | boolean |
| $.exploratory_GUI_built | boolean |
| $.building_transient_trials | object |
| $.building_transient_trials.XY | object |
| $.building_transient_trials.XY.duration_s | number |
| $.building_transient_trials.XY.requested_steps | integer |
| $.building_transient_trials.XY.completed | boolean |
| $.building_transient_trials.YX | object |
| $.building_transient_trials.YX.duration_s | number |
| $.building_transient_trials.YX.requested_steps | integer |
| $.building_transient_trials.YX.completed | boolean |
| $.building_walls_in_completed_trials | str |
| $.full_FSAM_building | str |
| $.full_building_record_run | boolean |
| $.portable_history_geometry_checks | str |

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

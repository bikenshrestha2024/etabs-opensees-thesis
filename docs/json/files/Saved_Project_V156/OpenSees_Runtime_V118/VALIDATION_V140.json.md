# Saved_Project_V156/OpenSees_Runtime_V118/VALIDATION_V140.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/VALIDATION_V140.json](../../../../../Saved_Project_V156/OpenSees_Runtime_V118/VALIDATION_V140.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 27f1639b22929bc0df322109848b068d5b2a3d24822a2e3882cbfc72e315e775
**Size:** 1166 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.load_set_parser | str |
| $.python_syntax | str |
| $.log_scrollbars | str |
| $.readiness_autofill | str |
| $.recovered_trial | object |
| $.recovered_trial.cases | array |
| $.recovered_trial.cases[] | object |
| $.recovered_trial.cases[].orientation | str |
| $.recovered_trial.cases[].status | str |
| $.recovered_trial.cases[].recorded_time_s | number |
| $.recovered_trial.cases[].requested_trial_duration_s | number |
| $.recovered_trial.cases[].requested_trial_reached | boolean |
| $.recovered_trial.cases[].accepted_rows | integer |
| $.recovered_trial.cases[].peak_roof_UX_m | number |
| $.recovered_trial.cases[].peak_roof_UY_m | number |
| $.recovered_trial.cases[].scope | str |
| $.recovered_trial.cases[].note | str |
| $.recovered_trial.source_run | str |
| $.recovered_trial.scope | str |
| $.recovered_trial.recovered_at | str |
| $.actual_short_opensees_summary | str |
| $.mrsm_copy_scrollbars | str |
| $.live_etabs | str |

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

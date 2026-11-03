# Saved_Project_V156/OpenSees_Runtime_V118/VALIDATION_V137.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/VALIDATION_V137.json](../../../../../Saved_Project_V156/OpenSees_Runtime_V118/VALIDATION_V137.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 92c6e25fa3a151f502e821ac4400d259177870de3a1d3f348d1b1632dccb25b4
**Size:** 919 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.release | integer |
| $.parsed_python_sources | integer |
| $.imported_mapped_modules | integer |
| $.opensees_version | str |
| $.portal_nonlinear_completed | boolean |
| $.gravity_equilibrium_kN | number |
| $.record_duration_s | number |
| $.dt_s | number |
| $.peak_roof_elastic_mm | number |
| $.peak_roof_nonlinear_mm | number |
| $.wall_element_command_smoke_check | str |
| $.time_step_verification | object |
| $.time_step_verification.dt_s | number |
| $.time_step_verification.refined_dt_s | number |
| $.time_step_verification.relative_changes | object |
| $.time_step_verification.relative_changes.linear | number |
| $.time_step_verification.relative_changes.nonlinear | number |
| $.time_step_verification.both_complete | boolean |
| $.time_step_verification.scope | str |
| $.scope | str |

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

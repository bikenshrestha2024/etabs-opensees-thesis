# Recovered_1s_Trial_V140/Recovered_Summary.json

**Source:** [Recovered_1s_Trial_V140/Recovered_Summary.json](../../../../Recovered_1s_Trial_V140/Recovered_Summary.json)
**Classification:** RUN_RESULT_OR_REPORT
**SHA-256 (source bytes):** b35cd079fede5799af4475c324b88fb0e2bde376e2704d2ded226c994474691c
**Size:** 844 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.cases | array |
| $.cases[] | object |
| $.cases[].orientation | str |
| $.cases[].status | str |
| $.cases[].recorded_time_s | number |
| $.cases[].requested_trial_duration_s | number |
| $.cases[].requested_trial_reached | boolean |
| $.cases[].accepted_rows | integer |
| $.cases[].peak_roof_UX_m | number |
| $.cases[].peak_roof_UY_m | number |
| $.cases[].scope | str |
| $.cases[].note | str |
| $.source_run | str |
| $.scope | str |
| $.recovered_at | str |

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

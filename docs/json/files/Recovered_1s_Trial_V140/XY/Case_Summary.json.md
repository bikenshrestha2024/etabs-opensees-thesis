# Recovered_1s_Trial_V140/XY/Case_Summary.json

**Source:** [Recovered_1s_Trial_V140/XY/Case_Summary.json](../../../../../Recovered_1s_Trial_V140/XY/Case_Summary.json)
**Classification:** RUN_RESULT_OR_REPORT
**SHA-256 (source bytes):** 0687274e8b5ad3e893354a93bc62ead153cdab4ee804185da721ae3cf1648bfa
**Size:** 529 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.orientation | str |
| $.status | str |
| $.recorded_time_s | number |
| $.requested_trial_duration_s | number |
| $.requested_trial_reached | boolean |
| $.accepted_rows | integer |
| $.peak_roof_UX_m | number |
| $.peak_roof_UY_m | number |
| $.scope | str |
| $.note | str |

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

# PACKAGED_MOTION_PAIRS_V141.json

**Source:** [PACKAGED_MOTION_PAIRS_V141.json](../../../PACKAGED_MOTION_PAIRS_V141.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 231d58095874f98d74bd01f13c231784b83e19ef051770d1296a7134de2627a3
**Size:** 3052 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.pairs | array |
| $.pairs[] | object |
| $.pairs[].pair_id | str |
| $.pairs[].field_type | str |
| $.pairs[].x_path | str |
| $.pairs[].y_path | str |
| $.pairs[].x_units | str |
| $.pairs[].x_dt_s | number |
| $.pairs[].x_samples | integer |
| $.pairs[].y_units | str |
| $.pairs[].y_dt_s | number |
| $.pairs[].y_samples | integer |
| $.missing_sources | array |
| $.missing_sources[] | array(empty) |
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

[All JSON files](../00_ALL_JSON_FILES.md) · [Research citations](../../00_RESEARCH_REFERENCES.md)

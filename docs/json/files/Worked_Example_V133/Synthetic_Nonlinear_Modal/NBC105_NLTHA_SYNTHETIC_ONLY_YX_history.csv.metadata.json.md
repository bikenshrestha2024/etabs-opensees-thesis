# Worked_Example_V133/Synthetic_Nonlinear_Modal/NBC105_NLTHA_SYNTHETIC_ONLY_YX_history.csv.metadata.json

**Source:** [Worked_Example_V133/Synthetic_Nonlinear_Modal/NBC105_NLTHA_SYNTHETIC_ONLY_YX_history.csv.metadata.json](../../../../../Worked_Example_V133/Synthetic_Nonlinear_Modal/NBC105_NLTHA_SYNTHETIC_ONLY_YX_history.csv.metadata.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 6037daf2f20d4ef2c24c399dc38c37ffadffd77ce25618e25bbe7057c72d8ddc
**Size:** 678 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.status | str |
| $.model_script | str |
| $.limit_state | str |
| $.stories | array |
| $.stories[] | object |
| $.stories[].story_number | integer |
| $.stories[].story_name | str |
| $.stories[].node | integer |
| $.stories[].elevation | number |
| $.stories[].height | number |
| $.model_data_sha256 | str |
| $.displacement_reference | str |
| $.sample_scope | str |
| $.units | object |
| $.units.translation | str |
| $.units.rotation | str |
| $.units.time | str |

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

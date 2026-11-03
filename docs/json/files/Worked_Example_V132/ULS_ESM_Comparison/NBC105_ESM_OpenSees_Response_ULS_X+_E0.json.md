# Worked_Example_V132/ULS_ESM_Comparison/NBC105_ESM_OpenSees_Response_ULS_X+_E0.json

**Source:** [Worked_Example_V132/ULS_ESM_Comparison/NBC105_ESM_OpenSees_Response_ULS_X+_E0.json](../../../../../Worked_Example_V132/ULS_ESM_Comparison/NBC105_ESM_OpenSees_Response_ULS_X+_E0.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** b370e05af0b8fdfb15a3af94c2b2b906cd7ddb9d37f31dabb62e6e5d6164840b
**Size:** 14892 bytes
**Root JSON type:** array
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $[] | object |
| $[].story_number | integer |
| $[].story_name | str |
| $[].height_m | number |
| $[].master_node_tag | integer |
| $[].Fx_kN | number |
| $[].Fy_kN | number |
| $[].Mz_kNm | number |
| $[].response_case | str |
| $[].U_elastic_m | number |
| $[].U_design_m | number |
| $[].story_height_m | number |
| $[].elastic_drift_ratio | number |
| $[].design_drift_ratio | number |
| $[].story_shear_kN | number |
| $[].story_stiffness_kN_per_m | number |
| $[].drift_limit | number |
| $[].drift_screen_pass | boolean |

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

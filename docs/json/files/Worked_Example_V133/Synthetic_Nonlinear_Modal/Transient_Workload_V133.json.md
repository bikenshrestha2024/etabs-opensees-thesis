# Worked_Example_V133/Synthetic_Nonlinear_Modal/Transient_Workload_V133.json

**Source:** [Worked_Example_V133/Synthetic_Nonlinear_Modal/Transient_Workload_V133.json](../../../../../Worked_Example_V133/Synthetic_Nonlinear_Modal/Transient_Workload_V133.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 8f1f198ab0e2c2723d1a4f09dc36a2e111fc44730310951882f1b8800f1ac9ae
**Size:** 893 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.cases | array |
| $.cases[] | object |
| $.cases[].case | str |
| $.cases[].dt_s | number |
| $.cases[].duration_s | number |
| $.cases[].requested_steps | integer |
| $.cases[].controlling_bounds | array |
| $.cases[].controlling_bounds[] | str |
| $.cases[].bounds_s | object |
| $.cases[].bounds_s.digitization | number |
| $.cases[].bounds_s.T1_over_100 | number |
| $.cases[].bounds_s.Tn | number |
| $.cases[].bounds_s.absolute_maximum | number |
| $.total_cases | integer |
| $.total_requested_steps | integer |
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

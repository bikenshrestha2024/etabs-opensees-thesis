# Worked_Example_V132/ULS_ESM_Comparison/Irregularity_ULS_X+_E0_V132.json

**Source:** [Worked_Example_V132/ULS_ESM_Comparison/Irregularity_ULS_X+_E0_V132.json](../../../../../Worked_Example_V132/ULS_ESM_Comparison/Irregularity_ULS_X+_E0_V132.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 19167146f5dae1c4083de2afc32e09619d905e8e80e5f24d100b73ccefe06c59
**Size:** 30225 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.checks | array |
| $.checks[] | object |
| $.checks[].clause | str |
| $.checks[].check | str |
| $.checks[].storey | integer |
| $.checks[].value | number |
| $.checks[].threshold | number |
| $.checks[].status | str |
| $.checks[].note | str |
| $.overall | str |
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

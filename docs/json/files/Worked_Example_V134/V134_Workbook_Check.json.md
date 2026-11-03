# Worked_Example_V134/V134_Workbook_Check.json

**Source:** [Worked_Example_V134/V134_Workbook_Check.json](../../../../Worked_Example_V134/V134_Workbook_Check.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 40fde71e2fcba8bd24c229f2d20ecb663ebd71dadd345f86a56d873bdad81a6e
**Size:** 296 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.ULS | object |
| $.ULS.Case summary | integer |
| $.ULS.Storey response | integer |
| $.ULS.Modal response | integer |
| $.ULS.Nodal 6DOF | integer |
| $.ULS.Sources and units | integer |
| $.SLS | object |
| $.SLS.Case summary | integer |
| $.SLS.Storey response | integer |
| $.SLS.Modal response | integer |
| $.SLS.Nodal 6DOF | integer |
| $.SLS.Sources and units | integer |

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

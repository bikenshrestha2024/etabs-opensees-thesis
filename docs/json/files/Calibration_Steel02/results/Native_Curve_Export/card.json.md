# Calibration_Steel02/results/Native_Curve_Export/card.json

**Source:** [Calibration_Steel02/results/Native_Curve_Export/card.json](../../../../../../Calibration_Steel02/results/Native_Curve_Export/card.json)
**Classification:** CALIBRATION_EVIDENCE
**SHA-256 (source bytes):** a43391b40ff796e87f445aa6ef348e56449ece66fa525c9ed6a8b30659b30e62
**Size:** 690 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.model | str |
| $.grade | str |
| $.parameters | object |
| $.parameters.Fy_MPa | number |
| $.parameters.E_MPa | number |
| $.parameters.b | number |
| $.parameters.R0 | number |
| $.parameters.cR1 | number |
| $.parameters.cR2 | number |
| $.parameters.a1 | number |
| $.parameters.a2 | number |
| $.parameters.a3 | number |
| $.parameters.a4 | number |
| $.protocol_csv | str |
| $.status | str |
| $.source | str |
| $.project_transfer_approved | boolean |
| $.finished_at | str |

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

[All JSON files](../../../../00_ALL_JSON_FILES.md) · [Research citations](../../../../../00_RESEARCH_REFERENCES.md)

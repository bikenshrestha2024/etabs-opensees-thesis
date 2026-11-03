# Saved_Project_V156/OpenSees_Complete_Model_Data_V118.json.processing.json

**Source:** [Saved_Project_V156/OpenSees_Complete_Model_Data_V118.json.processing.json](../../../../Saved_Project_V156/OpenSees_Complete_Model_Data_V118.json.processing.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** bfadc5539e6b5be156f9f76476ecffc768e0ed6195a914b8f91c914624b5bf61
**Size:** 390 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.stage | str |
| $.started_at | str |
| $.finished_at | str |
| $.elapsed_seconds | number |
| $.status | str |
| $.error | null |
| $.time_scope | str |
| $.artifact | str |
| $.size_bytes | integer |

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

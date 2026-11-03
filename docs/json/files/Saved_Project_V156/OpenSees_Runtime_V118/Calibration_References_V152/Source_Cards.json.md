# Saved_Project_V156/OpenSees_Runtime_V118/Calibration_References_V152/Source_Cards.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/Calibration_References_V152/Source_Cards.json](../../../../../../Saved_Project_V156/OpenSees_Runtime_V118/Calibration_References_V152/Source_Cards.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 9541b7780f43d1ac6952c1fe027935c2c2e7089f51ad6c2786749840e360e808
**Size:** 2153 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.status | str |
| $.papers | array |
| $.papers[] | object |
| $.papers[].authors | str |
| $.papers[].year | integer |
| $.papers[].doi | str |
| $.papers[].scope | str |
| $.papers[].locator | str |
| $.papers[].use | str |

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

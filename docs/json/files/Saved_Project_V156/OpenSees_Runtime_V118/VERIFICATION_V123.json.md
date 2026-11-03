# Saved_Project_V156/OpenSees_Runtime_V118/VERIFICATION_V123.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/VERIFICATION_V123.json](../../../../../Saved_Project_V156/OpenSees_Runtime_V118/VERIFICATION_V123.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** dad12ec19f29fb5edefe809dc13a1876a14f4046c6ea2aa4787e868f4f11788b
**Size:** 1057 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.version | integer |
| $.regression_checks_passed | integer |
| $.syntax | str |
| $.gui | str |
| $.workbook_import | str |
| $.gravity_output | str |
| $.active_story_weight_kN | number |
| $.mass_ledger_difference_percent | number |
| $.Rayleigh_X_s | number |
| $.Rayleigh_Y_s | number |
| $.generated_runner | str |
| $.remaining | array |
| $.remaining[] | str |

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

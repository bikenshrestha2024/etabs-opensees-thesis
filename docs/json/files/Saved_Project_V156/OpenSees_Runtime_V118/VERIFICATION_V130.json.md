# Saved_Project_V156/OpenSees_Runtime_V118/VERIFICATION_V130.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/VERIFICATION_V130.json](../../../../../Saved_Project_V156/OpenSees_Runtime_V118/VERIFICATION_V130.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 7f6d1f1b5db05f9b7943a65082962389d05bef3909080022b103de412b633c6e
**Size:** 553 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.release | integer |
| $.regression_tests_passed | integer |
| $.compatibility_imports_passed | integer |
| $.gui_constructors_passed | array |
| $.gui_constructors_passed[] | str |
| $.analysis_windows_have_modal_grab | boolean |
| $.source_function_inventory | integer |
| $.validation_document | str |
| $.not_verified | array |
| $.not_verified[] | str |
| $.source_export_modified | boolean |

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

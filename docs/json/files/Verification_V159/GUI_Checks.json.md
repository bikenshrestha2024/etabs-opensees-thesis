# Verification_V159/GUI_Checks.json

**Source:** [Verification_V159/GUI_Checks.json](../../../../Verification_V159/GUI_Checks.json)
**Classification:** VALIDATION_EVIDENCE
**SHA-256 (source bytes):** e091fc6e70bc808c30f9e8e09e96cd87b7b4257788ba1eba7bddc346fd759995
**Size:** 174 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.version | integer |
| $.main_startup_exit | integer |
| $.catalog_profiles_loaded | integer |
| $.saved_component_panels | integer |
| $.tuning_tabs | integer |
| $.export_preserves_parent_domain | boolean |
| $.project_validation | boolean |

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

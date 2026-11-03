# Saved_Project_V156/OpenSees_Export_Manifest_V118.json

**Source:** [Saved_Project_V156/OpenSees_Export_Manifest_V118.json](../../../../Saved_Project_V156/OpenSees_Export_Manifest_V118.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 2b3ed25f078ed945cb831dd60d60872252cc3d43cd615b4a06c2898656ff1b71
**Size:** 599 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.version | integer |
| $.report | str |
| $.gravity_model_script | str |
| $.modal_model_script | str |
| $.linear_model_script | str |
| $.nonlinear_model_script | str |
| $.story_master_csv | str |
| $.esm_story_weight_csv | str |
| $.readiness_manifest | str |
| $.elastic_assembled | boolean |
| $.nonlinear_ready | boolean |

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

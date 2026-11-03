# archive/previous_versions/RELEASE/RELEASE_V135.json

**Source:** [archive/previous_versions/RELEASE/RELEASE_V135.json](../../../../../../archive/previous_versions/RELEASE/RELEASE_V135.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 33d98bff4f3e71e2f395caa8b6e7424c34b85c0a71d13b46a9091cfdd5373444
**Size:** 264 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.release | integer |
| $.entry | str |
| $.new_module | str |
| $.scope | str |
| $.live_D_files_modified | boolean |

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

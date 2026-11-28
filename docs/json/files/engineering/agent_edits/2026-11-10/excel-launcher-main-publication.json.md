# engineering/agent_edits/2026-11-10/excel-launcher-main-publication.json

**Source:** [engineering/agent_edits/2026-11-10/excel-launcher-main-publication.json](../../../../../../engineering/agent_edits/2026-11-10/excel-launcher-main-publication.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** dbefd4372617fb1991349f6b5d22518c18fd2f425c24216ae5a4bff4c765f237
**Size:** 1263 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.tool | str |
| $.exact_model | str |
| $.timestamp_utc | str |
| $.branch | str |
| $.base_sha | str |
| $.user_authorization | str |
| $.classification | str |
| $.workbook_count | integer |
| $.existing_workbooks_moved | integer |
| $.new_source_workbooks_added | integer |
| $.new_verification_workbooks_added | integer |
| $.large_file_storage | str |
| $.catalog | str |
| $.compatibility | str |
| $.local_tests | str |
| $.native_solver_effect | str |
| $.main_merge_status | str |
| $.source_inventory | str |

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

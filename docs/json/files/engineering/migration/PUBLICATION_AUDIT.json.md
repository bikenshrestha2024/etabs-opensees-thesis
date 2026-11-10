# engineering/migration/PUBLICATION_AUDIT.json

**Source:** [engineering/migration/PUBLICATION_AUDIT.json](../../../../../engineering/migration/PUBLICATION_AUDIT.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 6f8f060582febf4cb907e0d5c5e989dfd80e9befc0e4de7adca4c9e8f4d6fee8
**Size:** 56189 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.source | str |
| $.baseline | str |
| $.scope | str |
| $.objects | object |
| $.objects.commit | integer |
| $.objects.tree | integer |
| $.objects.blob | integer |
| $.blob_bytes | integer |
| $.tracked_files | integer |
| $.finding_counts | object |
| $.finding_counts.PRIVATE_WINDOWS_PATH | integer |
| $.finding_counts.REDISTRIBUTION_REVIEW_FILE | integer |
| $.findings | array |
| $.findings[] | object |
| $.findings[].kind | str |
| $.findings[].blob | str |
| $.findings[].path | str |
| $.findings[].matches | integer |
| $.publication_status | str |
| $.root_license_present | boolean |
| $.source_modified | boolean |
| $.publication_decision | object |
| $.publication_decision.status | str |
| $.publication_decision.date | str |
| $.publication_decision.decision | str |
| $.publication_decision.rights_verification | str |
| $.status | str |

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

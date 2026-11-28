# engineering/agent_edits/2026-11-15/archive-three-release-design-notes.json

**Source:** [engineering/agent_edits/2026-11-15/archive-three-release-design-notes.json](../../../../../../engineering/agent_edits/2026-11-15/archive-three-release-design-notes.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 37751b3be6ed4b8d09ca90e3e0c9ca92294606fe91433d7c5643a80b7fa9d3ce
**Size:** 1304 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.baseline_sha | str |
| $.task | str |
| $.files_moved | array |
| $.files_moved[] | object |
| $.files_moved[].from | str |
| $.files_moved[].to | str |
| $.files_moved[].git_blob | str |
| $.read_only_dependency_checks | str |
| $.tests | str |
| $.pending | str |
| $.sourceModelsChanged | boolean |

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

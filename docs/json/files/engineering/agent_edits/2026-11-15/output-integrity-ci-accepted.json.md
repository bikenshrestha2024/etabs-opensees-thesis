# engineering/agent_edits/2026-11-15/output-integrity-ci-accepted.json

**Source:** [engineering/agent_edits/2026-11-15/output-integrity-ci-accepted.json](../../../../../../engineering/agent_edits/2026-11-15/output-integrity-ci-accepted.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 1d72ff22c6c314a8706490e2e8d88173916502d05d618723e9d672bbe865df7c
**Size:** 1103 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.baseline_sha | str |
| $.verified_commit | str |
| $.mesh_commit | str |
| $.fixture_fix | str |
| $.ci_results | object |
| $.ci_results.integrated | str |
| $.ci_results.compile | str |
| $.ci_results.nltha_python | str |
| $.ci_results.literature | str |
| $.all_four | str |
| $.native_etabs | str |
| $.native_opensees_full_building | str |
| $.nbc105 | str |
| $.files_changed | array |
| $.files_changed[] | str |
| $.source_data_unchanged | boolean |

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

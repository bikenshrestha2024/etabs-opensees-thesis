# engineering/agent_edits/2026-11-15/legacy-results-symlink-audit.json

**Source:** [engineering/agent_edits/2026-11-15/legacy-results-symlink-audit.json](../../../../../../engineering/agent_edits/2026-11-15/legacy-results-symlink-audit.json)
**Classification:** RUN_RESULT_OR_REPORT
**SHA-256 (source bytes):** 7d5349e7d86d7b0712a7f6a629ede31f82bc6ab0709ae1c5e1c972bc30061f21
**Size:** 1070 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.baseline_sha | str |
| $.task | str |
| $.inspected | array |
| $.inspected[] | str |
| $.source_files_modified | array |
| $.source_files_modified[] | str |
| $.tests_added | str |
| $.existing_ci | str |
| $.scope_limitations | array |
| $.scope_limitations[] | str |
| $.security | str |
| $.ci_status | str |

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

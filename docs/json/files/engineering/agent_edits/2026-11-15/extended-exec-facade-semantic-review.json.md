# engineering/agent_edits/2026-11-15/extended-exec-facade-semantic-review.json

**Source:** [engineering/agent_edits/2026-11-15/extended-exec-facade-semantic-review.json](../../../../../../engineering/agent_edits/2026-11-15/extended-exec-facade-semantic-review.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 52ad14942357eba4c3fd387d018c29f2846e1b642c88725f0bf51f8814d85f1e
**Size:** 1092 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.base_sha | str |
| $.scope | str |
| $.source_snapshot | str |
| $.active_python_snapshot | integer |
| $.root_exec_facades | integer |
| $.patches | array |
| $.patches[] | str |
| $.tests | array |
| $.tests[] | str |
| $.preservation | array |
| $.preservation[] | str |
| $.engineering_acceptance | str |
| $.full_semantic_review | str |
| $.ci | str |

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

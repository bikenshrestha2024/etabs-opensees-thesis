# engineering/agent_edits/2026-11-15/integrated-followup-ci-evidence.json

**Source:** [engineering/agent_edits/2026-11-15/integrated-followup-ci-evidence.json](../../../../../../engineering/agent_edits/2026-11-15/integrated-followup-ci-evidence.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 2ca6794f3fcd806ffaca828daa96eb30405f865b82cce9546d6d9dc9dfc38cec
**Size:** 1272 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.baseline_sha | str |
| $.source_commit | str |
| $.scope | str |
| $.test_evidence | object |
| $.test_evidence.integrated | str |
| $.test_evidence.repository | str |
| $.test_evidence.nltha_python | str |
| $.test_evidence.literature | str |
| $.test_evidence.artifact_id | integer |
| $.test_evidence.tracked_paths | integer |
| $.test_evidence.active_python | integer |
| $.test_evidence.exact_git_blob_duplicate_groups | integer |
| $.test_evidence.with_historical | integer |
| $.test_evidence.active_source_parse_failures | integer |
| $.test_evidence.static_gate | str |
| $.changed_paths | array |
| $.changed_paths[] | str |
| $.engineering_acceptance | str |
| $.windows_native | str |
| $.original_model_modified | boolean |

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

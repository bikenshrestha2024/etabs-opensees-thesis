# engineering/agent_edits/2026-11-15/active-source-semantic-ci-accepted.json

**Source:** [engineering/agent_edits/2026-11-15/active-source-semantic-ci-accepted.json](../../../../../../engineering/agent_edits/2026-11-15/active-source-semantic-ci-accepted.json)
**Classification:** ETABS_MODEL_OR_SOURCE_METADATA
**SHA-256 (source bytes):** 847a672aa665a306e38fca2ff81aafe1a73ee95b2c829e4bf31c63c82cce3a7a
**Size:** 1431 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.base_sha | str |
| $.scope | str |
| $.confirmed_ci | object |
| $.confirmed_ci.integrated | str |
| $.confirmed_ci.compilation | str |
| $.confirmed_ci.integrated_result | str |
| $.confirmed_ci.source_files | integer |
| $.confirmed_ci.tracked_paths | integer |
| $.confirmed_ci.generated_semantic_units | integer |
| $.confirmed_ci.completed_semantic_units | integer |
| $.local_ast_triage | object |
| $.local_ast_triage.named_definitions | integer |
| $.local_ast_triage.integer_cast_candidates | integer |
| $.local_ast_triage.suppressed_handler_candidates | integer |
| $.local_ast_triage.interpretation | str |
| $.software_fixes | array |
| $.software_fixes[] | str |
| $.source_changes_commit | str |
| $.test_fix_commit | str |
| $.native_acceptance | str |
| $.full_semantic_review | str |
| $.confidential_source_files_uploaded | boolean |

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

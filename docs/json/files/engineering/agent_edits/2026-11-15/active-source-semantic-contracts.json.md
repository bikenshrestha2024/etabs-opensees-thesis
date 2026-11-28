# engineering/agent_edits/2026-11-15/active-source-semantic-contracts.json

**Source:** [engineering/agent_edits/2026-11-15/active-source-semantic-contracts.json](../../../../../../engineering/agent_edits/2026-11-15/active-source-semantic-contracts.json)
**Classification:** ETABS_MODEL_OR_SOURCE_METADATA
**SHA-256 (source bytes):** 4e2f890540eefca7f7588ae646c34883fe479e27d29dae8f095e19d6d6001ea7
**Size:** 1926 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.branch | str |
| $.base_sha | str |
| $.source_only_CI_revision | str |
| $.reviewed_source_count | integer |
| $.integrated_semantic_review_units | integer |
| $.ast_named_definitions | integer |
| $.static_integer_cast_candidates | integer |
| $.static_suppressed_handler_candidates | integer |
| $.classification | str |
| $.confirmed_defect_groups | array |
| $.confirmed_defect_groups[] | str |
| $.changed_source | array |
| $.changed_source[] | str |
| $.tests | array |
| $.tests[] | str |
| $.test_results_local | str |
| $.unchanged | array |
| $.unchanged[] | str |
| $.acceptance | object |
| $.acceptance.static_review | str |
| $.acceptance.complete_line_by_line_semantic_review | str |
| $.acceptance.native_etabs_opensees | str |
| $.acceptance.X_wall_first_step | str |
| $.acceptance.nbc105_compliance | str |

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

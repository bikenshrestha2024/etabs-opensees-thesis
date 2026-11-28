# engineering/agent_edits/2026-11-17/brace-status-mesh-export-performance.json

**Source:** [engineering/agent_edits/2026-11-17/brace-status-mesh-export-performance.json](../../../../../../engineering/agent_edits/2026-11-17/brace-status-mesh-export-performance.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** d83249f49cd3d94c056adea13d7d27c75e58e41ea389514827e45d9cf4e6bbf4
**Size:** 6204 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.editor | str |
| $.model | str |
| $.branch | str |
| $.base_sha | str |
| $.classification | str |
| $.task | str |
| $.changed_files | array |
| $.changed_files[] | str |
| $.prior_search | str |
| $.tests | object |
| $.tests.focused | str |
| $.tests.full_discovery | str |
| $.tests.full_discovery_errors | array |
| $.tests.full_discovery_errors[] | str |
| $.tests.syntax | str |
| $.tests.diff | str |
| $.tests.review | str |
| $.tests.ci_followup | str |
| $.deferred | array |
| $.deferred[] | str |
| $.privacy | str |
| $.utc | str |
| $.followup | object |
| $.followup.request | str |
| $.followup.base_sha | str |
| $.followup.changes | str |
| $.followup.tests | str |
| $.followup.limitations | str |
| $.gui_freeze_followup | object |
| $.gui_freeze_followup.classification | str |
| $.gui_freeze_followup.root_cause | str |
| $.gui_freeze_followup.fix | str |
| $.gui_freeze_followup.evidence_scope | str |
| $.gui_freeze_followup.known_attachment_limits | str |
| $.gui_freeze_followup.verification | str |
| $.wall_edge_scope_fix | object |
| $.wall_edge_scope_fix.base | str |
| $.wall_edge_scope_fix.reason | str |
| $.wall_edge_scope_fix.change | str |
| $.wall_edge_scope_fix.tests | str |
| $.wall_edge_scope_fix.native_status | str |
| $.current_runtime_documentation | object |
| $.current_runtime_documentation.request | str |
| $.current_runtime_documentation.classification | str |
| $.current_runtime_documentation.report | str |
| $.current_runtime_documentation.finding | str |
| $.current_runtime_documentation.benchmark | str |
| $.current_runtime_documentation.privacy | str |
| $.current_runtime_documentation.limitations | str |
| $.current_runtime_documentation.integration_verification | str |

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

# engineering/agent_edits/2026-11-15/integrated-ci-evidence-v31.json

**Source:** [engineering/agent_edits/2026-11-15/integrated-ci-evidence-v31.json](../../../../../../engineering/agent_edits/2026-11-15/integrated-ci-evidence-v31.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** cd466543628f01f350a89638bbba0d4df073d79628ce9d0aacab3757b6107e12
**Size:** 1274 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.baseline_sha | str |
| $.scope | str |
| $.source_evidence | object |
| $.source_evidence.source_commit | str |
| $.source_evidence.integrated_ci_run | str |
| $.source_evidence.report_artifact_id | integer |
| $.source_evidence.tracked_paths | integer |
| $.source_evidence.active_python | integer |
| $.source_evidence.static_gate | str |
| $.source_evidence.eager_import_cycles | integer |
| $.source_evidence.deferred_possible_cycles | integer |
| $.source_evidence.unresolved_explicit_local_imports | integer |
| $.source_evidence.missing_src_guides | integer |
| $.source_evidence.source_parse_failures | integer |
| $.source_evidence.writer_occurrences | integer |
| $.source_evidence.legacy_literal_occurrences | integer |
| $.source_evidence.secret_pattern_candidates_current_tree | integer |
| $.changed_paths | array |
| $.changed_paths[] | str |
| $.engineering_acceptance | str |
| $.no_source_model_mutation | boolean |
| $.limitations | str |

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

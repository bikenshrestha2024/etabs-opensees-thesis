# engineering/agent_edits/2026-11-15/integrated-review-followup-v31.json

**Source:** [engineering/agent_edits/2026-11-15/integrated-review-followup-v31.json](../../../../../../engineering/agent_edits/2026-11-15/integrated-review-followup-v31.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 628546b8637e900c39ed8063f03279221fc9f7ca8a3636871fb466bc452a1d9a
**Size:** 1672 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.baseline_sha | str |
| $.parent_integrated_commit | str |
| $.review | str |
| $.confirmed_bug | str |
| $.corrected | array |
| $.corrected[] | str |
| $.files_changed | array |
| $.files_changed[] | str |
| $.original_user_models_changed | boolean |
| $.engineering_claim | str |
| $.validation | str |
| $.risk | str |

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

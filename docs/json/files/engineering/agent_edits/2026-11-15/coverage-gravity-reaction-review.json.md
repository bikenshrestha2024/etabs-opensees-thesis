# engineering/agent_edits/2026-11-15/coverage-gravity-reaction-review.json

**Source:** [engineering/agent_edits/2026-11-15/coverage-gravity-reaction-review.json](../../../../../../engineering/agent_edits/2026-11-15/coverage-gravity-reaction-review.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 305237646c5e6916551fdf72cd1335ab1fc5b7387f23cf74d06db3549ee4597c
**Size:** 1775 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.base_sha | str |
| $.scope | str |
| $.classification | str |
| $.inspected | array |
| $.inspected[] | str |
| $.changes | array |
| $.changes[] | str |
| $.unchanged | array |
| $.unchanged[] | str |
| $.gates | object |
| $.gates.static_CI | str |
| $.gates.native_gravity_32_76_97 | str |
| $.gates.nonlinear_X_wall | str |
| $.gates.NBC105_code | str |
| $.gates.windows_GUI | str |
| $.gates.complete_semantic_audit | str |
| $.safety | str |

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

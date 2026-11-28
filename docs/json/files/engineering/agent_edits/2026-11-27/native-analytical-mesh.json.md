# engineering/agent_edits/2026-11-27/native-analytical-mesh.json

**Source:** [engineering/agent_edits/2026-11-27/native-analytical-mesh.json](../../../../../../engineering/agent_edits/2026-11-27/native-analytical-mesh.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** b39a5b9dfdb9ef9e022b95d2f1a996e502326d85ef5e06b6e99729fffcdbae10
**Size:** 598 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.editor | str |
| $.model | str |
| $.base_sha | str |
| $.branch | str |
| $.changed_files | array |
| $.changed_files[] | str |
| $.scope | str |
| $.tests | str |
| $.deferred | str |

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

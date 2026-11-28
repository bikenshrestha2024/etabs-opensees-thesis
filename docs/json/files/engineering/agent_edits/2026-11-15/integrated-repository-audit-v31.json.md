# engineering/agent_edits/2026-11-15/integrated-repository-audit-v31.json

**Source:** [engineering/agent_edits/2026-11-15/integrated-repository-audit-v31.json](../../../../../../engineering/agent_edits/2026-11-15/integrated-repository-audit-v31.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** dc44b44ac92a4c6968d2623db704bec53acf1d466dc8e17c3aa67e796d734551
**Size:** 1836 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.branch | str |
| $.baseline_sha | str |
| $.workstream | str |
| $.classification | str |
| $.confirmed_findings | array |
| $.confirmed_findings[] | str |
| $.changed_modules | array |
| $.changed_modules[] | str |
| $.tests | array |
| $.tests[] | str |
| $.workflow | str |
| $.review | str |
| $.preserve | array |
| $.preserve[] | str |
| $.acceptance | object |
| $.acceptance.static_source | str |
| $.acceptance.every_file_semantically_reviewed | boolean |
| $.acceptance.native_etabs | boolean |
| $.acceptance.native_opensees | boolean |
| $.acceptance.gui_windows | boolean |
| $.acceptance.code_compliance | boolean |
| $.limitations | array |
| $.limitations[] | str |
| $.user_requested_commit | str |

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

# engineering/agent_edits/2026-11-15/mesh-source-identity-and-output-audit.json

**Source:** [engineering/agent_edits/2026-11-15/mesh-source-identity-and-output-audit.json](../../../../../../engineering/agent_edits/2026-11-15/mesh-source-identity-and-output-audit.json)
**Classification:** ETABS_MODEL_OR_SOURCE_METADATA
**SHA-256 (source bytes):** 2d4067af2b47fef34baf86cebbf5b5527b599c5684cc0e833b7625d9e6f40f9e
**Size:** 1675 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.baseline_sha | str |
| $.task | str |
| $.source_files_inspected | array |
| $.source_files_inspected[] | str |
| $.modified_source | array |
| $.modified_source[] | str |
| $.regressions | array |
| $.regressions[] | str |
| $.kept | array |
| $.kept[] | str |
| $.engineering_gates | object |
| $.engineering_gates.source_identity | str |
| $.engineering_gates.mesh_4_8_16_native | str |
| $.engineering_gates.gravity_32_76_97 | str |
| $.engineering_gates.nonlinear_x_wall | str |
| $.engineering_gates.nbc105_acceptance | str |
| $.security | str |
| $.limitations | array |
| $.limitations[] | str |

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

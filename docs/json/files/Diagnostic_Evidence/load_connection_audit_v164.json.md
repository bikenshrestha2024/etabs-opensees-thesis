# Diagnostic_Evidence/load_connection_audit_v164.json

**Source:** [Diagnostic_Evidence/load_connection_audit_v164.json](../../../../Diagnostic_Evidence/load_connection_audit_v164.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 1693a30d7175da85c01bb80f2b6c2791be75dcc4b8b775a79a677fc71fbe18e8
**Size:** 94168 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.folder | str |
| $.scope | str |
| $.slabs | array |
| $.slabs[] | object |
| $.slabs[].object | str |
| $.slabs[].cells | integer |
| $.slabs[].shared_beam_nodes | integer |
| $.slabs[].shared_wall_nodes | integer |
| $.slabs[].shared_column_nodes | integer |
| $.walls | array |
| $.walls[] | object |
| $.walls[].object | str |
| $.walls[].cells | integer |
| $.walls[].shared_frame_nodes | integer |
| $.walls[].supported_nodes | integer |
| $.summary | object |
| $.summary.slab_objects | integer |
| $.summary.slabs_without_direct_beam_or_wall_node | integer |
| $.summary.wall_objects | integer |
| $.summary.gravity_total_kN | number |
| $.summary.gravity_by_pattern_kN | object |
| $.summary.gravity_by_pattern_kN.Floor Finish | number |
| $.summary.gravity_by_pattern_kN.Live | number |
| $.summary.gravity_by_pattern_kN.Partition | number |
| $.summary.gravity_by_pattern_kN.Wall | number |
| $.summary.gravity_by_pattern_kN.Self Weight | number |

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

[All JSON files](../../00_ALL_JSON_FILES.md) · [Research citations](../../../00_RESEARCH_REFERENCES.md)

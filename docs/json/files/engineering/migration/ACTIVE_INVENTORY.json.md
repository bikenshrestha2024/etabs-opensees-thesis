# engineering/migration/ACTIVE_INVENTORY.json

**Source:** [engineering/migration/ACTIVE_INVENTORY.json](../../../../../engineering/migration/ACTIVE_INVENTORY.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 32403aacb0ba0a88fe47e682482c1cfbc27e2f70b64b2deac7bec6eb39584493
**Size:** 248399 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.kind | str |
| $.canonical_workflow | array |
| $.canonical_workflow[] | object |
| $.canonical_workflow[].step | str |
| $.canonical_workflow[].launch_file | str |
| $.canonical_workflow[].exists | boolean |
| $.numbered_alias_conflicts | object |
| $.numbered_alias_conflicts.01 | array |
| $.numbered_alias_conflicts.01[] | str |
| $.numbered_alias_conflicts.02 | array |
| $.numbered_alias_conflicts.02[] | str |
| $.numbered_alias_conflicts.03 | array |
| $.numbered_alias_conflicts.03[] | str |
| $.numbered_alias_conflicts.04 | array |
| $.numbered_alias_conflicts.04[] | str |
| $.numbered_alias_conflicts.05 | array |
| $.numbered_alias_conflicts.05[] | str |
| $.numbered_alias_conflicts.06 | array |
| $.numbered_alias_conflicts.06[] | str |
| $.numbered_alias_conflicts.07 | array |
| $.numbered_alias_conflicts.07[] | str |
| $.numbered_alias_conflicts.08 | array |
| $.numbered_alias_conflicts.08[] | str |
| $.numbered_alias_conflicts.09 | array |
| $.numbered_alias_conflicts.09[] | str |
| $.numbered_alias_conflicts.10 | array |
| $.numbered_alias_conflicts.10[] | str |
| $.numbered_alias_conflicts.11 | array |
| $.numbered_alias_conflicts.11[] | str |
| $.numbered_alias_conflicts.12 | array |
| $.numbered_alias_conflicts.12[] | str |
| $.numbered_alias_conflicts.13 | array |
| $.numbered_alias_conflicts.13[] | str |
| $.numbered_alias_conflicts.14 | array |
| $.numbered_alias_conflicts.14[] | str |
| $.numbered_alias_conflicts.15 | array |
| $.numbered_alias_conflicts.15[] | str |
| $.numbered_alias_conflicts.16 | array |
| $.numbered_alias_conflicts.16[] | str |
| $.numbered_alias_conflicts.17 | array |
| $.numbered_alias_conflicts.17[] | str |
| $.numbered_alias_conflicts.18 | array |
| $.numbered_alias_conflicts.18[] | str |
| $.numbered_alias_conflicts.20 | array |
| $.numbered_alias_conflicts.20[] | str |
| $.numbered_alias_conflicts.21 | array |
| $.numbered_alias_conflicts.21[] | str |
| $.active_python_module_count | integer |
| $.active_python_modules | array |
| $.active_python_modules[] | object |
| $.active_python_modules[].path | str |
| $.active_python_modules[].lines | integer |
| $.active_python_modules[].sha256 | str |
| $.active_python_modules[].parse_status | str |
| $.active_python_modules[].classes | array |
| $.active_python_modules[].classes[] | array(empty) |
| $.active_python_modules[].functions | array |
| $.active_python_modules[].functions[] | array(empty) |
| $.active_python_modules[].imports | array |
| $.active_python_modules[].imports[] | str |
| $.missing_source_guides | array |
| $.missing_source_guides[] | str |
| $.canonical_missing | array |
| $.canonical_missing[] | array(empty) |
| $.syntax_errors | array |
| $.syntax_errors[] | array(empty) |
| $.high_priority_code_index | array |
| $.high_priority_code_index[] | object |
| $.high_priority_code_index[].path | str |
| $.high_priority_code_index[].lines | integer |
| $.high_priority_code_index[].sha256 | str |
| $.high_priority_code_index[].parse_status | str |
| $.high_priority_code_index[].classes | array |
| $.high_priority_code_index[].classes[] | array(empty) |
| $.high_priority_code_index[].functions | array |
| $.high_priority_code_index[].functions[] | object |
| $.high_priority_code_index[].functions[].name | str |
| $.high_priority_code_index[].functions[].line | integer |
| $.high_priority_code_index[].imports | array |
| $.high_priority_code_index[].imports[] | str |
| $.stages | array |
| $.stages[] | object |
| $.stages[].step | str |
| $.stages[].name | str |
| $.stages[].evidence | str |
| $.warnings | array |
| $.warnings[] | str |

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

[All JSON files](../../../00_ALL_JSON_FILES.md) · [Research citations](../../../../00_RESEARCH_REFERENCES.md)

# Saved_Project_V156/Gravity_Storey_Load_Breakdown_V131.json

**Source:** [Saved_Project_V156/Gravity_Storey_Load_Breakdown_V131.json](../../../../Saved_Project_V156/Gravity_Storey_Load_Breakdown_V131.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 17a66376cde6873ce9d54706dd4d03d82175555641ecaaf33cb29d516fa143ce
**Size:** 1486042 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.rows | array |
| $.rows[] | object |
| $.rows[].storey | str |
| $.rows[].elevation_m | number |
| $.rows[].beam_self_weight_kN | number |
| $.rows[].column_self_weight_kN | number |
| $.rows[].brace_self_weight_kN | number |
| $.rows[].shear_wall_self_weight_kN | number |
| $.rows[].slab_self_weight_kN | number |
| $.rows[].other_self_weight_kN | number |
| $.rows[].floor_finish_kN | number |
| $.rows[].partition_kN | number |
| $.rows[].other_dead_kN | number |
| $.rows[].live_kN | number |
| $.rows[].roof_live_kN | number |
| $.rows[].unclassified_kN | number |
| $.rows[].dead_total_kN | number |
| $.rows[].live_total_kN | number |
| $.rows[].unfactored_total_kN | number |
| $.rows[].applied_dead_kN | number |
| $.rows[].applied_live_kN | number |
| $.rows[].applied_unclassified_kN | number |
| $.rows[].applied_total_kN | number |
| $.details | array |
| $.details[] | object |
| $.details[].storey | str |
| $.details[].source | str |
| $.details[].component | str |
| $.details[].pattern | str |
| $.details[].classification | str |
| $.details[].load_class | str |
| $.details[].gravity_factor | number |
| $.details[].unfactored_kN | number |
| $.details[].applied_kN | number |
| $.total_applied_kN | number |
| $.assembled_total_kN | number |
| $.reconciliation_error_kN | number |
| $.convention | str |

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

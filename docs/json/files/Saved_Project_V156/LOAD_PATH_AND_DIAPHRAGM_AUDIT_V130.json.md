# Saved_Project_V156/LOAD_PATH_AND_DIAPHRAGM_AUDIT_V130.json

**Source:** [Saved_Project_V156/LOAD_PATH_AND_DIAPHRAGM_AUDIT_V130.json](../../../../Saved_Project_V156/LOAD_PATH_AND_DIAPHRAGM_AUDIT_V130.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 91d4ad09e49a2923f34b6a519f39d2c58dccd3d44ef6b64c4cdb010bc712524c
**Size:** 472707 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.area_load_records | array |
| $.area_load_records[] | object |
| $.area_load_records[].object | str |
| $.area_load_records[].pattern | str |
| $.area_load_records[].area_m2 | number |
| $.area_load_records[].q_global_z_kN_m2 | number |
| $.area_load_records[].unfactored_vertical_force_kN | number |
| $.area_load_records[].resultant_and_moment_error | number |
| $.area_load_records[].beam_wall_connection_nodes | integer |
| $.area_load_records[].method | str |
| $.area_load_records[].gravity_factor | number |
| $.area_load_records[].seismic_mass_weight_factor | number |
| $.area_unfactored_global_z_kN_by_pattern | object |
| $.area_unfactored_global_z_kN_by_pattern.Floor Finish | number |
| $.area_unfactored_global_z_kN_by_pattern.Live | number |
| $.area_unfactored_global_z_kN_by_pattern.Partition | number |
| $.diaphragms | array |
| $.diaphragms[] | object |
| $.diaphragms[].master | integer |
| $.diaphragms[].z_m | number |
| $.diaphragms[].slaves | integer |
| $.diaphragms[].constrained_dofs | array |
| $.diaphragms[].constrained_dofs[] | integer |
| $.diaphragms[].unconstrained_slab_vertical_dof | integer |
| $.diaphragms[].kinematics | str |
| $.coverage | object |
| $.coverage.floor_nodes | integer |
| $.coverage.in_rigid_diaph | integer |
| $.coverage.without_rigid_diaph | integer |
| $.notes | array |
| $.notes[] | str |
| $.load_path | str |
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

[All JSON files](../../00_ALL_JSON_FILES.md) · [Research citations](../../../00_RESEARCH_REFERENCES.md)

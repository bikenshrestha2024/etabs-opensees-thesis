# Worked_Example_V134/Gravity_Six_DOF_V134.json

**Source:** [Worked_Example_V134/Gravity_Six_DOF_V134.json](../../../../Worked_Example_V134/Gravity_Six_DOF_V134.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 82252b06407859cc582a53b8bde3faf63cff837a5e627269a351c8eb5c9c71d4
**Size:** 2456788 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.ok | boolean |
| $.model_script | str |
| $.report | object |
| $.report.steps | integer |
| $.report.applied_vertical_load_kN | number |
| $.report.support_vertical_reaction_kN | number |
| $.report.equilibrium_error_percent | number |
| $.report.equilibrium_tolerance_percent | number |
| $.report.max_downward_vertical_displacement_m | number |
| $.report.elapsed_seconds_before_freeze | number |
| $.report.gravity_frozen | boolean |
| $.report.elapsed_seconds | number |
| $.nodes | array |
| $.nodes[] | object |
| $.nodes[].tag | integer |
| $.nodes[].x_m | number |
| $.nodes[].y_m | number |
| $.nodes[].z_m | number |
| $.nodes[].ux_m | number |
| $.nodes[].uy_m | number |
| $.nodes[].uz_m | number |
| $.nodes[].rx_rad | number |
| $.nodes[].ry_rad | number |
| $.nodes[].rz_rad | number |
| $.reactions | array |
| $.reactions[] | object |
| $.reactions[].node_tag | integer |
| $.reactions[].rx_kN | number |
| $.reactions[].ry_kN | number |
| $.reactions[].rz_kN | number |
| $.elements | array |
| $.elements[] | object |
| $.elements[].tag | integer |
| $.elements[].nodes | array |
| $.elements[].nodes[] | integer |
| $.local_forces | array |
| $.local_forces[] | object |
| $.local_forces[].tag | integer |
| $.local_forces[].N_i_kN | number |
| $.local_forces[].Vy_i_kN | number |
| $.local_forces[].Vz_i_kN | number |
| $.local_forces[].T_i_kNm | number |
| $.local_forces[].My_i_kNm | number |
| $.local_forces[].Mz_i_kNm | number |
| $.local_forces[].N_j_kN | number |
| $.local_forces[].Vy_j_kN | number |
| $.local_forces[].Vz_j_kN | number |
| $.local_forces[].T_j_kNm | number |
| $.local_forces[].My_j_kNm | number |
| $.local_forces[].Mz_j_kNm | number |

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

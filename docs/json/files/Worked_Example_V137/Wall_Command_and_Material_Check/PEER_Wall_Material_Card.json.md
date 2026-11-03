# Worked_Example_V137/Wall_Command_and_Material_Check/PEER_Wall_Material_Card.json

**Source:** [Worked_Example_V137/Wall_Command_and_Material_Check/PEER_Wall_Material_Card.json](../../../../../Worked_Example_V137/Wall_Command_and_Material_Check/PEER_Wall_Material_Card.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 14762d557a4b5786fe139cd5d0fa387436ae209bbdde834d0d4925aa93b1174d
**Size:** 2912 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.profile_id | str |
| $.status | str |
| $.source_citation | str |
| $.source_url | str |
| $.specimen | str |
| $.source_units | str |
| $.specimen_geometry_in | object |
| $.specimen_geometry_in.thickness | number |
| $.specimen_geometry_in.length | number |
| $.specimen_geometry_in.height | number |
| $.ksi_to_mpa | number |
| $.concrete_unconfined | object |
| $.concrete_unconfined.fc_ksi | number |
| $.concrete_unconfined.epsc0 | number |
| $.concrete_unconfined.Ec_ksi | number |
| $.concrete_unconfined.rc | number |
| $.concrete_unconfined.xcrn | number |
| $.concrete_unconfined.ft_ksi | number |
| $.concrete_unconfined.et | number |
| $.concrete_unconfined.rt | number |
| $.concrete_unconfined.xcrp | number |
| $.concrete_unconfined.gap_close | integer |
| $.concrete_confined | object |
| $.concrete_confined.fc_ksi | number |
| $.concrete_confined.epsc0 | number |
| $.concrete_confined.Ec_ksi | number |
| $.concrete_confined.rc | number |
| $.concrete_confined.xcrn | number |
| $.concrete_confined.ft_ksi | number |
| $.concrete_confined.et | number |
| $.concrete_confined.rt | number |
| $.concrete_confined.xcrp | number |
| $.concrete_confined.gap_close | integer |
| $.steel | object |
| $.steel.fy_web_x_ksi | number |
| $.steel.fy_web_y_ksi | number |
| $.steel.fy_boundary_y_ksi | number |
| $.steel.E0_ksi | number |
| $.steel.b_web_x | number |
| $.steel.b_web_y | number |
| $.steel.b_boundary_y | number |
| $.steel.R0 | number |
| $.steel.a1 | number |
| $.steel.a2 | number |
| $.reinforcement_ratio | object |
| $.reinforcement_ratio.rouX_web | number |
| $.reinforcement_ratio.rouY_web | number |
| $.reinforcement_ratio.rouX_boundary | number |
| $.reinforcement_ratio.rouY_boundary | number |
| $.fsam | object |
| $.fsam.rho | number |
| $.fsam.nu | number |
| $.fsam.alfadow | number |
| $.tags | object |
| $.tags.steel_x | integer |
| $.tags.steel_y_web | integer |
| $.tags.steel_y_boundary | integer |
| $.tags.concrete_web | integer |
| $.tags.concrete_boundary | integer |
| $.tags.fsam_web | integer |
| $.tags.fsam_boundary | integer |
| $.limitations | array |
| $.limitations[] | str |
| $.verification | str |
| $.verified_source_pdf | str |
| $.verified_on | str |
| $.usage | str |
| $.derived_MPa | object |
| $.derived_MPa.unconfined_fc | number |
| $.derived_MPa.confined_fc | number |
| $.derived_MPa.web_fy | number |
| $.derived_MPa.boundary_fy | number |
| $.derived_MPa.steel_E | number |

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

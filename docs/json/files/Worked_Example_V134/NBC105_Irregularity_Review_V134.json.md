# Worked_Example_V134/NBC105_Irregularity_Review_V134.json

**Source:** [Worked_Example_V134/NBC105_Irregularity_Review_V134.json](../../../../Worked_Example_V134/NBC105_Irregularity_Review_V134.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 96ab83847db7c92853d1035c401c292cf8c6386c8c1032ab827b3b199c1cd6f0
**Size:** 251785 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.checks | array |
| $.checks[] | object |
| $.checks[].clause | str |
| $.checks[].check | str |
| $.checks[].storey | integer |
| $.checks[].value | number |
| $.checks[].threshold | number |
| $.checks[].status | str |
| $.checks[].note | str |
| $.responses | array |
| $.responses[] | object |
| $.responses[].limit_state | str |
| $.responses[].axis | str |
| $.responses[].storey | integer |
| $.responses[].master_displacement_m | number |
| $.responses[].master_rotation_rad | number |
| $.responses[].interstorey_displacement_m | number |
| $.responses[].story_stiffness_kN_per_m | number |
| $.responses[].reference_story_shear_kN | number |
| $.responses[].end_min_m | number |
| $.responses[].end_max_m | number |
| $.responses[].torsion_ratio | number |
| $.responses[].reference_base_shear_kN | number |
| $.responses[].equilibrium_relative_error | number |
| $.plan_outlines | array |
| $.plan_outlines[] | object |
| $.plan_outlines[].storey | integer |
| $.plan_outlines[].exterior | array |
| $.plan_outlines[].exterior[] | array |
| $.plan_outlines[].exterior[][] | number |
| $.plan_outlines[].interior_openings | integer |
| $.plan_outlines[].corners | array |
| $.plan_outlines[].corners[] | object |
| $.plan_outlines[].corners[].x | number |
| $.plan_outlines[].corners[].y | number |
| $.plan_outlines[].corners[].projection_x_m | number |
| $.plan_outlines[].corners[].projection_y_m | number |
| $.model_sha256 | str |
| $.states | array |
| $.states[] | str |
| $.overall | str |
| $.scope | str |

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

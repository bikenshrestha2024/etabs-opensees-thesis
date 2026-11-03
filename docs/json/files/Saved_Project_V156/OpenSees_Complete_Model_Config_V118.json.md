# Saved_Project_V156/OpenSees_Complete_Model_Config_V118.json

**Source:** [Saved_Project_V156/OpenSees_Complete_Model_Config_V118.json](../../../../Saved_Project_V156/OpenSees_Complete_Model_Config_V118.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** f165b8ce7a65ea0c22522c93da8a72ea8e78c05ae0f7689f88765167bf1ec5c5
**Size:** 1120 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.gravity_factors | object |
| $.gravity_factors.Self Weight | number |
| $.gravity_factors.Dead | number |
| $.gravity_factors.DL | number |
| $.gravity_factors.Super Dead | number |
| $.gravity_factors.SDead | number |
| $.gravity_factors.Floor Finish | number |
| $.gravity_factors.Wall | number |
| $.gravity_factors.Partition | number |
| $.gravity_factors.Live | number |
| $.gravity_factors.Roof Live | number |
| $.mass_factors | object |
| $.mass_factors.Self Weight | number |
| $.mass_factors.Dead | number |
| $.mass_factors.DL | number |
| $.mass_factors.Super Dead | number |
| $.mass_factors.SDead | number |
| $.mass_factors.Floor Finish | number |
| $.mass_factors.Wall | number |
| $.mass_factors.Partition | number |
| $.mass_factors.Live | number |
| $.mass_factors.Roof Live | number |
| $.slab_bending_factor | number |
| $.slab_stiffness_source | str |
| $.frame_section_mapping | object |
| $.frame_section_mapping.Col 1100*1100 | str |
| $.frame_section_mapping.Col 1250*1250 | str |
| $.frame_section_mapping.Beam 600*800 | str |
| $.frame_section_mapping.350*350*16 SHS | str |
| $.nonlinear_parameters_reviewed | boolean |
| $.nonlinear_materials_file | str |
| $.nonlinear_wall_fsam_tags | object(empty) |
| $.section_overrides | object(empty) |
| $.area_property_overrides | object(empty) |
| $.slab_bending_factor_sls | number |
| $.floor_subdivisions | integer |

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

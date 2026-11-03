# Saved_Project_V156/OpenSees_Area_Model_Config_V116.json

**Source:** [Saved_Project_V156/OpenSees_Area_Model_Config_V116.json](../../../../Saved_Project_V156/OpenSees_Area_Model_Config_V116.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 4820f83601fa30e33e9bab27067c85331f6061fb0fa07aa86d3d9922ab7ecade
**Size:** 3481 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.coordinate_units | str |
| $.force_units | str |
| $.source_reviewed_by_user | boolean |
| $.audit_output_json | str |
| $.section_mapping_json | str |
| $.floor_sections | object |
| $.floor_sections.Slab 150 | object |
| $.floor_sections.Slab 150.section_tag | integer |
| $.floor_sections.Slab 150.E_kN_m2 | number |
| $.floor_sections.Slab 150.poisson_ratio | number |
| $.floor_sections.Slab 150.thickness_m | number |
| $.floor_sections.Slab 150.source | str |
| $.etabs_to_opensees_wall_mapping | object |
| $.etabs_to_opensees_wall_mapping.Wall 600 | str |
| $.opensees_wall_sections | object |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D | object |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.thickness_m | number |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.fsam_material_tag | null |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.center_of_rotation | number |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.out_of_plane_thickness_modifier | number |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.poisson_ratio | number |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.quad_width_tolerance_m | number |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.reinforcement_detail | object |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.reinforcement_detail.vertical_bar_diameter_mm | integer |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.reinforcement_detail.horizontal_bar_diameter_mm | integer |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.reinforcement_detail.vertical_spacing_mm | integer |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.reinforcement_detail.horizontal_spacing_mm | integer |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.reinforcement_detail.curtains | integer |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.reinforcement_detail.clear_cover_each_face_mm | integer |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.reinforcement_detail.steel_grade | str |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.reinforcement_detail.rho_vertical_gross | number |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.reinforcement_detail.rho_horizontal_gross | number |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.reinforcement_detail.ratio_basis | str |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.material_calibration_source | str |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.source_etabs_area_property | str |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.source | str |
| $.opensees_wall_sections.RC_WALL_600_E_SFI_MVLEM3D.section_status | str |
| $.load_mass_policy | object |
| $.load_mass_policy.shell_mass_density | number |
| $.load_mass_policy.apply_area_loads_here | boolean |
| $.load_mass_policy.apply_seismic_mass_here | boolean |
| $.load_mass_policy.note | str |
| $.floor_shell_nonlinearity_verified | boolean |
| $.notes | array |
| $.notes[] | str |

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

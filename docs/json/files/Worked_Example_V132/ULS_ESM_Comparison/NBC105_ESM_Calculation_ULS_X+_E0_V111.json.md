# Worked_Example_V132/ULS_ESM_Comparison/NBC105_ESM_Calculation_ULS_X+_E0_V111.json

**Source:** [Worked_Example_V132/ULS_ESM_Comparison/NBC105_ESM_Calculation_ULS_X+_E0_V111.json](../../../../../Worked_Example_V132/ULS_ESM_Comparison/NBC105_ESM_Calculation_ULS_X+_E0_V111.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 03ae827d0489323231b929fa5802b1c0f19794b13845fed86f74bfa3ac430660
**Size:** 32677 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.standard | str |
| $.clauses | str |
| $.limit_state | str |
| $.soil_type | str |
| $.period_s | number |
| $.location_name | str |
| $.zoning_factor_source | str |
| $.zoning_factor_Z | number |
| $.importance_factor_I | number |
| $.spectral_shape_Ch | number |
| $.elastic_spectrum_C_k | number |
| $.design_coefficient_Cd | number |
| $.coefficient_divisor | str |
| $.period_exponent_k | number |
| $.ductility_factor_R_mu | number |
| $.overstrength_factor_Omega_u | number |
| $.overstrength_factor_Omega_s | number |
| $.deflection_scale_factor_kd | number |
| $.drift_limit_ratio | number |
| $.uls_drift_amplification | number |
| $.total_seismic_weight_kN | number |
| $.base_shear_kN | number |
| $.total_floor_force_kN | number |
| $.height_m | number |
| $.esm_eligibility | str |
| $.code_eligible | boolean |
| $.diagnostic_reference_only | boolean |
| $.live_load_factors | object |
| $.live_load_factors.dead | number |
| $.live_load_factors.storage_live | number |
| $.live_load_factors.other_live | number |
| $.live_load_factors.roof_live | number |
| $.stories | array |
| $.stories[] | object |
| $.stories[].story_number | integer |
| $.stories[].story_name | str |
| $.stories[].height_m | number |
| $.stories[].master_node_tag | integer |
| $.stories[].dead_load_kN | number |
| $.stories[].storage_live_load_kN | number |
| $.stories[].other_live_load_kN | number |
| $.stories[].roof_live_load_kN_ignored | number |
| $.stories[].input_note | str |
| $.stories[].roof_live_factor | number |
| $.stories[].seismic_weight_kN | number |
| $.stories[].distribution_exponent_k | number |
| $.stories[].lateral_force_kN | number |
| $.source_pdf | str |
| $.period_source | str |
| $.input_provenance | object |
| $.input_provenance.values | object |
| $.input_provenance.values.soil | str |
| $.input_provenance.values.Z | number |
| $.input_provenance.values.I | integer |
| $.input_provenance.values.period_factor | number |
| $.input_provenance.values.system_excel | str |
| $.input_provenance.values.rmu | number |
| $.input_provenance.values.omegau | number |
| $.input_provenance.values.omegas | number |
| $.input_provenance.values.awx | number |
| $.input_provenance.values.awy | number |
| $.input_provenance.values.workbook_adopted_tx | number |
| $.input_provenance.values.workbook_adopted_ty | number |
| $.input_provenance.values.reference_base_shear_X | number |
| $.input_provenance.values.reference_base_shear_Y | number |
| $.input_provenance.values.source_edb | str |
| $.input_provenance.values.breadth_X | number |
| $.input_provenance.values.breadth_Y | number |
| $.input_provenance.values.workbook_awx | number |
| $.input_provenance.values.workbook_awy | number |
| $.input_provenance.values.wall_geometry_segments | array |
| $.input_provenance.values.wall_geometry_segments[] | object |
| $.input_provenance.values.wall_geometry_segments[].axis | str |
| $.input_provenance.values.wall_geometry_segments[].plane_m | number |
| $.input_provenance.values.wall_geometry_segments[].bay_start_m | number |
| $.input_provenance.values.wall_geometry_segments[].bay_end_m | number |
| $.input_provenance.values.wall_geometry_segments[].thickness_m | number |
| $.input_provenance.values.wall_geometry_segments[].net_wall_length_m | number |
| $.input_provenance.values.wall_geometry_segments[].net_area_m2 | number |
| $.input_provenance.values.wall_geometry_segments[].gross_wall_length_m | number |
| $.input_provenance.values.wall_geometry_segments[].Aw_contribution_m2 | number |
| $.input_provenance.audit | array |
| $.input_provenance.audit[] | object |
| $.input_provenance.audit[].field | str |
| $.input_provenance.audit[].value | str |
| $.input_provenance.audit[].source | str |
| $.input_provenance.audit[].sheet | str |
| $.input_provenance.audit[].cell | str |
| $.input_provenance.notes | array |
| $.input_provenance.notes[] | str |
| $.period_selection | object |
| $.period_selection.direction | str |
| $.period_selection.empirical_Aw_X_m2 | str |
| $.period_selection.empirical_Aw_Y_m2 | str |
| $.period_selection.empirical_multiplier | str |
| $.period_selection.Rayleigh_T1_X_s | null |
| $.period_selection.Rayleigh_T1_Y_s | null |
| $.period_selection.ETABS_or_Excel_reference_T1_X_s | str |
| $.period_selection.ETABS_or_Excel_reference_T1_Y_s | str |
| $.period_selection.ETABS_modal_metadata | object |
| $.period_selection.ETABS_modal_metadata.source | str |
| $.period_selection.ETABS_modal_metadata.references | object |
| $.period_selection.ETABS_modal_metadata.references.adopted_X | object |
| $.period_selection.ETABS_modal_metadata.references.adopted_X.value | number |
| $.period_selection.ETABS_modal_metadata.references.adopted_X.kind | str |
| $.period_selection.ETABS_modal_metadata.references.adopted_X.source | str |
| $.period_selection.ETABS_modal_metadata.references.adopted_X.sheet | str |
| $.period_selection.ETABS_modal_metadata.references.adopted_X.cell | str |
| $.period_selection.ETABS_modal_metadata.references.adopted_Y | object |
| $.period_selection.ETABS_modal_metadata.references.adopted_Y.value | number |
| $.period_selection.ETABS_modal_metadata.references.adopted_Y.kind | str |
| $.period_selection.ETABS_modal_metadata.references.adopted_Y.source | str |
| $.period_selection.ETABS_modal_metadata.references.adopted_Y.sheet | str |
| $.period_selection.ETABS_modal_metadata.references.adopted_Y.cell | str |
| $.period_selection.selected_period_s | str |
| $.period_selection.selection_rule | str |
| $.response_case | str |
| $.comparison_remark | str |
| $.direction_case | str |
| $.accidental_torsion_included | boolean |
| $.accidental_eccentricity_sign | integer |
| $.accidental_eccentricity_m | number |
| $.note | str |

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

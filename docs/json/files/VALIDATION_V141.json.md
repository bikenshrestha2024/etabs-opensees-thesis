# VALIDATION_V141.json

**Source:** [VALIDATION_V141.json](../../../VALIDATION_V141.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 8b60020dd40820f98406388fc0f40fa5a997c24bf3eae09bf6c7194490644724
**Size:** 2610 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.syntax | str |
| $.native_gui | str |
| $.shared_edges | integer |
| $.formula_validation | object |
| $.formula_validation.formula_counts | object |
| $.formula_validation.formula_counts.Storey totals | integer |
| $.formula_validation.formula_counts.Source detail | integer |
| $.formula_validation.formula_counts.Read me | integer |
| $.formula_validation.formula_counts.Surface load formulas | integer |
| $.formula_validation.formula_counts.Loaded node path | integer |
| $.formula_validation.formula_counts.Member weight formulas | integer |
| $.formula_validation.formula_counts.Vertical load path | integer |
| $.formula_validation.floor_load_formula_kN | number |
| $.formula_validation.floor_load_provenance_kN | number |
| $.formula_validation.note | str |
| $.gravity | object |
| $.gravity.steps | integer |
| $.gravity.applied_vertical_load_kN | number |
| $.gravity.support_vertical_reaction_kN | number |
| $.gravity.equilibrium_error_percent | number |
| $.gravity.equilibrium_tolerance_percent | number |
| $.gravity.max_downward_vertical_displacement_m | number |
| $.gravity.elapsed_seconds_before_freeze | number |
| $.gravity.gravity_frozen | boolean |
| $.gravity.elapsed_seconds | number |
| $.gravity.diaphragm_kinematics | object |
| $.gravity.diaphragm_kinematics.max_inplane_constraint_residual | number |
| $.gravity.diaphragm_kinematics.units | str |
| $.mesh_benchmark | object |
| $.mesh_benchmark.scope | str |
| $.mesh_benchmark.results | array |
| $.mesh_benchmark.results[] | object |
| $.mesh_benchmark.results[].subdivisions | integer |
| $.mesh_benchmark.results[].total_load_kN | integer |
| $.mesh_benchmark.results[].support_reaction_kN | number |
| $.mesh_benchmark.results[].max_beam_end_bending_kNm | number |
| $.mesh_benchmark.results[].max_downward_Uz_m | number |
| $.full_nonlinear_record | str |
| $.project_mesh_convergence | str |

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

[All JSON files](../00_ALL_JSON_FILES.md) · [Research citations](../../00_RESEARCH_REFERENCES.md)

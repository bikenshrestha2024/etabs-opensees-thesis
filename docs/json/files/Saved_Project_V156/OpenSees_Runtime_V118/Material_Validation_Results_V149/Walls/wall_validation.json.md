# Saved_Project_V156/OpenSees_Runtime_V118/Material_Validation_Results_V149/Walls/wall_validation.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/Material_Validation_Results_V149/Walls/wall_validation.json](../../../../../../../Saved_Project_V156/OpenSees_Runtime_V118/Material_Validation_Results_V149/Walls/wall_validation.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** a3df2e3bbbdf2f908b990fe05cca85f7cb9a3f9a6ae4afcadac56bff4f39ed4c
**Size:** 4898 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.started_at | str |
| $.sources | object |
| $.sources.kolozvari2023 | object |
| $.sources.kolozvari2023.doi | str |
| $.sources.kolozvari2023.documentation | str |
| $.sources.kolozvari2023.specimens | array |
| $.sources.kolozvari2023.specimens[] | str |
| $.sources.kolozvari2023.status | str |
| $.sources.kolozvari2023.note | str |
| $.sources.lu2015 | object |
| $.sources.lu2015.doi | str |
| $.sources.lu2015.documentation | str |
| $.sources.lu2015.repository | str |
| $.sources.lu2015.note | str |
| $.sources.regularization | object |
| $.sources.regularization.url | str |
| $.sources.regularization.note | str |
| $.checks | object |
| $.checks.formulation_and_native_commands | object |
| $.checks.formulation_and_native_commands.status | str |
| $.checks.formulation_and_native_commands.required_evidence | str |
| $.checks.units_and_density | object |
| $.checks.units_and_density.status | str |
| $.checks.units_and_density.required_evidence | str |
| $.checks.material_monotonic_and_cyclic | object |
| $.checks.material_monotonic_and_cyclic.status | str |
| $.checks.material_monotonic_and_cyclic.required_evidence | str |
| $.checks.axial_equilibrium | object |
| $.checks.axial_equilibrium.status | str |
| $.checks.axial_equilibrium.required_evidence | str |
| $.checks.rigid_body_and_orientation | object |
| $.checks.rigid_body_and_orientation.status | str |
| $.checks.rigid_body_and_orientation.required_evidence | str |
| $.checks.elastic_bending_and_shear | object |
| $.checks.elastic_bending_and_shear.status | str |
| $.checks.elastic_bending_and_shear.required_evidence | str |
| $.checks.cyclic_experiment | object |
| $.checks.cyclic_experiment.status | str |
| $.checks.cyclic_experiment.required_evidence | str |
| $.checks.mesh_objectivity | object |
| $.checks.mesh_objectivity.status | str |
| $.checks.mesh_objectivity.required_evidence | str |
| $.checks.biaxial_and_torsion | object |
| $.checks.biaxial_and_torsion.status | str |
| $.checks.biaxial_and_torsion.required_evidence | str |
| $.checks.openings_and_coupling | object |
| $.checks.openings_and_coupling.status | str |
| $.checks.openings_and_coupling.required_evidence | str |
| $.checks.out_of_plane_and_instability | object |
| $.checks.out_of_plane_and_instability.status | str |
| $.checks.out_of_plane_and_instability.required_evidence | str |
| $.checks.dynamic_convergence | object |
| $.checks.dynamic_convergence.status | str |
| $.checks.dynamic_convergence.required_evidence | str |
| $.checks.independent_validation | object |
| $.checks.independent_validation.status | str |
| $.checks.independent_validation.required_evidence | str |
| $.checks.building_transfer | object |
| $.checks.building_transfer.status | str |
| $.checks.building_transfer.required_evidence | str |
| $.routes | object |
| $.routes.kolozvari2023 | object |
| $.routes.kolozvari2023.status | str |
| $.routes.kolozvari2023.gravity_relative_error | number |
| $.routes.kolozvari2023.history_rows | integer |
| $.routes.kolozvari2023.material_scope | str |
| $.routes.kolozvari2023.boundary_scope | str |
| $.routes.kolozvari2023.loading | str |
| $.routes.kolozvari2023.elapsed_s | number |
| $.routes.lu2015 | object |
| $.routes.lu2015.status | str |
| $.routes.lu2015.gravity_relative_error | number |
| $.routes.lu2015.history_rows | integer |
| $.routes.lu2015.experimental_validation | str |
| $.routes.lu2015.native_units | str |
| $.routes.lu2015.source_sha256 | str |
| $.routes.lu2015.boundary_scope | str |
| $.routes.lu2015.elapsed_s | number |
| $.project_design_approval | boolean |
| $.elapsed_s | number |
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

[All JSON files](../../../../../00_ALL_JSON_FILES.md) · [Research citations](../../../../../../00_RESEARCH_REFERENCES.md)

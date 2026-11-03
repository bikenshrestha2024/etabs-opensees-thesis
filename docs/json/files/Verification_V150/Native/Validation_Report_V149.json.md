# Verification_V150/Native/Validation_Report_V149.json

**Source:** [Verification_V150/Native/Validation_Report_V149.json](../../../../../Verification_V150/Native/Validation_Report_V149.json)
**Classification:** VALIDATION_EVIDENCE
**SHA-256 (source bytes):** 388309726a330a660ef9137e4225814c81071dfaf0fd37edee889c0166b2d60c
**Size:** 11287 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.scope | str |
| $.sources | object |
| $.sources.Concrete01 | object |
| $.sources.Concrete01.documentation | str |
| $.sources.Concrete01.literature | str |
| $.sources.Steel02 | object |
| $.sources.Steel02.documentation | str |
| $.sources.Steel02.literature | str |
| $.sources.FVD | object |
| $.sources.FVD.documentation | str |
| $.sources.FVD.literature | str |
| $.sources.BRB | object |
| $.sources.BRB.documentation | str |
| $.sources.BRB.literature | str |
| $.cases | object |
| $.cases.Concrete01 | object |
| $.cases.Concrete01.parameters | object |
| $.cases.Concrete01.parameters.fpc_MPa | number |
| $.cases.Concrete01.parameters.epsc0 | number |
| $.cases.Concrete01.parameters.fpcu_MPa | number |
| $.cases.Concrete01.parameters.epsU | number |
| $.cases.Concrete01.checks | object |
| $.cases.Concrete01.checks.monotonic_envelope_max_error_MPa | number |
| $.cases.Concrete01.checks.zero_tension_MPa | number |
| $.cases.Concrete01.status | str |
| $.cases.Concrete01.parameter_basis | str |
| $.cases.Concrete01.x_label | str |
| $.cases.Concrete01.y_label | str |
| $.cases.Concrete01.files | array |
| $.cases.Concrete01.files[] | str |
| $.cases.Concrete01.elapsed_s | number |
| $.cases.Steel02 | object |
| $.cases.Steel02.parameters | object |
| $.cases.Steel02.parameters.Fy_MPa | number |
| $.cases.Steel02.parameters.E_MPa | number |
| $.cases.Steel02.parameters.b | number |
| $.cases.Steel02.parameters.R0 | integer |
| $.cases.Steel02.parameters.cR1 | number |
| $.cases.Steel02.parameters.cR2 | number |
| $.cases.Steel02.parameters.a1 | integer |
| $.cases.Steel02.parameters.a2 | integer |
| $.cases.Steel02.parameters.a3 | integer |
| $.cases.Steel02.parameters.a4 | integer |
| $.cases.Steel02.checks | object |
| $.cases.Steel02.checks.initial_modulus_MPa | number |
| $.cases.Steel02.checks.initial_modulus_reference_MPa | number |
| $.cases.Steel02.checks.initial_modulus_relative_error | number |
| $.cases.Steel02.status | str |
| $.cases.Steel02.parameter_basis | str |
| $.cases.Steel02.x_label | str |
| $.cases.Steel02.y_label | str |
| $.cases.Steel02.files | array |
| $.cases.Steel02.files[] | str |
| $.cases.Steel02.elapsed_s | number |
| $.cases.FVD | object |
| $.cases.FVD.parameters | object |
| $.cases.FVD.parameters.K_kN_m | number |
| $.cases.FVD.parameters.Cd_kN_s_m_alpha | number |
| $.cases.FVD.parameters.alpha | number |
| $.cases.FVD.parameters.frequency_Hz | number |
| $.cases.FVD.parameters.amplitudes_m | array |
| $.cases.FVD.parameters.amplitudes_m[] | number |
| $.cases.FVD.parameters.dt_s | number |
| $.cases.FVD.parameters.penalty_kN_m | number |
| $.cases.FVD.checks | object |
| $.cases.FVD.checks.linear_steady_cycle_work_kNm | number |
| $.cases.FVD.checks.linear_steady_cycle_reference_kNm | number |
| $.cases.FVD.checks.linear_cycle_work_relative_error | number |
| $.cases.FVD.checks.linear_Maxwell_error_kN | number |
| $.cases.FVD.checks.refined_error_kN | number |
| $.cases.FVD.checks.prescribed_motion_error_m | number |
| $.cases.FVD.status | str |
| $.cases.FVD.parameter_basis | str |
| $.cases.FVD.x_label | str |
| $.cases.FVD.y_label | str |
| $.cases.FVD.files | array |
| $.cases.FVD.files[] | str |
| $.cases.FVD.elapsed_s | number |
| $.cases.BRB | object |
| $.cases.BRB.parameters | object |
| $.cases.BRB.parameters.Fy_MPa | number |
| $.cases.BRB.parameters.E_MPa | number |
| $.cases.BRB.parameters.b | number |
| $.cases.BRB.parameters.R0 | integer |
| $.cases.BRB.parameters.cR1 | number |
| $.cases.BRB.parameters.cR2 | number |
| $.cases.BRB.parameters.a1 | integer |
| $.cases.BRB.parameters.a2 | integer |
| $.cases.BRB.parameters.a3 | integer |
| $.cases.BRB.parameters.a4 | integer |
| $.cases.BRB.parameters.core_area_m2 | number |
| $.cases.BRB.parameters.yielding_length_m | number |
| $.cases.BRB.checks | object |
| $.cases.BRB.checks.initial_modulus_MPa | number |
| $.cases.BRB.checks.initial_modulus_reference_MPa | number |
| $.cases.BRB.checks.initial_modulus_relative_error | number |
| $.cases.BRB.checks.yield_force_reference_kN | number |
| $.cases.BRB.checks.elastic_axial_stiffness_kN_m | number |
| $.cases.BRB.checks.coupon_vs_corotTruss_max_error_kN | number |
| $.cases.BRB.status | str |
| $.cases.BRB.parameter_basis | str |
| $.cases.BRB.x_label | str |
| $.cases.BRB.y_label | str |
| $.cases.BRB.files | array |
| $.cases.BRB.files[] | str |
| $.cases.BRB.elapsed_s | number |
| $.started | str |
| $.walls | object |
| $.walls.started_at | str |
| $.walls.sources | object |
| $.walls.sources.kolozvari2023 | object |
| $.walls.sources.kolozvari2023.doi | str |
| $.walls.sources.kolozvari2023.documentation | str |
| $.walls.sources.kolozvari2023.specimens | array |
| $.walls.sources.kolozvari2023.specimens[] | str |
| $.walls.sources.kolozvari2023.status | str |
| $.walls.sources.kolozvari2023.note | str |
| $.walls.sources.lu2015 | object |
| $.walls.sources.lu2015.doi | str |
| $.walls.sources.lu2015.documentation | str |
| $.walls.sources.lu2015.repository | str |
| $.walls.sources.lu2015.note | str |
| $.walls.sources.regularization | object |
| $.walls.sources.regularization.url | str |
| $.walls.sources.regularization.note | str |
| $.walls.checks | object |
| $.walls.checks.formulation_and_native_commands | object |
| $.walls.checks.formulation_and_native_commands.status | str |
| $.walls.checks.formulation_and_native_commands.required_evidence | str |
| $.walls.checks.units_and_density | object |
| $.walls.checks.units_and_density.status | str |
| $.walls.checks.units_and_density.required_evidence | str |
| $.walls.checks.material_monotonic_and_cyclic | object |
| $.walls.checks.material_monotonic_and_cyclic.status | str |
| $.walls.checks.material_monotonic_and_cyclic.required_evidence | str |
| $.walls.checks.axial_equilibrium | object |
| $.walls.checks.axial_equilibrium.status | str |
| $.walls.checks.axial_equilibrium.required_evidence | str |
| $.walls.checks.rigid_body_and_orientation | object |
| $.walls.checks.rigid_body_and_orientation.status | str |
| $.walls.checks.rigid_body_and_orientation.required_evidence | str |
| $.walls.checks.elastic_bending_and_shear | object |
| $.walls.checks.elastic_bending_and_shear.status | str |
| $.walls.checks.elastic_bending_and_shear.required_evidence | str |
| $.walls.checks.cyclic_experiment | object |
| $.walls.checks.cyclic_experiment.status | str |
| $.walls.checks.cyclic_experiment.required_evidence | str |
| $.walls.checks.mesh_objectivity | object |
| $.walls.checks.mesh_objectivity.status | str |
| $.walls.checks.mesh_objectivity.required_evidence | str |
| $.walls.checks.biaxial_and_torsion | object |
| $.walls.checks.biaxial_and_torsion.status | str |
| $.walls.checks.biaxial_and_torsion.required_evidence | str |
| $.walls.checks.openings_and_coupling | object |
| $.walls.checks.openings_and_coupling.status | str |
| $.walls.checks.openings_and_coupling.required_evidence | str |
| $.walls.checks.out_of_plane_and_instability | object |
| $.walls.checks.out_of_plane_and_instability.status | str |
| $.walls.checks.out_of_plane_and_instability.required_evidence | str |
| $.walls.checks.dynamic_convergence | object |
| $.walls.checks.dynamic_convergence.status | str |
| $.walls.checks.dynamic_convergence.required_evidence | str |
| $.walls.checks.independent_validation | object |
| $.walls.checks.independent_validation.status | str |
| $.walls.checks.independent_validation.required_evidence | str |
| $.walls.checks.building_transfer | object |
| $.walls.checks.building_transfer.status | str |
| $.walls.checks.building_transfer.required_evidence | str |
| $.walls.routes | object |
| $.walls.routes.kolozvari2023 | object |
| $.walls.routes.kolozvari2023.status | str |
| $.walls.routes.kolozvari2023.gravity_relative_error | number |
| $.walls.routes.kolozvari2023.history_rows | integer |
| $.walls.routes.kolozvari2023.material_scope | str |
| $.walls.routes.kolozvari2023.boundary_scope | str |
| $.walls.routes.kolozvari2023.loading | str |
| $.walls.routes.kolozvari2023.elapsed_s | number |
| $.walls.routes.lu2015 | object |
| $.walls.routes.lu2015.status | str |
| $.walls.routes.lu2015.gravity_relative_error | number |
| $.walls.routes.lu2015.history_rows | integer |
| $.walls.routes.lu2015.experimental_validation | str |
| $.walls.routes.lu2015.native_units | str |
| $.walls.routes.lu2015.source_sha256 | str |
| $.walls.routes.lu2015.boundary_scope | str |
| $.walls.routes.lu2015.elapsed_s | number |
| $.walls.project_design_approval | boolean |
| $.walls.elapsed_s | number |
| $.walls.scope | str |
| $.original_SFI_2021 | object |
| $.original_SFI_2021.status | str |
| $.original_SFI_2021.error | str |
| $.original_SFI_2021.native_exit_code | integer |
| $.original_SFI_source | str |
| $.elapsed_s | number |
| $.finished | str |
| $.project_approved | boolean |

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

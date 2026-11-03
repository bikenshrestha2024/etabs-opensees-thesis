# Verification_V159/Official_Concrete02/report.json

**Source:** [Verification_V159/Official_Concrete02/report.json](../../../../../Verification_V159/Official_Concrete02/report.json)
**Classification:** VALIDATION_EVIDENCE
**SHA-256 (source bytes):** 86cdbc342d5e2da00ff4dbbf1e40d0f2d191c5ee1a051e40c0909decfe1e8007
**Size:** 3811 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.input | object |
| $.input.model | str |
| $.input.parameters | object |
| $.input.parameters.fpc_MPa | number |
| $.input.parameters.epsc0 | number |
| $.input.parameters.fpcu_MPa | number |
| $.input.parameters.epsU | number |
| $.input.parameters.unloading_ratio | number |
| $.input.parameters.ft_MPa | number |
| $.input.parameters.Ets_MPa | number |
| $.input.parameter_basis | str |
| $.input.specimen_id | str |
| $.input.citation | str |
| $.input.source | str |
| $.input.protocol_csv | str |
| $.input.measured_csv | str |
| $.input.fit_bounds | object(empty) |
| $.input.train_fraction | number |
| $.input.scope | str |
| $.input.wall_formulation | str |
| $.input.targets | array |
| $.input.targets[] | number |
| $.input.samples_per_leg | integer |
| $.input.dt_s | number |
| $.input.profile_id | str |
| $.input.project_transfer_approved | boolean |
| $.input.provenance | object |
| $.input.provenance.fpc_MPa | object |
| $.input.provenance.fpc_MPa.value | number |
| $.input.provenance.fpc_MPa.unit | str |
| $.input.provenance.fpc_MPa.basis | str |
| $.input.provenance.fpc_MPa.source | str |
| $.input.provenance.fpc_MPa.locator | str |
| $.input.provenance.epsc0 | object |
| $.input.provenance.epsc0.value | number |
| $.input.provenance.epsc0.unit | str |
| $.input.provenance.epsc0.basis | str |
| $.input.provenance.epsc0.source | str |
| $.input.provenance.epsc0.locator | str |
| $.input.provenance.fpcu_MPa | object |
| $.input.provenance.fpcu_MPa.value | number |
| $.input.provenance.fpcu_MPa.unit | str |
| $.input.provenance.fpcu_MPa.basis | str |
| $.input.provenance.fpcu_MPa.source | str |
| $.input.provenance.fpcu_MPa.locator | str |
| $.input.provenance.epsU | object |
| $.input.provenance.epsU.value | number |
| $.input.provenance.epsU.unit | str |
| $.input.provenance.epsU.basis | str |
| $.input.provenance.epsU.source | str |
| $.input.provenance.epsU.locator | str |
| $.input.provenance.unloading_ratio | object |
| $.input.provenance.unloading_ratio.value | number |
| $.input.provenance.unloading_ratio.unit | str |
| $.input.provenance.unloading_ratio.basis | str |
| $.input.provenance.unloading_ratio.source | str |
| $.input.provenance.unloading_ratio.locator | str |
| $.input.provenance.ft_MPa | object |
| $.input.provenance.ft_MPa.value | number |
| $.input.provenance.ft_MPa.unit | str |
| $.input.provenance.ft_MPa.basis | str |
| $.input.provenance.ft_MPa.source | str |
| $.input.provenance.ft_MPa.locator | str |
| $.input.provenance.Ets_MPa | object |
| $.input.provenance.Ets_MPa.value | number |
| $.input.provenance.Ets_MPa.unit | str |
| $.input.provenance.Ets_MPa.basis | str |
| $.input.provenance.Ets_MPa.source | str |
| $.input.provenance.Ets_MPa.locator | str |
| $.input._output | str |
| $.optimizer | object(empty) |
| $.metrics | object(empty) |
| $.status | str |
| $.elapsed_s | number |
| $.finished_at | str |
| $.project_transfer_approved | boolean |

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

# Verification_V159/Fit_Steel02/report.json

**Source:** [Verification_V159/Fit_Steel02/report.json](../../../../../Verification_V159/Fit_Steel02/report.json)
**Classification:** VALIDATION_EVIDENCE
**SHA-256 (source bytes):** 00c4045afa5090a5bec55fd37e3a599fa5b926bc6a605c69008d141d821d94c8
**Size:** 8057 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.input | object |
| $.input.model | str |
| $.input.parameters | object |
| $.input.parameters.Fy_MPa | number |
| $.input.parameters.E_MPa | number |
| $.input.parameters.b | number |
| $.input.parameters.R0 | number |
| $.input.parameters.cR1 | number |
| $.input.parameters.cR2 | number |
| $.input.parameters.a1 | number |
| $.input.parameters.a2 | number |
| $.input.parameters.a3 | number |
| $.input.parameters.a4 | number |
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
| $.input.fit_metrics | object |
| $.input.fit_metrics.model | str |
| $.input.fit_metrics.specimen | str |
| $.input.fit_metrics.status | str |
| $.input.fit_metrics.parameters | object |
| $.input.fit_metrics.parameters.Fy_MPa | number |
| $.input.fit_metrics.parameters.E_MPa | number |
| $.input.fit_metrics.parameters.b | number |
| $.input.fit_metrics.parameters.cR1 | number |
| $.input.fit_metrics.parameters.cR2 | number |
| $.input.fit_metrics.parameters.a1 | number |
| $.input.fit_metrics.parameters.a3 | number |
| $.input.fit_metrics.fixed_parameters | object |
| $.input.fit_metrics.fixed_parameters.R0 | number |
| $.input.fit_metrics.fixed_parameters.a2 | number |
| $.input.fit_metrics.fixed_parameters.a4 | number |
| $.input.fit_metrics.fixed_parameters.sigInit | number |
| $.input.fit_metrics.training | object |
| $.input.fit_metrics.training.RMSE_MPa | number |
| $.input.fit_metrics.training.MAE_MPa | number |
| $.input.fit_metrics.training.max_absolute_error_MPa | number |
| $.input.fit_metrics.training.n | integer |
| $.input.fit_metrics.withheld_tail | object |
| $.input.fit_metrics.withheld_tail.RMSE_MPa | number |
| $.input.fit_metrics.withheld_tail.MAE_MPa | number |
| $.input.fit_metrics.withheld_tail.max_absolute_error_MPa | number |
| $.input.fit_metrics.withheld_tail.n | integer |
| $.input.fit_metrics.full_history | object |
| $.input.fit_metrics.full_history.RMSE_MPa | number |
| $.input.fit_metrics.full_history.MAE_MPa | number |
| $.input.fit_metrics.full_history.max_absolute_error_MPa | number |
| $.input.fit_metrics.full_history.n | integer |
| $.input.fit_metrics.training_samples | integer |
| $.input.fit_metrics.withheld_samples | integer |
| $.input.fit_metrics.validation_scope | str |
| $.input.fit_metrics.optimizer | object |
| $.input.fit_metrics.optimizer.method | str |
| $.input.fit_metrics.optimizer.success | boolean |
| $.input.fit_metrics.optimizer.message | str |
| $.input.fit_metrics.optimizer.nfev | integer |
| $.input.fit_metrics.elapsed_s | number |
| $.input.fit_metrics.sources | object |
| $.input.fit_metrics.sources.matTestAllParamsReadStrain.tcl | object |
| $.input.fit_metrics.sources.matTestAllParamsReadStrain.tcl.git_blob_sha | str |
| $.input.fit_metrics.sources.matTestAllParamsReadStrain.tcl.url | str |
| $.input.fit_metrics.sources.stress.1.coords | object |
| $.input.fit_metrics.sources.stress.1.coords.git_blob_sha | str |
| $.input.fit_metrics.sources.stress.1.coords.url | str |
| $.input.fit_metrics.sources.calDataField.csv | object |
| $.input.fit_metrics.sources.calDataField.csv.git_blob_sha | str |
| $.input.fit_metrics.sources.calDataField.csv.url | str |
| $.input.fit_metrics.documentation | str |
| $.input.fit_metrics.units | str |
| $.input.profile_id | str |
| $.input.project_transfer_approved | boolean |
| $.input.provenance | object |
| $.input.provenance.Fy_MPa | object |
| $.input.provenance.Fy_MPa.value | number |
| $.input.provenance.Fy_MPa.unit | str |
| $.input.provenance.Fy_MPa.basis | str |
| $.input.provenance.Fy_MPa.source | str |
| $.input.provenance.Fy_MPa.locator | str |
| $.input.provenance.E_MPa | object |
| $.input.provenance.E_MPa.value | number |
| $.input.provenance.E_MPa.unit | str |
| $.input.provenance.E_MPa.basis | str |
| $.input.provenance.E_MPa.source | str |
| $.input.provenance.E_MPa.locator | str |
| $.input.provenance.b | object |
| $.input.provenance.b.value | number |
| $.input.provenance.b.unit | str |
| $.input.provenance.b.basis | str |
| $.input.provenance.b.source | str |
| $.input.provenance.b.locator | str |
| $.input.provenance.R0 | object |
| $.input.provenance.R0.value | number |
| $.input.provenance.R0.unit | str |
| $.input.provenance.R0.basis | str |
| $.input.provenance.R0.source | str |
| $.input.provenance.R0.locator | str |
| $.input.provenance.cR1 | object |
| $.input.provenance.cR1.value | number |
| $.input.provenance.cR1.unit | str |
| $.input.provenance.cR1.basis | str |
| $.input.provenance.cR1.source | str |
| $.input.provenance.cR1.locator | str |
| $.input.provenance.cR2 | object |
| $.input.provenance.cR2.value | number |
| $.input.provenance.cR2.unit | str |
| $.input.provenance.cR2.basis | str |
| $.input.provenance.cR2.source | str |
| $.input.provenance.cR2.locator | str |
| $.input.provenance.a1 | object |
| $.input.provenance.a1.value | number |
| $.input.provenance.a1.unit | str |
| $.input.provenance.a1.basis | str |
| $.input.provenance.a1.source | str |
| $.input.provenance.a1.locator | str |
| $.input.provenance.a2 | object |
| $.input.provenance.a2.value | number |
| $.input.provenance.a2.unit | str |
| $.input.provenance.a2.basis | str |
| $.input.provenance.a2.source | str |
| $.input.provenance.a2.locator | str |
| $.input.provenance.a3 | object |
| $.input.provenance.a3.value | number |
| $.input.provenance.a3.unit | str |
| $.input.provenance.a3.basis | str |
| $.input.provenance.a3.source | str |
| $.input.provenance.a3.locator | str |
| $.input.provenance.a4 | object |
| $.input.provenance.a4.value | number |
| $.input.provenance.a4.unit | str |
| $.input.provenance.a4.basis | str |
| $.input.provenance.a4.source | str |
| $.input.provenance.a4.locator | str |
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

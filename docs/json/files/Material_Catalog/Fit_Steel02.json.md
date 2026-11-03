# Material_Catalog/Fit_Steel02.json

**Source:** [Material_Catalog/Fit_Steel02.json](../../../../Material_Catalog/Fit_Steel02.json)
**Classification:** MATERIAL_PROFILE
**SHA-256 (source bytes):** ad968102d43894782756caffb02a3dc3b081ad89bdfa1cc1349e87815cdb55b4
**Size:** 7361 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.model | str |
| $.parameters | object |
| $.parameters.Fy_MPa | number |
| $.parameters.E_MPa | number |
| $.parameters.b | number |
| $.parameters.R0 | number |
| $.parameters.cR1 | number |
| $.parameters.cR2 | number |
| $.parameters.a1 | number |
| $.parameters.a2 | number |
| $.parameters.a3 | number |
| $.parameters.a4 | number |
| $.parameter_basis | str |
| $.specimen_id | str |
| $.citation | str |
| $.source | str |
| $.protocol_csv | str |
| $.measured_csv | str |
| $.fit_bounds | object(empty) |
| $.train_fraction | number |
| $.scope | str |
| $.wall_formulation | str |
| $.targets | array |
| $.targets[] | number |
| $.samples_per_leg | integer |
| $.dt_s | number |
| $.fit_metrics | object |
| $.fit_metrics.model | str |
| $.fit_metrics.specimen | str |
| $.fit_metrics.status | str |
| $.fit_metrics.parameters | object |
| $.fit_metrics.parameters.Fy_MPa | number |
| $.fit_metrics.parameters.E_MPa | number |
| $.fit_metrics.parameters.b | number |
| $.fit_metrics.parameters.cR1 | number |
| $.fit_metrics.parameters.cR2 | number |
| $.fit_metrics.parameters.a1 | number |
| $.fit_metrics.parameters.a3 | number |
| $.fit_metrics.fixed_parameters | object |
| $.fit_metrics.fixed_parameters.R0 | number |
| $.fit_metrics.fixed_parameters.a2 | number |
| $.fit_metrics.fixed_parameters.a4 | number |
| $.fit_metrics.fixed_parameters.sigInit | number |
| $.fit_metrics.training | object |
| $.fit_metrics.training.RMSE_MPa | number |
| $.fit_metrics.training.MAE_MPa | number |
| $.fit_metrics.training.max_absolute_error_MPa | number |
| $.fit_metrics.training.n | integer |
| $.fit_metrics.withheld_tail | object |
| $.fit_metrics.withheld_tail.RMSE_MPa | number |
| $.fit_metrics.withheld_tail.MAE_MPa | number |
| $.fit_metrics.withheld_tail.max_absolute_error_MPa | number |
| $.fit_metrics.withheld_tail.n | integer |
| $.fit_metrics.full_history | object |
| $.fit_metrics.full_history.RMSE_MPa | number |
| $.fit_metrics.full_history.MAE_MPa | number |
| $.fit_metrics.full_history.max_absolute_error_MPa | number |
| $.fit_metrics.full_history.n | integer |
| $.fit_metrics.training_samples | integer |
| $.fit_metrics.withheld_samples | integer |
| $.fit_metrics.validation_scope | str |
| $.fit_metrics.optimizer | object |
| $.fit_metrics.optimizer.method | str |
| $.fit_metrics.optimizer.success | boolean |
| $.fit_metrics.optimizer.message | str |
| $.fit_metrics.optimizer.nfev | integer |
| $.fit_metrics.elapsed_s | number |
| $.fit_metrics.sources | object |
| $.fit_metrics.sources.matTestAllParamsReadStrain.tcl | object |
| $.fit_metrics.sources.matTestAllParamsReadStrain.tcl.git_blob_sha | str |
| $.fit_metrics.sources.matTestAllParamsReadStrain.tcl.url | str |
| $.fit_metrics.sources.stress.1.coords | object |
| $.fit_metrics.sources.stress.1.coords.git_blob_sha | str |
| $.fit_metrics.sources.stress.1.coords.url | str |
| $.fit_metrics.sources.calDataField.csv | object |
| $.fit_metrics.sources.calDataField.csv.git_blob_sha | str |
| $.fit_metrics.sources.calDataField.csv.url | str |
| $.fit_metrics.documentation | str |
| $.fit_metrics.units | str |
| $.profile_id | str |
| $.project_transfer_approved | boolean |
| $.provenance | object |
| $.provenance.Fy_MPa | object |
| $.provenance.Fy_MPa.value | number |
| $.provenance.Fy_MPa.unit | str |
| $.provenance.Fy_MPa.basis | str |
| $.provenance.Fy_MPa.source | str |
| $.provenance.Fy_MPa.locator | str |
| $.provenance.E_MPa | object |
| $.provenance.E_MPa.value | number |
| $.provenance.E_MPa.unit | str |
| $.provenance.E_MPa.basis | str |
| $.provenance.E_MPa.source | str |
| $.provenance.E_MPa.locator | str |
| $.provenance.b | object |
| $.provenance.b.value | number |
| $.provenance.b.unit | str |
| $.provenance.b.basis | str |
| $.provenance.b.source | str |
| $.provenance.b.locator | str |
| $.provenance.R0 | object |
| $.provenance.R0.value | number |
| $.provenance.R0.unit | str |
| $.provenance.R0.basis | str |
| $.provenance.R0.source | str |
| $.provenance.R0.locator | str |
| $.provenance.cR1 | object |
| $.provenance.cR1.value | number |
| $.provenance.cR1.unit | str |
| $.provenance.cR1.basis | str |
| $.provenance.cR1.source | str |
| $.provenance.cR1.locator | str |
| $.provenance.cR2 | object |
| $.provenance.cR2.value | number |
| $.provenance.cR2.unit | str |
| $.provenance.cR2.basis | str |
| $.provenance.cR2.source | str |
| $.provenance.cR2.locator | str |
| $.provenance.a1 | object |
| $.provenance.a1.value | number |
| $.provenance.a1.unit | str |
| $.provenance.a1.basis | str |
| $.provenance.a1.source | str |
| $.provenance.a1.locator | str |
| $.provenance.a2 | object |
| $.provenance.a2.value | number |
| $.provenance.a2.unit | str |
| $.provenance.a2.basis | str |
| $.provenance.a2.source | str |
| $.provenance.a2.locator | str |
| $.provenance.a3 | object |
| $.provenance.a3.value | number |
| $.provenance.a3.unit | str |
| $.provenance.a3.basis | str |
| $.provenance.a3.source | str |
| $.provenance.a3.locator | str |
| $.provenance.a4 | object |
| $.provenance.a4.value | number |
| $.provenance.a4.unit | str |
| $.provenance.a4.basis | str |
| $.provenance.a4.source | str |
| $.provenance.a4.locator | str |

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

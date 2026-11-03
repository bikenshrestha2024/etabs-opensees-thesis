# Saved_Project_V156/OpenSees_Runtime_V118/Calibration_Steel02/results/Steel02_Calibrated_Coupon.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/Calibration_Steel02/results/Steel02_Calibrated_Coupon.json](../../../../../../../Saved_Project_V156/OpenSees_Runtime_V118/Calibration_Steel02/results/Steel02_Calibrated_Coupon.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** eb5300a65855a3925b06c45101964164941854eef579e8286062b7b34804d678
**Size:** 2303 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.model | str |
| $.specimen | str |
| $.status | str |
| $.parameters | object |
| $.parameters.Fy_MPa | number |
| $.parameters.E_MPa | number |
| $.parameters.b | number |
| $.parameters.cR1 | number |
| $.parameters.cR2 | number |
| $.parameters.a1 | number |
| $.parameters.a3 | number |
| $.fixed_parameters | object |
| $.fixed_parameters.R0 | number |
| $.fixed_parameters.a2 | number |
| $.fixed_parameters.a4 | number |
| $.fixed_parameters.sigInit | number |
| $.training | object |
| $.training.RMSE_MPa | number |
| $.training.MAE_MPa | number |
| $.training.max_absolute_error_MPa | number |
| $.training.n | integer |
| $.withheld_tail | object |
| $.withheld_tail.RMSE_MPa | number |
| $.withheld_tail.MAE_MPa | number |
| $.withheld_tail.max_absolute_error_MPa | number |
| $.withheld_tail.n | integer |
| $.full_history | object |
| $.full_history.RMSE_MPa | number |
| $.full_history.MAE_MPa | number |
| $.full_history.max_absolute_error_MPa | number |
| $.full_history.n | integer |
| $.training_samples | integer |
| $.withheld_samples | integer |
| $.validation_scope | str |
| $.optimizer | object |
| $.optimizer.method | str |
| $.optimizer.success | boolean |
| $.optimizer.message | str |
| $.optimizer.nfev | integer |
| $.elapsed_s | number |
| $.sources | object |
| $.sources.matTestAllParamsReadStrain.tcl | object |
| $.sources.matTestAllParamsReadStrain.tcl.git_blob_sha | str |
| $.sources.matTestAllParamsReadStrain.tcl.url | str |
| $.sources.stress.1.coords | object |
| $.sources.stress.1.coords.git_blob_sha | str |
| $.sources.stress.1.coords.url | str |
| $.sources.calDataField.csv | object |
| $.sources.calDataField.csv.git_blob_sha | str |
| $.sources.calDataField.csv.url | str |
| $.documentation | str |
| $.units | str |

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

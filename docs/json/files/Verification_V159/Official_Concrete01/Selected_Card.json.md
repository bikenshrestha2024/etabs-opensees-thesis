# Verification_V159/Official_Concrete01/Selected_Card.json

**Source:** [Verification_V159/Official_Concrete01/Selected_Card.json](../../../../../Verification_V159/Official_Concrete01/Selected_Card.json)
**Classification:** VALIDATION_EVIDENCE
**SHA-256 (source bytes):** 78174e0c28482bf750fc1e44d11a18f965426fd2cdb1678c08706c6a4e634408
**Size:** 2233 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.model | str |
| $.parameters | object |
| $.parameters.fpc_MPa | number |
| $.parameters.epsc0 | number |
| $.parameters.fpcu_MPa | number |
| $.parameters.epsU | number |
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
| $.profile_id | str |
| $.project_transfer_approved | boolean |
| $.provenance | object |
| $.provenance.fpc_MPa | object |
| $.provenance.fpc_MPa.value | number |
| $.provenance.fpc_MPa.unit | str |
| $.provenance.fpc_MPa.basis | str |
| $.provenance.fpc_MPa.source | str |
| $.provenance.fpc_MPa.locator | str |
| $.provenance.epsc0 | object |
| $.provenance.epsc0.value | number |
| $.provenance.epsc0.unit | str |
| $.provenance.epsc0.basis | str |
| $.provenance.epsc0.source | str |
| $.provenance.epsc0.locator | str |
| $.provenance.fpcu_MPa | object |
| $.provenance.fpcu_MPa.value | number |
| $.provenance.fpcu_MPa.unit | str |
| $.provenance.fpcu_MPa.basis | str |
| $.provenance.fpcu_MPa.source | str |
| $.provenance.fpcu_MPa.locator | str |
| $.provenance.epsU | object |
| $.provenance.epsU.value | number |
| $.provenance.epsU.unit | str |
| $.provenance.epsU.basis | str |
| $.provenance.epsU.source | str |
| $.provenance.epsU.locator | str |
| $.source_native_values | object |
| $.source_native_values.fpc_ksi | integer |
| $.source_native_values.epsc0 | number |
| $.source_native_values.fpcu_ksi | integer |
| $.source_native_values.epsU | number |
| $.source_native_values.ksi_to_MPa | number |

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

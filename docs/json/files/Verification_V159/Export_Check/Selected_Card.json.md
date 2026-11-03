# Verification_V159/Export_Check/Selected_Card.json

**Source:** [Verification_V159/Export_Check/Selected_Card.json](../../../../../Verification_V159/Export_Check/Selected_Card.json)
**Classification:** VALIDATION_EVIDENCE
**SHA-256 (source bytes):** c8ede61e37a6b1d9fe9d1ccdd7c10bd03565c242a39a105d9009f55b948900d2
**Size:** 4409 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.model | str |
| $.parameters | object |
| $.parameters.fpcc | number |
| $.parameters.epcc | number |
| $.parameters.Ec | number |
| $.parameters.rc | number |
| $.parameters.xcrn | number |
| $.parameters.ft | number |
| $.parameters.et | number |
| $.parameters.rt | number |
| $.parameters.xcrp | number |
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
| $.provenance.fpcc | object |
| $.provenance.fpcc.value | number |
| $.provenance.fpcc.unit | str |
| $.provenance.fpcc.basis | str |
| $.provenance.fpcc.source | str |
| $.provenance.fpcc.locator | str |
| $.provenance.epcc | object |
| $.provenance.epcc.value | number |
| $.provenance.epcc.unit | str |
| $.provenance.epcc.basis | str |
| $.provenance.epcc.source | str |
| $.provenance.epcc.locator | str |
| $.provenance.Ec | object |
| $.provenance.Ec.value | number |
| $.provenance.Ec.unit | str |
| $.provenance.Ec.basis | str |
| $.provenance.Ec.source | str |
| $.provenance.Ec.locator | str |
| $.provenance.rc | object |
| $.provenance.rc.value | number |
| $.provenance.rc.unit | str |
| $.provenance.rc.basis | str |
| $.provenance.rc.source | str |
| $.provenance.rc.locator | str |
| $.provenance.xcrn | object |
| $.provenance.xcrn.value | number |
| $.provenance.xcrn.unit | str |
| $.provenance.xcrn.basis | str |
| $.provenance.xcrn.source | str |
| $.provenance.xcrn.locator | str |
| $.provenance.ft | object |
| $.provenance.ft.value | number |
| $.provenance.ft.unit | str |
| $.provenance.ft.basis | str |
| $.provenance.ft.source | str |
| $.provenance.ft.locator | str |
| $.provenance.et | object |
| $.provenance.et.value | number |
| $.provenance.et.unit | str |
| $.provenance.et.basis | str |
| $.provenance.et.source | str |
| $.provenance.et.locator | str |
| $.provenance.rt | object |
| $.provenance.rt.value | number |
| $.provenance.rt.unit | str |
| $.provenance.rt.basis | str |
| $.provenance.rt.source | str |
| $.provenance.rt.locator | str |
| $.provenance.xcrp | object |
| $.provenance.xcrp.value | number |
| $.provenance.xcrp.unit | str |
| $.provenance.xcrp.basis | str |
| $.provenance.xcrp.source | str |
| $.provenance.xcrp.locator | str |
| $.source_native_values | object |
| $.source_native_values.fpcc_ksi | number |
| $.source_native_values.Ec_ksi | integer |
| $.source_native_values.ft_ksi | number |
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

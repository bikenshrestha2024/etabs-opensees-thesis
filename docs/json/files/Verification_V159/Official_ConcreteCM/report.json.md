# Verification_V159/Official_ConcreteCM/report.json

**Source:** [Verification_V159/Official_ConcreteCM/report.json](../../../../../Verification_V159/Official_ConcreteCM/report.json)
**Classification:** VALIDATION_EVIDENCE
**SHA-256 (source bytes):** 70dac803a89b963c4974a204fb346d31a78a8c8811b5c232bd4c07c60b60e263
**Size:** 4989 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.input | object |
| $.input.model | str |
| $.input.parameters | object |
| $.input.parameters.fpcc | number |
| $.input.parameters.epcc | number |
| $.input.parameters.Ec | number |
| $.input.parameters.rc | number |
| $.input.parameters.xcrn | number |
| $.input.parameters.ft | number |
| $.input.parameters.et | number |
| $.input.parameters.rt | number |
| $.input.parameters.xcrp | number |
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
| $.input.provenance.fpcc | object |
| $.input.provenance.fpcc.value | number |
| $.input.provenance.fpcc.unit | str |
| $.input.provenance.fpcc.basis | str |
| $.input.provenance.fpcc.source | str |
| $.input.provenance.fpcc.locator | str |
| $.input.provenance.epcc | object |
| $.input.provenance.epcc.value | number |
| $.input.provenance.epcc.unit | str |
| $.input.provenance.epcc.basis | str |
| $.input.provenance.epcc.source | str |
| $.input.provenance.epcc.locator | str |
| $.input.provenance.Ec | object |
| $.input.provenance.Ec.value | number |
| $.input.provenance.Ec.unit | str |
| $.input.provenance.Ec.basis | str |
| $.input.provenance.Ec.source | str |
| $.input.provenance.Ec.locator | str |
| $.input.provenance.rc | object |
| $.input.provenance.rc.value | number |
| $.input.provenance.rc.unit | str |
| $.input.provenance.rc.basis | str |
| $.input.provenance.rc.source | str |
| $.input.provenance.rc.locator | str |
| $.input.provenance.xcrn | object |
| $.input.provenance.xcrn.value | number |
| $.input.provenance.xcrn.unit | str |
| $.input.provenance.xcrn.basis | str |
| $.input.provenance.xcrn.source | str |
| $.input.provenance.xcrn.locator | str |
| $.input.provenance.ft | object |
| $.input.provenance.ft.value | number |
| $.input.provenance.ft.unit | str |
| $.input.provenance.ft.basis | str |
| $.input.provenance.ft.source | str |
| $.input.provenance.ft.locator | str |
| $.input.provenance.et | object |
| $.input.provenance.et.value | number |
| $.input.provenance.et.unit | str |
| $.input.provenance.et.basis | str |
| $.input.provenance.et.source | str |
| $.input.provenance.et.locator | str |
| $.input.provenance.rt | object |
| $.input.provenance.rt.value | number |
| $.input.provenance.rt.unit | str |
| $.input.provenance.rt.basis | str |
| $.input.provenance.rt.source | str |
| $.input.provenance.rt.locator | str |
| $.input.provenance.xcrp | object |
| $.input.provenance.xcrp.value | number |
| $.input.provenance.xcrp.unit | str |
| $.input.provenance.xcrp.basis | str |
| $.input.provenance.xcrp.source | str |
| $.input.provenance.xcrp.locator | str |
| $.input.source_native_values | object |
| $.input.source_native_values.fpcc_ksi | number |
| $.input.source_native_values.Ec_ksi | integer |
| $.input.source_native_values.ft_ksi | number |
| $.input.source_native_values.ksi_to_MPa | number |
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

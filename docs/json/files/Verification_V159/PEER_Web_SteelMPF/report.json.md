# Verification_V159/PEER_Web_SteelMPF/report.json

**Source:** [Verification_V159/PEER_Web_SteelMPF/report.json](../../../../../Verification_V159/PEER_Web_SteelMPF/report.json)
**Classification:** VALIDATION_EVIDENCE
**SHA-256 (source bytes):** 05f6a269de9510dca14e6037b72b7f71942614d10a950f65b28c260ec7653807
**Size:** 6396 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.input | object |
| $.input.model | str |
| $.input.parameters | object |
| $.input.parameters.fyp | number |
| $.input.parameters.fyn | number |
| $.input.parameters.E0 | number |
| $.input.parameters.bp | number |
| $.input.parameters.bn | number |
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
| $.input.profile_id | str |
| $.input.project_transfer_approved | boolean |
| $.input.provenance | object |
| $.input.provenance.fyp | object |
| $.input.provenance.fyp.value | number |
| $.input.provenance.fyp.unit | str |
| $.input.provenance.fyp.basis | str |
| $.input.provenance.fyp.source | str |
| $.input.provenance.fyp.locator | str |
| $.input.provenance.fyn | object |
| $.input.provenance.fyn.value | number |
| $.input.provenance.fyn.unit | str |
| $.input.provenance.fyn.basis | str |
| $.input.provenance.fyn.source | str |
| $.input.provenance.fyn.locator | str |
| $.input.provenance.E0 | object |
| $.input.provenance.E0.value | number |
| $.input.provenance.E0.unit | str |
| $.input.provenance.E0.basis | str |
| $.input.provenance.E0.source | str |
| $.input.provenance.E0.locator | str |
| $.input.provenance.bp | object |
| $.input.provenance.bp.value | number |
| $.input.provenance.bp.unit | str |
| $.input.provenance.bp.basis | str |
| $.input.provenance.bp.source | str |
| $.input.provenance.bp.locator | str |
| $.input.provenance.bn | object |
| $.input.provenance.bn.value | number |
| $.input.provenance.bn.unit | str |
| $.input.provenance.bn.basis | str |
| $.input.provenance.bn.source | str |
| $.input.provenance.bn.locator | str |
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
| $.input.source_native_values | object |
| $.input.source_native_values.fy_web_x_ksi | number |
| $.input.source_native_values.fy_web_y_ksi | number |
| $.input.source_native_values.fy_boundary_y_ksi | number |
| $.input.source_native_values.E0_ksi | number |
| $.input.source_native_values.b_web_x | number |
| $.input.source_native_values.b_web_y | number |
| $.input.source_native_values.b_boundary_y | number |
| $.input.source_native_values.R0 | number |
| $.input.source_native_values.a1 | number |
| $.input.source_native_values.a2 | number |
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

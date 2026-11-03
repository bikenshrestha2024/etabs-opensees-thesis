# Saved_Project_V156/OpenSees_Runtime_V118/Material_Catalog/PEER_Web_SteelMPF.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/Material_Catalog/PEER_Web_SteelMPF.json](../../../../../../Saved_Project_V156/OpenSees_Runtime_V118/Material_Catalog/PEER_Web_SteelMPF.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** bd5e5f3936274990ebbbbea9da709aef3509d825e3755e97f76449481567bb83
**Size:** 6430 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.model | str |
| $.parameters | object |
| $.parameters.fyp | number |
| $.parameters.fyn | number |
| $.parameters.E0 | number |
| $.parameters.bp | number |
| $.parameters.bn | number |
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
| $.profile_id | str |
| $.project_transfer_approved | boolean |
| $.provenance | object |
| $.provenance.fyp | object |
| $.provenance.fyp.value | number |
| $.provenance.fyp.unit | str |
| $.provenance.fyp.basis | str |
| $.provenance.fyp.source | str |
| $.provenance.fyp.locator | str |
| $.provenance.fyn | object |
| $.provenance.fyn.value | number |
| $.provenance.fyn.unit | str |
| $.provenance.fyn.basis | str |
| $.provenance.fyn.source | str |
| $.provenance.fyn.locator | str |
| $.provenance.E0 | object |
| $.provenance.E0.value | number |
| $.provenance.E0.unit | str |
| $.provenance.E0.basis | str |
| $.provenance.E0.source | str |
| $.provenance.E0.locator | str |
| $.provenance.bp | object |
| $.provenance.bp.value | number |
| $.provenance.bp.unit | str |
| $.provenance.bp.basis | str |
| $.provenance.bp.source | str |
| $.provenance.bp.locator | str |
| $.provenance.bn | object |
| $.provenance.bn.value | number |
| $.provenance.bn.unit | str |
| $.provenance.bn.basis | str |
| $.provenance.bn.source | str |
| $.provenance.bn.locator | str |
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
| $.source_native_values | object |
| $.source_native_values.fy_web_x_ksi | number |
| $.source_native_values.fy_web_y_ksi | number |
| $.source_native_values.fy_boundary_y_ksi | number |
| $.source_native_values.E0_ksi | number |
| $.source_native_values.b_web_x | number |
| $.source_native_values.b_web_y | number |
| $.source_native_values.b_boundary_y | number |
| $.source_native_values.R0 | number |
| $.source_native_values.a1 | number |
| $.source_native_values.a2 | number |

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

[All JSON files](../../../../00_ALL_JSON_FILES.md) · [Research citations](../../../../../00_RESEARCH_REFERENCES.md)

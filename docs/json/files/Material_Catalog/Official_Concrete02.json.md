# Material_Catalog/Official_Concrete02.json

**Source:** [Material_Catalog/Official_Concrete02.json](../../../../Material_Catalog/Official_Concrete02.json)
**Classification:** MATERIAL_PROFILE
**SHA-256 (source bytes):** 6d915d22587dffd36c086cb271d92648e0599ea80273fa4486fe51ca1522c1c9
**Size:** 3275 bytes
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
| $.parameters.unloading_ratio | number |
| $.parameters.ft_MPa | number |
| $.parameters.Ets_MPa | number |
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
| $.provenance.unloading_ratio | object |
| $.provenance.unloading_ratio.value | number |
| $.provenance.unloading_ratio.unit | str |
| $.provenance.unloading_ratio.basis | str |
| $.provenance.unloading_ratio.source | str |
| $.provenance.unloading_ratio.locator | str |
| $.provenance.ft_MPa | object |
| $.provenance.ft_MPa.value | number |
| $.provenance.ft_MPa.unit | str |
| $.provenance.ft_MPa.basis | str |
| $.provenance.ft_MPa.source | str |
| $.provenance.ft_MPa.locator | str |
| $.provenance.Ets_MPa | object |
| $.provenance.Ets_MPa.value | number |
| $.provenance.Ets_MPa.unit | str |
| $.provenance.Ets_MPa.basis | str |
| $.provenance.Ets_MPa.source | str |
| $.provenance.Ets_MPa.locator | str |

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

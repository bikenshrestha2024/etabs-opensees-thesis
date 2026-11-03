# Material_Catalog/M30_Fe500_BRB.json

**Source:** [Material_Catalog/M30_Fe500_BRB.json](../../../../Material_Catalog/M30_Fe500_BRB.json)
**Classification:** MATERIAL_PROFILE
**SHA-256 (source bytes):** 27b4df4cc81ac886ae3e03547cb7f2388c273fc639508d7fa5aee2480530142d
**Size:** 5957 bytes
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
| $.parameters.core_area_m2 | number |
| $.parameters.yielding_length_m | number |
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
| $.sources | object |
| $.sources.Mander_theory_1988 | str |
| $.sources.Mander_experiment_1988 | str |
| $.sources.Concrete02 | str |
| $.sources.ConcreteCM | str |
| $.sources.Steel02 | str |
| $.sources.SteelMPF | str |
| $.sources.FSAM | str |
| $.sources.E_SFI_2023 | str |
| $.sources.E_SFI_authors | str |
| $.sources.PEER_2015 | str |
| $.sources.FVD | str |
| $.sources.BRB | str |
| $.sources.Outrigger_optimization_2021 | str |
| $.sources.Outrigger_2010 | str |
| $.sources.NBC2025 | str |
| $.sources.Diaphragm | str |
| $.project_transfer_approved | boolean |
| $.profile_id | str |
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
| $.provenance.core_area_m2 | object |
| $.provenance.core_area_m2.value | number |
| $.provenance.core_area_m2.unit | str |
| $.provenance.core_area_m2.basis | str |
| $.provenance.core_area_m2.source | str |
| $.provenance.core_area_m2.locator | str |
| $.provenance.yielding_length_m | object |
| $.provenance.yielding_length_m.value | number |
| $.provenance.yielding_length_m.unit | str |
| $.provenance.yielding_length_m.basis | str |
| $.provenance.yielding_length_m.source | str |
| $.provenance.yielding_length_m.locator | str |

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

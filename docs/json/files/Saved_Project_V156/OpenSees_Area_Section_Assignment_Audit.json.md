# Saved_Project_V156/OpenSees_Area_Section_Assignment_Audit.json

**Source:** [Saved_Project_V156/OpenSees_Area_Section_Assignment_Audit.json](../../../../Saved_Project_V156/OpenSees_Area_Section_Assignment_Audit.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 79d75c7965e6261fbe89855bc68dc694e3157571f4b6329c47ac104750f532b3
**Size:** 910980 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.source_edb | str |
| $.units_requested | str |
| $.note | str |
| $.assignments | array |
| $.assignments[] | object |
| $.assignments[].etabs_area_object | str |
| $.assignments[].assigned_property | str |
| $.assignments[].property_type | str |
| $.assignments[].material_name | str |
| $.assignments[].thickness_m | number |
| $.assignments[].extraction_status | str |
| $.assignments[].material_values | object |
| $.assignments[].material_values.material_name | str |
| $.assignments[].material_values.E | number |
| $.assignments[].material_values.poisson_ratio | number |
| $.assignments[].material_values.thermal_coefficient | number |
| $.assignments[].material_values.G | number |
| $.assignments[].material_values.G_from_E_nu | number |
| $.assignments[].material_values.weight_per_volume | number |
| $.assignments[].material_values.mass_per_volume | number |
| $.assignments[].material_values.material_type_code | number |
| $.assignments[].material_values.raw | object |
| $.assignments[].material_values.raw.GetMPIsotropic | str |
| $.assignments[].material_values.raw.GetWeightAndMass | str |
| $.assignments[].material_values.raw.GetTypeOAPI | str |
| $.assignments[].material_values.status | str |
| $.assignments[].raw_get_property | str |
| $.assignments[].raw_property_api | object |
| $.assignments[].raw_property_api.GetSlab | str |
| $.assignments[].raw_property_api.GetWall | str |
| $.assignments[].geometry_category | str |
| $.property_definitions | object |
| $.property_definitions.Wall 600 | object |
| $.property_definitions.Wall 600.property_name | str |
| $.property_definitions.Wall 600.property_type | str |
| $.property_definitions.Wall 600.material_name | str |
| $.property_definitions.Wall 600.thickness_m | number |
| $.property_definitions.Wall 600.raw_property_api | object |
| $.property_definitions.Wall 600.raw_property_api.GetSlab | str |
| $.property_definitions.Wall 600.raw_property_api.GetWall | str |
| $.property_definitions.Wall 600.extraction_status | str |
| $.property_definitions.Wall 600.material_values | object |
| $.property_definitions.Wall 600.material_values.material_name | str |
| $.property_definitions.Wall 600.material_values.E | number |
| $.property_definitions.Wall 600.material_values.poisson_ratio | number |
| $.property_definitions.Wall 600.material_values.thermal_coefficient | number |
| $.property_definitions.Wall 600.material_values.G | number |
| $.property_definitions.Wall 600.material_values.G_from_E_nu | number |
| $.property_definitions.Wall 600.material_values.weight_per_volume | number |
| $.property_definitions.Wall 600.material_values.mass_per_volume | number |
| $.property_definitions.Wall 600.material_values.material_type_code | number |
| $.property_definitions.Wall 600.material_values.raw | object |
| $.property_definitions.Wall 600.material_values.raw.GetMPIsotropic | str |
| $.property_definitions.Wall 600.material_values.raw.GetWeightAndMass | str |
| $.property_definitions.Wall 600.material_values.raw.GetTypeOAPI | str |
| $.property_definitions.Wall 600.material_values.status | str |
| $.property_definitions.Slab 150 | object |
| $.property_definitions.Slab 150.property_name | str |
| $.property_definitions.Slab 150.property_type | str |
| $.property_definitions.Slab 150.material_name | str |
| $.property_definitions.Slab 150.thickness_m | number |
| $.property_definitions.Slab 150.raw_property_api | object |
| $.property_definitions.Slab 150.raw_property_api.GetSlab | str |
| $.property_definitions.Slab 150.extraction_status | str |
| $.property_definitions.Slab 150.material_values | object |
| $.property_definitions.Slab 150.material_values.material_name | str |
| $.property_definitions.Slab 150.material_values.E | number |
| $.property_definitions.Slab 150.material_values.poisson_ratio | number |
| $.property_definitions.Slab 150.material_values.thermal_coefficient | number |
| $.property_definitions.Slab 150.material_values.G | number |
| $.property_definitions.Slab 150.material_values.G_from_E_nu | number |
| $.property_definitions.Slab 150.material_values.weight_per_volume | number |
| $.property_definitions.Slab 150.material_values.mass_per_volume | number |
| $.property_definitions.Slab 150.material_values.material_type_code | number |
| $.property_definitions.Slab 150.material_values.raw | object |
| $.property_definitions.Slab 150.material_values.raw.GetMPIsotropic | str |
| $.property_definitions.Slab 150.material_values.raw.GetWeightAndMass | str |
| $.property_definitions.Slab 150.material_values.raw.GetTypeOAPI | str |
| $.property_definitions.Slab 150.material_values.status | str |

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

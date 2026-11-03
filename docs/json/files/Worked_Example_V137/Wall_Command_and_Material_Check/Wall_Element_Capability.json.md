# Worked_Example_V137/Wall_Command_and_Material_Check/Wall_Element_Capability.json

**Source:** [Worked_Example_V137/Wall_Command_and_Material_Check/Wall_Element_Capability.json](../../../../../Worked_Example_V137/Wall_Command_and_Material_Check/Wall_Element_Capability.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** e00298abe950f6c4e266aaa63400946c3a7d78caafaef6a6af14cf8f848debb0
**Size:** 1509 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.scope | str |
| $.element | str |
| $.status | str |
| $.displacement_node3 | array |
| $.displacement_node3[] | number |
| $.global_force | array |
| $.global_force[] | number |
| $.macro_fiber_FSAM_tags | array |
| $.macro_fiber_FSAM_tags[] | integer |
| $.material_tags | object |
| $.material_tags.steel_x | integer |
| $.material_tags.steel_y_web | integer |
| $.material_tags.steel_y_boundary | integer |
| $.material_tags.concrete_web | integer |
| $.material_tags.concrete_boundary | integer |
| $.material_tags.fsam_web | integer |
| $.material_tags.fsam_boundary | integer |
| $.units | str |
| $.elapsed_s | number |
| $.explanation | str |
| $.sources | array |
| $.sources[] | str |

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

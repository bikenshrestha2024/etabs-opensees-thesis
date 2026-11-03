# OpenSees_Material_Section_Library_V117.json

**Source:** [OpenSees_Material_Section_Library_V117.json](../../../OpenSees_Material_Section_Library_V117.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** e4ee3b5462d0a0036dfcc5f0c1256b49df06499342b5059e378470adc0d946db
**Size:** 5221 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.schema_version | integer |
| $.units | str |
| $.principle | str |
| $.frame_sections | array |
| $.frame_sections[] | object |
| $.frame_sections[].name | str |
| $.frame_sections[].family | str |
| $.frame_sections[].source_input | str |
| $.frame_sections[].material_models | array |
| $.frame_sections[].material_models[] | str |
| $.frame_sections[].status | str |
| $.area_sections | array |
| $.area_sections[] | object |
| $.area_sections[].name | str |
| $.area_sections[].family | str |
| $.area_sections[].source_input | str |
| $.area_sections[].material_models | array |
| $.area_sections[].material_models[] | str |
| $.area_sections[].reinforcement_layout_candidate | str |
| $.area_sections[].status | str |
| $.devices | array |
| $.devices[] | object |
| $.devices[].name | str |
| $.devices[].element | str |
| $.devices[].material | str |
| $.devices[].required_parameters | array |
| $.devices[].required_parameters[] | str |
| $.devices[].source_required | str |
| $.devices[].status | str |
| $.devices[].mapping_target | str |
| $.devices[].citation | str |
| $.devices[].assignment_file | str |
| $.devices[].selection_scope | str |
| $.validation_references | array |
| $.validation_references[] | object |
| $.validation_references[].citation | str |
| $.validation_references[].doi | str |
| $.validation_references[].use | str |
| $.validation_references[].limit | str |

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

[All JSON files](../00_ALL_JSON_FILES.md) · [Research citations](../../00_RESEARCH_REFERENCES.md)

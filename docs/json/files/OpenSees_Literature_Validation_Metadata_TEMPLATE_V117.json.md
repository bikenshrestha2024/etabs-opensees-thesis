# OpenSees_Literature_Validation_Metadata_TEMPLATE_V117.json

**Source:** [OpenSees_Literature_Validation_Metadata_TEMPLATE_V117.json](../../../OpenSees_Literature_Validation_Metadata_TEMPLATE_V117.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** c9baccefca38aa158b0f7c1b978271598f9598bb0cd6bed6f70627c0a1a4cce9
**Size:** 1783 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.reference | object |
| $.reference.citation | str |
| $.reference.doi | str |
| $.reference.specimen_id | str |
| $.reference.data_source_page_table_figure | str |
| $.reference.units | object |
| $.reference.units.displacement | str |
| $.reference.units.force | str |
| $.benchmark | object |
| $.benchmark.wall_length_to_height_ratio | null |
| $.benchmark.axial_load_ratio | null |
| $.benchmark.wall_thickness_m | null |
| $.benchmark.opening_configuration | null |
| $.benchmark.coupling_beam_detail | null |
| $.benchmark.boundary_elements | null |
| $.benchmark.vertical_reinforcement_ratio | null |
| $.benchmark.horizontal_reinforcement_ratio | null |
| $.benchmark.concrete_strength_MPa | null |
| $.benchmark.steel_yield_strength_MPa | null |
| $.benchmark.loading_protocol | null |
| $.benchmark.element_formulation | str |
| $.project | object |
| $.project.wall_length_to_height_ratio | null |
| $.project.axial_load_ratio | null |
| $.project.wall_thickness_m | number |
| $.project.opening_configuration | str |
| $.project.coupling_beam_detail | str |
| $.project.boundary_elements | str |
| $.project.vertical_reinforcement_ratio | number |
| $.project.horizontal_reinforcement_ratio | number |
| $.project.concrete_strength_MPa | null |
| $.project.steel_yield_strength_MPa | integer |
| $.project.loading_protocol | str |
| $.project.element_formulation | str |
| $.note | str |

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

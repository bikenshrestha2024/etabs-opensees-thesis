# Research_Components/paper_specimens/PEER_2015_12_WALL_SPECIMENS.json

**Source:** [Research_Components/paper_specimens/PEER_2015_12_WALL_SPECIMENS.json](../../../../../Research_Components/paper_specimens/PEER_2015_12_WALL_SPECIMENS.json)
**Classification:** EXPERIMENTAL_SOURCE_REGISTER
**SHA-256 (source bytes):** aabd6b15c8d7f63f82b06a164e59ccfb87f815f1c2bb8eff9a6c317514cfa2c4
**Size:** 3095 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.schema_version | str |
| $.purpose | str |
| $.source | object |
| $.source.report | str |
| $.source.url | str |
| $.source.section | str |
| $.source.extraction_status | str |
| $.specimens | array |
| $.specimens[] | object |
| $.specimens[].specimen_id | str |
| $.specimens[].reference_test | str |
| $.specimens[].model_family | str |
| $.specimens[].width_in | integer |
| $.specimens[].thickness_in | integer |
| $.specimens[].height_in | integer |
| $.specimens[].aspect_ratio | number |
| $.specimens[].boundary_reinforcement | str |
| $.specimens[].web_reinforcement | str |
| $.specimens[].concrete_test_fc_ksi | number |
| $.specimens[].axial_load_ratio_approx | number |
| $.specimens[].discretization | object |
| $.specimens[].discretization.height_elements | integer |
| $.specimens[].discretization.base_element_height_in | integer |
| $.specimens[].discretization.section_macrofibers | integer |
| $.specimens[].discretization.confined_boundary_macrofibers | integer |
| $.specimens[].discretization.unconfined_web_macrofibers | integer |
| $.specimens[].source_locator | str |
| $.specimens[].validation_state | str |
| $.specimens[].project_transfer_approved | boolean |
| $.missing_for_building | array |
| $.missing_for_building[] | str |
| $.notice | str |

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

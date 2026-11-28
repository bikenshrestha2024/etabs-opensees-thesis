# engineering/run_configs/RunConfig_CLEARBEAM_relaxed.json

**Source:** [engineering/run_configs/RunConfig_CLEARBEAM_relaxed.json](../../../../../engineering/run_configs/RunConfig_CLEARBEAM_relaxed.json)
**Classification:** RUN_CONFIGURATION
**SHA-256 (source bytes):** 978c48312cd8fed26adfa928ec0667b33b3c11a8c29a03148c5ccac6fb5cf9ac
**Size:** 1153 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.model_folder | str |
| $.output_dir | str |
| $.x_path | str |
| $.y_path | str |
| $.dt_s | number |
| $.scale | number |
| $.orientations | array |
| $.orientations[] | str |
| $.limit_state | str |
| $.tracked_frame_tag | integer |
| $.tracked_element_tags | array |
| $.tracked_element_tags[] | array(empty) |
| $.nonlinear_walls | boolean |
| $.material_basis | str |
| $.steelmpf_transition | str |
| $.gravity_system | str |
| $.transient_system | str |
| $.material_overrides | object |
| $.material_overrides.brace.fy_mpa | number |
| $.material_overrides.brace.b | number |
| $.diagnostic_excitation | str |
| $.inherent_damping_ratio | number |
| $.inherent_damping_five_percent | boolean |
| $.variant_id | str |
| $.pair_id | str |
| $.convergence_tolerance | number |
| $.final_relaxed_tolerance | null |

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

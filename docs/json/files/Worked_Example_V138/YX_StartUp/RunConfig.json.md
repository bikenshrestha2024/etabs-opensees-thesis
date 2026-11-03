# Worked_Example_V138/YX_StartUp/RunConfig.json

**Source:** [Worked_Example_V138/YX_StartUp/RunConfig.json](../../../../../Worked_Example_V138/YX_StartUp/RunConfig.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** bed88b161e56530ce63476b95b8bb48e0d3276aa2abad09f7d2debb49f9aebd5
**Size:** 573 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.model_folder | str |
| $.output_dir | str |
| $.x_path | str |
| $.y_path | str |
| $.duration_s | number |
| $.dt_s | number |
| $.scale | number |
| $.orientations | array |
| $.orientations[] | str |
| $.limit_state | str |

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

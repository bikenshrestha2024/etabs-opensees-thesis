# excel/SOURCE_REGISTRY.json

**Source:** [excel/SOURCE_REGISTRY.json](../../../../excel/SOURCE_REGISTRY.json)
**Classification:** ETABS_MODEL_OR_SOURCE_METADATA
**SHA-256 (source bytes):** 1b8e212aa66b0afec35f390509a0513c3d142830598e53717ba088f5d2defb91
**Size:** 958 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.schema | str |
| $.source_edb_sha256 | str |
| $.sources | object |
| $.sources.etabs_assignment | object |
| $.sources.etabs_assignment.path | str |
| $.sources.etabs_assignment.sha256 | str |
| $.sources.etabs_full_table | object |
| $.sources.etabs_full_table.path | str |
| $.sources.etabs_full_table.sha256 | str |
| $.sources.slab_load_path | object |
| $.sources.slab_load_path.path | str |
| $.sources.slab_load_path.sha256 | str |
| $.sources.nbc_calculator | object |
| $.sources.nbc_calculator.path | str |
| $.sources.nbc_calculator.sha256 | str |

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

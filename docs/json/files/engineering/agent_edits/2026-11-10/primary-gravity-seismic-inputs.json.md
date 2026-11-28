# engineering/agent_edits/2026-11-10/primary-gravity-seismic-inputs.json

**Source:** [engineering/agent_edits/2026-11-10/primary-gravity-seismic-inputs.json](../../../../../../engineering/agent_edits/2026-11-10/primary-gravity-seismic-inputs.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** b21e7c5b07680f16ca0b6f4b391816cd48fe460101d777d9a1d8f85dcde8f78e
**Size:** 2258 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.tool | str |
| $.exact_model | str |
| $.timestamp_utc | str |
| $.branch | str |
| $.base_sha | str |
| $.classification | str |
| $.changed_paths | array |
| $.changed_paths[] | str |
| $.tests | object |
| $.tests.gravity_esm_mrsm_regression | str |
| $.tests.static_inventory | str |
| $.tests.native_tk | str |
| $.tests.native_opensees | str |
| $.tests.saved_vs_rerun | str |
| $.tests.native_etabs_solve | str |
| $.tests.full_seismic_rerun | str |
| $.tests.reference_tags | str |
| $.tests.new_source_tests_in_ci | str |
| $.engineering_effect | str |
| $.reviewer_status | str |
| $.private_sources_uploaded | boolean |

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

[All JSON files](../../../../00_ALL_JSON_FILES.md) · [Research citations](../../../../../00_RESEARCH_REFERENCES.md)

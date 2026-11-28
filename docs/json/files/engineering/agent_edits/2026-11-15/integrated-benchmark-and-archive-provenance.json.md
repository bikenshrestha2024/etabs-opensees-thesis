# engineering/agent_edits/2026-11-15/integrated-benchmark-and-archive-provenance.json

**Source:** [engineering/agent_edits/2026-11-15/integrated-benchmark-and-archive-provenance.json](../../../../../../engineering/agent_edits/2026-11-15/integrated-benchmark-and-archive-provenance.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 70bdc7d1b6eaf081c342df9e5687bd4558e837475c35daed905a6a9c9925953d
**Size:** 1750 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.base_sha | str |
| $.scope | str |
| $.verified_source_files | array |
| $.verified_source_files[] | str |
| $.fixed_candidates | array |
| $.fixed_candidates[] | str |
| $.unchanged | array |
| $.unchanged[] | str |
| $.tests | array |
| $.tests[] | str |
| $.human_gates | object |
| $.human_gates.windows_spyder | str |
| $.human_gates.native_etabs | str |
| $.human_gates.full_opensees_nltha | str |
| $.human_gates.original_32_supports | str |
| $.human_gates.nbc_105_2025_acceptance | str |
| $.security | str |
| $.ci_status | str |

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

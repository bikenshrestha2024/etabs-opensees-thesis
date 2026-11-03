# archive/previous_versions/RELEASE/RELEASE_V137.json

**Source:** [archive/previous_versions/RELEASE/RELEASE_V137.json](../../../../../../archive/previous_versions/RELEASE/RELEASE_V137.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** af798532c185fb0b8b498c8fa7d57fc8bdd679e079b2254e231895d6f23db966
**Size:** 242 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.release | integer |
| $.entry | str |
| $.demo_entry | str |
| $.implementation_modules | integer |
| $.live_D_files_modified | boolean |
| $.github_repositories_modified | boolean |
| $.wall_command_bug_fixed | boolean |

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

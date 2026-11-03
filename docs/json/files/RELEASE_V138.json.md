# RELEASE_V138.json

**Source:** [RELEASE_V138.json](../../../RELEASE_V138.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 7d7f1eaab6ab585d2aab74c98cc46d96d99193efe4cb3d3fc1a69f290d06177e
**Size:** 274 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.release | integer |
| $.entry | str |
| $.implementation_modules | integer |
| $.live_D_files_modified | boolean |
| $.production_readiness_autoapproved | boolean |
| $.building_research_scope | str |
| $.full_FSAM_building_resolved | boolean |

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

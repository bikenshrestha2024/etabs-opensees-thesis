# Saved_Project_V156/OpenSees_Analysis_Results/Case_Review_V142/All_Case_Review_V142.json

**Source:** [Saved_Project_V156/OpenSees_Analysis_Results/Case_Review_V142/All_Case_Review_V142.json](../../../../../../Saved_Project_V156/OpenSees_Analysis_Results/Case_Review_V142/All_Case_Review_V142.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 4c4e5e44ae1113e1bb7169b6fac5e4140d2fbd101227e1bef68c82d3dcf13156
**Size:** 132347 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.drift | array |
| $.drift[] | array(empty) |
| $.deflection | array |
| $.deflection[] | array(empty) |
| $.issues | array |
| $.issues[] | array(empty) |
| $.preload_profiles | array |
| $.preload_profiles[] | array(empty) |
| $.combination_coverage | array |
| $.combination_coverage[] | object |
| $.combination_coverage[].case | str |
| $.combination_coverage[].limit_state | str |
| $.combination_coverage[].method | str |
| $.combination_coverage[].factors | str |
| $.combination_coverage[].status | str |
| $.combination_coverage[].note | str |

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

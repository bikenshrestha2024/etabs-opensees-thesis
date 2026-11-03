# Saved_Project_V156/OpenSees_Runtime_V118/REDUNDANCY_REVIEW_V133.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/REDUNDANCY_REVIEW_V133.json](../../../../../Saved_Project_V156/OpenSees_Runtime_V118/REDUNDANCY_REVIEW_V133.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 63960926e244d9210263853c0c06d925e9aba48def482a9fa387e48a96fc1851
**Size:** 7662 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.removed_duplicate | str |
| $.remaining_exact_function_ast_groups | array |
| $.remaining_exact_function_ast_groups[] | array |
| $.remaining_exact_function_ast_groups[][] | object |
| $.remaining_exact_function_ast_groups[][].file | str |
| $.remaining_exact_function_ast_groups[][].function | str |
| $.remaining_exact_function_ast_groups[][].line | integer |
| $.remaining_exact_function_ast_groups[][].end_line | integer |
| $.remaining_exact_function_ast_groups[][].sha256 | str |
| $.scope | str |

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

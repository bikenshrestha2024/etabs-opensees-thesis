# Regression_Trial_V140/Exploratory_Summary.json

**Source:** [Regression_Trial_V140/Exploratory_Summary.json](../../../../Regression_Trial_V140/Exploratory_Summary.json)
**Classification:** RUN_RESULT_OR_REPORT
**SHA-256 (source bytes):** 2c1f4eaf4b774df4498cc08e976b74166e21d841570cd66232d0eb5bc4f3f415
**Size:** 1939 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.cases | array |
| $.cases[] | object |
| $.cases[].orientation | str |
| $.cases[].wall_model | str |
| $.cases[].frame_model | str |
| $.cases[].status | str |
| $.cases[].physical_time_s | number |
| $.cases[].full_record_duration_s | number |
| $.cases[].elapsed_s | number |
| $.cases[].peak_roof_UX_m | number |
| $.cases[].peak_roof_UY_m | number |
| $.cases[].periods_inspected_s | array |
| $.cases[].periods_inspected_s[] | number |
| $.cases[].initial_damping_ratios | array |
| $.cases[].initial_damping_ratios[] | number |
| $.cases[].diagnostics | object |
| $.cases[].diagnostics.attempts | integer |
| $.cases[].diagnostics.algorithm_Newton | integer |
| $.cases[].diagnostics.minimum_accepted_dt_s | number |
| $.cases[].diagnostics.max_convergence_iterations | integer |
| $.cases[].scope | str |
| $.elapsed_s | number |
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

[All JSON files](../../00_ALL_JSON_FILES.md) · [Research citations](../../../00_RESEARCH_REFERENCES.md)

# Worked_Example_V133/Synthetic_Full_Model_Linear/SYNTHETIC_PIPELINE_ONLY_XY_Performance_V133.json

**Source:** [Worked_Example_V133/Synthetic_Full_Model_Linear/SYNTHETIC_PIPELINE_ONLY_XY_Performance_V133.json](../../../../../Worked_Example_V133/Synthetic_Full_Model_Linear/SYNTHETIC_PIPELINE_ONLY_XY_Performance_V133.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** fd754c373b83374363b714b53a8f02f69a55f824c8a76e0f9e38b6d2761bdf10
**Size:** 752 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.case | str |
| $.analysis | str |
| $.status | str |
| $.error | null |
| $.started_at | str |
| $.finished_at | str |
| $.elapsed_seconds | number |
| $.stages_seconds | object |
| $.stages_seconds.model_and_gravity | number |
| $.stages_seconds.damping_eigenanalysis | number |
| $.stages_seconds.transient_with_recording | number |
| $.stages_seconds.case_exports_and_drift | number |
| $.accepted_internal_steps | integer |
| $.recording_seconds | number |
| $.solver_diagnostics | object(empty) |
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

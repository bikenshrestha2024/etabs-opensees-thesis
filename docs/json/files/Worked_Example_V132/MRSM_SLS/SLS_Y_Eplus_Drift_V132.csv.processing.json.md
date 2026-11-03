# Worked_Example_V132/MRSM_SLS/SLS_Y_Eplus_Drift_V132.csv.processing.json

**Source:** [Worked_Example_V132/MRSM_SLS/SLS_Y_Eplus_Drift_V132.csv.processing.json](../../../../../Worked_Example_V132/MRSM_SLS/SLS_Y_Eplus_Drift_V132.csv.processing.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** ba9f54f804f3d0cc9893e691cf07a55c90c432e1ef5a63fcbd9551a93ae12298
**Size:** 386 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.stage | str |
| $.started_at | str |
| $.finished_at | str |
| $.elapsed_seconds | number |
| $.status | str |
| $.error | null |
| $.time_scope | str |
| $.artifact | str |
| $.size_bytes | integer |

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

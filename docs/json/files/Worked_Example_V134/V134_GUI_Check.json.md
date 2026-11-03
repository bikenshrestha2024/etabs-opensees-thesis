# Worked_Example_V134/V134_GUI_Check.json

**Source:** [Worked_Example_V134/V134_GUI_Check.json](../../../../Worked_Example_V134/V134_GUI_Check.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 09f002e8ae44d748188025c358f844a00262e3b3d633570002ebb6252e5fb538
**Size:** 323 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.spectrum | object |
| $.spectrum.embedded_plot | boolean |
| $.spectrum.SLS_omega | str |
| $.completed_linear_run | object |
| $.completed_linear_run.saved_summary_loaded | boolean |
| $.completed_linear_run.case_count | integer |
| $.response_viewer | object |
| $.response_viewer.constructed | boolean |
| $.response_viewer.six_dof_count | integer |
| $.irregularity_rows | integer |
| $.ESM | object |
| $.ESM.two_rows | boolean |
| $.ESM.case_count | integer |

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

# Worked_Example_V137/RC_Portal_Direct_Integration/Literature_RC_Profile.json

**Source:** [Worked_Example_V137/RC_Portal_Direct_Integration/Literature_RC_Profile.json](../../../../../Worked_Example_V137/RC_Portal_Direct_Integration/Literature_RC_Profile.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** ad82a1aa330a9f5cc1e6af1112c3efa50134e78dd69d9ae3ce08f53886937bc8
**Size:** 1441 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.status | str |
| $.units | str |
| $.span_m | number |
| $.height_m | number |
| $.width_m | number |
| $.depth_m | number |
| $.cover_m | number |
| $.core_Concrete01 | array |
| $.core_Concrete01[] | number |
| $.cover_Concrete01 | array |
| $.cover_Concrete01[] | number |
| $.steel_Steel01 | array |
| $.steel_Steel01[] | number |
| $.bar_area_m2 | number |
| $.bars | integer |
| $.gravity_per_roof_node_kN | number |
| $.beam_A_m2 | number |
| $.beam_E_kN_m2 | number |
| $.beam_I_m4 | number |
| $.lobatto_points | integer |
| $.betaKcomm_s | number |
| $.newmark_gamma | number |
| $.newmark_beta | number |
| $.sources | array |
| $.sources[] | str |
| $.notes | str |

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

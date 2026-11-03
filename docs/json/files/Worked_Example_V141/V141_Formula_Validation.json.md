# Worked_Example_V141/V141_Formula_Validation.json

**Source:** [Worked_Example_V141/V141_Formula_Validation.json](../../../../Worked_Example_V141/V141_Formula_Validation.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 36124ab1f4797b188eae67cd18327bd302dcc70acd9e463eb6cb238b3c78dd58
**Size:** 453 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.formula_counts | object |
| $.formula_counts.Storey totals | integer |
| $.formula_counts.Source detail | integer |
| $.formula_counts.Read me | integer |
| $.formula_counts.Surface load formulas | integer |
| $.formula_counts.Loaded node path | integer |
| $.formula_counts.Member weight formulas | integer |
| $.formula_counts.Vertical load path | integer |
| $.floor_load_formula_kN | number |
| $.floor_load_provenance_kN | number |
| $.note | str |

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

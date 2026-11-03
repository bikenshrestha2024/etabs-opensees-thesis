# Saved_Project_V156/OpenSees_Analysis_Results/Design_Checks_V135/Design_Check_Report_V135.json

**Source:** [Saved_Project_V156/OpenSees_Analysis_Results/Design_Checks_V135/Design_Check_Report_V135.json](../../../../../../Saved_Project_V156/OpenSees_Analysis_Results/Design_Checks_V135/Design_Check_Report_V135.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 88073dde306a0abd2955c8209acc47524a122a9561177f1806512374650106ad
**Size:** 962764 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.model_sha256 | str |
| $.started | str |
| $.finished | str |
| $.elapsed_s | number |
| $.overall | str |
| $.sources | array |
| $.sources[] | str |
| $.tables | object |
| $.tables.Combination coverage | array |
| $.tables.Combination coverage[] | object |
| $.tables.Combination coverage[].case | str |
| $.tables.Combination coverage[].limit_state | str |
| $.tables.Combination coverage[].expression | str |
| $.tables.Combination coverage[].clause | str |
| $.tables.Combination coverage[].action_rows | integer |
| $.tables.Combination coverage[].status | str |
| $.tables.Combination coverage[].note | str |
| $.tables.Seismic drift | array |
| $.tables.Seismic drift[] | array(empty) |
| $.tables.Project deflection | array |
| $.tables.Project deflection[] | array(empty) |
| $.tables.Section checks | array |
| $.tables.Section checks[] | object |
| $.tables.Section checks[].status | str |
| $.tables.Section checks[].reason | str |
| $.tables.Nonlinear performance | array |
| $.tables.Nonlinear performance[] | array(empty) |
| $.tables.Section inventory | array |
| $.tables.Section inventory[] | object |
| $.tables.Section inventory[].member | str |
| $.tables.Section inventory[].category | str |
| $.tables.Section inventory[].section | str |
| $.tables.Section inventory[].status | str |
| $.tables.Section inventory[].checks_supplied | integer |
| $.tables.Section inventory[].required_checks | str |
| $.tables.Section inventory[].reason | str |
| $.tables.Combined actions | array |
| $.tables.Combined actions[] | array(empty) |
| $.tables.Missing action basis | array |
| $.tables.Missing action basis[] | array(empty) |
| $.tables.Open items | array |
| $.tables.Open items[] | object |
| $.tables.Open items[].check | str |
| $.tables.Open items[].status | str |
| $.tables.Open items[].reason | str |
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

[All JSON files](../../../../00_ALL_JSON_FILES.md) · [Research citations](../../../../../00_RESEARCH_REFERENCES.md)

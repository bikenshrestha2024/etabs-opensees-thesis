# Worked_Example_V133/V133_GUI_Feature_Check.json

**Source:** [Worked_Example_V133/V133_GUI_Feature_Check.json](../../../../Worked_Example_V133/V133_GUI_Feature_Check.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 09a953f4e37bd0b71067c56bde3c351d166ec16649f1cabe42076942bf94fc01
**Size:** 633 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.NonlinearTimeHistoryGUI | object |
| $.NonlinearTimeHistoryGUI.selected_pair_ids | array |
| $.NonlinearTimeHistoryGUI.selected_pair_ids[] | str |
| $.NonlinearTimeHistoryGUI.preliminary_selection | boolean |
| $.NonlinearTimeHistoryGUI.execution | str |
| $.LinearTimeHistoryGUI | object |
| $.LinearTimeHistoryGUI.selected_pair_ids | array |
| $.LinearTimeHistoryGUI.selected_pair_ids[] | str |
| $.LinearTimeHistoryGUI.preliminary_selection | boolean |
| $.LinearTimeHistoryGUI.execution | str |
| $.history_inspector | str |
| $.playback | str |
| $.gravity_sources | str |

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

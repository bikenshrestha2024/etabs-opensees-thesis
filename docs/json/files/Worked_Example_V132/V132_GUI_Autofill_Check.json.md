# Worked_Example_V132/V132_GUI_Autofill_Check.json

**Source:** [Worked_Example_V132/V132_GUI_Autofill_Check.json](../../../../Worked_Example_V132/V132_GUI_Autofill_Check.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 31e5df7e3940730ec66b5d057bcf479c6475b72e4c8f97c7c12d58d38872a6b1
**Size:** 1947 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.LinearTimeHistoryGUI | object |
| $.LinearTimeHistoryGUI.model | str |
| $.LinearTimeHistoryGUI.python | str |
| $.LinearTimeHistoryGUI.output | str |
| $.LinearTimeHistoryGUI.stories | str |
| $.LinearTimeHistoryGUI.t1x | str |
| $.LinearTimeHistoryGUI.t1y | str |
| $.LinearTimeHistoryGUI.tnx | str |
| $.LinearTimeHistoryGUI.tny | str |
| $.LinearTimeHistoryGUI.p1 | str |
| $.LinearTimeHistoryGUI.p2 | str |
| $.NonlinearTimeHistoryGUI | object |
| $.NonlinearTimeHistoryGUI.model | str |
| $.NonlinearTimeHistoryGUI.python | str |
| $.NonlinearTimeHistoryGUI.output | str |
| $.NonlinearTimeHistoryGUI.stories | str |
| $.NonlinearTimeHistoryGUI.t1x | str |
| $.NonlinearTimeHistoryGUI.t1y | str |
| $.NonlinearTimeHistoryGUI.tnx | str |
| $.NonlinearTimeHistoryGUI.tny | str |
| $.NonlinearTimeHistoryGUI.p1 | str |
| $.NonlinearTimeHistoryGUI.p2 | str |
| $.gravity | object |
| $.gravity.model | str |
| $.gravity.applied_load | str |
| $.modal | object |
| $.modal.model | str |
| $.modal.H | str |
| $.modal.AwX | str |
| $.modal.AwY | str |
| $.site_spectra | object |
| $.site_spectra.soil | str |
| $.site_spectra.z | str |
| $.site_spectra.imp | str |
| $.site_spectra.rmu | str |
| $.site_spectra.omega | str |
| $.site_spectra.t1x | str |
| $.site_spectra.t1y | str |

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

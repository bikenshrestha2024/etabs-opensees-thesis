# Verification_V159/Native_Profile_Checks.json

**Source:** [Verification_V159/Native_Profile_Checks.json](../../../../Verification_V159/Native_Profile_Checks.json)
**Classification:** VALIDATION_EVIDENCE
**SHA-256 (source bytes):** a953c6abe9538da319132674115077e6c0a093264e58846f3fae1ac12f093af8
**Size:** 808 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.results | object |
| $.results.Official_Concrete01 | object |
| $.results.Official_Concrete01.exit_code | integer |
| $.results.Official_Concrete01.status | str |
| $.results.Official_Concrete02 | object |
| $.results.Official_Concrete02.exit_code | integer |
| $.results.Official_Concrete02.status | str |
| $.results.Official_ConcreteCM | object |
| $.results.Official_ConcreteCM.exit_code | integer |
| $.results.Official_ConcreteCM.status | str |
| $.results.Official_SteelMPF | object |
| $.results.Official_SteelMPF.exit_code | integer |
| $.results.Official_SteelMPF.status | str |
| $.results.Fit_Steel02 | object |
| $.results.Fit_Steel02.exit_code | integer |
| $.results.Fit_Steel02.status | str |
| $.results.Official_FVD | object |
| $.results.Official_FVD.exit_code | integer |
| $.results.Official_FVD.status | str |
| $.results.PEER_Web_ConcreteCM | object |
| $.results.PEER_Web_ConcreteCM.exit_code | integer |
| $.results.PEER_Web_ConcreteCM.status | str |
| $.results.PEER_Web_SteelMPF | object |
| $.results.PEER_Web_SteelMPF.exit_code | integer |
| $.results.PEER_Web_SteelMPF.status | str |
| $.results.PEER_Web_ESFI_Patch | object |
| $.results.PEER_Web_ESFI_Patch.exit_code | integer |
| $.results.PEER_Web_ESFI_Patch.status | str |
| $.elapsed_s | number |

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

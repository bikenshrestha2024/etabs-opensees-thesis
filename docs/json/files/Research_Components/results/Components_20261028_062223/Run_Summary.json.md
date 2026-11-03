# Research_Components/results/Components_20261028_062223/Run_Summary.json

**Source:** [Research_Components/results/Components_20261028_062223/Run_Summary.json](../../../../../../Research_Components/results/Components_20261028_062223/Run_Summary.json)
**Classification:** RUN_RESULT_OR_REPORT
**SHA-256 (source bytes):** 762b28b471d6d85f1932821c530e3f63319762e4f5635a0ed38dc9b3d98190ce
**Size:** 1560 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.Concrete01 | object |
| $.Concrete01.exit_code | integer |
| $.Concrete01.output | str |
| $.Concrete02 | object |
| $.Concrete02.exit_code | integer |
| $.Concrete02.output | str |
| $.ConcreteCM | object |
| $.ConcreteCM.exit_code | integer |
| $.ConcreteCM.output | str |
| $.Steel02 | object |
| $.Steel02.exit_code | integer |
| $.Steel02.output | str |
| $.SteelMPF | object |
| $.SteelMPF.exit_code | integer |
| $.SteelMPF.output | str |
| $.FVD | object |
| $.FVD.exit_code | integer |
| $.FVD.output | str |
| $.BRB | object |
| $.BRB.exit_code | integer |
| $.BRB.output | str |
| $.SFI_MVLEM_3D | object |
| $.SFI_MVLEM_3D.exit_code | integer |
| $.SFI_MVLEM_3D.output | str |

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

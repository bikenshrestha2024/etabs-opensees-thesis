# Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/Verification.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/Verification.json](../../../../../../Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/Verification.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 0cf5e08320a210a624bc74814bb2662004534651289a3a68717d7b16428fd1bb
**Size:** 869 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.component_runs | object |
| $.component_runs.Concrete01 | str |
| $.component_runs.Concrete02 | str |
| $.component_runs.ConcreteCM | str |
| $.component_runs.Steel02 | str |
| $.component_runs.SteelMPF | str |
| $.component_runs.FVD | str |
| $.component_runs.BRB | str |
| $.component_runs.SFI_MVLEM_3D | str |
| $.ranker_incomplete_case_exclusion | str |
| $.building_NLTHA_executed | boolean |
| $.project_validation | boolean |
| $.source_review_date | str |
| $.version | str |
| $.GUI_saved_results | str |
| $.GUI_entrypoint | str |
| $.runner_auto_GUI | str |

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

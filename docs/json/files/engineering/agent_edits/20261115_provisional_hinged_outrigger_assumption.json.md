# engineering/agent_edits/20261115_provisional_hinged_outrigger_assumption.json

**Source:** [engineering/agent_edits/20261115_provisional_hinged_outrigger_assumption.json](../../../../../engineering/agent_edits/20261115_provisional_hinged_outrigger_assumption.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** e10b6c84ec96a2756bab690347f45141915103d49d7a79b8b0fb6028cc6af9e7
**Size:** 2226 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.record_type | str |
| $.date_local | str |
| $.observed_editor | str |
| $.editor_confidence | str |
| $.base_main_sha | str |
| $.branch | str |
| $.decision | str |
| $.source_reviewed | array |
| $.source_reviewed[] | str |
| $.edited_paths | array |
| $.edited_paths[] | str |
| $.code_or_physics_changes | boolean |
| $.private_pdf_uploaded_to_repository | boolean |
| $.original_etabs_model_changed | boolean |
| $.required_gates | array |
| $.required_gates[] | str |
| $.test_evidence | object |
| $.test_evidence.synthetic_tests | str |
| $.test_evidence.ci_status | str |
| $.test_evidence.native_solver | str |
| $.test_evidence.etabs_oapi | str |

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

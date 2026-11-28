# engineering/agent_edits/20261115_gravity_full_source_reaction_evidence.json

**Source:** [engineering/agent_edits/20261115_gravity_full_source_reaction_evidence.json](../../../../../engineering/agent_edits/20261115_gravity_full_source_reaction_evidence.json)
**Classification:** ETABS_MODEL_OR_SOURCE_METADATA
**SHA-256 (source bytes):** 9a7b6e717d7dd88c40dad8f42a7d5eea2d647976d580a01bc3e4de162647f92f
**Size:** 2012 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.record_type | str |
| $.date_local | str |
| $.observed_editor | str |
| $.base_main | str |
| $.branch | str |
| $.actual_source_inspected | array |
| $.actual_source_inspected[] | str |
| $.user_private_evidence_inspected_locally | array |
| $.user_private_evidence_inspected_locally[] | str |
| $.source_public_code_only | boolean |
| $.private_model_uploaded_to_github | boolean |
| $.physical_changes_to_model | boolean |
| $.original_restraints_changed | boolean |
| $.work_product | array |
| $.work_product[] | str |
| $.tests | array |
| $.tests[] | str |
| $.native_gates | str |
| $.structural_equivalence | str |
| $.folder_removal | str |

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

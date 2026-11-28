# engineering/agent_edits/2026-11-15/exec-facade-source-root-semantic-review.json

**Source:** [engineering/agent_edits/2026-11-15/exec-facade-source-root-semantic-review.json](../../../../../../engineering/agent_edits/2026-11-15/exec-facade-source-root-semantic-review.json)
**Classification:** ETABS_MODEL_OR_SOURCE_METADATA
**SHA-256 (source bytes):** d0ccc0cc863881d661c6b1bf6dd654aff3888913e7d3aee15465ec105c2c9165
**Size:** 1452 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.base_sha | str |
| $.verified_source_bundle | str |
| $.code_snapshot_files | integer |
| $.facades_discovered | integer |
| $.scope | str |
| $.source_findings | array |
| $.source_findings[] | str |
| $.changes | array |
| $.changes[] | str |
| $.nonbreaking | array |
| $.nonbreaking[] | str |
| $.validation | str |
| $.native_etabs | str |
| $.native_opensees | str |
| $.complete_semantic_review | str |

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

# engineering/agent_edits/2026-11-15/integrated-audit-output-layout.json

**Source:** [engineering/agent_edits/2026-11-15/integrated-audit-output-layout.json](../../../../../../engineering/agent_edits/2026-11-15/integrated-audit-output-layout.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** d72f00727cbb031b9ce8f237589834243f4707143708ac93612fe4b1c92828ab
**Size:** 884 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.date | str |
| $.editor | str |
| $.baseline_sha | str |
| $.workflow | str |
| $.changes | array |
| $.changes[] | str |
| $.compatibility | str |
| $.source_inputs_changed | boolean |
| $.solver_outputs_changed | boolean |
| $.native_etabs_opensees_verified | boolean |
| $.ci | str |

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

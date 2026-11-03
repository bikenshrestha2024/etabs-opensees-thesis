# Research_Components/References.json

**Source:** [Research_Components/References.json](../../../../Research_Components/References.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** 91dd64156a1db063d04b177bda3387daadb144903ec0b1029243d4e5ba125b2b
**Size:** 1456 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.Mander_theory_1988 | str |
| $.Mander_experiment_1988 | str |
| $.Concrete02 | str |
| $.ConcreteCM | str |
| $.Steel02 | str |
| $.SteelMPF | str |
| $.FSAM | str |
| $.E_SFI_2023 | str |
| $.E_SFI_authors | str |
| $.PEER_2015 | str |
| $.FVD | str |
| $.BRB | str |
| $.Outrigger_optimization_2021 | str |
| $.Outrigger_2010 | str |
| $.NBC2025 | str |
| $.Diaphragm | str |

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

# Research_Components/results/Components_20261028_062223/SFI_MVLEM_3D/report.json

**Source:** [Research_Components/results/Components_20261028_062223/SFI_MVLEM_3D/report.json](../../../../../../../Research_Components/results/Components_20261028_062223/SFI_MVLEM_3D/report.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** c4f72bd468b270430e2871d0075a746f0dd3ff79de37f44745cefd97e8ca85cd
**Size:** 4079 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.input | object |
| $.input.model | str |
| $.input.parameters | object |
| $.input.parameters.width_m | number |
| $.input.parameters.height_m | number |
| $.input.parameters.thickness_m | number |
| $.input.parameters.fibers | integer |
| $.input.parameters.axial_kN | number |
| $.input.parameters.rho_x | number |
| $.input.parameters.rho_y | number |
| $.input.parameters.nu | number |
| $.input.parameters.CoR | number |
| $.input.parameters.ThickMod | number |
| $.input.parameters.steel_Fy_MPa | number |
| $.input.parameters.steel_E_MPa | number |
| $.input.parameters.concrete_fc_MPa | number |
| $.input.parameter_basis | str |
| $.input.specimen_id | str |
| $.input.citation | str |
| $.input.source | str |
| $.input.protocol_csv | str |
| $.input.measured_csv | str |
| $.input.fit_bounds | object(empty) |
| $.input.train_fraction | number |
| $.input.scope | str |
| $.input.wall_formulation | str |
| $.input.targets | array |
| $.input.targets[] | number |
| $.input.samples_per_leg | integer |
| $.input.dt_s | number |
| $.input.wall_concrete | object |
| $.input.wall_concrete.fpcc | number |
| $.input.wall_concrete.epcc | number |
| $.input.wall_concrete.Ec | number |
| $.input.wall_concrete.rc | number |
| $.input.wall_concrete.xcrn | number |
| $.input.wall_concrete.ft | number |
| $.input.wall_concrete.et | number |
| $.input.wall_concrete.rt | number |
| $.input.wall_concrete.xcrp | number |
| $.input.wall_steel | object |
| $.input.wall_steel.fyp | number |
| $.input.wall_steel.fyn | number |
| $.input.wall_steel.E0 | number |
| $.input.wall_steel.bp | number |
| $.input.wall_steel.bn | number |
| $.input.wall_steel.R0 | number |
| $.input.wall_steel.cR1 | number |
| $.input.wall_steel.cR2 | number |
| $.input.wall_steel.a1 | number |
| $.input.wall_steel.a2 | number |
| $.input.wall_steel.a3 | number |
| $.input.wall_steel.a4 | number |
| $.input.fsam | object |
| $.input.fsam.nu | number |
| $.input.fsam.alpha | number |
| $.input.boundary_scope | str |
| $.input.sources | object |
| $.input.sources.Mander_theory_1988 | str |
| $.input.sources.Mander_experiment_1988 | str |
| $.input.sources.Concrete02 | str |
| $.input.sources.ConcreteCM | str |
| $.input.sources.Steel02 | str |
| $.input.sources.SteelMPF | str |
| $.input.sources.FSAM | str |
| $.input.sources.E_SFI_2023 | str |
| $.input.sources.E_SFI_authors | str |
| $.input.sources.PEER_2015 | str |
| $.input.sources.FVD | str |
| $.input.sources.BRB | str |
| $.input.sources.Outrigger_optimization_2021 | str |
| $.input.sources.Outrigger_2010 | str |
| $.input.sources.NBC2025 | str |
| $.input.sources.Diaphragm | str |
| $.input.project_transfer_approved | boolean |
| $.input._output | str |
| $.optimizer | object(empty) |
| $.metrics | object(empty) |
| $.status | str |
| $.elapsed_s | number |
| $.finished_at | str |
| $.project_transfer_approved | boolean |

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

[All JSON files](../../../../../00_ALL_JSON_FILES.md) · [Research citations](../../../../../../00_RESEARCH_REFERENCES.md)

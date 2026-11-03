# Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/cards/SFI_MVLEM_3D.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/cards/SFI_MVLEM_3D.json](../../../../../../../Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/cards/SFI_MVLEM_3D.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** b9c81ae84f9d39313dbb456038005cdfbd7b7f96e6a2bac82f3479723f6df80a
**Size:** 3532 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.model | str |
| $.parameters | object |
| $.parameters.width_m | number |
| $.parameters.height_m | number |
| $.parameters.thickness_m | number |
| $.parameters.fibers | integer |
| $.parameters.axial_kN | number |
| $.parameters.rho_x | number |
| $.parameters.rho_y | number |
| $.parameters.nu | number |
| $.parameters.CoR | number |
| $.parameters.ThickMod | number |
| $.parameters.steel_Fy_MPa | number |
| $.parameters.steel_E_MPa | number |
| $.parameters.concrete_fc_MPa | number |
| $.parameter_basis | str |
| $.specimen_id | str |
| $.citation | str |
| $.source | str |
| $.protocol_csv | str |
| $.measured_csv | str |
| $.fit_bounds | object(empty) |
| $.train_fraction | number |
| $.scope | str |
| $.wall_formulation | str |
| $.targets | array |
| $.targets[] | number |
| $.samples_per_leg | integer |
| $.dt_s | number |
| $.wall_concrete | object |
| $.wall_concrete.fpcc | number |
| $.wall_concrete.epcc | number |
| $.wall_concrete.Ec | number |
| $.wall_concrete.rc | number |
| $.wall_concrete.xcrn | number |
| $.wall_concrete.ft | number |
| $.wall_concrete.et | number |
| $.wall_concrete.rt | number |
| $.wall_concrete.xcrp | number |
| $.wall_steel | object |
| $.wall_steel.fyp | number |
| $.wall_steel.fyn | number |
| $.wall_steel.E0 | number |
| $.wall_steel.bp | number |
| $.wall_steel.bn | number |
| $.wall_steel.R0 | number |
| $.wall_steel.cR1 | number |
| $.wall_steel.cR2 | number |
| $.wall_steel.a1 | number |
| $.wall_steel.a2 | number |
| $.wall_steel.a3 | number |
| $.wall_steel.a4 | number |
| $.fsam | object |
| $.fsam.nu | number |
| $.fsam.alpha | number |
| $.boundary_scope | str |
| $.sources | object |
| $.sources.Mander_theory_1988 | str |
| $.sources.Mander_experiment_1988 | str |
| $.sources.Concrete02 | str |
| $.sources.ConcreteCM | str |
| $.sources.Steel02 | str |
| $.sources.SteelMPF | str |
| $.sources.FSAM | str |
| $.sources.E_SFI_2023 | str |
| $.sources.E_SFI_authors | str |
| $.sources.PEER_2015 | str |
| $.sources.FVD | str |
| $.sources.BRB | str |
| $.sources.Outrigger_optimization_2021 | str |
| $.sources.Outrigger_2010 | str |
| $.sources.NBC2025 | str |
| $.sources.Diaphragm | str |
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

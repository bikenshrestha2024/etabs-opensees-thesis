# `components/sections/library_excel.py` — source and behavior

- **Purpose:** export all four actual material-and-section GUI table datasets to a single local XLSX with a provenance sheet. This is a read-only engineering-review snapshot and **does not calibrate** OpenSees constitutive laws or update the solver.
- **Entry:** `components/ui/results.py:library_window` → `export_material_section_library(folder)`.
- **Producer:** `OpenSees_Mapping_Audit_V125.py` facade → `components/sections/mapping_audit.py` functions `library`, `parameter_sources`, `source_parameter_inventory`, `validation_inventory`. The active `Define_Section_V109` source and selected `OpenSees_Complete_Model_Data_V118.json` produce current records.
- **Inputs:** source-bound local model export folder; optional explicit output path (must not exist), optional 4-tuple table fixtures for tests. The source model EDB is **never opened**.
- **Outputs:** `02_MODEL/MATERIAL_SECTION_LIBRARY/OpenSees_Material_Section_Library_YYYYMMDD_HHMMSS.xlsx`, with UTC timestamp and SHA256 of source model-data/config JSON; no mutable source file.
- **Units:** native mm and MPa for editable fiber input, kN/m² for source stiffness, kN/m³ for weight and kN*(s/m)^alpha for FVD damper coefficient. Keep separate unit systems and review before solver assignment.
- **Security:** escape source text starting with Excel formula prefixes; no network upload. Preserve source paths only within the selected user's own private export folder, not GitHub.
- **Limitations:** a source/value/citation is *not* project cyclic calibration. Section previews are perimeter-only and are not validated reinforcement schedules. Workbook is not automatically imported into nonlinear solver settings. Works with `openpyxl` installed from conda-forge.
- **Tests:** `tests/test_model_material_section_library_excel.py` covers four sheets, source hash, source values, overwrite prevention and formula escaping. Native Windows Tkinter remains untested in CI.
- **References:** [OpenSees Concrete01](https://opensees.github.io/OpenSeesDocumentation/user/manual/material/uniaxialMaterials/Concrete01.html), [Steel02](https://opensees.github.io/OpenSeesDocumentation/user/manual/material/uniaxialMaterials/Steel02.html); governing NBC 105:2025 seismic scope (and project-adopted IS16700 slab/P-Delta exceptions).

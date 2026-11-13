# 02 Model — Independent slab mesh load-path cases (4, 8, 16)

**Source:** UI: `components/gravity/load_path_formulas.py`; case orchestration: `components/gravity/mesh_cases.py`. **State:** implemented code change; requires Windows native verification and actual gravity/ETABS comparison.

## Why the old stale-model warning was correct

The `Save mesh choice` setting changed `floor_subdivisions` in `OpenSees_Complete_Model_Config_V118.json` without recalculating the model `OpenSees_Complete_Model_Data_V118.json`. The latter stores the SHA256 of the configuration actually assembled. A new label does not refine the real shell mesh. The old workbook generator built formula tables before checking the SHA and then refused to save. We retain the strict SHA gate, move it **before Excel generation**, and provide a dedicated build action.

## Operating procedure (who, what, when, how, where)

1. **Source**: Run `1. Import` once to populate source `OpenSees_Element_Connectivity.json`, `OpenSees_Section_Assignment_Audit.json`, `OpenSees_Load_Conversion_Audit.json`, ETABS source metadata/material CSV and a model config. Independently verify source EDB model identity and exported loads.
2. **2. Model**: Open `Slab load path / mesh + Excel formulas`. Click **Prepare 4 / 8 / 16 configs**. The three `Model_Config_MESH_XX.json` files are **only settings**; they are not numerical models.
3. **Assemble**: Choose `4`, `8`, or `16`, then **Build selected mesh + Excel**. A worker thread stages the source audit in a unique mesh-specific run folder, calls `prepare_complete_export()` for that case, compares assembled `config_sha256` with the case config SHA256, and exports formula Excel and JSON evidence when the check passes. The UI remains responsive. A failed case leaves an explicit `MESH_BUILD_STATUS.json` with `ASSEMBLY_FAILED`.
4. **Solve separately**: Use each case's `MODEL_RUN` script and selected gravity/ULS/SLS definitions for a native OpenSees solve. Do **not** assume the formula workbook proves that all load transfers/reactions match ETABS. Store solver outcomes and compare floors/walls/beam end forces, support Rz, deflection and convergence.
5. **Assess mesh convergence**: Compare physically identical cases, numerical totals and key response to 4→8→16. A setting named `MESH_16` is not a substituted or simulated 16-mesh result.

## Output structure

```
<export>/02_MODEL/SLAB_LOAD_PATH/
  PREPARED_CONFIGS/
    Model_Config_MESH_04.json
    Model_Config_MESH_08.json
    Model_Config_MESH_16.json
  MESH_04/
    EXCEL/Slab_Load_Path_MESH_04_<timestamp>_V141.xlsx
    JSON/Slab_Load_Path_MESH_04_<timestamp>_MANIFEST.json
    RUNS/RUN_<timestamp>_<id>/   # ETABS saved-audit snapshot + assembled OpenSees model
      MESH_CASE_PROVENANCE.json
      MESH_BUILD_STATUS.json
      OpenSees_Complete_Model_Config_V118.json
      OpenSees_Complete_Model_Data_V118.json
      OpenSees_Complete_Export_Report_V118.json
      OpenSees_Runtime_V118/
  MESH_08/ ... (same structure)
  MESH_16/ ... (same structure)
```

The root source export is untouched by a case build, apart from `02_MODEL/SLAB_LOAD_PATH` new case outputs. Each case has a unique run ID and independent reconstructed nodes and shell cells. The selected case runner uses **saved ETABS audit** rather than launching ETABS or modifying EDB. No results are manufactured.

## Mechanics and limitations

- **ShellMITC4** distributes external surface loading to shared slab, beam and wall degrees of freedom. Direct applied load `q A` on a mesh cell is an **input nodal equivalent**, not a computed shear/moment or a substitute for solving the assembled FE stiffness.
- The rigid diaphragm constrains selected in-plane displacements/rotation; it does not itself carry slab vertical pressure to columns. Beam and slab node connectivity, support restraints, shear-wall discretization and element stiffness still control load path.
- **Physical self-weight** should depend on source thickness and material unit weight, not the slab bending multiplier. For a conventional beam-supported slab, the project-adopted IS 16700:2023 Table 5 bending coefficient is a supplementary requirement; NBC 105:2025 remains the primary seismic basis.
- The initial cases will be marked `FORMULA_WORKBOOK_CREATED_NOT_GRAVITY_VERIFIED`, **not** `PASS`. Project numerical mesh convergence requires actual 4/8/16 gravity solutions and physical ETABS comparison, with source identical except subdivision.
- Nonlinear wall, reinforcement and device parameter review is separate and not established by changing slab meshes. All three configurations have `nonlinear_parameters_reviewed: false` unless independently updated with evidence.
- The case writer copies selected source audit inputs and copies runtime modules from the current code root to ensure reproducible per-case scripts. This may be time-consuming for mesh 16; it runs on a background thread, with no guessed duration.
- No old analysis results are deleted or silently reused. The original single-root workbook action remains available but fails closed when source/model config hashes differ.

## References

- OpenSees [ShellMITC4](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/ShellMITC4.html)
- OpenSees [Rigid Diaphragm](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidDiaphragm.html)
- NBC 105:2025 official Nepali seismic design code, governing model analysis and seismic-weight/TH assumptions
- IS 16700:2023 Table 5, supplementary slab stiffness convention as adopted for this beam-supported slab

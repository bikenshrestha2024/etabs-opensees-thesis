# 02 Model source guide — `components/gravity/mesh_cases.py`

Purpose: convert a set of source-identical ETABS saved audit inputs into **independent, SHA-verified** assembled slab meshes of 4, 8 and 16 subdivisions per original panel. Do not touch original EDB, root model config or old gravity outputs. Do not interpret a configuration as analysis proof.

Entry and implementation: `components/gravity/load_path_formulas.py:launch` → `prepared_configs`, `stage_case`, `build_case`. `OpenSees_Complete_Export_V118.prepare_complete_export` performs actual independent model assembly (not ETABS extraction); `OpenSees_Load_Path_V141.export(..., output_root=...)` creates the spreadsheet only if model config SHA matches and floor shells exist.

Inputs: selected exported root's saved `OpenSees_Element_Connectivity.json`, `OpenSees_Section_Assignment_Audit.json`, `OpenSees_Load_Conversion_Audit.json`, `OpenSees_Complete_Model_Config_V118.json` and optional saved source ETABS materials, section and metadata. Reject missing core audit files, unsupported subdivisions, prepared setting mismatch.

Outputs: `02_MODEL/SLAB_LOAD_PATH/MESH_XX/RUNS/RUN_<timestamp>_<id>/` model/config/manifest, per case status JSON; non-overwriting per-case `EXCEL/Slab_Load_Path_MESH_XX_<timestamp>_V141.xlsx` and `JSON/...`. No fabricated reaction or moment outputs. Status `FORMULA_WORKBOOK_CREATED_NOT_GRAVITY_VERIFIED` is not a design or code acceptance.

Engineering limits: NBC 105:2025 governs seismic; project-required conventional slab bending uses IS 16700:2023 Table 5 where NBC is not specific. Mesh convergence requires three independent native OpenSees gravity solves using matched loads, restaints and ETABS source evidence; `ShellMITC4` load distribution alone is not solver force verification. Check missing ETABS frame sections and source base restraints separately.

Tests: `tests/test_model_mesh_case_workflow.py` stages dummy source audits, verifies original SHA stability, checks 4/8/16 configuration and rejects stale/missing inputs. End-to-end native ETABS/large shell mesh analysis remains an independent Windows validation task.

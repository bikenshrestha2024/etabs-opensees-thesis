# 02 Model source guide — `components/gravity/mesh_cases.py`

Purpose: convert a set of source-identical ETABS saved audit inputs into **independent, SHA-verified** assembled slab meshes of 4, 8 and 16 subdivisions per original panel. Do not touch original EDB, root model config or old gravity outputs. Do not interpret a configuration as analysis proof.

Entry and implementation: `components/gravity/load_path_formulas.py:launch` → `prepared_configs`, `stage_case`, `build_case`. `OpenSees_Complete_Export_V118.prepare_complete_export` performs actual independent model assembly (not ETABS extraction); `OpenSees_Load_Path_V141.export(..., output_root=...)` creates the spreadsheet only if model config SHA matches and floor shells exist.

Inputs: selected exported root's saved `OpenSees_Element_Connectivity.json`, `OpenSees_Section_Assignment_Audit.json`, `OpenSees_Load_Conversion_Audit.json`, `OpenSees_Complete_Model_Config_V118.json` and optional saved source ETABS materials, section and metadata. Reject missing core audit files, unsupported subdivisions, prepared setting mismatch.

Outputs: `02_MODEL/SLAB_LOAD_PATH/MESH_XX/RUNS/RUN_<timestamp>_<id>/` model/config/manifest, per case status JSON; non-overwriting per-case `EXCEL/Slab_Load_Path_MESH_XX_<timestamp>_V141.xlsx` and `JSON/...`. No fabricated reaction or moment outputs. Status `FORMULA_WORKBOOK_CREATED_NOT_GRAVITY_VERIFIED` is not a design or code acceptance.

Engineering limits: NBC 105:2025 governs seismic; project-required conventional slab bending uses IS 16700:2023 Table 5 where NBC is not specific. Mesh convergence requires three independent native OpenSees gravity solves using matched loads, restaints and ETABS source evidence; `ShellMITC4` load distribution alone is not solver force verification. Check missing ETABS frame sections and source base restraints separately.

Tests: `tests/test_model_mesh_case_workflow.py` stages dummy source audits, verifies original SHA stability, checks 4/8/16 configuration and rejects stale/missing inputs. End-to-end native ETABS/large shell mesh analysis remains an independent Windows validation task.


## 2026-11-15 mesh input-identity and link hardening

Before generating any derived mesh configuration or run, the source export root and every existing ancestor/output directory component are checked for symbolic links. The staged configuration set preflights **all three** 4/8/16 destinations before writing even the first derived config. Required/optional saved ETABS audit inputs are checked for linked sources and individually SHA256-hashed *before* a new run directory is created. On copying, each staged non-derived source hash must match both the preflight hash and the original file's post-copy digest, refusing source mutation during copying. The new `original_source_file_sha256` manifest field records each original input separately from the pre-existing `source_file_sha256` (which records the **actual staged bytes**, including the derived mesh-specific config). Existing run folder and config naming remain compatible. This protects reproducibility but cannot eliminate every concurrent filesystem race; it does not validate a native shell mesh/gravity response.

Regressions in `tests/test_model_mesh_case_workflow.py` confirm both digest roles, required source symlink rejection before any output, linked 02_MODEL root rejection and prevention of partial prepared config writing when a later target is linked. No original EDB, workbook or ETABS model data is committed or altered.


## 2026-11-15 exact comparative mesh size validation

The shared `validated_mesh_size` function accepts only **integer** 4, 8, 16 or the exact GUI text values `"4"`, `"8"`, `"16"`. It rejects `8.9`, `8.0`, `True`, and malformed text before creating any source-copy run. The same validator is used for case-base naming, case staging, assembly status and assembled config verification. Prior `int(...)` conversion could relabel a different requested floating value as a valid mesh size; this is a model identity defect, not merely a UI issue. Status remains `STAGED_NOT_ASSEMBLED` until real assembly has run; neither stage output nor SHA evidence proves native gravity response or mesh convergence.


## 2026-11-15 — diagnostic ZIP archive and SHA-checked spreadsheet-only recovery

`package_mesh_case(export_root,n)` creates `02_MODEL/SLAB_LOAD_PATH/UPLOAD_PACKAGES/MESH_04.zip` (or 08/16) by copying the contents of that **one** mesh case subtree (`RUNS`, `EXCEL`, `JSON`, logs as saved) into the ZIP without modifying the original. Each ZIP entry is prefixed with `MESH_nn/` to prevent ambiguous extraction. `ZIP_SHA256_MANIFEST.json` lists exact per-file checksums and status `DIAGNOSTIC_PACKAGE_NOT_SOLVER_ACCEPTANCE`. Linked source and outputs are refused; ZIP CRC validated before atomic replacement. This is for private debugging, **not a test result**, and must not be committed publicly if real EDB derivatives or source coordinates are included.

`recover_assembled_mesh_workbook` examines the latest saved assembled run and compares original source audit SHA256 to `MESH_CASE_PROVENANCE`, staged config to a freshly derived `root_config + floor_subdivisions` and model `config_sha256` to the staged config. Only a complete SHA-matched saved floor mesh may be used to **re-export the formula workbook**, never a stale model, a settings-only PREPARED_CONFIG or a fake solver gravity result. This permits recovery after an Excel row-limit error without rerunning expensive assembly. It records `FORMULA_WORKBOOK_REEXPORTED_NOT_GRAVITY_VERIFIED`. Native gravity and ETABS equivalence are still not established.

Tests: `tests/test_model_mesh_case_workflow.py`; `tests/test_slab_mesh_excel_paging.py`. User 2026-11-15 MESH_04 and MESH_08 manifests had 7,000 and 28,400 floor shell cells respectively, and explicitly said `FORMULA_AUDIT_ONLY_NOT_SOLVER_VERIFICATION`. MESH_16 was aborted by Excel before a complete workbook was saved; do not mark it as passed until recovery and actual native solver checks.

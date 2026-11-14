# Unified output contract V1 — implementation and residual migration review

**Review date:** 2026-11-14 (NPT). **Status:** PYTHON SOURCE CHANGES + TESTS; NATIVE WINDOWS ACCEPTANCE OPEN. Engineering model, source EDB, existing original Excel workbooks, OpenSees numerical analysis and accepted structural results **unchanged**.

## Completed source-level work

1. `components/inputs/output_layout.py`: central canonical seven-stage registry plus explicitly separate `02_MODEL`, `08_ETABS_COMPARISONS`, `09_SOFTWARE_DIAGNOSTICS`, `90_UPLOAD_PACKAGES`; explicit read-only aliases `06_LINEAR_TH` and `07_NONLINEAR_TH`; `result_roots()` finds present canonical and historical stage directories without creating outputs or scanning nested selected cases twice.
2. `components/inputs/project_output_layout.py`: derives created project directories from the same registry. `case_folder()` accepts legacy stage identifiers but resolves them into canonical destination folders; preserved caller signature and source EDB SHA binding.
3. `components/inputs/output_contract.py`: common `RUNS/<STATE>/<CASE>/<RUN_ID>` case structure with `00_INPUT_SOURCE`, `01_LOGS`, `02_RESULTS`, `03_EXCEL`, `04_FIGURES`, `05_COMPARISONS`, `06_REVIEW`, `07_EXPORT_ZIP`; manifest with explicit model/EDB SHA, kN–m–s unit basis, solver-only completion vs engineering acceptance; deterministic UTF-8 JSON/CSV and shared Excel formatting.
4. `components/validation/response_inventory.py`: searches canonical gravity/seismic and historical result paths for **read-only evidence**, without counting stored `REVIEW_SNAPSHOTS` or archive copies as independent numerical runs.
5. `components/validation/case_review.py` (V142): discovers compatible seismic stage roots, eliminates identical drift/deflection entries, records missing-data and source-identity gates, writes report under `09_SOFTWARE_DIAGNOSTICS/CASE_REVIEW_V142` instead of creating an old-style nested `OpenSees_Analysis_Results`; uses common Excel style and atomic stable JSON.
6. Tests: `tests/test_unified_output_contract.py`, `tests/test_response_root_compatibility.py`, `tests/test_case_review_canonical_output.py` plus existing `test_output_layout.py` and `test_project_output_layout_v171.py`.

## Updated outputs and uniform formatting

- New derived CSV: UTF-8, header order specified by producer, LF lines, no unrecognized columns, atomic update. Include units in column names and model/case identities in separate manifest.
- New derived JSON: sorted keys, indentation two, UTF-8, strict no NaN/Inf, atomic replacement; status is **not engineering acceptance**.
- New V142 Excel: dark navy header, wrapped white bold text, restrained alternating row fills, auto-filter, frozen headers, readable column widths; formulas/engineering values unchanged.
- All new stage writers **can** call `create_case_run` but have **not all yet been switched**. This avoids breaking old ESM/MRSM/modal/LTHA/NLTHA runners and evidence links.

## Open discrepancy/next migration tasks

| ID | Severity | Open item | Acceptance evidence |
|---|---|---|---|
| UO-01 | P0 | Legacy flat ETABS exports and old `OpenSees_Analysis_Results` are preserved; producer-side migration still needed | Full writer+reader+GUI+ZIP smoke test per module with verified hashes |
| UO-02 | P0 | V135 design-check writer remains bound to legacy `OpenSees_Analysis_Results/Design_Checks_V135`, although response inventory is dual-path | Link V135 output source identity with modern reader and prove no missing case |
| UO-03 | P0 | Gravity support cases 32/76/97 still materially differ per foundation despite global equilibrium | ETABS-native restraint/DOF/coordinates, 6-component reaction comparison and shell/beam/wall equivalent stiffness |
| UO-04 | P0 | Conventional RC slab modifiers 0.25/0.35 required per project-adopted IS Table 5; GUI policy is not proof generated shell section uses these values | Native section-command audit ULS/SLS; MESH_04/08/16 force/reaction convergence |
| UO-05 | P1 | V142 can find compatible results but no source-model SHA gate on each legacy CSV; duplicate physical results saved as distinct files can still appear | Native case registry/identity checks before combined acceptance; report unreviewed/stale explicitly |
| UO-06 | P1 | `02_MODEL/SLAB_LOAD_PATH` remains a supported **auxiliary model stage**; migrating its current writer is separate | New mesh source hash/solver provenance/staged model/solver acceptance and all GUI path readers |
| UO-07 | P1 | Other stage workbooks and figure exporters do not yet use shared `style_workbook`, `atomic_json`, `write_table` | Add stage-by-stage adapters and compare old/new numerical outputs byte-wise or value-wise as appropriate |
| UO-08 | P1 | Full Windows interactive GUI, local copied Excel/ZIP and active launcher version not executed by GitHub CI | Native Python 3.12 / ETABS + OpenSees smoke test per action with evidence manifest |
| UO-09 | P1 | Nonlinear RC core/FSAM, pinned brace end releases, FVD calibration and full NLTHA are separate physical gates | project reinforcement/test evidence, calibrated law, intact model and complete response record |

## Commands (local only)

Run from the updated repository checkout:
```powershell
python -m unittest discover -s tests -p 'test_unified_output_contract.py' -v
python -m unittest discover -s tests -p 'test_response_root_compatibility.py' -v
python -m unittest discover -s tests -p 'test_case_review_canonical_output.py' -v
python -m unittest discover -s tests -p 'test_output_layout.py' -v
python -m unittest discover -s tests -p 'test_project_output_layout_v171.py' -v
```

No native simulations or file migration were performed here. The contract is deliberately opt-in for stage producers; it is unsafe to claim the whole application has completed migration from changing one shared library. See `docs/source/components/inputs/output_contract.py.md` for API and formatting rules.

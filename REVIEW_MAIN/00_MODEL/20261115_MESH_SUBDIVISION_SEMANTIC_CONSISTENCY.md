# Mesh subdivision identity — coordinated semantic source review (2026-11-15)

**Scope:** Source-only snapshot at Git revision `4e837643a11345c99e0bbec3f4e4eea674f7fbf2` (533 active Python files), and fresh source fetched from latest `main` for the three relevant live components. This is a completed **targeted model-identity semantic review**, not completion of all 3,939 repository-wide review units.

## Confirmed behavior defect

Three active layers previously used `int(floor_subdivisions)` or equivalent:

1. `components/model/assembly.py::_mesh_areas` accepted floats and truncated fractional geometry subdivisions before generating floor mesh coordinates. Example: `8.9 -> 8`. This incorrectly represents a requested discretization and can silently invalidate a mesh convergence comparison.
2. `components/gravity/mesh_cases.py::case_base/stage_case/build_case` converted a requested mesh count to an integer before validating 4/8/16 and publishing a case directory, allowing `8.9` to produce a labeled MESH_08 result.
3. `components/gravity/load_path_formulas.py::export/add_formula_audit` performed the same conversion when making the mesh-specific workbook and its identity sheet.

The source code showed these exact conversions. This is not an inferred code requirement or a confirmed nonlinear wall failure root cause.

## Coordinated fix

- Comparative mesh `validated_mesh_size` accepts only integers 4, 8, 16 or exact GUI strings `"4"`, `"8"`, `"16"`. Reject float/bool/malformed types before staging. Recheck assembled config before treating any spreadsheet as belonging to the requested mesh.
- Source-model assembly keeps **2 through 16** as its documented general mesher range, but requires a true integral value or exact decimal string; no silent truncation. No stiffness/loads/mass/wall/reinforcement assumptions changed.
- Workbook identity and exported run status use the exact same comparative validator.
- Dedicated negative/positive regression tests in `tests/test_model_mesh_case_workflow.py` include `8.9`, `4.1`, `8.0`, `True`, malformed strings and accepted 2/4/8/16 assembly or 4/8/16 staged cases.
- Independently executed local source-snapshot Python tests (`tests.test_model_mesh_case_workflow`, `tests.verify_slab_full_gravity_factors`, `tests.test_project_source_reuse`): 12 passed. GitHub CI and native structural acceptance are separate gates.

## Acceptance matrix

| Gate | Status |
| --- | --- |
| Source-line root cause and caller inspection | CONFIRMED |
| Supported 4/8/16 and 2..16 contracts preserved | SOURCE REVIEW COMPLETE_FOR_THIS_CHANGE |
| Synthetic regression tests | LOCAL_PASS; CI_PENDING |
| ETABS model identity and workbook provenance for an actual user case | NOT_VERIFIED |
| ShellMITC4 mesh convergence and ETABS/OpenSees reaction comparison | NATIVE_EVIDENCE_REQUIRED |
| 32/76/97 supports, X-wall first-step and full M0–M6 | NOT_VERIFIED |

Preserve all legacy run paths, source EDB and original Excel source files. Never label a staged configuration or formula workbook as solved gravity analysis.

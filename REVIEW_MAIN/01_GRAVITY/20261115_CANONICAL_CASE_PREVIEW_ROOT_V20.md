# V20 gravity organized case index — duplicate stage root correction (2026-11-15)

**Status:** SOURCE_PATCH_COMMITTED; NATIVE_WINDOWS_RETEST_REQUIRED.
**Source inspected:** `components/gravity/reaction_case_registry.py`, `tests/test_gravity_organized_case_index_v172.py`, `tests/verify_gravity_case_reaction_registry.py`, `components/inputs/output_layout.py`, related source guide. Not a full semantic audit of the entire repository.

## Confirmed issue V20-01

`publish_gravity_case_index(output_root, record)` previously searched **only** for a parent named `OpenSees_Analysis_Results` to identify the selected export case. When called with an already canonical path such as `<selected-export>/02_GRAVITY/RUNS/ULS/X`, it treated the selected run path as a standalone root and constructed `<selected-export>/02_GRAVITY/RUNS/ULS/X/02_GRAVITY/...`. This violates the one-owning-case directory requirement and scatters lightweight preview indexes.

## Corrective change

Reuse the existing canonical `export_root_for()` resolver, which recognizes legacy results and canonical stages, when resolving the preview index root. The destination remains `<selected-export>/02_GRAVITY/<support-scenario>/<case-identity>` for compatibility with existing readers and the original tests. The full native gravity result is **not moved**. Standalone non-stage directories retain their previous `<standalone>/02_GRAVITY` behavior. This is a preview/index routing correction, not a model or physics change.

**Regression:** `tests/test_gravity_organized_case_index_v172.py::OrganizedGravityCaseTests::test_canonical_gravity_run_does_not_create_nested_stage` asserts that no `02_GRAVITY` folder is created inside a canonical run and that the source result bytes remain unchanged. The existing legacy three-strategy test is preserved.

**Remaining limitations:** The project currently has both indexed preview folders and contract-run folders. This change does not move old previews into `REVIEW_SNAPSHOTS`, alter historical outputs, change the 32/76/97 support strategies or prove ETABS/OpenSees gravity equivalence. A writer/reader migration plan is still necessary before changing established preview names.

## Desired case-level evidence package

```text
<export-case>/02_GRAVITY/
  RUNS/<STATE>/<CASE_ID>/<RUN_ID>/
    00_INPUT_SOURCE/
    01_LOGS/
    02_RESULTS/
    03_EXCEL/
    04_FIGURES/
    05_COMPARISONS/
    06_REVIEW/
    07_EXPORT_ZIP/
  <SUPPORT_SCENARIO>/<PREVIEW_ID>/  # existing compatible preview/index folders
  LATEST_GRAVITY_CASES.json
```

## Reproduction

```powershell
python -m unittest tests.test_gravity_organized_case_index_v172 -v
python tests/verify_gravity_case_reaction_registry.py
python -m unittest tests.test_output_layout tests.test_unified_output_contract -v
```

Do not treat a preview index or total vertical gravity equilibrium as native ETABS structural equivalence. Project model identity, wall/slab loads and **physical 32/76/97 support restraints** remain independently unverified.

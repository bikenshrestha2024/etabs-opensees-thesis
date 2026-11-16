# 2026-11-16 regression investigation: ETABS import and MESH_04

Status: STATIC CODE REGRESSION CONFIRMED; WINDOWS BOTTLENECK STAGE STILL REQUIRES PRIVATE WORKER LOG.

## Historical comparison

- Compared the November 15 baseline commit `9041cb630b46` to November 16 main commit `cb4c296138d0`: 119 intervening commits.
- The primary ETABS import GUI changed from synchronous `convert_model()` execution to a subprocess `tools/etabs_conversion_worker.py`. This resolved GUI responsiveness but inserted new source-digest, workbook preflight and categorized export-copy work into the user-visible conversion lifecycle.
- In `components/inputs/lfs_workbook_recovery.py`, optional workbook preflight previously hashed the same EDB once in `audit_optional_gui_workbooks()` and once per each of four `_registered_source()` role calls, even when no source registry was installed. The optimized version passes the initial digest into the role lookup. The separate project layout SHA remains authoritative and registered workbooks are still individually verified.
- `components/inputs/export_mirror.py` hashes flat files, hashes pre-existing categorized copies, and (for new copies) hashes the copied files. This is substantial additional disk activity when the optional mirror is selected. It is now unchecked by default; no existing source or mirror is altered.
- The converter also generates four detailed Plotly source viewers and used to embed the full Plotly JS into each HTML, then opened all four browser tabs. This patch shares a single local Plotly JS bundle and leaves HTML files available in Import on demand.

## Important stage distinction

- `floor_subdivisions=4` changes the ACTUAL floor ShellMITC4 analysis mesh. It is not Plotly resolution. Previously recorded assembled MESH_04 has 10,400 total shell cells and 3,862 frame segments; the latest selected output must establish its own counts.
- `components/gravity/mesh_cases.py::build_case` stages a separate source copy, reassembles the whole building, then generates a large load-path formula workbook. That is a separate expensive workflow from just viewing an already assembled 4x4 grid. Do not run a mesh-case rebuild merely to display a model.
- The on-demand `components/ui/assembled_mesh_view.py` reads the existing SHA-matched model; it aggregates actual shell edges into at most four Plotly traces without changing engineering discretization.
- A 19-minute elapsed worker with 18+ minutes since last log has a silent stage. The screenshot does not indicate which one. Its last `[WORKER STAGE START]`, `[ETABS COM START]`, `[ETABS API HEARTBEAT]`, `[STEP START]`, `[ASSEMBLY TIMING]`, and `[TIMING]` lines determine the cause. It is NOT valid to attribute the entire delay to 4x4 without that evidence.

## User-side verification

1. Update main and launch the current `01_MAIN_GUI.py` in `etabs_env312`, ensuring no older Python/ETABS conversion remains running.
2. Select the exact same original EDB SHA, output root and unchanged 4x4 FEM config as the five-minute run. Do not mix results from other versions.
3. Leave `Also create SHA-verified categorized copies` unchecked for first profile. Run one normal import and open `09_SOFTWARE_DIAGNOSTICS/ETABS_Conversion_Worker.log` from the Import tab.
4. Compare each new timed phase with the historical `ETABS_OpenSees_Conversion_Log.txt`. If `OpenFile` is slow, investigate ETABS process/EDB loading; if API loops slow, instrument that call; if assembly slow, compare mesh count/IO and formula workbook; if mirror slow, leave mirroring optional.
5. Open the actual assembled mesh on demand only after a completed SHA-matched export. The viewer must not initiate ETABS extraction or create new shell elements.
6. Preserve original input/output hashes, original ETABS EDB, all 32/76/97 gravity support cases and unresolved per-node equivalence gates. A performance regression pass is not an engineering validation pass.

## Code tests

- tests/test_import_workbook_digest_cache.py validates a single EDB digest per optional role audit and unchanged SHA mismatch refusal.
- tests/test_assembled_mesh_view.py validates actual shell-edge rendering, source immutability, and stale config gate.
- Existing importer/GUI/ETABS worker/Windows contracts remain separate CI gates.

Original private worker logs and ETABS EDB were not present for this GitHub CI investigation; no actual physical ETABS import time can be claimed yet.
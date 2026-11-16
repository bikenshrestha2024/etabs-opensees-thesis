# 2026-11-16 — MESH_04/08/16 slow independent rebuild investigation

**Scope:** `02 Model → Slab mesh and load-path study`, not the original EDB import/HTML and not OpenSeesStudio. **Status:** high-complexity source loops identified and optimized; native Windows timing still required. The complete ETABS source and solver numeric acceptance remain unchanged.

## Screenshot evidence

The screenshot identifies a GUI that says `RUNNING | Fresh MESH_04 assembly from saved source audit` while the mesh selector can show `8` and the root configuration displays `4`. The previous GUI did not lock the selector after launching a thread; changing the dropdown during a run changed its *display*, not the mesh value captured by `size=int(choice.get())`. The root config remains 4 intentionally because the 4/8/16 comparison builds **independent run folders**, never overwriting the original source configuration.

The lack of a progressing text log does not establish solver deadlock. `build_case` previously only returned to the GUI after fresh whole-building assembly **and** formula workbook export; intermediate stage completions were not shown. The previous run's full stage timing was not attached.

## Confirmed avoidable algorithmic costs

**P0 (optimized): global coplanar-point search per source area.** In `components/model/assembly.py::_mesh_areas`, every area panel scanned all original source points plus all seeded floor grid points, filtering by normal-plane projection. Shell refinement multiplies both number of points and number of shell cells. This creates cross-panel repeated geometric searches. Replaced with pre-indexed *exactly axis-aligned* plane buckets (1 micrometre indexing with neighbor-bin tolerance), while retaining the original candidate checks and the full scan for tilted panels. Crucially **coplanar points outside a panel must remain eligible** to propagate shared mesh lines; a simple panel bounding-box filter would change the FEM mesh and is not permitted.

**P0 (optimized): per-beam full assembled-node scan.** The original frame split loop `for n,r in nodes.items()` was executed once for each original frame, including all mesh-generated shell nodes. Replaced with one spatial 1.5 m voxel index and beam bounding-box candidate extraction before the unchanged centerline and parametric-cut tolerance check. Candidates are restored to original `nodes.items()` ordering for duplicate/cut priority consistency. No frame release, physical offset or load vector was intentionally modified.

**P1 (optimized): openpyxl column-width calculation scanned all worksheet data.** In `load_path_formulas.py`, looping `for col in sheet.columns` to inspect `col[0]` loaded/traversed entire large surface and node-path worksheets. Width depends only on header row. Now iterates `sheet[1]`, avoiding unnecessary scans of potentially millions of cells.

## Inherent, not merely algorithmic, costs

Each 6 m×6 m source slab begins with 16/64/256 cells for MESH_04/08/16; MESH_16 has 16× the base cell count of MESH_04 before additional intersections. The 4-floor/8-floor/16-floor naming means subdivisions **per source panel direction**, not four/eight/sixteen cells total. The full 25-storey model can create very large `OpenSees_Complete_Model_Data_V118.json`, ShellMITC4 cell arrays, and Excel ledgers.

The Excel workbook writes one row **per floor shell cell and per assigned pressure pattern**, four separate node-load path rows per such record, and copies the surface sheet for a separate preload view. This can be memory/CPU intensive on 16×16 models; large files also take time to save and to recalculate in Excel. None of this proves the solver was stuck.

## UI corrections

- Corrected text widget inserting literal characters `\\n` instead of real line breaks.
- `build_case(..., progress=callback)` now emits input staging, assembly completion, workbook start/end, and total elapsed duration.
- The GUI uses a thread-safe `queue.SimpleQueue`, an elapsed-time heartbeat updated every 500 ms on Tk's main thread, and the last actual stage.
- Locks mesh selection while a run is active so the displayed size is consistent with the submitted worker size; restores it on success or failure.
- Remains an independent case and does not change the root EDB, existing solved case, source config or structural model defaults.

## Verification and acceptance

Offline tests include source-panel area conservation (4/8/16) and preservation of an off-panel coplanar gridline, plus the backwards-compatible optional progress callback. These tests are added to `export-staging-regressions.yml`. A synthetic test originally failed because its mock material dictionary used `nu` instead of production's `poisson_ratio`; fixture corrected. Final CI result must be checked separately.

**No claim of native run-time reduction is yet made**: the model must be rerun in the user's Windows conda environment and the actual `MESH_BUILD_STATUS.json`, timestamps, output file counts/sizes and run log inspected. `FORMULA_WORKBOOK_CREATED_NOT_GRAVITY_VERIFIED` means no independent gravity solver or ETABS equivalence check has passed.

## Recommended reproducibility record

For each n=4,8,16 separately retain elapsed:
1. `source staging SHA/copy`;
2. `prepare_complete_export` assembly;
3. `add_formula_audit` workbook build;
4. `wb.save` serialization;
5. output file size, node/shell/frame counts and peak memory;
6. full independent gravity solver + ETABS-matched reactions and slab/beam response.

If Excel export fails after assembly, use **Retry Excel from assembled mesh (no rebuild)** to avoid recomputing shells. Do not claim convergence from pressure conservation alone.

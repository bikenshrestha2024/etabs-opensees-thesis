# 2026-11-16 — Export took ~30 minutes: evidence, bottlenecks and follow-up instrumentation

**Scope:** main ETABS→OpenSees thesis converter, not the separate OpenSeesStudio interface fork. **Status:** bottlenecks identified from static code, but the exact historical 30-minute time breakdown cannot be proved without the timestamped export log `ETABS_OpenSees_Conversion_Log.txt`. Do not fabricate timings.

## What the user supplied

- The completed GUI reports **3,862 assembled frame segments** and **10,400 wall/slab shell cells**, with `assembly_errors: []`, but both engineering and nonlinear readiness remain REVIEW REQUIRED.
- The report excerpt records gross downward gravity load `286,419.7582311328 kN`, active seismic weight `284,691.5561853357 kN`; the excerpt confirms **model assembly finished**, not native ETABS–OpenSees response equivalence.
- Extracted reference workbook tabs: 8 properties, 2,093 element mappings, **14,263 solver elements**, **11,098 nodes**, 1,368 frame-load rows, 730 area-load rows, 144 library parameter rows; its counts show model complexity but do not timestamp stage duration.
- Source visualization snapshots show at least **2,092 element records**, 2,850 total load traces/triangles, 750 frame-load traces, 1,050 plotted load areas and an overflowing repeated legend. Images do not determine CPU time.
- Older timing records for source metadata only showed completed stages of 10.22 and 6.73 seconds. A small metadata step is not a full ETABS extraction/assembly/export profile.
- The original GUI showed a modal completion dialog **after the export**. Its prior implementation performed the entire converter inside Tkinter's UI callback and therefore stopped processing window events throughout long conversion stages. This accounts for the *Not Responding* appearance even if computation was proceeding.

## Static source findings / ranked suspects

1. **Confirmed UI responsiveness defect (fixed):** `components/ui/application.py App._run` previously invoked `convert_model` synchronously. Fixed by `tools/etabs_conversion_worker.py` child-process launch and responsive `root.after` polling. This isolates the GUI, but does not guarantee faster computation.
2. **Repeated O(N) mapping scans inside visualizer (fixed):** four source-element tag assignments used `next(... for rec in element_records ...)` for every source frame/polygon, repeatedly scanning the mapping list. Replaced with a one-time `_visual_element_tags[(source_object, dimension)]` indexed dictionary. The index uses the first matching record to preserve legacy visual ID behavior; it is not a numerical assembly mapping change. Speed benefit needs actual measurement.
3. **Expensive 3D HTML output (plausible, profile added):** `Interactive 3D and floor-plan visualizations` creates thousands of Plotly `Scatter3d`, `Mesh3d`, and floor-plan traces across **four complete HTML documents** with `include_plotlyjs=True`. Large trace counts, repeated figures and browser startup can stress Python memory and browser rendering. All four viewers were opened automatically at completion. It is not proven this caused the historical 30-minute runtime.
4. **Large source COM extraction (plausible):** thousands of ETABS point/object/frame/area queries are made through OAPI. Windows ETABS process initialization, model opening, external file/AV latency and individual API calls need timestamps to distinguish.
5. **Assembly, downstream file organization and output metadata (plausible):** complete export builds frame/shell solver records. The `@timed_outputs` decorator recursively scans new files and generates per-artifact metadata after conversion. Processing a repeatedly reused output folder can increase tree scanning/serialization overhead. The decorator timing currently records converter body time before the final post-run recursive metadata scan; use wall clock versus `[CONVERSION COMPLETED]` and `[TIMING]` logs to determine any additional overhead.
6. **Browser slowdown separate from Python calculation:** 3D HTML with thousands of traces / 3D objects can render slowly after the converter has completed. Do not equate browser loading time with solver execution.

## Instrumentation added

Source `components/ui/application.py` now logs
- `[STEP START]`, `[STEP OK]`: source extraction, node crosswalk, connectivity, section audit, seismic setup, load conversion, visualizations, final assembly;
- `[VISUALIZATION TIMING]`: structural trace construction, structural HTML writing, connectivity trace construction, connectivity HTML writing, 3D load trace construction, 3D load HTML writing, floor-plan trace construction, floor-plan HTML writing;
- `[ASSEMBLY TIMING]`: `extract_source_metadata` and `prepare_complete_export`;
- `[CONVERSION COMPLETED]`: total conversion duration;
- `[TIMING]`: whole-stage metadata decorator timing, emitted after per-artifact metadata handling;
- `[WORKER RESULT]` and worker exit code, from the separate process.

The new `[VISUALIZATION INDEX]` counts the indexed element identifiers. The user can compare **total runtime versus sum of stage times** without changing analysis configurations.

## How to identify the exact delayed stage

Run `git pull origin main` and `python 01_MAIN_GUI.py` from `etabs_env312` after ensuring no older Python GUI instance is running. Inspect the private case log at `09_SOFTWARE_DIAGNOSTICS/ETABS_Conversion_Worker.log`; also check `ETABS_OpenSees_Conversion_Log.txt` from the previous run. A gap between one `[STEP START]` and the next `[STEP OK]` identifies a slow conversion stage; gaps inside visualization or assembly are now instrumented.

Do **not** delete/rewrite the source EDB, remove essential shell nodes, force-match reactions, disable mass checks or classify the successful export as a native engineering PASS to improve speed. Maintain source/solver comparison and 32-support/76/97 sensitivity gates.

**Outcome:** the UI blocking mechanism was fixed; one clear visualizer inefficiency was removed; extensive timing was added. Without the historical full log, no defensible statement that any single stage consumed a specific number of minutes can be made.

# Source viewer trace compaction (read-only)

Source: `components/ui/source_view_compaction.py`

## Purpose

Replace thousands of browser-side Plotly 3D objects with batched geometry while keeping every exact ETABS source object/element mapping accessible. This module executes only in the visualization step of ETABS source export. It cannot change solver nodes, FE mesh, gravity loads, supports, material models or analysis cases.

### Connectivity

`compact_connectivity_figure(fig, metadata)` groups original source frame and area geometry by (category, story, assigned ETABS section/property). Coordinates and source ID metadata for **every element** remain in the HTML's immutable indexed metadata. Groups render as a few batched Scatter3d traces; selecting an individual ETABS object/solver element creates a single bright overlay using the exact original source coordinates. Clicking a grouped line uses the stored object index. Node lookup and sections are shown in the detail panel. Source object count and batch count are separately displayed. B/C/BT/CO/CT/FVD/BRB/BR functional classifications are **not deleted**; the mapping/lookup data remain the source of truth for more specialized element selectors.

### 3D applied loads

`compact_load_figure(fig, metadata)` batches triangles of the same load pattern, story and intensity into one Mesh3d trace with remapped triangle vertex indices. All frame-load UDL arrow strokes of the same pattern/story/value are batched into one line trace; end intensity is a separate grouping key. The exact original per-vertex customdata and hover template are retained to identify ETABS object, load pattern and member. Existing storey, load-pattern and UDL-value filters operate over batched traces. Summary counts use the **original triangle/arrow counts**, not just batch counts. The original load ledger, raw API output and CSV audit remain unchanged.

## Separate performance gates

- Measure original source viewer trace count versus batched trace count from `[VISUALIZATION COMPACTION]` and the `[VISUALIZATION TIMING]` timestamps.
- Measure browser cold load, orbit/zoom and filter changes separately from ETABS conversion process duration.
- The user log (November 16, 22:48) shows source 3D views generated in 3.74 seconds; this does not explain the assembly-only delay.
- A complete model assembly has to print `[ASSEMBLY PHASE START]`, `[ASSEMBLY HEARTBEAT]`, and `[ASSEMBLY PHASE OK]` for shell meshing, spatial index, frame segmentation, audited load ledger and load path. A substage without an OK line identifies the stalled operation.

## Verification

`python -m unittest tests.test_source_view_compaction -v`

Tests compare geometry vertices, triangle connectivity, original source IDs, element sections and customdata against the source Figure; they do not run native ETABS.

Do not call a plot/report an engineering-equivalence PASS. Original gravity 32/76/97 boundary conditions are untouched.

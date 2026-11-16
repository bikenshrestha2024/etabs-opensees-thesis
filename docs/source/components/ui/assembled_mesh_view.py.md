# Actual assembled OpenSees 3D mesh viewer

**Code:** components/ui/assembled_mesh_view.py. The viewer is explicitly separate from ETABS model extraction and numerical assembly.

## Input provenance and semantics
- Reads *completed* OpenSees_Complete_Model_Data_V118.json and OpenSees_Complete_Model_Config_V118.json from the same selected export.
- Rejects the model when its recorded config_sha256 differs from actual config bytes (stale mesh). Does not invoke ETABS/COM, a solver, material changes, wall support or remeshing.
- 'floor_subdivisions = 4' means four divisions in each direction **per original floor source panel**, not a Plotly resolution control. It can produce 16 or more refined cells per panel once conforming joins are included. It can affect element count and gravity load path.
- Builds one aggregated Scatter3d line trace per family (floor shell, wall shell, other shell, frame), deduplicating shared edges. This avoids a separate Plotly trace per shell. All actual mesh edges remain present; no viewer-only coarsening occurs.
- Saves 02_MODEL/03_3D_VIEWS/OpenSees_Assembled_Mesh_3D.html with directory-local plotly.min.js. The saved generated HTML is for review only and has no structural verification status.

## GUI and CLI
- Main Import stage: **3D actual assembled 4×4 mesh (on demand; no ETABS rerun)**. The actual subdivision number appears in the HTML title; the button remains usable if it is 8 or 16 instead.
- Runs the HTML render in a background Python thread and opens the browser only after the file exists. The GUI rejects clicks during conversion and concurrent render attempts.
- Command line: python -m components.ui.assembled_mesh_view 'D:/Thesis Opensees/ETABS 11-16-2026/3'

## Performance
Original detailed source visualization runs during ETABS conversion; this actual assembled mesh viewer is **not added to that conversion critical path**. Generating and opening the HTML are independent manual actions. Large meshes still incur JSON parsing and browser rendering, and native performance must be measured in the existing ETABS_Conversion_Worker.log.

## Test and validation
Run python -m unittest tests.test_assembled_mesh_view. Synthetic tests verify unique shared edges, source configuration hash gate, output structure and no source mutation. Native ETABS/OpenSees gravitational response validation remains separate.
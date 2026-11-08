# view_controls.py — source documentation

**Python source:** [components/ui/view_controls.py](../../../../components/ui/view_controls.py)
**Git baseline content SHA:** 2ae4e26b53bfd987e35745f5a01c820ee0d3beeb
**Subsystem:** Modern GUI and data display
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the ui implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: See module's underlying computational dependencies. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)

## November 2026 — Native 3D Zoom to Node and visible selection

The `components/ui/view_controls.py` shared camera utilities
`resolve_node_tag`, `center_camera_on_node`,
`node_selection_artists` and `remove_selection_artists` are used
in both gravity and SLS/ULS response viewers.

ETABS source point mappings can contain integer OpenSees node tags,
but the 3D node dictionaries use string keys. The previous lookup
silently failed for such mapped points. The new lookup normalizes
tags to strings, highlights a selected node with a prominent magenta
crosshair/yellow marker and reports unknown IDs.

**Zoom to Node** focuses the 3D camera at the selected node's
actual plotted XYZ, retaining the current camera orientation
(isometric, front, top, etc.). **Fit all** restores the full building.
These controls modify the viewer only, not engineering geometry,
loads, boundary conditions, materials or structural analysis.

Test: `python tests/verify_3d_zoom_to_node.py`.

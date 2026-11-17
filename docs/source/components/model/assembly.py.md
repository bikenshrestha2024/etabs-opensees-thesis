# assembly.py — source-model assembly and E-SFI node orientation

**Implementation:** [assembly.py](../../../../components/model/assembly.py), notably `_wall_panel_nodes`, `_mesh_areas` and `build_complete_model`.

- **Source:** actual ETABS export geometry, family tags, material/section records, wall quads and opening mesh, kg/kN-m-s consistency.
- **Geometry contract:** wall quad must be bottom-first; i→j wall width horizontal; i→l storey height vertical upward; 4 counterclockwise corners, normal and nondegenerate area. Correct source *node topology* is essential; no automatic triangulation/reconstruction of nonparallelogram wall openings.
- **Numerical element:** `ops.element('E_SFI_MVLEM_3D',tag,*nodes,m,'-thick',...,'-width',...,'-mat',...,'-Density',0.)`. Width uses actual i–j distance in metres; do not use diagonal or storey-height length. Mass is assigned separately to nodes and must be audited against ETABS source.
- **Material warning:** Current research constructor still assigns nominal unconfined frame and PEER/M30 wall benchmark values. It does NOT implement validated boundary/web project material cards; the thesis intent is now correctly blocked at source input, not an auto-approval.

**Native evidence needed:** project ETABS model and openings schedule, verified frame/wall reinforcement and confinement, source gravity/mass, individual FSAM cyclic wall element and full 3D core. Do not repair a nonfinite value by silently inventing stiffness or altering source geometry. [P0 review](../../../review/01_WALL_GEOMETRY_MATERIALS_FIRST_STEP.md).

Source: [OpenSees E-SFI 3D](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html); [NBC 105:2025](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf) §§9.3.1–9.3.3.

2026-11-10 publication: runtime workbook packaging delegates to
`copy_project_workbooks` in the canonical inputs module. New exports receive
only the three small calculator/scaling workbooks under excel/source and a
verified private source registry where available. Large ETABS tables remain
referenced. No model assembly, stiffness or solver equations changed.


## 2026-11-15 verified context contract source review

Direct-import prepare_complete_export previously defaulted runtime_dir to components/model instead of actual project/runtime root; original root facade happened to work. Modal input populate(gui,Path(__file__).parent,folder) likewise depended on facade. Both now use _runtime_repo_root. Do not touch __file__ strings inside generated model/GUI scripts; those belong to generated-runtime context. No geometry or element physics changes.

Scope of tests: synthetic direct-module import, exec-root facade, exported-runtime facade path consistency in `tests/test_facade_runtime_context.py`. No native ETABS/OpenSees, source workbook or full engineering model was executed in these path-only regressions.


## 2026-11-15 exact integer mesh-grid contract

`_mesh_areas(..., floor_subdivisions=...)` now rejects floats, booleans, missing or malformed values **before meshing**. The source/assembly contract preserves exact integral subdivisions 2–16 (including exact decimal strings such as `"8"`); it must never silently convert an input like `8.9` to `8`. Unlike the comparative 4/8/16 study, this general source mesher is intentionally not restricted to 4/8/16. Source ETABS geometry, model parameters, stiffness, gravity/mass factors and wall topology remain unmodified. Synthetic `tests/test_model_mesh_case_workflow.py` checks the early failure and accepted 2/4/8/16 cases; actual wall/shell gravity convergence and ETABS parity still require native model evidence.


## 2026-11-15 — ETABS 6-DOF release provenance for 112 pinned-brace candidates
The V118 complete export report now includes `hinged_brace_release_review` with ETABS frame unique object ID, topology preview tag, *actual* assembled frame segment integer tags, physical source section/category and raw ETABS `GetReleases` arrays. This is an additional audit schema: existing warnings remain and constitutive formulations are unchanged. No bracket from a source BRACE to CO/BT/CT is assumed, and no edited device calibration is accepted. The elastic `elasticBeamColumn`, exploratory `corotTruss + Steel01`, and reviewed nonlinear blocking behavior are intentionally distinguished, with native engineering acceptance unresolved. Source-only contract regression is in `tests/test_area_folder_and_hinged_brace_review.py`; review case document in `REVIEW_MAIN/00_MODEL/20261115_AREA_HINGED_BRACE_AND_MESH_EVIDENCE.md`.


## 2026-11-15 researcher-adopted pin-ended diagonal assumption

The researcher has approved **retaining the existing ETABS pin-ended steel diagonal outrigger-brace assumption provisionally** while progressing source comparison and exploratory studies. This is **not** acceptance of the 112 members as physically verified pins, nor a blanket hinge for chord, belt, core/panel-zone, cap-truss or peripheral-column connections. The decision record [DB-OUT-2026-11-15-01](../../../../REVIEW_MAIN/00_MODEL/20261115_PROVISIONAL_HINGED_OUTRIGGER_BRACE_DESIGN_BASIS.md) grounds this modeling choice in the CTBUH outrigger guide §§2.2/2.8 and Jin Mao §3.5 example, Gunda & Anthugari (2022), and general truss/FEM mechanics (Shrikhande); these sources **do not** explicitly calibrate this ETABS member-end release pattern. Existing `GetReleases` parsing, elastic beam rotational releases and exploratory axial truss remain unchanged. The reviewed nonlinear `hinged_brace` rejection remains in force pending source connections, native benchmark, nonlinear buckling/connection and device calibration.


## 2026-11-17 — completed elastic brace IDs and assembly progress

Per-member elastic messages are now emitted after successful model-data
assembly using the actual `solver_element_tags` already recorded by the frame
segment loop. The pre-assembly identity string is retained for unsupported
release errors only. Completed members record
`elastic_status=ASSEMBLED_SOURCE_END_RELEASES`; they no longer claim their tags
are pending or conflate elastic source releases with nonlinear hinges.
The separate reviewed nonlinear warning and
`BLOCKED_UNVERIFIED_CONNECTION_AND_BRACE` status remain: neither source
releases nor a successful elastic export calibrates connection behavior,
compression buckling or cyclic fracture. No constitutive equations changed.

`prepare_complete_export(..., progress=None)` accepts an optional single-string
callback alongside existing stdout logging. Phase starts/completions and frame
heartbeats can reach a GUI queue without redirecting process-wide stdout.
Runtime packaging and mapping-workbook generation also report their stage.
Callbacks run synchronously in the caller's worker thread and must be quick;
they must not touch Tk widgets directly. Existing callers need no changes.

The synthetic complete-export fixture in
`tests/test_area_folder_and_hinged_brace_review.py` checks a source brace split
into two assigned tags, raw release preservation, completed elastic messages,
nonlinear blocking and phase callbacks. This is solver-free assembly evidence,
not a native element or project calibration test.

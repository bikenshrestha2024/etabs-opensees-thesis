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


## 2026-11-17 — keep wall and floor restraint propagation independent

`_resolve_refined_wall_supports` applied the opt-in confirmed WALL propagation
policy to every area polygon, including floor edges. It now ignores explicit
non-wall categories and horizontal polygons. Unclassified legacy vertical wall
quads remain compatible. Source-only supports and the explicit source-confirmation
requirement are unchanged; this correction does not enable propagation or alter
existing saved models. Synthetic tests in `tests/verify_wall_base_restraints.py`
check a restrained floor edge receives no added nodes, while a confirmed vertical
wall edge still does. Exact ETABS analysis-node restraints and source hashes must
be verified independently; a screenshot of a setting is not a per-object source
manifest or a native equivalence result.

## 2026-11-21 story-weight ledger follows the §5.2 mid-height rule

The story ledger (`NBC105_ESM_Story_Weights_Assembled_V118.csv`) now assigns each active node's weight with `storey_index_for_elevation` ([clause 5 module](../nbc105/clause_05_dynamic_characteristics.py.md)): weight below the mid-height between adjacent floors goes to the lower floor, otherwise to the upper floor. Nodes at or below the first floor stay with floor 1; nodes at or above the roof go to the roof. Total weight is unchanged; per-storey Wi change, so exports must be re-assembled. Weight-to-mass conversion and its inverse use the shared `GRAVITY_M_S2` (9.81 m/s^2, USER_DECISION 2026-11-21; NBC 105:2025 prints 9.81, see the [constants guide](../nbc105/constants.py.md) and the [compliance matrix](../../../nbc105/clause_05_dynamic_characteristics_matrix.md)); the numeric value is unchanged.


## 2026-11-21: opt-in wall mesh limit `wall_max_cell_size_m` and shell mesh audit

**Finding.** `_mesh_areas` refines floors with `floor_subdivisions`. Walls only receive the coplanar coordinate lines: horizontal lines come from slab subdivision points on the wall plane, and vertical (height) lines come only from storey and opening levels. Wall cell heights are therefore 1.5, 2.3 or 3.8 m in MESH_04, MESH_08 and MESH_16 alike. ETABS meshes the walls at 1 m (`Analysis - Wall Mesh Settings`).

**Option.** `OpenSees_Complete_Model_Config_V118.json` key `wall_max_cell_size_m`. Absent or `None` gives the historical mesh. The key is never written as a default, so existing configs, their SHA and the model data stay identical. Checked: on the user's MESH_04/08/16 topology the default mesh digest is identical before and after this change. A positive float, for example `1.0`, runs `_seed_wall_refinement_lines` before meshing:

- **Height:** one global set of wall elevations (all wall horizontal lines, each gap split uniformly to the limit or less) is applied to any wall that has a taller cell. The points go on both vertical panel edges, so walls meeting at a corner share every level. As a side effect, the historical 2.3 m corner T-junctions are removed.
- **Width:** wall intervals longer than the limit are split uniformly. The points go on the top and bottom edges of every coplanar wall panel at every storey, so the floor planes receive the same lines. New floor-edge grid points are fed back so that walls on other slab edges share them. The loop stops when no new point appears.
- **Safeguards:** a limit larger than every wall cell is a no-op. Node tags are allocated by the unchanged mesher. Frame segments are cut at the new wall nodes by the existing exact cut (`1e-7` m). Under `EDGE_PROPAGATE_CONFIRMED`, every new base node on a source wall edge is restrained. `SOURCE_ONLY` still adds none. Cell areas are exact sub-areas, so self-weight, the area-load ledger, the slab and joint-volume audits, the mass ledger and the §5.2 mid-height ledger keep their totals. `active_horizontal_seismic_weight_kN` excludes fixed-node mass and therefore changes slightly when base cells become shorter.

**Audit.** `shell_mesh_quality_audit` (see [shell_mesh_quality.py](shell_mesh_quality.py.md)) is always written to the export report and `MESH_BUILD_STATUS.json`. It is a diagnostic only.

**Measured on the user's topology, mesher only (no solver).** With `wall_max_cell_size_m=1.0`:

- MESH_04: wall cells 3,400 → 10,650, wall edges ≤ 1.0 m, max wall aspect 23 → 7.7.
- MESH_08: max wall aspect 46 → 15.3.
- MESH_16: max wall aspect 92 → 30.7.

The remaining high ratios come from historical narrow widths (0.1/0.05/0.025 m), not from height. Hanging nodes fall from 1,250 to 1,100. The 1,100 are pre-existing wall nodes (opening lines) on slab edges that the slabs do not share; the option does not change them. A MESH_04 full `prepare_complete_export` run gives the same totals with and without the option: total downward load 286,419.7582 kN in both, and total seismic weight 286,419.7582 kN in both. Frame segments go from 3,862 to 4,062. Base supports stay at 76 (`SOURCE_ONLY`).

**GUI.** No GUI widget exists for comparable config keys (`wall_base_restraint_policy` and others are edited in the config JSON). Set the key in the JSON of a copied export root. Tests: `tests/test_wall_mesh_refinement_option.py`. Native OpenSees gravity/modal comparison with ETABS is PENDING.

## 2026-11-21: opt-in `rigid_end_zones` hook

`prepare_complete_export` reads the config block `rigid_end_zones` just before `compile_settings`. When it is absent or `enabled: false`, nothing changes. When it is enabled, [rigid_end_zones.py](rigid_end_zones.py.md) resolves the ETABS end length offsets (assignment workbook or EDB metadata) and writes them as `end_offsets_m` into every `elastic_etabs_comparison` state. The export report gets a `rigid_end_zones` audit. The block without a non-empty `elastic_etabs_comparison` raises. Loads, masses and self-weight are unchanged (solved: 311,367.3139 kN in every step of the [run finding §8](../../../validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md)). Named preset: [etabs_comparison_preset.py](etabs_comparison_preset.py.md).

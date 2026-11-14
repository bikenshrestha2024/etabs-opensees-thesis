# 2026-11-14 — V118 export, ID namespaces, hinged brace and slab-mesh review

Status: **REVIEW REQUIRED / ENGINEERING ACCEPTANCE NOT GRANTED**. Sources: user-supplied V118 JSON, V144 inventory, ETABS/OpenSees ID lookup, two Excel audit workbooks, prepared MESH_04/08/16 configs, screenshots and current repository. The original ETABS EDB and local assembled models were **not** available to execute or modify. This branch introduces *display-only* ID code/tests; it does **not** claim the 3D UI or vertical load path has been repaired.

## Observable evidence
- V118: zero `assembly_errors`, 120 warnings, `elastic_assembled=true`, `analysis_ready=false`, `nonlinear_ready=false`. `frame_objects=1312`, `frame_segments=3862`, `area_objects=725`, `shell_mesh_cells=10400`, `source_nodes=1101`, `mesh_nodes=11072`, downward gravity load **286419.758231 kN**.
- `wall_base_restraint_policy=SOURCE_ONLY`, `wall_base_support_count=76`. Earlier 32 / 76 / 97 alternatives remain unapproved as interchangeable supports. Verify source restraint roles and ETABS reaction distribution.
- `ETABS frame unique ID 1308` maps to preview topology tag 25049. The text `solver tag pending assembly` and `nonlinear hinge implementation remains gated` is a warning about mapping/status, **not proof** of ETABS member failure or actual solver-tag nonexistence. The ID workbook shows assembled frame element tags as a separate namespace. Join IDs from the assembled mapping, never assume preview == solver.
- V118 config: `floor_subdivisions=4`, slab flexural modifiers strength 0.25 and serviceability 0.35, `nonlinear_parameters_reviewed=false`, empty `nonlinear_materials_file` and `nonlinear_wall_fsam_tags`. Merely preparing MESH_08/16 config JSON does not assemble either case.
- `etabs_beam_weight_policy=GROSS_SECTION_LENGTH`; report estimates potential offset reduction 8652.444352 kN, explicitly unconfirmed. No physical weight correction should be silently activated.
- The Windows screenshots show older V116/V160 labels, while this repository's main branch includes newer changes. Record launcher path, source commit, imported component path, saved runtime path, export schema and active model SHA at every run.

## A — Distinguish hinge mechanisms (P0)
1. Export ETABS frame unique name, section, local axes, I/J release flags for U1/U2/U3/R1/R2/R3, partial spring stiffness, end offsets, insertion points, auto mesh connectivity and native end forces. Inspect **1308–1363** and other distinct brace families, including source sections/levels.
2. Compare to OpenSees assigned element **type**, node IDs, section, mass, transformation and released bending DOFs. Do **not** confuse a topology preview tag with actual solver tag or map all steel elements as pinned diagonals.
3. For an ideal axial-only brace, inspect `corotTruss` (geometrically nonlinear) or elastic truss when applicable. This removes moment transmission inherently; it does NOT model flexural buckling/plastic hinging. For flexural elastic members, use `elasticBeamColumn -releasey/-releasez` following verified ETABS local directions. Zero torsional stiffness must not be claimed to reproduce a CSI conventional frame with unstable dual R1 releases.
4. Independently bench-test pure axial extension, transverse perturbation, free-joint modes, equal/opposite end forces, member force sign and (where required) lateral buckling, connection stiffness and device series flexibility.
5. Keep nonlinear connection/material **gated** until section-specific physical model, cyclic constitutive data, FVD/BRB qualification and documented acceptance exist.
References: [CSI releases](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/Frame_Releases_and_Partial_Fixity.htm), [CSI end offsets](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm), [OpenSees elasticBeamColumn](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/elasticBeamColumn.html), [OpenSees corotTruss](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/CorotationalTruss.html), [OpenSees Truss](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/Truss.html).

## B — One canonical visualization service (P1, not implemented by this branch)
The shared UI in `components/model/id_audit.py` already injects common Plotly selection controls; refactor it rather than cloning four separate controls. All 3D views should use same aspectmode=data, camera presets, z-elevation convention, trace labels, height, legend grouping, virtualized per-storey categories, selected-ID overlay, restore/reset semantics and bounded hover fields. Avoid one legend entry per individual floor/load triangle: group by category + load pattern + storey and use compact legend or legendgroups. Use throttled pointer hover and avoid regenerating full figures when toggling layers. Verify click/hover returns source ETABS ID, preview topology tag, actual assembled solver tag and source/solver node mapping, with unmapped fields shown as **unavailable**, never fabricated.

## C — Non-destructive ID labels (P1, utility and tests added)
`components/model/display_ids.py` implements human-readable storey aliases only: N1 (base first), N101 (first level first), N202 (second level second), B701, C2501, CO/BT/CT, SW, FL. Position order is stable numeric native ID within each category and storey, **not** original ETABS point order. First 99 objects per storey use the requested 100-number stride; objects 100+ require `N-S01-0100`-style overflow to prevent collisions between levels. Original integer solver tags, ETABS IDs and saved case references stay unchanged. Explicit source classification required for CO/BT/CT; a diagonal is not automatically a conventional outrigger. UI/Excel integration and physical member taxonomy remain future gated work.

## D — Output isolation (P1, proposed, not yet migrated)
Never move the original EDB; do not rename the existing canonical Python launchers. A selected export folder should have a single manifest and isolated stages:
```text
01_ETABS_EXPORT/
  00_MANIFEST/{export_manifest.json,checksums.sha256}
  01_SOURCE/{source_metadata,geometry,material,sections,restraints}
  02_MAPPING/{nodes,elements,display_aliases,etabs_to_opensees}
  03_LOADS/{area,frame,self_weight,mass,load_patterns}
  04_VISUALIZATION/{3d_frames,3d_connectivity,3d_loads,floor_plan}
  05_AUDITS/{id_support,property_load,weight,overlaps}
  06_CONFIG/{model_config,mesh_case_presets}
  07_LOGS/{export,diagnostics,errors}
  08_PROCESSING/{intermediates,checksums,completion}
  09_REVIEW/{hinges,mesh_load_path,exceptions}
```
Keep downstream `02_MODEL`, `03_GRAVITY`, `04_LINEAR`, `05_NONLINEAR` etc. as independent stage outputs instead of mislabelling completed analyses as ETABS export. Implement **manifest-based canonical-path resolver with legacy flat-file compatibility** before changing writes. Use atomic temporary-file -> rename with hash and completed status; mark partial outputs invalid. Protect user's local data from being committed to the public repository.

## E — Vertical ShellMITC4 load path (P0, not yet validated)
V164 documentation states: source area pressure -> four-node shell-consistent nodal loading -> shell bending/shear -> shared nodes -> beams/walls/columns -> reactions; rigid diaphragm UX/UY/RZ constraint is not a vertical load-transfer mechanism. Existing `components/gravity/load_path_formulas.py` exposes member force and joint balance checks; mesh-case builder `components/gravity/mesh_cases.py` already stages and assembles 4/8/16 cases independently. Avoid reimplementing them or adding area pressure again as beam UDL. Compare **identically factored** ETABS and OpenSees cases; use source pattern-by-pattern gravity, not a mixed 0.3L seismic preload as a universal gravity benchmark.

Required evidence for each mesh resolution: source-model SHA, unique mesh-model SHA, node/element counts, shell and frame interface conformity at every beam span and wall boundary, restrained DOF audit, signed load sums and resultant moment checks, base reactions, joint residual norms, beam end Fz/M2/M3, wall cut forces, maximum slab deflection, diaphragm handling, time/solver settings and refinement ratios. Compare 4->8 and 8->16 on identical physical geometry. A successful mesh workbook (or a zero resultant error for applied nodal forces) does NOT imply correct stiffness transfer or ETABS parity. Check whether line loads already assigned to beams coexist with floor area loads, and audit both self-weight and overlap deductions without double-counting.

**Stale mesh configuration**: if config was changed after a run was assembled, decline to generate a misleading workbook and guide a fresh `build_case()` using the matching case directory. Existing code added this safeguard on main; the screenshot's popup alone does not establish a bug in the latest code.

## Acceptance table
| Gate | Status now | Proof needed |
|---|---|---|
| Source EDB unchanged | NOT TESTED | SHA before/after and ETABS OAPI read-only audit |
| Exact ID/solver mapping | PARTIAL | assembled tag and roundtrip/uniqueness checks |
| Category/storey labels | CODE ADDED / UI NOT WIRED | tests then GUI/Excel checked |
| Brace release equivalence | BLOCKED | member-specific ETABS releases and calibrated solver benchmark |
| Slab applied-load resultant | REPORTED, NOT INDEPENDENTLY VERIFIED | independent nodal force audit |
| Slab-to-frame interface | BLOCKED | edge-node geometry and frame segmentation evidence |
| 4/8/16 converged forces | BLOCKED | assembled + gravity solver outputs for all three |
| Gravity ETABS equivalence | BLOCKED | per-pattern and per-support reactions + beam/wall forces |
| Nonlinear earthquake acceptance | BLOCKED | project material evidence and full-record convergence |
| Folder migration | PROPOSED | manifest resolver compatibility/atomic-write regression tests |
| Uniform 3D UI | PROPOSED | click/hover/camera/filter/performance tests |

Do not merge this branch into main or mark any physical issue corrected until the above checks are executed on the actual Windows/ETABS model.

# 2026-11-16 — Beam segmentation, node 3751, FEM identity and 3D viewer review

**Status:** SOURCE-CODE MECHANISM CONFIRMED; SPECIFIC PAIR PARENT IDs AND NATIVE MESH STILL NEED CURRENT RUN DATA. No solver geometry, constraints, loads or tag IDs have been changed.

## What screenshots establish

- The user selected **assembled frame solver tags 100619 and 100620** and observed adjacent highlighted segments along a visually continuous beam.
- The user also selected **100251 / 100252** and a separately highlighted **node 3751**.
- These pictures do **not** establish that both consecutive tags belong to the same ETABS source object; inspect assembled `frames[i].object`, endpoints, and the intermediate node identity before labeling them a physical duplicate.
- The HTML selection inspector still shows an old `SELECTED: COLUMN ...` readout after a different beam/node highlight. This is a **viewer synchronization/selection-display issue**, not automatically a physical connectivity defect.
- Supplied 112,000-line pasted text contains role strings (mostly `beam joint`, `slab interior / other joint`, `wall joint`) but does not provide node IDs or incidences. Do **not** treat row numbers as node tags or this file as a verified joint-role map.

## Confirmed conversion mechanisms in current code

In `components/model/assembly.py`, the frame assembly loop scans **all** active model nodes and inserts a cut at any node inside the frame centerline using `1e-7` m transverse distance and `t` between endpoints. Then it creates one OpenSees frame child for each successive interval, with unique solver element tags. This is potentially necessary when a beam crosses conforming slab-shell mesh nodes, intersections or imposed concentrated actions. It can also split at a coincident but not intentionally connected node: present coordinate-only criterion does not independently establish physical connectivity. Distinct source objects can also have the same centerline; tag adjacency alone proves nothing.

`_mesh_areas` uses XYZ rounded to 8 decimals as an existing-node lookup. The resulting node may already belong to a source object. Non-one-to-one source identifiers and coincident but independently tagged nodes require audit before changing this operation. An unconditional geometry merge is NOT authorized.

## Required source-to-FEM identity contract

Keep all identities distinct:
1. ETABS source frame object ID (physical member, immutable);
2. ETABS source point name and original source/analysis mesh point classification;
3. OpenSees solver node tag (integer, immutable for matching results);
4. OpenSees solver element tag (integer, unique to each segment);
5. Display-only member alias, child index/count and node role.

Suggested display: `B1107 · part 1/2 | solver 100619 | ETABS frame <id>`; `B1107 · part 2/2 | solver 100620 | ETABS frame <id>`. Do **not** assume these example IDs are identical-parent until proven.

Suggested mutually comprehensible **incidence-derived** labels:
- `SOURCE_FRAME_COLUMN_JOINT` for a verified frame-column intersection source point;
- `FRAME_INTERSECTION_JOINT` for 2+ distinct incident source frame objects;
- `FRAME_SHELL_INTERFACE_NODE` when both frame and shell element incidence exists;
- `FRAME_INTERNAL_SUBDIVISION_NODE` when 2+ frame segments of one source object meet without other element incidence;
- `FRAME_END_NODE`, `SHELL_ONLY_NODE`, `WALL_MESH_NODE` (only on source wall evidence);
- `COINCIDENT_DISTINCT_NODES_REVIEW` and `NONCONFORMING_EDGE_REVIEW` **warnings**, not automatic constraints.

The same node can simultaneously serve multiple roles; record separate Boolean roles and incident elements instead of forcing a misleading single physical name. Physical beam/column joints and mesh-only mid-side nodes should be visually different in the viewer; keep native integer IDs for selection and provenance. Do not reassign existing OpenSees numerical tags.

## Decision tests for 100619/100620 and 100251/100252

For each pair export: two solver tags, `frame_elements[tag-100001].object`, source category/property, ordered `nodes`, `start/end`, beam length, shared node tag, shared node XYZ, every incident frame and shell element, and whether shared node is original ETABS point or generated mesh node. Require (a) same parent when claimed physical single beam, (b) continuous correct oriented endpoints and summed source length, (c) shared tag and compatible 6-DOF connections OR an explicit modelled interface, (d) matching stiffness/mass/loads and end offsets, (e) no duplicate element covering exactly the same interval without source justification.

For node **3751**, report XYZ and incident frames, shell panels, braces and column elements. Distinguish slab-edge connection requiring mesh split from an unnecessary isolated split. A 3D screenshot alone cannot identify the right physical action.

For every source beam, compute number of children and each true split cause, flag arbitrary disconnected coincidence and hanging shell T-junction, compare ETABS native frame auto mesh options, and perform one-bay force/displacement benchmarks before altering assembly. Confirm element loads are partitioned and mass/self-weight counted once.

## Literature and authoritative reference

- CSI ETABS, [Frame Auto Mesh Options](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/Frame_Auto_Mesh_Options.htm): default intersecting edges/joints generate internal analysis subdivisions; original frame object unchanged.
- CSI ETABS, [Divide Frames](https://docs.csiamerica.com/help-files/etabs/Menus/Edit/Edit_Frames/Divide_Frames.htm): manual object division differs from internal analysis subdivision; assigned loads/mass and end-zone releases are handled at appropriate ends.
- CSI ETABS, [Automatic Mesh Settings for Floors](https://docs.csiamerica.com/help-files/etabs/Menus/Analyze/Automatic_Mesh_Settings_for_Floors.htm): matching slab grids/joints and beam-edge compatibility.
- OpenSees, [Elastic Beam Column](https://openseesdocumentation.readthedocs.io/en/latest/user/manual/model/elements/elasticBeamColumn.html): each beam element has unique tag and two end node tags.
- OpenSees, [MP Constraints](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mpConstraints.html): multi-point constraints require explicit DOF meaning; not a substitute for compatible mesh without justification.
- Cook, Malkus, Plesha & Witt, *Concepts and Applications of Finite Element Analysis*, 4th ed., Wiley, 2001/2002, ISBN 9780471356059. Emphasizes compatibility, error, convergence, constraint assessment.
- Zienkiewicz, Taylor & Zhu, *The Finite Element Method: Its Basis and Fundamentals*, 7th ed., Elsevier, 2013, ISBN 9781856176330. Relevant to mesh generation, patch tests and FE convergence.
- Zienkiewicz & Taylor, *The Finite Element Method for Solid and Structural Mechanics*, 7th ed., Elsevier, 2013/2014, ISBN 9781856176347.

**Engineering acceptance:** Until source object IDs, shared tags and shell incidence are verified in the exact current assembled model, do not delete split nodes, renumber beam IDs or apply equalDOF to force geometry to look tidy. UI labels can change independently once model identities have been audited.

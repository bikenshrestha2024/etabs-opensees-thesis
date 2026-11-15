# 2026-11-15 — 32/76/97 support reaction discrepancy: engineering decision record

**Case:** exact uploaded comparison `1.0D + 1.0L`. **Status:** GLOBAL_GRAVITY_EQUILIBRIUM_PASS / PER_NODE_DISTRIBUTION_FAIL / NATIVE_ETABS_EQUIVALENCE_NOT_PROVEN.

## Verified from supplied numerical tables

- ETABS sum of source vertical reactions: **311367.313600 kN**; all three OpenSees models: **311367.31387955 kN**. Difference = **0.00027955 kN**.
- In the independently solved **32 support case**, signed 32-node reaction difference nearly cancels, but absolute discrepancy total = **37297.02723 kN**; mean absolute discrepancy = **1165.5321 kN/node**, RMS = **1322.6666 kN/node**; largest = **3041.26578 kN** at ETABS source points 263/264 (20.62% each).
- **76 source restraint records** all show all-six-DOF fixed flags `111111`: 32 primary, 44 additional wall-mesh locations. 44 have reported ETABS FZ = 0, but independently fixed OpenSees 76 model attributes **104463.01353 kN (33.55%)** reaction to those 44. **No inference of physically released support from ETABS FZ=0 is justified.**
- 97 support model adds 21 non-source fixed locations; diagnostic only.
- The point reaction table has 97 rows (32 primary, 44 other source, 21 diagnostic). Per-node matching must use ETABS unique object ID and mapped OpenSees tag, never numeric tag equality.
- The end-zone table records **1367** frame objects, including **450** I=0/J=0.8 m, **300** I=J=0.55 m, and **100** I=J=0.625 m, with rigid-zone factor 1.0 on all records. This is strong evidence that the ETABS beam/column rigid-end stiffness MUST be reconstructed and independently tested, not merely the beam self-weight length.
- The 11097-node displacement comparison gives maximum vertical displacement: **32: -21.017645 mm; 76: -20.737735 mm; 97: -20.732239 mm**. This shows the boundary choice changes deformation, but does not explain ETABS response without matched native displacements.
- MESH_04 workbook: sheets include 28000-cell surface-load rows, 112000 loaded-node path rows, 28000 seismic preload rows, 3862 member-weight rows, and 54 material unit formula rows. Spreadsheet identity and algebra do **not** prove solver load-path equivalence.

## Ordered causal hypotheses (NOT root causes established by this dataset)

**P0 — reaction-reporting identity and 32 vs 76 physical constraints.** ETABS wall auto-mesh can propagate restraints from corner joints to intermediate edge joints, and CSI auto-edge constraints transfer forces to master corners. The 44 ETABS zero FZ entries could therefore reflect object-vs-analysis node reporting or master/slave condensation, not unrestrained shell feet. Required: original EDB GetRestraint six flags, object vs analysis joint IDs/XYZ, generated mesh and edge propagation switches, master/slave/equation maps, source `JointReact` Object and Element at all six components, wall-base section cuts.

**P1 — frame end zone and overlapping concrete.** ETABS rigid factor = 1.0 for bending/shear over recorded offset lengths, but axial/torsion use total frame length. A simple clear-length element or lumped joint overlap subtraction is not equivalent. Check object dimensions/geometry/weights, split bending/shear integration from axial/torsion, frame local releases/transformations and support reaction changes in one-bay equivalent subassemblies. Never subtract audit-only 8652 kN or 19359 kN overlap candidates from already reconciled source loading.

**P1 — floor load distribution and compatibility.** ETABS slab membrane vs shell bending and auto 'uniform to frame' can transfer vertical load differently from OpenSees ShellMITC4 with `q*A/4` nodal loads. For distorted quads compute consistent `F_i=∫ N_i q dA` by quadrature, compare beam end shears, walls, floor load ledger, and mesh04/08/16 convergence. Check actual floor-shell area object load type and connectivity. `rigidDiaphragm(3)` constrains UX/UY/RZ, not UZ.

**P1 — shear-wall openings, split wall mesh and junction.** Check actual exported door void polygons, net concrete area and weight, wall thickness, mesh adjacency to beams/columns, corner duplicate nodes, shell normal/section/membrane/plate stiffness modifiers, wall-foundation edge kinematics and wall-base section resultant. An empirical effective wall area Aw used for NBC period is NOT the physical gross/net finite-element mesh area.

**P2 — braces and releases.** Verify ETABS brace assignments and source local end releases, geometric length, tension/compression axial stiffness, gravity participation, eccentricity and local axes. A pin-ended axial truss can approximate a hinged steel brace for an elastic gravity benchmark, but not automatic lateral/buckling/nonlinear equivalence. Run braces enabled/disabled in BOTH solvers on identical models to isolate their reaction contribution. Do not replace the research-model hinge basis solely to force matching.

**P2 — auxiliary mismatches.** Frame and wall elastic E, G, Poisson, self-weight density and stiffness modifiers, P-Delta geometric transformations, load factors, superposed joint/frame/shell loads, diaphragm/slab rotational constraints, model geometry, solver element axes, isolated zero-energy DOFs, and invalid duplicate tied DOFs.

## Controlled resolution experiments

1. Freeze original EDB, case, unit convention (kN-m-s), source SHA and converted model SHA. Prove the 311367.3136 kN 1D+1L load ledger by independent D and L contributions; do NOT substitute the 0.3L seismic mass/preload.
2. Extract original ETABS authored point restraints AND analysis-stage supported mesh DOF map, master/slave equations, six-component reactions and wall-base section cuts. Build a force-conserving **master-resultant aggregation** so the 32 ETABS reported objects can be compared with OpenSees 76 distributed nodal forces on equivalent physical foundation patches; include moment transformations about common origin.
3. Run 32-only independently fixed, source76 independently fixed, and an optional **CSI-equivalent constraint equation** prototype (only after CSI interpolation topology is known) on identical source load and mesh; compare full six-component global force/moment balance and member force flow. 97 remains sensitivity-only.
4. In parallel, validate single-column, column-beam, single-slab bay, pier with door opening, fixed-edge wall and brace-pair subassemblies with matching equivalent interface actions; compare stiffness matrix or load-displacement/reaction vectors; then enable effects one at a time.
5. Validate rigid-end offsets, local member releases, self-weight once, shell consistent loads and 04/08/16 convergence. Any observed whole-building reduction in mismatch is only evidence when perturbation experiments isolate a physical mechanism in both solvers.
6. Require native ETABS/OpenSees match of source support IDs and 6-DOF boundaries/constraints, global Fx/Fy/Fz/Mx/My/Mz, identical applied loads, wall base cuts, individual physical foundation resultants, member end forces and displacement, with justified numerical tolerances. **Global sum match alone is an insufficient acceptance gate.** Do not proceed to thesis nonlinear verification until baseline accepted.

## Official references and research

- CSI, [Wall Auto Mesh Options](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Wall_Auto_Mesh_Options.htm) — edge restraint propagation.
- CSI, [Auto Edge Constraints](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Auto_Edge_Constraints.htm) — interpolated connection and force transmission; warning for collinear frames.
- CSI, [End Length Offsets](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm) — effect on shear/bending only and brace default no offset.
- CSI, [Floor Auto Mesh Options](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Floor_Auto_Mesh_Options.htm) — floor vertical load transfer and compatibility.
- CSI, [ETABS Welcome manual](https://docs.csiamerica.com/manuals/etabs/Welcome%20to%20ETABS.pdf), discussion of shell bending vs membrane floor load transfer.
- OpenSees, [Rigid Diaphragm](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidDiaphragm.html) — in-plane rigid DOF, not vertical UZ.
- Dvorkin & Bathe (1984), continuum-based four-node shell, DOI [10.1108/eb023562](https://doi.org/10.1108/eb023562); Bathe & Dvorkin (1985), mixed interpolation plate bending, DOI [10.1002/nme.1620210213](https://doi.org/10.1002/nme.1620210213). These support shell formulation theory, not proof of equivalence for this specific model.
- Zhang et al. (2024), RC wall shear behavior under axial tension-flexure-shear, DOI [10.1016/j.engstruct.2024.118774](https://doi.org/10.1016/j.engstruct.2024.118774), relevant later to nonlinear wall validation, NOT present gravity discrepancy calibration.

## Evidence and safety boundaries

This record is a read-only investigation of supplied CSV/XLSX and repository documents. It does not claim an ETABS v23 native rerun or an OpenSees executable native rerun. No EDB, proprietary structural geometry, raw support dataset or model input is committed to this public repo. A solver-side code change is not justified until the source-equivalence experiment discriminates these hypotheses.

Cross-references: `REVIEW_MAIN/01_GRAVITY/20261115_FULL_76_SUPPORT_REACTIONS_AND_NATIVE_DISCREPANCY.md`, `20261112_MESH_SUPPORT_AND_SLAB_TRANSFER_VALIDATION.md`, `20261115_V25_PRIMARY32_RESTRAINT_AND_OUTPUT_INTEGRITY.md`.

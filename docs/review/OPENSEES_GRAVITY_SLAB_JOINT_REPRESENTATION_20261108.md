# Official OpenSees documentation review: 3D ETABS gravity and joint-weight modeling

**Date:** 2026-11-08. **Status:** engineering review, not certified ETABS
equivalence. This is an evidence-backed recommended modeling basis for
the asymmetric-plan damped-outrigger RCC frame/core model.

## Core decision

Retain 3D frame elements, shell slab elements and connected core-wall
meshes for stiffness and displacement response. Independently compute
physical member/slab/wall self-weight and seismic masses, assigning the
physical joint intersection volume to one owner only. **Do not use the
beam's stiffness end offset, nor a structural element's section area,
as an automatic permission to remove overlapping dead weight.**

For source-ETABS fidelity, separately retain the ETABS clear-length
self-weight *convention* with its source offset and material-list audit;
do not stack it with a second three-dimensional volume-union deduction.

## Official OpenSees commands and what they solve

| OpenSees feature | Documentation | Use and limits |
| --- | --- | --- |
| `ShellMITC4` | https://openseespydoc.readthedocs.io/en/latest/src/ShellMITC4.html | Four-node, 3D, six-DOF shell, membrane plus plate-bending; keep for initial gravity validation; requires shared structural nodes |
| `ASDShellQ4` | https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/ASDShellQ4.html | Optional shell formulation sensitivity, especially distorted cells; do not swap during baseline validation without an independent convergence study |
| `rigidDiaphragm(3,...)` | https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidDiaphragm.html | Ties Ux, Uy, Rz only: Uz, Rx, Ry remain free for transverse slab bending; synthetic master is massless |
| `geomTransf('PDelta',tag,vecxz,'-jntOffset',...)` | https://opensees.github.io/OpenSeesDocumentation/user/manual/model/geomTransf/PDelta.html | Frame-end *kinematic* offsets, in global coordinates; do not reduce the gravity weight by `rigidZoneFactor` |
| `elasticBeamColumn` | https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/elasticBeamColumn.html | Frame stiffness E,A,Iy,Iz,G,J; `-mass` is mass per unit length, not automatic weight; verify that mass is counted once |
| `eleLoad` | https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/PlainPatternloadcommands/eleLoad.html | Frame uniform or point loads; 3D local axes; caution Corotational unsupported combination |
| `SurfaceLoad` | https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/SurfaceLoad.html | Pressure **normal** to shell/brick face; gravity global -Z is not generally normal to vertical walls; not a cure for arbitrary gravity pressure mapping |
| `constraints('Transformation')` | https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/constraint/TransformationMethod.html | Suitable for multiple-point constraints but no chained retained/constrained nodes, and fixed nodes must use `fix`; audit diaphragm membership |
| `beamColumnJoint` | https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/BeamColumnJoint.html | Two-dimensional joint panel, can be used within 3D but transfers joint deformation only in element plane, **not** an automatic volumetric 3D joint-weight correction |
| `Joint2D` | https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/Joint2D.html | Two-dimensional joint idealization, not replacement for 3D asymmetric-core connections or self-weight ownership |

## Existing repository implementation and risks

The elastic converter in `components/model/assembly.py` currently uses:
- `ShellMITC4` slabs/walls with a massless `ElasticMembranePlateSection`
  (density argument 0); gravity load and mass are assembled separately
  from source loads and material unit weights.
- `rigidDiaphragm(3,...)` for Ux, Uy, Rz; primary/master node is
  fixed only in Uz, Rx, Ry. Check source diaphragm membership, shell
  boundary mesh sharing, and transformation constraint chains.
- Frame `geomTransf('PDelta',tag,*basis[2])` **without**
  `-jntOffset`; it currently does NOT reproduce ETABS rigid end zones
  in frame stiffness, regardless of the source `GetEndLengthOffset`
  metadata captured for self-weight.
- Equal quarter nodal surface loads in `surface(pattern,cell,total)`.
  This is exact for uniform pressures on rectangular mesh cells but
  requires a consistent integration/mesh check for distorted quads.
- Source-derived `ops.mass(n,m,m,m,0,0,0)`, while shell-section density
  and frame-element `-mass` are both zero/unspecified; do not switch
  those on without removing the corresponding nodal mass. The
  historical `GROSS_SECTION_LENGTH` and independent mass factors
  remain distinct from the full gravity 1.0D+1.0L profile.
- The physical intersection audit in
  `components/model/joint_volume_ownership.py` assumes centered
  solids. The ETABS beam snapshot showed `CP 8 - Top Center`;
  the present approximate audit is **not** physical geometry ground
  truth. Its ~19,358.527 kN potential overlap MUST NOT be applied.

## Recommended model tracks

1. **ETABS fidelity (gravity baseline)**: preserve ETABS sources,
   explicit restraint/mesh options, fixed original ETABS support nodes,
   full DL+LL and source material list. Activate `ETABS_BEAM_CLEAR_LENGTH`
   only after comparing actual source end offset metadata and beam
   material-weight line items. Do not additionally subtract slab-beam
   volume; check if this mismatches physical solid geometry and
   document the distinction.
2. **Physically unique weight (research sensitivity)**: explicitly
   reconstruct physical 3D solid placement for slab, column, beam
   and wall from section dimensions and ETABS insertion point offsets.
   Model shell/slab reference surface and true top/bottom levels;
   clip walls around actual openings; compute the union of volumes
   assigning each intersection one owner, with material-aware
   volumetric calculations. Apply net weights as gravity loads and
   matching seismic masses, but retain intended frame/shell
   structural stiffness. This must be a separate source-verified
   analysis configuration; do NOT combine its deduction with a
   clear-length beam-weight deduction.
3. **Joint kinematics study**: separately use validated
   `geomTransf('PDelta',...,'-jntOffset',...)` for **stiffness**. Compare
   gravity deflections, beam end moments, modal T1, participating masses
   and response spectrum; do not assert this is equivalent to
   simply taking `L_clear` for weight.

## Required acceptance tests (not implemented by this review)

- Small 6 m, 600×800 mm beam, 550 mm ETABS end offsets, CP8 top-centre
  and 150 mm slab: verify actual vertical solid coordinates and
  beam/slab/column intersection volumes, plus slab reference plane.
- Test overlapping beam-column-slab/wall union volumes; prove total
  removed weight equals the volume union once, with equal material
  densities for single-material overlaps. Audit mixed densities and
  re-entrant corner openings explicitly.
- Single shell floor panel with exact total qA, deflection and four
  reactions; compare to same frame supports with and without diaphragm.
- Three-dimensional one-bay subframe with wall: compare ETABS and
  OpenSees original support Rz, UZ and beam end actions using the
  *same gravity load and restraint arrangement*.
- Use actual ETABS source point mapping, not a coordinate-only match,
  for the 76 original supports. Audit the 44 ETABS null-line-only
  points with zero reaction and the current OpenSees support
  connectivity before evaluating roof drift/modal/RSA.
- Check global force and moment equilibrium, self-weight per component,
  non-self-weight load-pattern ledgers, final gravity and active
  seismic mass. Run both full gravity and 0.3 live seismic
  preload **as different load combinations**.

**Acceptance:** No "matched ETABS" flag is allowed from a perfect
global reaction alone, nor from a numerical overlap estimate tuned to
the ETABS gravity result. Require component weights, actual mesh
connectivity, nodal reactions, gravity displacements and independently
verified source geometry.

# Single-owner RCC joint volume self-weight / mass ledger

[REF components/model/joint_volume_ownership.py]

**Objective:** Reinforced-concrete volume at beam-column, wall-column, or
slab-beam intersections is owned by one geometric component, not counted in
every overlapping element. This does NOT change frame stiffness, rigid end
zones, rigid diaphragm constraints or wall-base restraints.

**Priority**: COLUMN > SHEAR WALL > FLOOR > BEAM. Braces (especially hollow
steel SHS) and unmodeled connection plates are excluded and retain their
independent gross weight. Two coincident RCC solids with the same priority
are resolved deterministically by ETABS source object and child index.
For an RCC solid, the algorithm subtracts the union of all higher-priority
axis-aligned physical solids, using an exact rectangular-box partition,
rather than subtracting each intersection twice. All before/after weights
are expressed in kN and volumes in m³.

For example, on a 6.0 m long 600×800 mm RCC beam the gross concrete weight
is 72.0 kN at 25 kN/m³. End offsets of 550 mm each imply a 4.9 m clear span,
but this alone does not justify subtracting 13.2 kN: a slab may own part
of the overlapping volume, and the ETABS `Auto` self-weight option is not
equivalent to the rigid-zone factor. A single-owner union checks all
supported intersections to prevent repeated subtraction or triple counting.

## Export settings

The generated `OpenSees_Complete_Model_Config_V118.json` supports:

- `"joint_volume_weight_policy": "AUDIT_ONLY"` (**default**): original
  gross self-weight and lumped seismic mass remain exactly unchanged.
  If the audit supports geometry, it generates
  `OpenSees_Joint_Volume_Ownership_Audit.json` and
  `OpenSees_Joint_Volume_Ownership_Audit.csv` in the export folder,
  with per-source-object gross/net volumes and weights.
- `"joint_volume_weight_policy": "VERIFIED_SINGLE_OWNER"` together with
  `"joint_volume_geometry_verified": true`: explicit opt-in correction
  to both equivalent self-weight nodal gravity loads and source-derived
  seismic mass, so those quantities remain consistent. It never rescales
  the frame or shell **stiffness**. It rejects unresolved axis orientation,
  nonrectangular sections, missing physical dimensions, and ETABS frames
  with noncentroid `GetInsertionPoint` cardinal points. Your screenshot
  includes a beam with `CP 8 - Top Center`, so this mode MUST remain
  blocked until physical solid placement is explicitly reconstructed.
  These geometry checks do not certify ETABS `Auto` weight calculation.
  When enabled, retained-to-gross volume fractions are applied uniformly
  over each source element's equivalent load. Local support/moment
  distribution can differ from exact load-centroid placement and therefore
  requires a separate reaction/beam-force test.

## Exact geometries supported

- Rectangular RCC **columns** along global Z
- Rectangular RCC **beams** along global X or Y
- Axis-aligned quadrilateral wall shells with source physical thickness
- Axis-aligned horizontal floor shells with source physical thickness

The net physical volume of a joint is counted once by order of priority.
It is **not** a CAD/BRep Boolean union of arbitrary rotated solids, nonuniform
walls, reentrant corner details or noncentroid insertion geometry.
Missing coordinate/insertion provenance must block activating corrected
gravity weights. A diagnostic-only calculation cannot be labeled an
ETABS-validated correction.

## OpenSees documentation and CSI source

OpenSees has explicit `load`/`eleLoad` patterns: it does not magically
deduct concrete at intersecting finite elements. Refer to
[OpenSees eleLoad](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/PlainPatternloadcommands/eleLoad.html)
and
[OpenSees Elastic Beam Column](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/elasticBeamColumn.html).
Rigid offsets are a separate stiffness/geometric-transform issue, explained
in
[Rigid Joint Offsets](https://openseesdigital.com/2020/11/19/rigid-joint-offsets/).
CSI describes offset lengths and rigid-zone factors separately in
[ETABS End Length Offsets](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm).
`GetEndLengthOffset` API alone does not establish ETABS's actual `Auto`
self-weight rule for each source object.

## Required acceptance checks before turning on correction

1. Verify the original ETABS physical section positions, **including CP 8
   Top Center** beam insertion and slab physical z levels.
2. Compare physical RCC net volumes across ETABS, OpenSees, and drawings.
3. Audit frame offsets, `Self Weight Option`, column/beam intersections,
   slab-beam double counts, wall openings and disjoint floors.
4. Compare source self-weight total to the candidate net-weight audit:
   the difference **8,680.475 kN** is a target discrepancy, NOT an adjustment
   or an acceptance threshold.
5. Rerun both independent full gravity wall-base strategies, check applied
   loads versus reactions and compare original mapped 76 ETABS support
   locations, floor deflections and storey reaction distribution.
6. Rerun modal/RSA/NLTHA if the corrected source-derived seismic mass is
   accepted for the production model; do not silently propagate research
   calibration without review.

Tests: `python tests/verify_joint_volume_ownership.py`.

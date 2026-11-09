# Gravity physical quantity and RCC joint-overlap investigation — 2026-11-09

## Governing comparison and evidence status

Primary numeric reaction reference: the **32 ETABS reaction-bearing source joints**,
`ETABS_NONZERO_REACTION_DIAGNOSTIC`, with original ETABS unique IDs mapped to
OpenSees tags. The other **44 zero-reaction ETABS points are retained as
wall-mesh/constraint evidence**, not erased or reclassified as free DOFs
without verifying their ETABS analytical restraints. The 76-point and 97-point
OpenSees cases remain sensitivity comparisons.

Observed source evidence in user-supplied `Gravity_ETABS_OpenSees_Evidence_V04`:
- OpenSees applied/reacted: 320019.7582311494 kN.
- Direct ETABS working-copy analyzed source EDB: 311367.31387954176 kN.
- Difference: +8652.4443516077 kN (+2.779% relative to ETABS).
- ETABS Dead 263367.313879543 kN and Live 48000.000000 kN.
- OpenSees `Live` 48000.000000 kN, **non-live** 272019.758231 kN.
- OpenSees self weight 209919.758231 kN; applied area loads
  84000 kN (including 48000 Live + 18000 Floor Finish + 18000 Partition);
  frame loads 26100 kN (Wall pattern).
- Original 750 BEAM objects / 3300 meshed beam segments:
  gross 53984.054880 kN; source offset candidate **8652.444352 kN**.
  The beam-clear-only scenario therefore reproduces the ETABS global total
  to floating-point precision. This is numerical evidence for investigation,
  **not proof of actual native ETABS per-member self-weight treatment**.

## Source RCC geometric union

The axis-aligned centered-box RCC ledger reports (gross, potential overlap) kN:

| Element | Gross | Potential overlap |
| --- | ---: | ---: |
| Column | 56733.867675 | 0 |
| Shear wall | 52934.364936 | 1709.495082 |
| Slab | 44986.712403 | 2500.694192 |
| Beam | 53984.054880 | 15148.338178 |
| TOTAL | 208638.999894 | 19358.527452 |

Single-owner priority `COLUMN > SHEAR WALL > FLOOR > BEAM`. Ownership
attributions from the exact current source ledger are kN:
`BEAM_OVERLAPS_COLUMN=8479.395465`,
`BEAM_OVERLAPS_FLOOR=5966.700132`,
`BEAM_OVERLAPS_SHEAR WALL=529.043738`,
`BEAM_OVERLAPS_BEAM=173.198843`,
`FLOOR_OVERLAPS_COLUMN=986.216516`,
`FLOOR_OVERLAPS_SHEAR WALL=1514.477675`,
`SHEAR WALL_OVERLAPS_SHEAR WALL=1709.495082`.
The union is not geometrically verified; real openings, insertion-point
eccentricity, beam/slab relative elevations, and frame cross-section rotations
may change the quantities. The union-only scenario predicts 300661.230779
kN, **10706.083101 kN below ETABS**. Do NOT subtract this union on top of
beam offsets.

## Physical takeoff rules to verify on original ETABS quantities

1. **Columns:** full story-joint-to-story-joint length `A_col*H*gamma`
   can be assigned to columns as the first owner of intersection volumes.
   This is a physical ownership choice; it is not proof of the ETABS analysis
   self-weight rule. Columns with transitions, offsets, splices and nonstandard
   sections require per-object inventory.
2. **Beams:** test `A_beam*(Lcenter - end_i - end_j)*gamma`, using actual
   `FrameObj.GetEndLengthOffset` for EACH original object. Endpoint column
   half-width is appropriate only where the recorded actual source connection
   supports it. Beams connected to walls/beam junctions may differ. Never
   multiply by the 3300 mesh segment count as if they were 3300 source beams.
3. **Slabs:** use original polygon area minus *actually intersecting column
   and wall footprint volumes* (the physical slab's z interval must overlap
   that member at the floor). Source slab polygons may already exclude
   openings. A second footprint deduction when holes are already present
   is **prohibited**. Beam-slab overlap must be assigned ONCE in a complete
   union; deducting it again after clear beam ends is wrong.
4. **Shear walls:** wall polygon `A_wall*t*gamma` over actual story
   elevation; wall-wall intersections and door/window openings must be
   subtracted precisely once under an explicit volume ownership priority.
   Source wall shell patches can already exclude openings. Never infer solid
   concrete above/beside an opening where the original geometry is void.
5. **Braces:** currently `self_weight_brace=1280.758352 kN` in OpenSees.
   ETABS auto frame end-offset rule defaults to zero for braces, not
   necessarily the physical brace/gusset trimmed length. SHS members are
   not included in the RCC rectangle solid union; record independently and
   obtain native brace section, weight and connection offset evidence.

## Relevant official CSI references

- ETABS [End length offsets](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm): auto beam offsets depend on connected columns, default brace auto offset is zero, rigid zone controls bending/shear flexibility.
- [CSI Analysis Reference Manual](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf), frame Self-Weight Load chapter: frame self-weight is weight density multiplied by area, applied along the frame including end offset zones.
- ETABS [Self weight multiplier](https://web.wiki.csiamerica.com/wiki/spaces/kb/pages/2001661): preserve single load-pattern allocation.

## Implemented safety and files

`components/gravity/joint_weight_reconciliation.py` audits exclusive
CURRENT_ASSEMBLED, BEAM_CLEAR_LENGTH_ONLY and GEOMETRIC_RCC_SINGLE_OWNER_ONLY
scenarios without changing ANY load, mass, support, stiffness, seismic
scaling or selected original EDB. It verifies arithmetic source solids,
the original beam object/mesh distinction, slab quantity, category
conservation and exclusive geometry attribution, and writes:

- `Gravity_Joint_Weight_Reconciliation.json`
- `Gravity_Joint_Weight_Scenarios.csv`
- `Gravity_Joint_Weight_By_Solid.csv`
- `Gravity_Source_Components_Audit.xlsx` > Exclusive weight scenarios

Outputs are written beside each latest gravity case. The evidence bundle
collects these outputs for 32, 76 and 97 diagnostic runs when available.
Legacy exports missing full source evidence remain marked incomplete.

**No physical correction was activated**: before selecting one, obtain
the source EDB's native beam/column/slab/wall/brace material quantities and
self-weight rules **per source object**, plus ETABS original-area geometry
and restraints. Validate each original source ID and the total global Dead
and Live loads separately. Under a model correction, rebuild and rerun
gravity, modes, and the entire nonlinear preload; previously calculated
reaction and transient results become stale.

## Regression test commands

From repository root:

```powershell
python tests/verify_gravity_joint_weight_reconciliation.py
python tests/verify_gravity_joint_overlap_integration.py
python tests/verify_gravity_source_load_reconciliation.py
python tests/verify_joint_overlap_review.py
python tests/verify_joint_volume_ownership.py
```

These are code checks and synthetic quantity conservation tests, **not**
native ETABS/OpenSees physical acceptance.

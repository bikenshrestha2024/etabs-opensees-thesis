# Slab self-weight, shell meshing and RCC joint-volume ownership — engineering implementation review

**Project:** ETABS v23 → OpenSeesPy elastic ULS validation before MRSM / NLTHA of a 25-storey asymmetric damped-outrigger building.

**Module:** `components/gravity/slab_self_weight_audit.py`. Reviewed with `components/model/assembly.py`, `components/model/joint_volume_ownership.py` and `components/gravity/joint_overlap_review.py`.

## 1. Exact physical slab self-weight equation

For every original ETABS floor polygon `i`:

`W_slab,i = A_source,i × t_physical,i × gamma_material,i × ETABS_self_weight_pattern_multiplier × gravity_case_factor`.

All dimensions are **kN, m, s**. For a homogeneous ordinary RCC slab, `gamma` is the ETABS source material **weight per unit volume** in kN/m³. Do not assume exactly 25 if the ETABS material uses 24.992618. Example: 6 × 6 × 0.150 × 25 = **135 kN** for a single 36 m² slab, before any area-load superimposed dead or live loads. Each element's gross physical weight is calculated ONCE before distribution to the discretized nodes. The floor pressure from finishes / partition / imposed loads is an additional *separately sourced* assigned load, not another RCC slab weight.

**Actual repository algorithm:** `_mesh_areas()` partitions each original ETABS floor parallelogram into quads. `cell.area` is the corresponding area fraction of the *original source polygon*, regardless of mesh refinement. In `prepare_complete_export()`, original self-weight load is `-source_multiplier * cell.area * section.physical_thickness * source_material.weight_density`. `surface()` adds one-quarter of that resultant to the four cell nodes, preserving total applied vertical force. `ShellMITC4` is the stiffness element; it does **not** independently apply a second self-weight when this explicit nodal load is used. In this converter, elastic shell section `rho=0` is used to avoid duplicating mass because the assembled seismic mass ledger is independently assigned with `ops.mass()`. A genuine alternative shell-body-force formulation would require removing/reconciling the explicit nodal weight and mass sources.

**Not a self-weight correction:** ETABS slab flexural `m11/m22/m12=0.25` and other NBC ULS cracked-section stiffness factors do not multiply physical volume or material weight. Likewise, reduced ETABS wall stiffness does not remove 50% of the wall dead weight.

## 2. Independent area-mesh integrity / duplicate check

The new audit independently constructs each original slab polygon from ETABS source node coordinates, then maps each meshed quad into original local affine coordinates `(u,v)`. It verifies:

1. Unique original ETABS floor object ID and matching meshed slab object ID.
2. Original slab is a nondegenerate four-node parallelogram (unsupported source polygon must fail).
3. Each child has four geometrically valid vertices, a finite positive area, lies in its original floor plane and within its parent polygon.
4. Each child covers an axis-aligned rectangle in the original local `u-v` coordinate grid, with its *calculated geometric* area equal to the recorded `cell.area`.
5. No positive-area intersection between two child rectangles. Together with equality of all child areas to the original source area, this means the source floor polygon has neither a gap nor a duplicate mesh area.
6. Slab physical thickness and material weight density remain unchanged across one parent polygon's mesh cells.
7. Sum of child `area × t × gamma` is exactly the parent `area × t × gamma` to numerical tolerance.
8. Geometric ownership audit reports any positive `FLOOR_OVERLAPS_FLOOR` solid intersection; where present this is flagged as a duplicate source RCC floor volume and blocks purported source validation.

A duplicated shell cell with misleadingly correct `cell.area` is rejected because its actual XYZ polygon duplicates another child. A source slab polygon outside the supported meshing scheme is rejected; the exporter is **not allowed to invent another area** or compensate by scaling loads.

## 3. Beam–column–slab physical intersection

A typical RC beam 600 mm wide × 800 mm overall deep and slab 150 mm thick has two conceptually different ways to account for physical volume:

* **Full isolated solids**: `V_beam = 0.600 × 0.800 × L` and `V_slab = A_slab × 0.150`. If physical solids overlap, their summed weight double-counts *that actual intersection* unless ETABS self-weight convention already excludes it.
* **Slab owns overlapping concrete**: for a beam fully below the top of an overlapping 150-mm slab over a verified common clear span, and with beam width fully within slab, the beam's unique extra volume might be `0.600 × (0.800 - 0.150) × L`, while the slab retains its full `A_slab × 0.150`. This gives a 650-mm *net additional beam depth*, **not** an instruction to reduce the slab thickness to 650 mm or to subtract the overlap twice.

The second formula is **only valid if measured 3D section placement confirms 150 mm of slab actually lies inside the 800 mm beam**. An ETABS `Top Center` insertion at a shell *mid-surface*, for example, need not have the full 150 mm of volume overlapping the beam; there could be only 75 mm of common slab depth depending on the actual physical reference-plane placement. Do not infer it from the cardinal-point number alone. The concrete beam end offsets, the slab-beam overlap along the beam, and the column-node overlap are different physical sets; their volumes must not be deducted independently and then added.

## 4. Beam–shear-wall–slab and three-wall core junction

At the core there may be **no beams framing into the wall**. In that region:

* `W_wall = sum(wall_panel_area × original_wall_thickness × gamma)` once.
* `W_slab = sum(floor_area × physical_slab_thickness × gamma)` once.
* When a 600-mm wall crosses a 150-mm slab, account for only the physical **wall–slab union intersection**, if proven. Do not invent a 600 × 800 beam at that location.
* At a three-wall intersection, count the union of the actual wall plates once. Triple overlap is not three independent joint cubes; inclusion–exclusion is essential.
* At a wall opening, exclude any genuinely missing wall polygon, not a hypothetical volume removed merely because a node happens to be an opening corner.

The existing `joint_volume_ownership.py` gives one physical volume to the first owner in the order `COLUMN > SHEAR WALL > FLOOR > BEAM`, retaining the remaining disjoint sub-volumes. This is a **project-specific engineering ownership policy, not a clause in NBC105:2025**. It works only for *validated centered axis-aligned rectangular solids* and keeps the **default policy `AUDIT_ONLY`**. The physical ETABS frame insertion offsets and shell physical midplanes are not automatically known. The named `VERIFIED_SINGLE_OWNER` load correction is never enabled merely because a geometric audit reports a nonzero intersection.

## 5. Why not automatically deduct 800−150 mm and beam end offsets

An overall RCC beam clear span measured between column/wall faces **and** a vertical slab-beam cross-section overlap refer to different dimensions. Removing all of both from nominal beam weight can subtract the same joint concrete twice.

For a true beam–column–slab junction, compute 3D union of original beam solid, column solid and slab solid, *or* independently reproduce CSI's verified self-weight length/depth conventions; do not combine arbitrary corrections. The existing exporter explicitly blocks using both `ETABS_BEAM_CLEAR_LENGTH` and `VERIFIED_SINGLE_OWNER` simultaneously.

The reported earlier 8,680.475 kN global discrepancy broke down in the earlier material-list review into approximately 8,652.444 kN RCC beam and 28.031 kN SHS brace differences. This strongly suggests a source beam **longitudinal length** convention, not proof that the whole difference is 150-mm slab overlap or 32 repeated joint cubes. All of those alternatives remain hypotheses pending native source EDB and per-material weight reconciliation.

## 6. Full gravity versus seismic mass / stiffness under NBC 105:2025

**NBC 105:2025 Clause 3.4 and Table 3-1**, *effective stiffness of cracked sections*, give ULS and serviceability **flexural stiffness factors**: beam 0.35, column 0.70, cracked wall 0.50, flat slab 0.25 for the ULS flexural examples. These affect the elastic analysis stiffness, not self-weight (the source property-level + object-level assignments must be independently reconciled).

**NBC 105:2025 Clause 5.2 and Table 5-1** prescribe *seismic weight*: dead load plus factored seismic live. Typical other occupancy live has factor 0.30 and roof imposed live is Nil for **seismic weight**. They do NOT replace the distinct full-gravity reference `1.0DL + 1.0LL`, which includes 100% of assigned roof live. Seismic preload and ULS design combinations are different cases and must not overwrite full-gravity validation load definitions.

**NBC 105:2025 Clause 3.6** contains the **structural load combinations**; neither this clause nor 3.4 tells an ETABS/OpenSees converter to delete 150 mm of beam concrete at every slab junction. The volume and joint ownership rules above are **source-model reconstruction and geometry-consistency engineering**, not a codally prescribed reduction.

## 7. Provenance and source documentation

* Official Government of Nepal NBC 105:2025 PDF (DUDBC / Kathmandu eBPS):
  https://ebps.kathmandu.gov.np/UploadFiles/NBC_105_2025_Sesmic_Design.pdf
  — sections 3.4, 3.6 and 5.2.
* CSI ETABS/SAP2000 **Analysis Reference Manual**, Shell Element → *Self-Weight Load* and *Mass*, and Material Properties → Weight Density:
  https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf
  — shell self-weight = weight density × membrane physical thickness, times area.
* CSI ETABS **User's Guide**, Load Patterns → Self-Weight Multiplier:
  https://docs.csiamerica.com/manuals/etabs/User%27s%20Guide.pdf
  — source-pattern multiplier allocates self-weight; when repeated in two patterns used together, double weight can occur.
* CSI **Property Stiffness Modification Factors**:
  https://docs.csiamerica.com/help-files/etabs/Menus/Define/Property_Stiffness_Modification_Factors_Form.htm
  — stiffness and weight modifiers are distinct inputs.
* OpenSeesPy `ShellMITC4`:
  https://openseespydoc.readthedocs.io/en/latest/src/ShellMITC4.html
* OpenSeesPy `ElasticMembranePlateSection`:
  https://openseespydoc.readthedocs.io/en/latest/src/elasticMembranePlateSection.html
* Michael H. Scott (2022), *Element Self-Weight*, OpenSees Digital:
  https://openseesdigital.com/2022/11/02/element-self-weight/

## 8. What the new evidence means

Outputs are saved in the original model export folder and included in the gravity evidence bundle:

* `Gravity_Slab_Self_Weight_Audit.xlsx` — per-object area, thickness, unit weight, gross slab self-weight, actual cell load sum, potential joint overlap and engineering gates.
* `Gravity_Slab_Self_Weight_Audit.csv` / `.json` — repeatable numerical source data.
* Existing `Gravity_Joint_Type_Overlap_Review.xlsx` — beam, column, slab and wall intersection categories.
* Existing `OpenSees_Joint_Volume_Ownership_Audit.csv` — actual represented candidate solids.
* `Gravity_Source_Components_Audit.xlsx` — final selected pattern factors, physical self-weight and other applied gravity sources.

**Acceptance restrictions**: The audit can verify area conservation, no mesh-cell duplication, physical slab weight and internally consistent source load sums. It cannot establish fully correct ETABS material weight unless native ETABS section, source physical insertion planes, section/object weight modifiers, and material-list totals are independently checked. Leave reported `ETABS_equivalence = NOT_VALIDATED` until those external validations pass.

**Version note:** ChatGPT GPT-6 authored the additive audit and documentation; historical code authorship is not inferred.

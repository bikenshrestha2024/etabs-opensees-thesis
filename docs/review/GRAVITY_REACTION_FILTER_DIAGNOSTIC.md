# ETABS zero-reaction support filter: diagnostic only

The original completed ETABS 1. DL + LL Joint Reactions table contains 76 mapped base points. In the supplied comparison, 44 points have FZ=0 while OpenSees assigned reactions at those points. The user requests two separately displayed support lists:

* **ETABS Reaction Validation** — an opt-in, reaction-filtered **diagnostic** gravity run, using only mapped points with |ETABS FZ| > 0.000001 kN. This does **not** prove true native ETABS restraint equivalence. Current evidence suggests 32 retained and 44 released, but counts are always read from the selected workbook.
* **ETABS Node Position / Continuous** — the pre-existing 76-mapped-node `ETABS_SOURCE_SUPPORTS` case, unchanged in its support assignment.
* **Continuous Wall Base (97)** — the original `CONTINUOUS_WALL_BASE_FIXED` sensitivity, preserved independently, including the existing 21 additional foundation mesh supports.

## Essential engineering qualification

ETABS FZ=0 is **not** proof of a free UZ restraint. Internal wall auto-mesh constraints may transfer nodal reactions to other points, and a boundary node can be fixed yet have a zero reported reaction. This diagnostic intentionally removes all fixed DOFs at the 44 zero-force points, which is an idealization and may cause loss of support, mechanisms or a different reaction redistribution from ETABS. It must **not** be called a validated ETABS replica until the original EDB `PointObj.GetRestraint` flags, internal wall mesh constraints, and source structural support conditions have been verified.

The source case uses the *same 1.0DL+1.0LL loads*, including assigned roof live, and uses no seismic live reduction. It does not alter the original source model JSON, the 76-support baseline, the 97-support baseline, seismic masses, stiffness or nonlinear wall models.

## Workflow

1. Update the repository and restart the application. Select the original exported gravity model and select the completed original ETABS *Joint Reactions* XLSX/CSV for `1. DL + LL` (not `1.5(DL+LL)`).
2. Click **Read BOTH support lists and gravity load**. Two independent read-only rows show the reaction-filtered and original mapped-source node lists. The third dropdown selection preserves the original 97-support model.
3. Choose **ETABS Reaction Validation** and **Run gravity, check, freeze + export**. It runs only if every source support maps uniquely to a base ETABS point with one finite original reaction. The solver saves to a new `Gravity_Reaction_Diagnostic/<timestamp>/` subfolder.
4. The new folder writes `ETABS_Nonzero_Reaction_Support_Audit.json` (original/retained/released points, ETABS unique names, FZ, table path and SHA256) plus normal gravity outputs and an evidence ZIP. Solver failure remains a failure; do not relabel it a PASS.
5. Choose **ETABS Node Position / Continuous** for the original 76-support case. Choose **Continuous Wall Base (97)** for the original 97-support case. The existing **Run existing 76-support + 97-support cases** button remains compatible with historical dual-run evidence and the offline comparison.

## Acceptance tests

* Source table must have the exact native combination `1. DL + LL`, complete base reaction rows, no duplicate ETABS point unique names, no ambiguous point mapping and no missing source support.
* ETABS zero reaction requires **non-validated diagnostic** flag, even when the gravity solver converges or integrated reactions look similar.
* Compare point 264 / OpenSees 41 and the three connected wall-region totals, wall openings, beam offset self weight, ULS wall stiffness and actual native source restraints. A near-perfect global gravity total is not enough to prove the structure is equivalent.
* Validate true source support flags and the ETABS edge-constraint propagation option before making the 32-node pattern a physical model boundary condition.

References:
* [OpenSees Fix Command](https://openseespydoc.readthedocs.io/en/latest/src/fix.html)
* [Existing ETABS reaction comparison](GRAVITY_ETABS_COMPARISON.md)
* [Existing wall mesh restraint audit](GRAVITY_3D_WALL_MESH_RESTRAINT_AUDIT.md)
